"""
API Security middleware using core Stinger rate limiting.

This module integrates with Stinger's existing GlobalRateLimiter to provide
consistent rate limiting across the API and core engine.
"""

import hashlib
import os
import time
from typing import Optional

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

from stinger.core.rate_limiter import get_global_rate_limiter

# API Key header configuration
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Get valid API key hashes from environment
VALID_API_KEY_HASHES = set(
    h.strip() for h in os.getenv("STINGER_API_KEY_HASHES", "").split(",") if h.strip()
)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify API key authentication.

    Returns:
        The validated API key for use in rate limiting

    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not VALID_API_KEY_HASHES:
        # No keys configured - fail safe by rejecting all
        raise HTTPException(status_code=503, detail="API authentication not configured")

    # Hash the provided key
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    if key_hash not in VALID_API_KEY_HASHES:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return api_key


async def check_rate_limit(request: Request, api_key: str) -> None:
    """
    Check rate limits using core Stinger rate limiter.

    Args:
        request: FastAPI request object
        api_key: The API key to check limits for

    Raises:
        HTTPException: If rate limit is exceeded
    """
    # Get the global rate limiter instance
    rate_limiter = get_global_rate_limiter()

    # Use API key as the rate limit key
    # You could also use IP address or a combination
    rate_limit_key = f"api:{hashlib.sha256(api_key.encode()).hexdigest()[:16]}"

    # Check if rate limit is exceeded
    result = rate_limiter.check_rate_limit(rate_limit_key)

    if result["exceeded"]:
        # Get reset time using public interface
        status = rate_limiter.get_status(rate_limit_key)
        reset_times = []
        for limit_type in result["exceeded_limits"]:
            if limit_type in status["details"]:
                reset_times.append(status["details"][limit_type]["reset_time"])

        reset_time = min(reset_times) if reset_times else 0

        # Add rate limit headers
        headers = {
            "X-RateLimit-Limit": str(result["limit"]["minute"]),
            "X-RateLimit-Remaining": str(result["remaining"]["minute"]),
            "X-RateLimit-Reset": str(int(reset_time)),
            "Retry-After": str(int(reset_time - time.time())),
        }

        raise HTTPException(
            status_code=429,
            detail=result["reason"],
            headers=headers,
        )

    # Record the request
    rate_limiter.record_request(rate_limit_key)

    # Add rate limit headers to response
    request.state.rate_limit_headers = {
        "X-RateLimit-Limit": str(result["limit"]["minute"]),
        "X-RateLimit-Remaining": str(result["remaining"]["minute"]),
    }


async def verify_api_key_with_rate_limit(
    request: Request, api_key: Optional[str] = Security(api_key_header)
) -> str:
    """
    Combined authentication and rate limiting check.

    This is a convenience function that combines API key verification
    and rate limiting in a single dependency.

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is invalid or rate limit exceeded
    """
    # First verify the API key
    validated_key = await verify_api_key(api_key)

    # Then check rate limits
    await check_rate_limit(request, validated_key)

    return validated_key


def configure_rate_limits(
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000,
    requests_per_day: int = 10000,
) -> None:
    """
    Configure default rate limits for the API.

    This should be called during API startup to set appropriate limits.

    Args:
        requests_per_minute: Max requests per minute per API key
        requests_per_hour: Max requests per hour per API key
        requests_per_day: Max requests per day per API key
    """
    rate_limiter = get_global_rate_limiter()
    rate_limiter.set_default_limits(
        {
            "requests_per_minute": requests_per_minute,
            "requests_per_hour": requests_per_hour,
            "requests_per_day": requests_per_day,
        }
    )


def get_rate_limit_status(api_key: str) -> dict:
    """
    Get current rate limit status for an API key.

    Args:
        api_key: The API key to check

    Returns:
        Dict with current rate limit status
    """
    rate_limiter = get_global_rate_limiter()
    rate_limit_key = f"api:{hashlib.sha256(api_key.encode()).hexdigest()[:16]}"

    return rate_limiter.get_status(rate_limit_key)
