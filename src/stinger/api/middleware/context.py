"""
Minimal context middleware for API that integrates with core logging.

This adds request IDs and passes context to the existing audit system
rather than duplicating logging functionality.
"""

import uuid
from fastapi import Request


async def add_request_context(request: Request, call_next):
    """
    Add request ID and context for core engine logging.
    
    This middleware:
    1. Generates or extracts request ID
    2. Makes it available to endpoints
    3. Adds it to response headers
    
    The core audit system will handle all security logging.
    """
    # Get or generate request ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    # Store in request state for endpoints to use
    request.state.request_id = request_id
    
    # Also store client info for audit trail
    request.state.client_ip = request.client.host if request.client else None
    request.state.user_agent = request.headers.get("User-Agent", "Unknown")
    
    # Process request
    response = await call_next(request)
    
    # Add request ID to response
    response.headers["X-Request-ID"] = request_id
    
    return response