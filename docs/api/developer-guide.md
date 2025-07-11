# Stinger API Developer Guide

This guide provides detailed information for developers integrating with the Stinger API.

## Architecture Overview

The Stinger API is built on FastAPI and provides:
- RESTful endpoints for content checking
- Real-time guardrail evaluation
- Preset-based configuration
- CORS support for browser extensions
- Async request handling

## Setting Up Development Environment

### Prerequisites

```bash
# Python 3.8+
python --version

# Install Stinger with API extras
pip install -e ".[api]"

# Set up API key for AI guardrails
export OPENAI_API_KEY="your-key-here"
```

### Running Tests

```bash
# Run API tests
pytest tests/api/ -v

# Run with coverage
pytest tests/api/ -v --cov=src/stinger/api
```

## API Design Principles

### 1. Stateless Operation
Each request is independent. Conversation context is passed explicitly when needed.

### 2. Preset-Based Configuration
Guardrails are organized into presets for different use cases. This simplifies client integration.

### 3. Action-Based Responses
The API returns clear actions: `allow`, `warn`, or `block` with detailed reasons.

### 4. Extensibility
New presets and guardrails can be added without breaking existing clients.

## Common Integration Patterns

### 1. Pre-LLM Validation

```python
async def send_to_llm(user_input: str):
    # Check input before sending to LLM
    check_result = await check_content(user_input, "prompt")
    
    if check_result["action"] == "block":
        return {"error": "Input contains prohibited content"}
    
    # Proceed with LLM call
    llm_response = await call_llm(user_input)
    
    # Check LLM response
    response_check = await check_content(llm_response, "response")
    
    if response_check["action"] == "block":
        return {"error": "Response contains prohibited content"}
    
    return {"response": llm_response}
```

### 2. Streaming Response Validation

```python
async def stream_with_guardrails(prompt: str):
    # Pre-check prompt
    prompt_check = await check_content(prompt, "prompt")
    if prompt_check["action"] == "block":
        yield {"error": prompt_check["reasons"]}
        return
    
    # Stream from LLM
    buffer = ""
    async for chunk in llm_stream(prompt):
        buffer += chunk
        
        # Check complete sentences
        if buffer.endswith(('.', '!', '?')):
            check = await check_content(buffer, "response")
            if check["action"] != "block":
                yield chunk
            buffer = ""
```

### 3. Multi-Turn Conversations

```python
class ConversationManager:
    def __init__(self, session_id: str, user_id: str):
        self.context = {
            "sessionId": session_id,
            "userId": user_id
        }
    
    async def process_message(self, message: str):
        # Check with conversation context
        result = await check_content(
            message, 
            "prompt",
            context=self.context
        )
        
        if result["action"] == "block":
            return {"blocked": True, "reasons": result["reasons"]}
        
        # Continue processing...
```

## Performance Optimization

### 1. Client-Side Caching

```javascript
class StingerCache {
    constructor(ttl = 300000) { // 5 minutes
        this.cache = new Map();
        this.ttl = ttl;
    }
    
    async getRules(preset) {
        const key = `rules:${preset}`;
        const cached = this.cache.get(key);
        
        if (cached && Date.now() - cached.timestamp < this.ttl) {
            return cached.data;
        }
        
        const response = await fetch(`/v1/rules?preset=${preset}`);
        const data = await response.json();
        
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
        
        return data;
    }
}
```

### 2. Batch Processing

```python
async def check_batch(items: List[Dict[str, str]]):
    """Check multiple items concurrently"""
    tasks = []
    for item in items:
        task = check_content(item["text"], item["kind"])
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

### 3. Connection Pooling

```python
import httpx

# Create a client with connection pooling
client = httpx.AsyncClient(
    base_url="http://localhost:8888",
    timeout=30.0,
    limits=httpx.Limits(max_keepalive_connections=5)
)

async def check_with_pool(text: str):
    response = await client.post("/v1/check", json={
        "text": text,
        "kind": "prompt",
        "preset": "customer_service"
    })
    return response.json()
```

## Error Handling Best Practices

### 1. Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def reliable_check(text: str, kind: str):
    try:
        response = await httpx.post(
            "http://localhost:8888/v1/check",
            json={"text": text, "kind": kind, "preset": "basic"},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            # Don't retry client errors
            raise
        # Retry server errors
        raise
```

### 2. Graceful Degradation

