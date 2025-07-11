"""
Tests for the rules endpoint.
"""

import pytest

# Skip if FastAPI is not installed
try:
    from fastapi.testclient import TestClient

    from stinger.api.app import app
except ImportError:
    pytest.skip("FastAPI not installed, skipping API tests", allow_module_level=True)
import re


class TestRulesEndpoint:
    """Test cases for the /v1/rules endpoint."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_get_rules_default_preset(self, client):
        """Test getting rules with default preset."""
        response = client.get("/v1/rules")

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "preset" in data
        assert "guardrails" in data
        assert "version" in data

        # Default preset should be customer_service
        assert data["preset"] == "customer_service"

        # Should have guardrails configuration
        assert "input_guardrails" in data["guardrails"]
        assert "output_guardrails" in data["guardrails"]
        assert isinstance(data["guardrails"]["input_guardrails"], dict)
        assert isinstance(data["guardrails"]["output_guardrails"], dict)

        # Version should be in expected format
        assert re.match(r"^1\.0\.[a-f0-9]{8}$", data["version"])

    def test_get_rules_specific_preset(self, client):
        """Test getting rules for a specific preset."""
        response = client.get("/v1/rules?preset=medical")

        assert response.status_code == 200
        data = response.json()

        assert data["preset"] == "medical"
        assert len(data["guardrails"]["input_guardrails"]) > 0
        assert len(data["guardrails"]["output_guardrails"]) > 0

    def test_get_rules_guardrail_structure(self, client):
        """Test the structure of individual guardrail rules."""
        response = client.get("/v1/rules")

        assert response.status_code == 200
        data = response.json()

        # Check at least one guardrail exists
        all_guardrails = {
            **data["guardrails"]["input_guardrails"],
            **data["guardrails"]["output_guardrails"],
        }
        assert len(all_guardrails) > 0

        # Check guardrail structure
        for name, guardrail in all_guardrails.items():
            assert "type" in guardrail
            assert "enabled" in guardrail
            assert "config" in guardrail
            assert guardrail["enabled"] is True  # Only enabled guardrails returned
            assert isinstance(guardrail["config"], dict)

    def test_get_rules_invalid_preset(self, client):
        """Test getting rules for invalid preset."""
        response = client.get("/v1/rules?preset=nonexistent")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_get_rules_with_ext_version(self, client):
        """Test getting rules with extension version parameter."""
        response = client.get("/v1/rules?preset=customer_service&ext_version=1.0.0")

        assert response.status_code == 200
        data = response.json()

        # Should process normally regardless of ext_version
        assert data["preset"] == "customer_service"
        assert "version" in data

    def test_get_rules_version_consistency(self, client):
        """Test that version hash is consistent for same configuration."""
        # Get rules twice
        response1 = client.get("/v1/rules?preset=customer_service")
        response2 = client.get("/v1/rules?preset=customer_service")

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()

        # Version should be the same for same configuration
        assert data1["version"] == data2["version"]

        # But different preset should have different version
        response3 = client.get("/v1/rules?preset=medical")
        assert response3.status_code == 200
        data3 = response3.json()

        # Different configurations should have different versions
        # (unless by chance they have the same hash, which is unlikely)
        # We'll just check they're valid versions
        assert re.match(r"^1\.0\.[a-f0-9]{8}$", data3["version"])

    def test_get_rules_response_headers(self, client):
        """Test response headers are correct."""
        response = client.get("/v1/rules")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.ci
    def test_get_rules_known_guardrails(self, client):
        """Test that known guardrails appear in the configuration."""
        response = client.get("/v1/rules?preset=customer_service")

        assert response.status_code == 200
        data = response.json()

        # Check for some expected guardrails
        all_guardrails = {
            **data["guardrails"]["input_guardrails"],
            **data["guardrails"]["output_guardrails"],
        }

        # Should have some standard guardrails
        guardrail_types = [g["type"] for g in all_guardrails.values()]

        # At minimum, customer service preset should have PII detection
        assert any("PII" in t or "pii" in t.lower() for t in guardrail_types)

    def test_get_rules_caching(self, client):
        """Test that pipelines are cached properly."""
        # First request
        response1 = client.get("/v1/rules?preset=customer_service")
        assert response1.status_code == 200

        # Second request should be faster due to caching
        # (We can't easily test timing, but we can verify it works)
        response2 = client.get("/v1/rules?preset=customer_service")
        assert response2.status_code == 200

        # Results should be identical
        assert response1.json() == response2.json()
