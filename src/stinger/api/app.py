"""
FastAPI application for Stinger API service.
"""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from stinger.api import metrics
from stinger.api.endpoints import check, health
from stinger.api.endpoints import metrics as metrics_endpoint
from stinger.api.endpoints import rules
from stinger.core import audit

# Configure logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Stinger Guardrails API",
    description="REST API for Stinger Guardrails Framework",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for browser extensions
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://*",
        "moz-extension://*",
        "http://localhost:*",
        "http://127.0.0.1:*",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add request size limit (1MB default)
MAX_REQUEST_SIZE = int(os.getenv("STINGER_MAX_REQUEST_SIZE", "1048576"))  # 1MB


@app.middleware("http")
async def limit_request_size(request, call_next):
    """Limit request body size to prevent abuse."""
    if request.headers.get("content-length"):
        try:
            content_length = int(request.headers["content-length"])
            if content_length > MAX_REQUEST_SIZE:
                logger.warning(f"Request too large: {content_length} bytes")
                return JSONResponse(
                    status_code=413,
                    content={"detail": f"Request too large. Max size: {MAX_REQUEST_SIZE} bytes"},
                )
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid Content-Length header: {request.headers.get('content-length')}"
            )
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid Content-Length header"},
            )
    return await call_next(request)


@app.middleware("http")
async def track_metrics(request, call_next):
    """Track request metrics for monitoring."""
    import time

    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Record metrics
    metrics.record_request(
        endpoint=request.url.path,
        method=request.method,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )

    # Add response time header
    response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

    return response


# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(check.router, prefix="/v1", tags=["guardrails"])
app.include_router(rules.router, prefix="/v1", tags=["configuration"])
app.include_router(metrics_endpoint.router, tags=["monitoring"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Stinger Guardrails API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.on_event("startup")
async def startup_event():
    """Initialize audit logging on API startup."""
    # Get audit log configuration from environment
    audit_file = os.getenv("STINGER_AUDIT_LOG", "./api_audit.log")

    # Enable audit logging
    audit.enable(
        destination=audit_file,
        redact_pii=False,  # Keep PII for security analysis
        buffer_size=1,  # Flush immediately for real-time monitoring
        flush_interval=1.0,
    )

    logger.info(f"Audit logging enabled: {audit_file}")
    logger.info("Stinger API started with conversation tracking enabled")
