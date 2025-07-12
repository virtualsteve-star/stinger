"""
Check endpoint with integrated security and rate limiting.

This version uses the core engine's rate limiting system.
"""

import logging
import threading
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request

from stinger.api.models import CheckRequest, CheckResponse
from stinger.api.security import verify_api_key_with_rate_limit
from stinger.core.conversation import Conversation
from stinger.core.pipeline import GuardrailPipeline

logger = logging.getLogger(__name__)
router = APIRouter()

# Thread-safe cache for pipelines to avoid recreation
_pipeline_cache = {}
_pipeline_cache_lock = threading.RLock()


def get_pipeline(preset: str) -> GuardrailPipeline:
    """Get or create a pipeline for the given preset (thread-safe)."""
    # Fast path: check if already cached
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
async def check_content(
    request: Request,
    check_request: CheckRequest,
    api_key: str = Depends(verify_api_key_with_rate_limit),
):
    """
    Check content against guardrails with authentication and rate limiting.

    This endpoint:
    1. Verifies the API key
    2. Checks rate limits using the core engine
    3. Evaluates content against configured guardrails
    4. Returns an action decision

    The rate limiting is integrated with the core Stinger engine, so rate limits
    are shared across all Stinger components (API, SDK, etc.) for the same key.
    """
    try:
        # Get pipeline for the requested preset
        pipeline = get_pipeline(check_request.preset)

        # Create conversation context if needed
        conversation = None
        if check_request.context:
            # Use API key as part of the user ID for conversation tracking
            user_id = check_request.context.get("userId", f"api-user-{api_key[:8]}")

            # Create conversation with rate limiting if specified
            rate_limit_config = check_request.context.get("rate_limit")
            conversation = Conversation.human_ai(
                user_id=user_id,
                model_id="gpt-4",  # Default, not used for checking
                rate_limit=rate_limit_config,
            )

            # Add session tracking if provided
            if session_id := check_request.context.get("sessionId"):
                conversation.conversation_id = session_id

        # Check the content based on type
        if check_request.kind == "prompt":
            result = await pipeline.check_input_async(check_request.text, conversation=conversation)
        else:  # response
            result = await pipeline.check_output_async(
                check_request.text, conversation=conversation
            )

        # Check conversation-level rate limits if applicable
        if conversation and conversation.check_rate_limit():
            # Conversation rate limit exceeded
            raise HTTPException(
                status_code=429,
                detail="Conversation rate limit exceeded",
                headers={
                    "X-RateLimit-Type": "conversation",
                    "X-RateLimit-Limit": str(
                        conversation.rate_limit.get("turns_per_minute", "N/A")
                    ),
                },
            )

        # Convert to response format
        action = "block" if result["blocked"] else "allow"
        if result.get("warnings") and not result["blocked"]:
            action = "warn"

        # Add API key info to metadata for tracking
        metadata = {
            "guardrails_triggered": result.get("guardrails_triggered", []),
            "processing_time_ms": result.get("processing_time_ms", 0),
            "api_key_id": api_key[:8] + "...",  # Partial key for tracking
        }

        # Add conversation rate limit info if available
        if conversation and conversation.rate_limit:
            metadata["conversation_rate_limit"] = {
                "turns_per_minute": conversation.rate_limit.get("turns_per_minute"),
                "current_turns": len(
                    [
                        t
                        for t in conversation.rate_limit_turns
                        if t >= (datetime.now() - timedelta(minutes=1))
                    ]
                ),
            }

        return CheckResponse(
            action=action,
            reasons=result.get("reasons", []),
            warnings=result.get("warnings", []),
            metadata=metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/check/status")
async def get_rate_limit_status(
    api_key: str = Depends(verify_api_key_with_rate_limit),
):
    """
    Get current rate limit status for the authenticated API key.

    This endpoint shows:
    - Current usage across different time windows
    - Remaining requests
    - Reset times
    """
    from stinger.api.security import get_rate_limit_status as get_status

    status = get_status(api_key)

    # Format response
    return {
        "api_key_id": api_key[:8] + "...",
        "rate_limits": status["details"],
    }
