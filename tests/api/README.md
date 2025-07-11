# API Tests

This directory contains tests for the Stinger API endpoints.

## Test Structure

- `test_health_endpoint.py` - Tests for the `/health` endpoint
- `test_check_endpoint.py` - Tests for the `/v1/check` endpoint
- `test_rules_endpoint.py` - Tests for the `/v1/rules` endpoint
- `test_api_integration.py` - Integration tests for API workflows
- `conftest.py` - Shared fixtures and test configuration

## Running the Tests

### Run all API tests
```bash
pytest tests/api/ -v
```

### Run specific test file
```bash
pytest tests/api/test_health_endpoint.py -v
```

### Run with coverage
```bash
pytest tests/api/ -v --cov=src/stinger/api --cov-report=html
```

### Run only CI-appropriate tests (no API keys required)
```bash
pytest tests/api/ -m "ci" -v
```

### Run efficacy tests (requires OPENAI_API_KEY)
```bash
pytest tests/api/ -m "efficacy" -v
```

## Test Categories

1. **Unit Tests** - Test individual endpoints in isolation
2. **Integration Tests** - Test workflows across multiple endpoints
3. **Error Handling** - Test error responses and edge cases
4. **Performance** - Test concurrent requests and caching

## Key Test Scenarios

### Health Endpoint
- Basic health check functionality
- Pipeline availability detection
- API key configuration status
- Error handling when pipeline creation fails

### Check Endpoint
- Prompt checking (allow/warn/block)
- Response checking
- PII detection
- Context handling
- Invalid preset handling
- Missing/invalid field validation
- Metadata and processing time

### Rules Endpoint
- Default preset retrieval
- Specific preset retrieval
- Guardrail configuration structure
- Version consistency
- Invalid preset handling
- Caching behavior

### Integration
- Root endpoint information
- API documentation accessibility
- CORS headers
- Typical workflows (get rules → check content)
- Concurrent request handling
- Error response consistency

## Writing New Tests

When adding new API tests:

1. Use `TestClient` from FastAPI for testing
2. Follow the existing test structure and naming conventions
3. Add appropriate pytest markers (@pytest.mark.ci, @pytest.mark.efficacy)
4. Test both success and error cases
5. Verify response structure and headers
6. Consider adding integration tests for new workflows

## Dependencies

The API tests require:
- `pytest`
- `fastapi[all]` (includes TestClient)
- The Stinger API module (`stinger.api`)

## Notes

- Some tests require `OPENAI_API_KEY` to be set for AI-powered guardrails
- Tests use FastAPI's TestClient which runs the app in-process
- Mock fixtures are available in conftest.py for testing without external dependencies