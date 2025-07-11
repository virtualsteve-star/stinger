# Phase 13: API Service Integration

**Status**: Planning  
**Priority**: High  
**Estimated Duration**: 3-4 days  
**Dependencies**: Chrome Extension Project needs API endpoints

## 🎯 Objective

Add a simple REST API service to Stinger core that can be run directly from the Python package, enabling browser extensions and other remote clients to use Stinger's guardrails without complex deployment.

## 📋 Background

- A Chrome extension is being developed that needs to call Stinger for policy evaluation
- The extension spec (in `docs/specs/stinger_chrome_extension_design.md`) defines needed endpoints
- We want the simplest possible deployment - just `pip install` and run

## 🏗️ Technical Approach

### Simple Python Package Approach (No Docker Required)

1. **Installation**:
   ```bash
   pip install stinger-guardrails-alpha[api]
   ```

2. **Running the API**:
   ```bash
   # Option 1: Direct module execution
   python -m stinger.api
   
   # Option 2: CLI command
   stinger-api serve --port 8080
   
   # Option 3: Programmatic
   from stinger.api import app
   import uvicorn
   uvicorn.run(app, host="0.0.0.0", port=8080)
   ```

3. **Structure**:
   ```
   src/stinger/
   ├── api/
   │   ├── __init__.py
   │   ├── __main__.py      # For python -m stinger.api
   │   ├── app.py           # FastAPI application
   │   ├── endpoints/
   │   │   ├── __init__.py
   │   │   ├── check.py     # POST /v1/check
   │   │   ├── rules.py     # GET /v1/rules
   │   │   └── health.py    # GET /health
   │   └── models.py        # Request/response models
   └── cli/
       └── main.py          # Add 'stinger-api' command
   ```

## 📝 Implementation Tasks

### Task 1: Core API Structure (Day 1)
- [ ] Create `src/stinger/api/` directory structure
- [ ] Set up FastAPI application with CORS support
- [ ] Add basic health check endpoint
- [ ] Update pyproject.toml with `api` extras (fastapi, uvicorn)
- [ ] Add `__main__.py` for direct module execution

### Task 2: Main Endpoints (Day 2)
- [ ] Implement `POST /v1/check` endpoint:
  ```python
  {
    "text": "User prompt or LLM response",
    "kind": "prompt" | "response",
    "context": {
      "userId": "optional-user-id",
      "sessionId": "optional-session-id"
    }
  }
  ```
- [ ] Implement `GET /v1/rules` endpoint for policy configuration
- [ ] Add request/response validation with Pydantic models
- [ ] Integrate with existing GuardrailPipeline

### Task 3: CLI Integration (Day 3)
- [ ] Add `stinger-api` command to CLI
- [ ] Support configuration via:
  - Command line args (`--port`, `--host`, `--config`)
  - Environment variables (`STINGER_API_PORT`, etc.)
  - Config file (`~/.stinger/api.yaml`)
- [ ] Add `--reload` option for development
- [ ] Add graceful shutdown handling

### Task 4: Testing & Documentation (Day 4)
- [ ] Write API endpoint tests
- [ ] Add example client code (Python, JavaScript)
- [ ] Update main README with API section
- [ ] Create `docs/API_SERVICE.md` with:
  - Installation instructions
  - Running the service
  - API endpoint documentation
  - Security considerations
  - Example integrations

## 🔧 Technical Details

### Why FastAPI?
- Automatic OpenAPI/Swagger documentation
- Built-in request validation
- Async support for better performance
- Easy to embed in Python package
- Minimal dependencies

### Security Considerations
- CORS configuration for browser extensions
- Optional API key authentication
- Rate limiting support
- Request size limits
- No default external exposure (localhost only)

### Configuration Approach
```yaml
# ~/.stinger/api.yaml
api:
  host: "127.0.0.1"  # localhost only by default
  port: 8080
  cors:
    allowed_origins:
      - "chrome-extension://*"
      - "http://localhost:*"
  auth:
    enabled: false  # Can add API keys later
  pipeline:
    preset: "customer_service"  # Or custom config
```

## 📊 Success Criteria

1. ✅ API can be installed with `pip install stinger-guardrails-alpha[api]`
2. ✅ Service starts with simple command: `python -m stinger.api`
3. ✅ Chrome extension can successfully call `/v1/check` endpoint
4. ✅ API responses are fast (<100ms for typical requests)
5. ✅ No Docker or complex deployment required
6. ✅ Clear documentation for developers

## 🚀 Future Enhancements (Not Phase 13)

- WebSocket support for streaming
- Batch check endpoints
- Admin endpoints for configuration
- Metrics/monitoring endpoints
- Authentication/authorization
- Deployment guides for cloud platforms

## 📝 Notes

- Keep it simple - this is for development and small deployments
- Enterprise users can add their own deployment wrappers
- Focus on making the Chrome extension integration work smoothly
- Performance is important but simplicity is key

## 🔄 Updates

- 2025-07-10: Initial plan created based on Chrome extension requirements