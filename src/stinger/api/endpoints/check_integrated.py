"""
Check endpoint with proper core engine integration.

This version shows how to properly pass context to the core engine's
audit system without duplicating any logging.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request

from stinger.api.models import CheckRequest, CheckResponse
from stinger.core.conversation import Conversation
from stinger.core.pipeline import GuardrailPipeline

logger = logging.getLogger(__name__)
router = APIRouter()

# Cache for pipelines
_pipeline_cache = {}


def get_pipeline(preset: str) -> GuardrailPipeline:
    """Get or create a pipeline for the given preset."""
    if preset not in _pipeline_cache:
        try:
            _pipeline_cache[preset] = GuardrailPipeline.from_preset(preset)
        except Exception as e:
            logger.error(f"Failed to create pipeline for preset {preset}: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid preset: {preset}")
    return _pipeline_cache[preset]


@router.post("/check", response_model=CheckResponse)
async def check_content(
    request: Request,
    check_request: CheckRequest,
):
    """
    Check content against guardrails.

    This endpoint properly integrates with the core engine's audit system by:
    1. Passing request context via conversation metadata
    2. Letting the pipeline handle all security logging
    3. Only logging API-specific events (HTTP layer)
    """
    # Log API-specific info only
    logger.info(
        f"API request: {request.method} {request.url.path} "
        f"[{getattr(request.state, 'request_id', 'no-id')}]"
    )

    try:
        # Get pipeline for the requested preset
        pipeline = get_pipeline(check_request.preset)

        # Create conversation with full context for audit trail
        conversation = None
        if check_request.context or hasattr(request.state, "request_id"):
            # Build metadata for audit trail
            metadata = {
                "request_id": getattr(request.state, "request_id", None),
                "user_ip": getattr(request.state, "client_ip", None),
                "user_agent": getattr(request.state, "user_agent", None),
            }

            # Add any context from the request
            if check_request.context:
                metadata.update(
                    {
                        "session_id": check_request.context.get("sessionId"),
                        "api_version": "v1",
                        "preset": check_request.preset,
                    }
                )

            # Create conversation with metadata
            user_id = (
                check_request.context.get("userId", "anonymous")
                if check_request.context
                else "anonymous"
            )

            conversation = Conversation(
                initiator=user_id,
                responder="stinger-api",
                initiator_type="human",
                responder_type="agent",
                conversation_id=(
                    check_request.context.get("sessionId") if check_request.context else None
                ),
                metadata=metadata,
                rate_limit=(
                    check_request.context.get("rate_limit") if check_request.context else None
                ),
            )

        # Check the content - pipeline will handle all audit logging
        if check_request.kind == "prompt":
            result = await pipeline.check_input_async(check_request.text, conversation=conversation)
        else:  # response
            result = await pipeline.check_output_async(
                check_request.text, conversation=conversation
            )

        # Convert to response format
        action = "block" if result["blocked"] else "allow"
        if result.get("warnings") and not result["blocked"]:
            action = "warn"

        response = CheckResponse(
            action=action,
            reasons=result.get("reasons", []),
            warnings=result.get("warnings", []),
            metadata={
                "guardrails_triggered": result.get("guardrails_triggered", []),
                "processing_time_ms": result.get("processing_time_ms", 0),
            },
        )

        # Log API response (HTTP layer only)
        logger.info(
            f"API response: 200 action={action} "
            f"[{getattr(request.state, 'request_id', 'no-id')}]"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        # Log API error
        logger.error(
            f"API error: {e} [{getattr(request.state, 'request_id', 'no-id')}]", exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")
