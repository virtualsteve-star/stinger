"""
Check endpoint for evaluating content against guardrails.
"""

import logging
import threading

from fastapi import APIRouter, HTTPException

from stinger.api.models import CheckRequest, CheckResponse
from stinger.api import metrics
from stinger.core.conversation import Conversation
from stinger.core.pipeline import GuardrailPipeline

logger = logging.getLogger(__name__)
router = APIRouter()

# Thread-safe cache for pipelines to avoid recreation
_pipeline_cache = {}
_pipeline_cache_lock = threading.RLock()


def get_pipeline(preset: str) -> GuardrailPipeline:
    """Get or create a pipeline for the given preset (thread-safe)."""
    # Fast path: check if already cached (double-checked locking pattern)
    if preset in _pipeline_cache:
        return _pipeline_cache[preset]
    
    # Slow path: create pipeline with lock
    with _pipeline_cache_lock:
        # Check again in case another thread created it
        if preset not in _pipeline_cache:
            try:
                _pipeline_cache[preset] = GuardrailPipeline.from_preset(preset)
                logger.info(f"Created pipeline for preset: {preset}")
            except Exception as e:
                logger.error(f"Failed to create pipeline for preset {preset}: {e}")
                raise HTTPException(status_code=400, detail=f"Invalid preset: {preset}")
        return _pipeline_cache[preset]


@router.post("/check", response_model=CheckResponse)
async def check_content(request: CheckRequest):
    """
    Check content against guardrails.

    This endpoint evaluates user prompts or LLM responses against
    the configured guardrails and returns an action decision.
    """
    try:
        # Get pipeline for the requested preset
        pipeline = get_pipeline(request.preset)

        # Create conversation context if provided
        conversation = None
        if request.context:
            # Extract participant information
            user_id = request.context.get("userId", "anonymous")
            bot_id = request.context.get("botId", "unknown-ai")
            session_id = request.context.get("sessionId")

            # Extract participant types (with sensible defaults)
            user_type = request.context.get("userType", "human")
            bot_type = request.context.get("botType", "ai_model")

            # Build metadata for audit trail
            metadata = request.context.copy()
            metadata["participants"] = f"{user_id} ({user_type}) <-> {bot_id} ({bot_type})"

            conversation = Conversation(
                initiator=user_id,
                responder=bot_id,
                initiator_type=user_type,
                responder_type=bot_type,
                conversation_id=session_id,
                metadata=metadata,
            )

        # Check the content based on type
        if request.kind == "prompt":
            result = await pipeline.check_input_async(request.text, conversation=conversation)
        else:  # response
            result = await pipeline.check_output_async(request.text, conversation=conversation)

        # Record guardrail metrics
        details = result.get("details", {})
        if details:
            # Calculate per-guardrail time (approximate)
            total_time = result.get("processing_time_ms", 0)
            per_guardrail_time = total_time / len(details) if details else 0
            
            for guardrail_name, guardrail_result in details.items():
                metrics.record_guardrail_check(
                    guardrail=guardrail_name,
                    pipeline_type=request.kind,
                    blocked=guardrail_result.get("blocked", False),
                    duration_ms=per_guardrail_time
                )
        
        # Convert to response format
        action = "block" if result["blocked"] else "allow"
        if result.get("warnings") and not result["blocked"]:
            action = "warn"

        # Extract guardrail names from details
        guardrails_triggered = list(details.keys()) if details else []
        
        return CheckResponse(
            action=action,
            reasons=result.get("reasons", []),
            warnings=result.get("warnings", []),
            metadata={
                "guardrails_triggered": guardrails_triggered,
                "processing_time_ms": result.get("processing_time_ms", 0),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking content: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
