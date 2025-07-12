# Stinger API Rate Limiting Integration

## Overview

The Stinger REST API integrates with the core engine's `GlobalRateLimiter` to provide consistent rate limiting across all access methods (API, SDK, CLI). This ensures that rate limits are enforced uniformly regardless of how users access Stinger.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   REST API      │     │   Python SDK    │     │      CLI        │
│  (FastAPI)      │     │   (Direct)      │     │   (Commands)    │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                         │
         └───────────────────────┴─────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   GlobalRateLimiter     │
                    │  (Core Engine)          │
                    ├─────────────────────────┤
                    │ • Per-key tracking      │
                    │ • Multiple time windows │
                    │ • Role-based overrides │
                    │ • Memory/Redis backend │
                    └─────────────────────────┘
```

## Integration Points

### 1. API-Level Rate Limiting

The API uses the core `GlobalRateLimiter` for API key-based rate limiting:

```python
# In api/security.py
from stinger.core.rate_limiter import get_global_rate_limiter

async def check_rate_limit(request: Request, api_key: str) -> None:
    rate_limiter = get_global_rate_limiter()
    rate_limit_key = f"api:{hashlib.sha256(api_key.encode()).hexdigest()[:16]}"
    
    result = rate_limiter.check_rate_limit(rate_limit_key)
    if result["exceeded"]:
        raise HTTPException(status_code=429, detail=result["reason"])
    
    rate_limiter.record_request(rate_limit_key)
```

### 2. Conversation-Level Rate Limiting

The API also respects conversation-level rate limits:

```python
# In check endpoint
conversation = Conversation.human_ai(
    user_id=user_id,
    model_id="gpt-4",
    rate_limit={"turns_per_minute": 10, "turns_per_hour": 100}
)

if conversation.check_rate_limit():
    raise HTTPException(
        status_code=429,
        detail="Conversation rate limit exceeded"
    )
```

## Rate Limit Hierarchy

1. **API Key Rate Limits** (Global)
   - Applied first
   - Shared across all conversations for an API key
   - Default: 60/min, 1000/hour, 10000/day

2. **Conversation Rate Limits** (Per-Conversation)
   - Applied after API key check passes
   - Specific to individual conversations
   - Useful for preventing single conversation abuse

3. **Role-Based Overrides**
   - Premium API keys can have higher limits
   - Exempt roles bypass rate limiting

## Configuration

### Environment Variables

```bash
# Default rate limits
export STINGER_API_RATE_LIMIT_MINUTE=60
export STINGER_API_RATE_LIMIT_HOUR=1000
export STINGER_API_RATE_LIMIT_DAY=10000

# Redis backend (optional, for distributed rate limiting)
export REDIS_URL=redis://localhost:6379
```

### Programmatic Configuration

```python
# During API startup
from stinger.api.security import configure_rate_limits

configure_rate_limits(
    requests_per_minute=100,
    requests_per_hour=2000,
    requests_per_day=20000
)
```

### Role-Based Configuration

```yaml
# rate_limits.yaml
default_limits:
  requests_per_minute: 60
  requests_per_hour: 1000
  requests_per_day: 10000

role_overrides:
  premium:
    max_requests_per_minute: 200
    max_requests_per_hour: 5000
  
  enterprise:
    exempt: true  # No rate limits
```

## API Response Headers

The API provides standard rate limit headers:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1625097600
Retry-After: 120
```

## Client Implementation

### Python Client Example

```python
import requests
import time

class StingerAPIClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8888"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})
    
    def check_content(self, text: str, kind: str = "prompt", retry: bool = True):
        """Check content with automatic retry on rate limit."""
        response = self.session.post(
            f"{self.base_url}/v1/check",
            json={"text": text, "kind": kind}
        )
        
        if response.status_code == 429 and retry:
            # Rate limited - wait and retry
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return self.check_content(text, kind, retry=False)
        
        response.raise_for_status()
        return response.json()
```

### JavaScript Client Example

```javascript
class StingerAPIClient {
    constructor(apiKey, baseUrl = 'http://localhost:8888') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
    }
    
    async checkContent(text, kind = 'prompt') {
        const response = await fetch(`${this.baseUrl}/v1/check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.apiKey
            },
            body: JSON.stringify({ text, kind })
        });
        
        if (response.status === 429) {
            // Rate limited
            const retryAfter = parseInt(response.headers.get('Retry-After') || '60');
            const reason = await response.text();
            
            throw new Error(`Rate limited: ${reason}. Retry after ${retryAfter}s`);
        }
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return response.json();
    }
}
```

## Monitoring Rate Limits

### Check Current Status

```bash
# Get rate limit status for an API key
curl -H "X-API-Key: YOUR_KEY" \
  http://localhost:8888/v1/check/status

# Response
{
  "api_key_id": "8Qx3K9mN...",
  "rate_limits": {
    "requests_per_minute": {
      "limit": 60,
      "current": 15,
      "remaining": 45,
      "reset_time": 1625097600
    },
    "requests_per_hour": {
      "limit": 1000,
      "current": 150,
      "remaining": 850,
      "reset_time": 1625101200
    }
  }
}
```

### Monitor with Metrics

```python
# If Prometheus metrics are enabled
http://localhost:8888/metrics

# Relevant metrics
stinger_api_rate_limit_exceeded_total{api_key="..."} 5
stinger_api_rate_limit_remaining{api_key="...",window="minute"} 45
```

## Best Practices

1. **Use Conversation Rate Limits**: For chat applications, add per-conversation limits to prevent single-session abuse.

2. **Implement Client-Side Rate Limiting**: Don't rely solely on server-side limits. Implement client-side throttling.

3. **Handle 429 Gracefully**: Always check for 429 status and respect Retry-After headers.

4. **Monitor Usage**: Track rate limit metrics to identify patterns and adjust limits.

5. **Use Redis for Distributed Systems**: For multi-instance deployments, use Redis backend for consistent rate limiting.

## Migration from External Rate Limiters

If migrating from nginx or other rate limiters:

1. **Map Existing Limits**: Convert existing limits to Stinger format
2. **Test Thoroughly**: Ensure limits work as expected
3. **Monitor Closely**: Watch for unexpected behavior during transition
4. **Keep Fallback**: Maintain external rate limiter until confident

## Advantages of Integrated Rate Limiting

1. **Consistency**: Same limits across API, SDK, and CLI
2. **Flexibility**: Per-key, per-conversation, and role-based limits
3. **Visibility**: Built-in monitoring and status endpoints
4. **Performance**: In-process rate limiting is faster than external
5. **Context-Aware**: Can consider conversation context and user roles

## Troubleshooting

### Common Issues

1. **"Rate limit exceeded" immediately**
   - Check if API key is shared across multiple services
   - Verify time windows are configured correctly
   - Check for role-based overrides

2. **Limits not applying**
   - Ensure GlobalRateLimiter is initialized
   - Verify API key is being passed correctly
   - Check logs for rate limiter initialization

3. **Redis connection issues**
   - Fallback to memory backend automatically
   - Check Redis connection string
   - Monitor Redis memory usage

### Debug Mode

```python
# Enable debug logging
import logging
logging.getLogger("stinger.core.rate_limiter").setLevel(logging.DEBUG)

# Check rate limiter state
from stinger.core.rate_limiter import get_global_rate_limiter
limiter = get_global_rate_limiter()
print(limiter.get_all_keys())  # List all tracked keys
```