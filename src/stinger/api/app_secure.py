"""
FastAPI application for Stinger API service with integrated security.

This is an enhanced version that uses the core engine's rate limiting
and adds proper authentication.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from stinger.api.endpoints import check, health, rules
from stinger.api.security import configure_rate_limits

# Create FastAPI app
app = FastAPI(
    title="Stinger Guardrails API",
    description="REST API for Stinger Guardrails Framework",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS with specific headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://*",
        "moz-extension://*",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key", "X-Request-ID"],
)


@app.on_event("startup")
async def startup_event():
    """Configure rate limits on startup."""
    # Configure rate limits using core engine
    # These can be overridden by environment variables or config
    configure_rate_limits(
        requests_per_minute=60,
        requests_per_hour=1000,
        requests_per_day=10000,
    )


@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    """Add rate limit headers to response."""
    response = await call_next(request)

    # Add rate limit headers if they were set
    if hasattr(request.state, "rate_limit_headers"):
        for header, value in request.state.rate_limit_headers.items():
            response.headers[header] = value

    return response


# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(check.router, prefix="/v1", tags=["guardrails"])
app.include_router(rules.router, prefix="/v1", tags=["configuration"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Stinger Guardrails API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "authentication": "Required (X-API-Key header)",
        "rate_limits": {
            "per_minute": 60,
            "per_hour": 1000,
            "per_day": 10000,
        },
    }


# Custom exception handler for rate limit errors
@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    """Custom handler for rate limit exceptions."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": str(exc.detail),
            "type": "rate_limit_exceeded",
        },
        headers=getattr(exc, "headers", {}),
    )
