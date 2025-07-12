"""
Pydantic models for API request/response validation.
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class CheckRequest(BaseModel):
    """Request model for content checking."""

    text: str = Field(
        ..., 
        min_length=1, 
        max_length=100000,  # 100KB text limit
        description="Text content to check"
    )
    kind: Literal["prompt", "response"] = Field(
        "prompt", description="Type of content - user prompt or LLM response"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, 
        description="Optional context with userId, botId, sessionId, etc."
    )
    preset: Optional[str] = Field(
        "customer_service", 
        min_length=1,
        max_length=50,
        description="Guardrail preset to use"
    )
    
    @field_validator("context")
    def validate_context(cls, v):
        """Validate context size and structure."""
        if v is not None:
            # Limit context size to prevent abuse
            import json
            context_str = json.dumps(v)
            if len(context_str) > 10000:  # 10KB limit for context
                raise ValueError("Context too large (max 10KB)")
            
            # Validate known fields if present
            if "userId" in v and len(str(v["userId"])) > 200:
                raise ValueError("userId too long (max 200 chars)")
            if "sessionId" in v and len(str(v["sessionId"])) > 200:
                raise ValueError("sessionId too long (max 200 chars)")
                
        return v


class CheckResponse(BaseModel):
    """Response model for content checking."""

    action: Literal["allow", "warn", "block"] = Field(..., description="Action to take")
    reasons: List[str] = Field(default_factory=list, description="Reasons for the action")
    warnings: List[str] = Field(default_factory=list, description="Non-blocking warnings")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class RulesResponse(BaseModel):
    """Response model for rules configuration."""

    preset: str = Field(..., description="Active preset name")
    guardrails: Dict[str, Any] = Field(..., description="Active guardrail configurations")
    version: str = Field(..., description="Configuration version")
