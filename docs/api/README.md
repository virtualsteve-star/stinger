# Stinger API Documentation

The Stinger API provides a REST interface for integrating guardrail functionality into remote applications, browser extensions, and other services.

## Quick Start

### Installation

```bash
# Install with API dependencies
pip install stinger[api]

# Or install all extras
pip install stinger[all]
```

### Starting the Server

```bash
# Start in foreground (default port 8888)
stinger-api

# Start in background/detached mode
stinger-api --detached

# Custom host and port
stinger-api --host 0.0.0.0 --port 8080

# With auto-reload for development
stinger-api --reload
```

### Environment Variables

- `STINGER_API_HOST` - Server host (default: 127.0.0.1)
- `STINGER_API_PORT` - Server port (default: 8888)
- `STINGER_API_RELOAD` - Enable auto-reload (default: false)
- `OPENAI_API_KEY` - Required for AI-powered guardrails

## API Endpoints

### Health Check

```http
GET /health
```

Returns the health status of the API service.

**Response:**
```json
{
  "status": "healthy",
  "pipeline_available": true,
  "guardrail_count": 5,
  "api_key_configured": true
}
```

### Check Content

```http
POST /v1/check
```

Evaluates content against configured guardrails.

**Request Body:**
```json
{
  "text": "The content to check",
  "kind": "prompt",           // "prompt" or "response"
  "preset": "customer_service", // Preset configuration to use
  "context": {                // Optional conversation context
    "sessionId": "session123",
    "userId": "user456"
  }
}
```

**Response:**
```json
{
  "action": "block",          // "allow", "warn", or "block"
  "reasons": [
    "pii_check: PII detected (regex): email"
  ],
  "warnings": [],
  "metadata": {
    "guardrails_triggered": ["pii_check"],
    "processing_time_ms": 12
  }
}
```

### Get Rules

```http
GET /v1/rules?preset=customer_service
```

Retrieves the active guardrail configuration for a preset.

**Query Parameters:**
- `preset` - The preset configuration name (default: "customer_service")
- `ext_version` - Optional extension version for compatibility

**Response:**
```json
{
  "preset": "customer_service",
  "guardrails": {
    "input_guardrails": {
      "pii_check": {
        "type": "SimplePIIDetectionGuardrail",
        "enabled": true,
        "config": {}
      }
    },
    "output_guardrails": {}
  },
  "version": "1.0.f7c3ea55"
}
```

## Available Presets

- `basic` - Basic pipeline with toxicity, PII, and code generation checks
- `content_moderation` - Content moderation for social media platforms
- `customer_service` - Customer service with PII and toxicity checks
- `medical` - Medical pipeline with strict PII protection
- `educational` - Educational platform with safety checks
- `financial` - Financial pipeline with PII and prompt injection protection

## CORS Configuration

The API is configured to accept requests from:
- Chrome extensions (`chrome-extension://*`)
- Firefox extensions (`moz-extension://*`)
- Local development (`http://localhost:*`, `http://127.0.0.1:*`)

## Integration Examples

### Browser Extension

```javascript
// Check user input before sending to LLM
async function checkInput(text) {
  const response = await fetch('http://localhost:8888/v1/check', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      text: text,
      kind: 'prompt',
      preset: 'customer_service'
    })
  });
  
  const result = await response.json();
  
  if (result.action === 'block') {
    alert(`Input blocked: ${result.reasons.join(', ')}`);
    return false;
  }
  
  if (result.action === 'warn') {
    console.warn('Warnings:', result.warnings);
  }
  
  return true;
}
```

### Python Client

```python
import requests

class StingerClient:
    def __init__(self, base_url="http://localhost:8888"):
        self.base_url = base_url
        
    def check_content(self, text, kind="prompt", preset="customer_service"):
        response = requests.post(
            f"{self.base_url}/v1/check",
            json={
                "text": text,
                "kind": kind,
                "preset": preset
            }
        )
        return response.json()
    
    def get_rules(self, preset="customer_service"):
        response = requests.get(
            f"{self.base_url}/v1/rules",
            params={"preset": preset}
        )
        return response.json()

# Usage
client = StingerClient()

# Check user input
result = client.check_content("My email is test@example.com")
if result["action"] == "block":
    print(f"Blocked: {result['reasons']}")
```

### cURL Examples

```bash
# Health check
curl http://localhost:8888/health

# Check content
curl -X POST http://localhost:8888/v1/check \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "kind": "prompt",
    "preset": "customer_service"
  }'

# Get rules
curl "http://localhost:8888/v1/rules?preset=financial"
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message"
}
```

Common status codes:
- `200` - Success
- `400` - Bad request (invalid input)
- `404` - Not found (invalid preset)
- `500` - Internal server error

## Performance Considerations

- The API caches pipeline instances to avoid recreation overhead
- First request for a preset may be slower due to initialization
- AI-powered guardrails require API keys and add latency
- Consider implementing client-side caching for rules

## Security Notes

- Always run the API behind a reverse proxy in production
- Configure appropriate rate limiting
- Use HTTPS for production deployments
- Validate and sanitize all inputs
- Consider authentication for production use

## Monitoring

Monitor the API using:
- Health endpoint for uptime checks
- Application logs in `/tmp/stinger-api.log` (detached mode)
- FastAPI's built-in `/docs` endpoint for interactive testing
- Standard HTTP monitoring tools

## Troubleshooting

### API Key Issues
If guardrails using AI are not working:
1. Ensure `OPENAI_API_KEY` is set in environment
2. Check the health endpoint for `api_key_configured` status
3. Review logs for API key related errors

### CORS Issues
If browser requests are blocked:
1. Ensure the origin is in the allowed list
2. Check browser console for CORS errors
3. Consider using a proxy for development

### Performance Issues
If the API is slow:
1. Check if AI-powered guardrails are causing delays
2. Monitor pipeline initialization times
3. Consider using simpler presets for testing
4. Implement caching on the client side