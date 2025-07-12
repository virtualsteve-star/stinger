# Stinger REST API Security Audit Report

**Date**: July 11, 2025  
**Version**: 0.1.0a5  
**Auditor**: Security Review Team

## Executive Summary

The Stinger REST API provides a clean, well-structured interface for guardrail functionality. However, several critical security issues must be addressed before production deployment. This audit identifies these issues and provides concrete remediation steps.

## Critical Security Issues (MUST FIX)

### 1. ❌ No Authentication or Authorization

**Current State**: The API is completely open with no authentication mechanism.

**Risk**: High - Anyone can access the API and consume resources.

**Impact**: 
- Resource exhaustion
- Unauthorized data access
- Potential abuse of AI resources
- No audit trail of who is using the system

**Recommendation**: Implement API key authentication immediately.

```python
# src/stinger/api/security.py
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from typing import Optional
import os
import hashlib

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Store hashed API keys for security
VALID_API_KEY_HASHES = set(
    os.getenv("STINGER_API_KEY_HASHES", "").split(",")
)

async def verify_api_key(api_key: Optional[str] = Security(api_key_header)):
    """Verify API key authentication."""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Hash the provided key
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    if key_hash not in VALID_API_KEY_HASHES:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    return api_key

# Update endpoints to require authentication
@router.post("/check", response_model=CheckResponse)
async def check_content(
    request: CheckRequest,
    api_key: str = Depends(verify_api_key)
):
    # ... existing code ...
```

### 2. ✅ Rate Limiting (Core Engine Integration Available)

**Current State**: No rate limiting implemented in API, but core engine has comprehensive `GlobalRateLimiter`.

**Opportunity**: High - Can leverage existing rate limiting infrastructure.

**Benefits of Integration**:
- Consistent rate limits across API, SDK, and CLI
- Existing support for multiple time windows
- Role-based overrides already implemented
- Memory backend with Redis support planned
- Conversation-level rate limiting available

**Recommendation**: Integrate with core `GlobalRateLimiter` instead of adding separate rate limiting.

```python
# src/stinger/api/security.py
from stinger.core.rate_limiter import get_global_rate_limiter

async def check_rate_limit(request: Request, api_key: str) -> None:
    """Check rate limits using core Stinger rate limiter."""
    rate_limiter = get_global_rate_limiter()
    
    # Use API key as the rate limit key
    rate_limit_key = f"api:{hashlib.sha256(api_key.encode()).hexdigest()[:16]}"
    
    # Check if rate limit is exceeded
    result = rate_limiter.check_rate_limit(rate_limit_key)
    
    if result["exceeded"]:
        raise HTTPException(
            status_code=429,
            detail=result["reason"],
            headers={
                "X-RateLimit-Limit": str(result["limit"]["minute"]),
                "X-RateLimit-Remaining": str(result["remaining"]["minute"]),
                "Retry-After": "60",
            }
        )
    
    # Record the request
    rate_limiter.record_request(rate_limit_key)

# Apply to endpoints with combined auth + rate limit
@router.post("/check", response_model=CheckResponse)
async def check_content(
    request: Request,
    check_request: CheckRequest,
    api_key: str = Depends(verify_api_key_with_rate_limit)
):
    # ... existing code ...
```

**Additional Integration Benefits**:
- Supports conversation-level rate limits
- No additional dependencies (no slowapi/Redis needed)
- Consistent with core Stinger philosophy
- Already battle-tested in the core engine

### 3. ❌ No Request Size Limits

**Current State**: No limits on request body size.

**Risk**: Medium - Large payloads could cause memory exhaustion.

**Impact**:
- Service crashes
- Memory exhaustion
- Slow processing for all users

**Recommendation**: Add request size validation.

```python
# src/stinger/api/models.py
from pydantic import BaseModel, Field, validator

class CheckRequest(BaseModel):
    """Request model for content checking."""
    
    text: str = Field(
        ..., 
        description="Text content to check",
        max_length=50000  # 50KB limit
    )
    kind: Literal["prompt", "response"] = Field(
        "prompt", 
        description="Type of content - user prompt or LLM response"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, 
        description="Optional context (userId, sessionId, etc.)"
    )
    preset: Optional[str] = Field(
        "customer_service", 
        description="Guardrail preset to use",
        regex="^[a-zA-Z0-9_-]+$"  # Validate preset name format
    )
    
    @validator('text')
    def validate_text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v
    
    @validator('context')
    def validate_context_size(cls, v):
        if v and len(str(v)) > 1000:
            raise ValueError('Context too large (max 1KB)')
        return v

# Also add middleware for overall request size
from starlette.middleware.base import BaseHTTPMiddleware

class ContentSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_content_size: int = 1_000_000):  # 1MB default
        super().__init__(app)
        self.max_content_size = max_content_size
    
    async def dispatch(self, request, call_next):
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.max_content_size:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"}
            )
        return await call_next(request)

# In app.py
app.add_middleware(ContentSizeLimitMiddleware, max_content_size=1_000_000)
```

