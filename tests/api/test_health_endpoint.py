"""
Tests for the health check endpoint.
"""

import pytest

# Skip if FastAPI is not installed
try:
    from fastapi.testclient import TestClient

    from stinger.api.app import app
except ImportError:
    pytest.skip("FastAPI not installed, skipping API tests", allow_module_level=True)


class TestHealthEndpoint:
    """Test cases for the /health endpoint."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_health_check_success(self, client):
        """Test that health check returns success."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "status" in data
        assert data["status"] == "healthy"
        assert "pipeline_available" in data
        assert "guardrail_count" in data
        assert "api_key_configured" in data

        # Pipeline should be available
        assert data["pipeline_available"] is True

        # Should have some guardrails loaded
        assert isinstance(data["guardrail_count"], int)
        assert data["guardrail_count"] > 0

    def test_health_check_headers(self, client):
        """Test that health check returns proper headers."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_health_check_api_key_status(self, client, monkeypatch):
        """Test API key status reporting."""
        # Import the module to access the global manager
        import stinger.core.api_key_manager

        # Test with no API key
        monkeypatch.setenv("OPENAI_API_KEY", "")
        # Reset the global API key manager to pick up new env var
        stinger.core.api_key_manager._api_key_manager = None

        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["api_key_configured"] is False

        # Test with API key set
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        # Reset the global API key manager again
        stinger.core.api_key_manager._api_key_manager = None

        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["api_key_configured"] is True

    @pytest.mark.ci
    def test_health_check_pipeline_error_handling(self, client, monkeypatch):
        """Test health check handles pipeline creation errors gracefully."""

        # Mock pipeline creation to fail
        def mock_from_preset(*args, **kwargs):
            raise Exception("Pipeline creation failed")

        import stinger.core.pipeline

        monkeypatch.setattr(
            stinger.core.pipeline.GuardrailPipeline, "from_preset", mock_from_preset
        )

        response = client.get("/health")

        # Should still return 200 OK
        assert response.status_code == 200
        data = response.json()

        # But pipeline_available should be False
        assert data["status"] == "healthy"
        assert data["pipeline_available"] is False
        assert data["guardrail_count"] == 0
