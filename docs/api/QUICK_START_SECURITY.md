# Quick Start: Securing Stinger API

This guide provides immediate steps to secure your Stinger API deployment.

## 🚨 Critical: Add API Key Authentication (5 minutes)

### Step 1: Generate API Keys

```bash
# Generate secure API keys
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Example output: 8Qx3K9mN2pL5vR7wY1tZ4aB6cD0eF3gH

# Generate the SHA256 hash of your key
python -c "import hashlib; print(hashlib.sha256('YOUR_API_KEY'.encode()).hexdigest())"
```

### Step 2: Set Environment Variables

```bash
# Set the hashed keys (comma-separated for multiple keys)
export STINGER_API_KEY_HASHES="hash1,hash2,hash3"

# Example:
export STINGER_API_KEY_HASHES="a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
```

### Step 3: Create Security Middleware

Create `src/stinger/api/security.py`:

```python
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from typing import Optional
import os
import hashlib

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Get valid key hashes from environment
VALID_API_KEY_HASHES = set(
    h.strip() for h in os.getenv("STINGER_API_KEY_HASHES", "").split(",") 
    if h.strip()
)

async def verify_api_key(api_key: Optional[str] = Security(api_key_header)):
    """Verify API key authentication."""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if not VALID_API_KEY_HASHES:
        # No keys configured - fail safe by rejecting all
        raise HTTPException(
            status_code=503,
            detail="API authentication not configured"
        )
    
    # Hash the provided key
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    if key_hash not in VALID_API_KEY_HASHES:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    return api_key
```

### Step 4: Update Endpoints

Update each endpoint in `src/stinger/api/endpoints/`:

```python
from fastapi import Depends
from stinger.api.security import verify_api_key

# Update check.py
@router.post("/check", response_model=CheckResponse)
async def check_content(
    request: CheckRequest,
    api_key: str = Depends(verify_api_key)  # Add this line
):
    # ... existing code ...

# Update rules.py
@router.get("/rules", response_model=RulesResponse)
async def get_rules(
    preset: Optional[str] = Query("customer_service"),
    api_key: str = Depends(verify_api_key)  # Add this line
):
    # ... existing code ...
```

### Step 5: Test Authentication

```bash
# Start the secured API
stinger-api

# Test without API key (should fail)
curl -X POST http://localhost:8888/v1/check \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "kind": "prompt"}'
# Expected: 401 Unauthorized

# Test with API key (should work)
curl -X POST http://localhost:8888/v1/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_ACTUAL_API_KEY" \
  -d '{"text": "test", "kind": "prompt"}'
# Expected: 200 OK
```

## 🔒 Additional Quick Wins

### 1. Add Basic Rate Limiting (10 minutes)

```bash
pip install slowapi
```

```python
# src/stinger/api/app.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In endpoints/check.py
from slowapi import limiter

@router.post("/check", response_model=CheckResponse)
@limiter.limit("30/minute")  # 30 requests per minute per IP
async def check_content(
    request: Request,
    check_request: CheckRequest,
    api_key: str = Depends(verify_api_key)
):
    # ... existing code ...
```

### 2. Fix CORS Headers (2 minutes)

```python
# src/stinger/api/app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://*",
        "moz-extension://*",
        # Add your specific origins here
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],  # Specific headers only
)
```

### 3. Add Request Size Limit (5 minutes)

```python
# src/stinger/api/models.py
class CheckRequest(BaseModel):
    text: str = Field(..., max_length=50000)  # 50KB limit
    # ... rest of model ...
```

## 🚀 Production Deployment Checklist

- [ ] API keys generated and hashed
- [ ] Environment variables set
- [ ] Authentication middleware added
- [ ] All endpoints protected
- [ ] Rate limiting configured
- [ ] CORS headers restricted
- [ ] Request size limits set
- [ ] Tested with and without valid keys
- [ ] Monitoring/alerting configured
- [ ] API documentation updated

## 📊 Monitoring Your Secured API

```bash
# Check unauthorized attempts
grep "401" /tmp/stinger-api.log | wc -l

# Check rate limit hits  
grep "429" /tmp/stinger-api.log | wc -l

# Monitor active API keys (hashed)
echo $STINGER_API_KEY_HASHES | tr ',' '\n' | wc -l
```

## Next Steps

1. Review the full [Security Audit Report](./SECURITY_AUDIT.md)
2. Implement structured logging for better monitoring
3. Add metrics collection for operational visibility
4. Consider Redis-based rate limiting for distributed deployments
5. Implement key rotation strategy

Remember: **Never expose API keys in logs, error messages, or responses!**