### 4. ⚠️ CORS Configuration Too Permissive

**Current State**: `allow_headers=["*"]` allows any headers.

**Risk**: Medium - Could enable certain attack vectors.

**Recommendation**: Explicitly list allowed headers.

```python
# src/stinger/api/app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://*",
        "moz-extension://*", 
        "http://localhost:3000",  # Specific ports
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=[
        "Content-Type",
        "X-API-Key",
        "X-Request-ID",
        "User-Agent"
    ],  # Explicit headers only
)
```

### 5. ⚠️ Pipeline Cache Not Thread-Safe

**Current State**: Simple dict without locking mechanism.

**Risk**: Medium - Race conditions under concurrent load.

**Recommendation**: Add thread-safe caching.

```python
# src/stinger/api/endpoints/check.py
import threading
from functools import lru_cache
from typing import Dict

# Thread-safe pipeline cache
_pipeline_cache: Dict[str, GuardrailPipeline] = {}
_cache_lock = threading.RLock()

def get_pipeline(preset: str) -> GuardrailPipeline:
    """Get or create a pipeline for the given preset (thread-safe)."""
    # Fast path - check without lock first
    if preset in _pipeline_cache:
        return _pipeline_cache[preset]
    
    # Slow path - create with lock
    with _cache_lock:
        # Double-check pattern
        if preset not in _pipeline_cache:
            try:
                _pipeline_cache[preset] = GuardrailPipeline.from_preset(preset)
            except Exception as e:
                logger.error(f"Failed to create pipeline for preset {preset}: {e}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid preset: {preset}"
                )
        return _pipeline_cache[preset]

# Alternative: Use TTL cache for automatic cleanup
from cachetools import TTLCache
from cachetools import cached
import threading

pipeline_cache_lock = threading.RLock()

@cached(
    cache=TTLCache(maxsize=100, ttl=3600),  # 1 hour TTL
    lock=pipeline_cache_lock
)
def get_cached_pipeline(preset: str) -> GuardrailPipeline:
    """Get pipeline with automatic cache expiration."""
    return GuardrailPipeline.from_preset(preset)
```

## Architecture Issues (SHOULD FIX)

### 6. ⚠️ No Centralized Configuration

**Current State**: Configuration scattered across files.

**Recommendation**: Implement settings management.

```python
# src/stinger/api/config.py
from pydantic import BaseSettings, Field, validator
from typing import List, Optional
import os

class Settings(BaseSettings):
    """API configuration settings."""
    
    # Server settings
    api_host: str = Field("127.0.0.1", env="STINGER_API_HOST")
    api_port: int = Field(8888, env="STINGER_API_PORT")
    api_workers: int = Field(1, env="STINGER_API_WORKERS")
    
    # Security settings
    api_key_hashes: List[str] = Field([], env="STINGER_API_KEY_HASHES")
    allowed_origins: List[str] = Field(
        ["chrome-extension://*", "moz-extension://*"],
        env="STINGER_ALLOWED_ORIGINS"
    )
    
    # Rate limiting
    rate_limit_enabled: bool = Field(True, env="STINGER_RATE_LIMIT_ENABLED")
    rate_limit_default: str = Field("100/minute", env="STINGER_RATE_LIMIT")
    redis_url: Optional[str] = Field(None, env="REDIS_URL")
    
    # Request limits
    max_request_size: int = Field(1_000_000, env="STINGER_MAX_REQUEST_SIZE")
    max_text_length: int = Field(50_000, env="STINGER_MAX_TEXT_LENGTH")
    
    # Operational
    log_level: str = Field("INFO", env="STINGER_LOG_LEVEL")
    enable_metrics: bool = Field(False, env="STINGER_ENABLE_METRICS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @validator("api_key_hashes", pre=True)
    def parse_api_keys(cls, v):
        if isinstance(v, str):
            return [k.strip() for k in v.split(",") if k.strip()]
        return v

# Singleton
settings = Settings()

# Usage in other files
from stinger.api.config import settings
```