```javascript
async function checkWithFallback(text, kind) {
    try {
        const response = await fetch('/v1/check', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text, kind, preset: 'customer_service'}),
            signal: AbortSignal.timeout(5000) // 5s timeout
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Guardrail check failed:', error);
        // Fallback to basic client-side checks
        return {
            action: text.includes('@') ? 'warn' : 'allow',
            reasons: [],
            warnings: text.includes('@') ? ['Possible email detected'] : []
        };
    }
}
```

## Security Considerations

### 1. Input Validation

Always validate inputs before sending to the API:

```python
def validate_check_request(text: str, kind: str, preset: str):
    if not text or len(text) > 10000:
        raise ValueError("Invalid text length")
    
    if kind not in ["prompt", "response"]:
        raise ValueError("Invalid kind")
    
    valid_presets = [
        "basic", "customer_service", "medical",
        "educational", "financial", "content_moderation"
    ]
    if preset not in valid_presets:
        raise ValueError("Invalid preset")
```

### 2. Rate Limiting

Implement client-side rate limiting:

```javascript
class RateLimiter {
    constructor(maxRequests = 100, windowMs = 60000) {
        this.maxRequests = maxRequests;
        this.windowMs = windowMs;
        this.requests = [];
    }
    
    canMakeRequest() {
        const now = Date.now();
        this.requests = this.requests.filter(
            time => now - time < this.windowMs
        );
        
        if (this.requests.length >= this.maxRequests) {
            return false;
        }
        
        this.requests.push(now);
        return true;
    }
}
```

### 3. Authentication (Future)

Prepare for future authentication:

```python
class AuthenticatedStingerClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    async def check_content(self, text: str, kind: str):
        response = await httpx.post(
            "http://localhost:8888/v1/check",
            json={"text": text, "kind": kind, "preset": "basic"},
            headers=self.headers
        )
        return response.json()
```

## Debugging Tips

### 1. Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("stinger.api")

# Log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.debug(f"Response: {response.status_code}")
    return response
```

### 2. Request Tracing

Add request IDs for tracing:

```python
import uuid

async def check_with_trace(text: str):
    request_id = str(uuid.uuid4())
    response = await httpx.post(
        "http://localhost:8888/v1/check",
        json={"text": text, "kind": "prompt", "preset": "basic"},
        headers={"X-Request-ID": request_id}
    )
    print(f"Request {request_id}: {response.status_code}")
    return response.json()
```

### 3. Performance Profiling

```python
import time

async def profile_check(text: str):
    start = time.time()
    result = await check_content(text, "prompt")
    duration = (time.time() - start) * 1000
    
    print(f"Check took {duration:.2f}ms")
    print(f"Server processing: {result['metadata']['processing_time_ms']}ms")
    print(f"Network overhead: {duration - result['metadata']['processing_time_ms']:.2f}ms")
    
    return result
```

## Testing Your Integration

### 1. Unit Tests

```python
import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_guardrail_integration():
    with patch('httpx.post') as mock_post:
        mock_post.return_value = AsyncMock(
            json=AsyncMock(return_value={
                "action": "block",
                "reasons": ["PII detected"],
                "warnings": []
            })
        )
        
        result = await check_user_input("test@example.com")
        assert result["blocked"] == True
        assert "PII" in str(result["reasons"])
```

### 2. Integration Tests

```python
@pytest.mark.integration
async def test_real_api():
    # Start test server
    async with TestServer() as server:
        client = StingerClient(server.url)
        
        # Test various scenarios
        scenarios = [
            ("Hello world", "allow"),
            ("test@example.com", "block"),
            ("You stupid idiot", "block")
        ]
        
        for text, expected_action in scenarios:
            result = await client.check_content(text)
            assert result["action"] == expected_action
```

## Deployment Considerations

### 1. Reverse Proxy Configuration

nginx example:
```nginx
location /stinger-api/ {
    proxy_pass http://localhost:8888/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
    proxy_read_timeout 30s;
}
```

### 2. Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8888

CMD ["python", "-m", "stinger.api", "--host", "0.0.0.0"]
```

### 3. Health Monitoring

```bash
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health
    port: 8888
  initialDelaySeconds: 30
  periodSeconds: 10
```

## Troubleshooting Common Issues

### Issue: Slow Response Times
- Check if AI guardrails are enabled
- Monitor API key rate limits
- Enable response caching
- Use simpler presets for testing

### Issue: CORS Errors
- Verify origin is in allowed list
- Check browser console for specifics
- Use proxy for development

### Issue: Connection Timeouts
- Increase client timeout settings
- Check server resource usage
- Verify network connectivity

### Issue: Inconsistent Results
- Ensure same preset is used
- Check for API version differences
- Verify guardrail configurations