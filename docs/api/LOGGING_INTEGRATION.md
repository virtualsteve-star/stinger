# API Logging Integration with Core Engine

## Overview

The Stinger API leverages the core engine's existing logging infrastructure rather than creating duplicate systems.

## Core Engine Logging Systems

### 1. Security Audit Trail (`audit.py`)
**Purpose**: Forensic security logging for compliance

**Automatically Captures**:
- User prompts with metadata
- LLM responses with timing
- Guardrail decisions with reasons
- Request IDs, user IDs, conversation IDs

**API Integration**: Pass context, don't duplicate

### 2. Debug Logging
**Purpose**: Operational debugging

**Uses**: Standard Python `logging` module

**API Integration**: Use for API-specific debug info only

## What the API Does

### 1. Generate Request IDs
```python
# Minimal middleware
@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

### 2. Pass Context to Pipeline
```python
# In check endpoint
conversation = Conversation(
    user_id=user_id,
    model_id="gpt-4",
    metadata={
        "request_id": request.state.request_id,
        "user_ip": request.state.client_ip,
        "user_agent": request.state.user_agent,
        "session_id": check_request.context.get("sessionId")
    }
)

# Pipeline automatically logs to audit trail with this context
result = await pipeline.check_input_async(text, conversation=conversation)
```

### 3. Enable Audit Trail on Startup
```python
@app.on_event("startup")
async def startup():
    # Enable core audit trail
    from stinger.core import audit
    audit.enable()  # Uses smart defaults
```

## What the API Does NOT Do

❌ **Does NOT re-log**:
- User prompts (audit trail does this)
- Guardrail decisions (audit trail does this)
- Processing times (audit trail does this)

❌ **Does NOT create**:
- Separate audit files
- Duplicate security logs
- Custom audit formats

## API-Specific Logging Only

The API only logs what's unique to the HTTP layer:

```python
# Example: Log API-specific events
logger = logging.getLogger(__name__)

# Log only HTTP-specific info
logger.info(f"API request: {request.method} {request.url.path}")
logger.info(f"API response: {response.status_code} in {duration}ms")

# Log API-specific errors
logger.error(f"API serialization error: {e}")
```

## Benefits

1. **No Duplication**: Single audit trail for all access methods
2. **Consistent Format**: Same log format across API, SDK, CLI
3. **Automatic Context**: Request IDs flow through all layers
4. **Performance**: Async audit buffering already implemented
5. **Compliance**: Single audit trail for security reviews

## Example Audit Trail Entry

When API processes a request, the core engine automatically logs:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "event_type": "prompt",
  "user_id": "api-user-123",
  "conversation_id": "conv-456",
  "request_id": "req-789",
  "prompt": "Check this content",
  "user_ip": "192.168.1.1",
  "user_agent": "MyApp/1.0",
  "session_id": "session-abc"
}
{
  "timestamp": "2024-01-01T12:00:00.1Z",
  "event_type": "guardrail_decision",
  "request_id": "req-789",
  "guardrail_name": "simple_pii_detection",
  "decision": "block",
  "reason": "SSN detected",
  "confidence": 1.0
}
```

## Debugging

To see audit logs during development:

```python
# Enable verbose audit logging
import os
os.environ["STINGER_AUDIT_VERBOSE"] = "true"

# Or programmatically
audit.enable(destination="stdout", verbose=True)
```

## Summary

The API acts as a thin HTTP layer that:
1. Generates request IDs
2. Extracts HTTP context
3. Passes everything to the core engine
4. Lets the core handle all security logging

This approach maintains a single source of truth for security events while avoiding duplicate logging infrastructure.