### 7. ⚠️ No Structured Logging

**Current State**: Basic logging without request context.

**Recommendation**: Implement structured logging with request tracking.

```python
# src/stinger/api/logging.py
import structlog
import logging
import uuid
from fastapi import Request
from typing import Optional

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)

# Request ID middleware
from starlette.middleware.base import BaseHTTPMiddleware
import contextvars

request_id_var = contextvars.ContextVar("request_id", default=None)

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Add to request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response
        response.headers["X-Request-ID"] = request_id
        
        return response

# Logging middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("api.request")
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        self.logger.info(
            "request_started",
            request_id=request.state.request_id,
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
        )
        
        # Process request
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            self.logger.info(
                "request_completed",
                request_id=request.state.request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            self.logger.error(
                "request_failed",
                request_id=request.state.request_id,
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
                error=str(e),
                exc_info=True,
            )
            raise
```

### 8. ⚠️ Synchronous Operations in Async Endpoints

**Current State**: Async endpoints calling sync pipeline methods.

**Risk**: Low - But defeats purpose of async framework.

**Recommendation**: True async implementation or thread pool.

```python
# src/stinger/api/endpoints/check.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Thread pool for CPU-bound operations
executor = ThreadPoolExecutor(max_workers=4)

@router.post("/check", response_model=CheckResponse)
async def check_content(
    request: CheckRequest,
    api_key: str = Depends(verify_api_key)
):
    """Check content against guardrails (truly async)."""
    try:
        # Get pipeline
        pipeline = get_cached_pipeline(request.preset)
        
        # Create conversation context if needed
        conversation = None
        if request.context and request.context.get("sessionId"):
            conversation = Conversation.human_ai(
                user_id=request.context.get("userId", "user"),
                model_id="gpt-4",
            )
        
        # Run CPU-bound operation in thread pool
        loop = asyncio.get_event_loop()
        
        if request.kind == "prompt":
            result = await loop.run_in_executor(
                executor,
                pipeline.check_input,
                request.text,
                conversation
            )
        else:
            result = await loop.run_in_executor(
                executor,
                pipeline.check_output,
                request.text,
                conversation
            )
        
        # Convert to response
        action = "block" if result["blocked"] else "allow"
        if result.get("warnings") and not result["blocked"]:
            action = "warn"
        
        return CheckResponse(
            action=action,
            reasons=result.get("reasons", []),
            warnings=result.get("warnings", []),
            metadata={
                "guardrails_triggered": result.get("guardrails_triggered", []),
                "processing_time_ms": result.get("processing_time_ms", 0),
            },
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error checking content",
            request_id=request_id_var.get(),
            error=str(e),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Operational Improvements (NICE TO HAVE)

### 9. 📊 Add Metrics Collection

```python
# src/stinger/api/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
request_count = Counter(
    'stinger_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'stinger_api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'stinger_api_active_requests',
    'Number of active requests'
)

guardrail_triggers = Counter(
    'stinger_guardrail_triggers_total',
    'Guardrail trigger count',
    ['guardrail_name', 'action']
)

# Metrics middleware
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip metrics endpoint
        if request.url.path == "/metrics":
            return await call_next(request)
        
        # Track active requests
        active_requests.inc()
        
        # Time the request
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Record metrics
            request_count.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            request_duration.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(time.time() - start_time)
            
            return response
            
        finally:
            active_requests.dec()

# Add metrics endpoint
from prometheus_client import generate_latest
from fastapi.responses import Response

@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

### 10. 🏥 Enhanced Health Checks

