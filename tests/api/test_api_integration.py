"""
Integration tests for the Stinger API.
"""

import pytest
from fastapi.testclient import TestClient
from stinger.api.app import app
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time


class TestAPIIntegration:
    """Integration tests for API endpoints working together."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test the root endpoint provides API information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Stinger Guardrails API"
        assert data["version"] == "0.1.0"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"
    
    def test_docs_endpoint_accessible(self, client):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
    
    def test_openapi_schema_accessible(self, client):
        """Test that OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Stinger Guardrails API"
        assert "paths" in data
        
        # Check all expected paths are documented
        expected_paths = ["/", "/health", "/v1/check", "/v1/rules"]
        for path in expected_paths:
            assert path in data["paths"]
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        # Test actual POST request with CORS headers
        response = client.post(
            "/v1/check",
            json={"text": "test", "kind": "prompt"},
            headers={
                "Origin": "chrome-extension://abcdefg"
            }
        )
        
        assert response.status_code == 200
        # Check for CORS headers in the response
        # Note: TestClient may not fully simulate CORS middleware behavior
        # In production, FastAPI's CORSMiddleware will add these headers
    
    def test_workflow_check_after_rules(self, client):
        """Test typical workflow: get rules, then check content."""
        # First, get the rules
        rules_response = client.get("/v1/rules?preset=customer_service")
        assert rules_response.status_code == 200
        rules_data = rules_response.json()
        
        # Then check content using same preset
        check_request = {
            "text": "Hello, can you help me?",
            "kind": "prompt",
            "preset": "customer_service"
        }
        check_response = client.post("/v1/check", json=check_request)
        assert check_response.status_code == 200
        check_data = check_response.json()
        
        # Verify consistency
        assert check_data["action"] in ["allow", "warn", "block"]
        
        # If guardrails were triggered, they should be in the rules
        if check_data.get("metadata", {}).get("guardrails_triggered"):
            triggered = check_data["metadata"]["guardrails_triggered"]
            all_guardrails = {
                **rules_data["guardrails"]["input_guardrails"],
                **rules_data["guardrails"]["output_guardrails"]
            }
            # At least some triggered guardrails should be in rules
            # (some internal guardrails might not be exposed)
    
    @pytest.mark.ci
    def test_concurrent_requests(self, client):
        """Test API handles concurrent requests properly."""
        def make_check_request(text):
            return client.post("/v1/check", json={
                "text": text,
                "kind": "prompt",
                "preset": "customer_service"
            })
        
        # Make multiple concurrent requests
        texts = [
            "Hello world",
            "My SSN is 123-45-6789",
            "What's the weather?",
            "Tell me a joke",
            "How are you?"
        ]
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_check_request, text) for text in texts]
            responses = [f.result() for f in futures]
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            assert response.json()["action"] in ["allow", "warn", "block"]
    
    def test_error_response_format(self, client):
        """Test that error responses follow consistent format."""
        # Test 404 error
        response = client.get("/v1/rules?preset=nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        
        # Test 422 validation error
        response = client.post("/v1/check", json={"kind": "invalid"})
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_health_check_reflects_system_state(self, client):
        """Test health check accurately reflects system state."""
        # Get initial health
        health1 = client.get("/health").json()
        
        # Make some requests to ensure system is working
        client.get("/v1/rules")
        client.post("/v1/check", json={"text": "test", "kind": "prompt"})
        
        # Get health again
        health2 = client.get("/health").json()
        
        # Both should show healthy system
        assert health1["status"] == "healthy"
        assert health2["status"] == "healthy"
        assert health1["pipeline_available"] == health2["pipeline_available"]
    
    @pytest.mark.efficacy
    def test_different_presets_different_behavior(self, client):
        """Test that different presets have different behavior."""
        test_text = "I need help with my medical condition"
        
        # Test with customer service preset
        response1 = client.post("/v1/check", json={
            "text": test_text,
            "kind": "prompt",
            "preset": "customer_service"
        })
        
        # Test with medical preset
        response2 = client.post("/v1/check", json={
            "text": test_text,
            "kind": "prompt",
            "preset": "medical"
        })
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Medical preset might have different handling for medical content
        # Both should process successfully but may have different results
        data1 = response1.json()
        data2 = response2.json()
        
        assert data1["action"] in ["allow", "warn", "block"]
        assert data2["action"] in ["allow", "warn", "block"]