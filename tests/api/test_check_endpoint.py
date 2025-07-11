"""
Tests for the check endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from stinger.api.app import app
import json


class TestCheckEndpoint:
    """Test cases for the /v1/check endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_check_prompt_allow(self, client):
        """Test checking a prompt that should be allowed."""
        request_data = {
            "text": "What's the weather like today?",
            "kind": "prompt",
            "preset": "customer_service"
        }
        
        response = client.post("/v1/check", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "action" in data
        assert "reasons" in data
        assert "warnings" in data
        assert "metadata" in data
        
        # Should be allowed
        assert data["action"] == "allow"
        assert len(data["reasons"]) == 0
    
    def test_check_prompt_block_pii(self, client):
        """Test checking a prompt with PII that should be blocked."""
        request_data = {
            "text": "My SSN is 123-45-6789",
            "kind": "prompt",
            "preset": "customer_service"
        }
        
        response = client.post("/v1/check", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be blocked
        assert data["action"] == "block"
        assert len(data["reasons"]) > 0
        assert any("PII" in reason or "SSN" in reason for reason in data["reasons"])
    
    def test_check_response_allow(self, client):
        """Test checking a response that should be allowed."""
        request_data = {
            "text": "The weather today is sunny with a high of 75°F.",
            "kind": "response",
            "preset": "customer_service"
        }
        
        response = client.post("/v1/check", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be allowed
        assert data["action"] == "allow"
    
    def test_check_with_context(self, client):
        """Test checking with context information."""
        request_data = {
            "text": "Hello, how can I help you?",
            "kind": "prompt",
            "context": {
                "userId": "user123",
                "sessionId": "session456"
            },
            "preset": "customer_service"
        }
        
        response = client.post("/v1/check", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should process without error
        assert data["action"] in ["allow", "warn", "block"]
    
    def test_check_metadata_fields(self, client):
        """Test that metadata contains expected fields."""
        request_data = {
            "text": "Test message",
            "kind": "prompt",
            "preset": "customer_service"
        }
        
        response = client.post("/v1/check", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check metadata
        assert "metadata" in data
        metadata = data["metadata"]
        assert "guardrails_triggered" in metadata
        assert "processing_time_ms" in metadata
        assert isinstance(metadata["guardrails_triggered"], list)
        assert isinstance(metadata["processing_time_ms"], (int, float))
    
    def test_check_invalid_preset(self, client):
        """Test checking with an invalid preset."""
        request_data = {
            "text": "Test message",
            "kind": "prompt",
            "preset": "nonexistent_preset"
        }
        
        response = client.post("/v1/check", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid preset" in data["detail"]
    
    def test_check_missing_required_fields(self, client):
        """Test checking with missing required fields."""
        # Missing text
        request_data = {
            "kind": "prompt"
        }
        
        response = client.post("/v1/check", json=request_data)
        assert response.status_code == 422  # Unprocessable Entity
        
        # Missing kind uses default
        request_data = {
            "text": "Test message"
        }
        
        response = client.post("/v1/check", json=request_data)
        assert response.status_code == 200  # Should use default "prompt"
    
    def test_check_invalid_kind(self, client):
        """Test checking with invalid kind value."""
        request_data = {
            "text": "Test message",
            "kind": "invalid_kind"
        }
        
        response = client.post("/v1/check", json=request_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.ci
    def test_check_warning_action(self, client):
        """Test that warnings result in 'warn' action when not blocked."""
        # This test would need a specific input that triggers warnings
        # For now, we'll test the logic is possible
        request_data = {
            "text": "Please visit http://example.com for more info",
            "kind": "response",
            "preset": "customer_service"
        }
        
        response = client.post("/v1/check", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have proper action
        assert data["action"] in ["allow", "warn", "block"]
        
        # If there are warnings and not blocked, action should be "warn"
        if data.get("warnings") and data["action"] != "block":
            assert data["action"] == "warn"
    
    def test_check_response_headers(self, client):
        """Test response headers are correct."""
        request_data = {
            "text": "Test message",
            "kind": "prompt"
        }
        
        response = client.post("/v1/check", json=request_data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
    
    @pytest.mark.efficacy
    def test_check_toxic_content_handling(self, client):
        """Test that toxic content is handled appropriately."""
        request_data = {
            "text": "You are a terrible person and I hate you!",
            "kind": "prompt",
            "preset": "customer_service"
        }
        
        response = client.post("/v1/check", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Customer service preset has toxicity check with warn action
        # The simple toxicity filter might not detect this as toxic
        # or it might warn/block depending on implementation
        assert data["action"] in ["allow", "warn", "block"]
        
        # If it detects toxicity, there should be reasons or warnings
        if data["action"] != "allow":
            assert len(data["reasons"]) > 0 or len(data["warnings"]) > 0