```python
# src/stinger/api/endpoints/health.py
from enum import Enum
from typing import Dict, Any
import asyncio

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"

class HealthCheckResponse(BaseModel):
    status: HealthStatus
    version: str
    checks: Dict[str, Dict[str, Any]]
    
@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "ok"}

@router.get("/health/ready")
async def readiness_check():
    """Detailed readiness check."""
    checks = {}
    overall_status = HealthStatus.HEALTHY
    
    # Check pipeline loading
    try:
        test_pipeline = get_cached_pipeline("customer_service")
        checks["pipeline"] = {
            "status": "healthy",
            "cached_presets": len(_pipeline_cache)
        }
    except Exception as e:
        checks["pipeline"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = HealthStatus.UNHEALTHY
    
    # Check Redis if configured
    if settings.redis_url:
        try:
            await redis_client.ping()
            checks["redis"] = {"status": "healthy"}
        except Exception as e:
            checks["redis"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            overall_status = HealthStatus.DEGRADED
    
    # Check API keys configured
    if not settings.api_key_hashes:
        checks["auth"] = {
            "status": "unhealthy",
            "error": "No API keys configured"
        }
        overall_status = HealthStatus.UNHEALTHY
    else:
        checks["auth"] = {
            "status": "healthy",
            "configured_keys": len(settings.api_key_hashes)
        }
    
    return HealthCheckResponse(
        status=overall_status,
        version=app.version,
        checks=checks
    )
```

## Testing Recommendations

Add security-focused tests:

```python
# tests/api/test_security.py
import pytest
from fastapi.testclient import TestClient

def test_no_auth_rejected(client: TestClient):
    """Test that requests without API key are rejected."""
    response = client.post(
        "/v1/check",
        json={"text": "test", "kind": "prompt"}
    )
    assert response.status_code == 401
    assert "API key required" in response.json()["detail"]

def test_invalid_auth_rejected(client: TestClient):
    """Test that invalid API keys are rejected."""
    response = client.post(
        "/v1/check",
        json={"text": "test", "kind": "prompt"},
        headers={"X-API-Key": "invalid-key"}
    )
    assert response.status_code == 403
    assert "Invalid API key" in response.json()["detail"]

def test_rate_limiting(client: TestClient, valid_api_key: str):
    """Test rate limiting enforcement."""
    # Make many requests quickly
    for i in range(101):  # Exceed 100/minute limit
        response = client.post(
            "/v1/check",
            json={"text": f"test {i}", "kind": "prompt"},
            headers={"X-API-Key": valid_api_key}
        )
        
        if i < 100:
            assert response.status_code == 200
        else:
            assert response.status_code == 429
            assert "Rate limit exceeded" in response.json()["detail"]

def test_large_payload_rejected(client: TestClient, valid_api_key: str):
    """Test large payloads are rejected."""
    large_text = "x" * 100_000  # 100KB
    response = client.post(
        "/v1/check",
        json={"text": large_text, "kind": "prompt"},
        headers={"X-API-Key": valid_api_key}
    )
    assert response.status_code == 422
    assert "ensure this value has at most" in str(response.json())

def test_sql_injection_in_preset(client: TestClient, valid_api_key: str):
    """Test SQL injection attempt in preset parameter."""
    response = client.post(
        "/v1/check",
        json={
            "text": "test",
            "kind": "prompt",
            "preset": "customer_service'; DROP TABLE users;--"
        },
        headers={"X-API-Key": valid_api_key}
    )
    assert response.status_code == 422
    assert "string does not match regex" in str(response.json())
```

## Implementation Priority

1. **Week 1 - Critical Security**
   - [ ] API Key Authentication
   - [ ] Rate Limiting
   - [ ] Request Size Limits
   - [ ] Fix CORS Headers

2. **Week 2 - Architecture**
   - [ ] Thread-Safe Caching
   - [ ] Centralized Settings
   - [ ] Structured Logging
   - [ ] Request ID Tracking

3. **Week 3 - Operations**
   - [ ] Metrics Collection
   - [ ] Enhanced Health Checks
   - [ ] Performance Monitoring
   - [ ] Documentation Updates

## Conclusion

The Stinger REST API has a solid foundation but requires immediate security hardening before production use. The most critical issue is the lack of authentication. Rate limiting can be elegantly solved by integrating with the existing core engine's `GlobalRateLimiter`.

**Overall Grade: B- (Good foundation, authentication gap, but rate limiting ready)**

### Strengths
- Clean code structure
- Good use of FastAPI patterns
- Comprehensive test coverage
- Clear separation of concerns
- **Core rate limiting available for integration**

### Critical Gaps
- No authentication
- Rate limiting not yet integrated (but infrastructure exists)
- Not thread-safe
- No operational instrumentation

### Unique Advantages
- Can leverage existing `GlobalRateLimiter` for consistent rate limiting
- Conversation-level rate limiting already available
- No need for external dependencies (Redis optional)
- Unified rate limiting across API, SDK, and CLI

Implement authentication immediately and integrate with the core rate limiter to bring the security posture to production standards.