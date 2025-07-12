"""
Test request validation for API endpoints.
"""

import pytest

try:
    from fastapi.testclient import TestClient

    from stinger.api.app import app
except ImportError:
    pytest.skip("FastAPI not installed, skipping API tests", allow_module_level=True)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.ci
def test_request_size_limit(client):
    """Test that oversized requests are rejected."""
    # Create a request larger than 1MB
    large_text = "x" * (1024 * 1024 + 1)  # 1MB + 1 byte

    response = client.post(
        "/v1/check",
        json={"text": large_text, "kind": "prompt"},
        headers={"Content-Length": str(len(large_text) + 1000)},  # Approximate
    )

    assert response.status_code == 413
    assert "Request too large" in response.json()["detail"]


@pytest.mark.ci
def test_text_validation(client):
    """Test text field validation."""
    # Empty text
    response = client.post("/v1/check", json={"text": "", "kind": "prompt"})
    assert response.status_code == 422

    # Text too long (over 100KB)
    large_text = "x" * 100001
    response = client.post("/v1/check", json={"text": large_text, "kind": "prompt"})
    assert response.status_code == 422


@pytest.mark.ci
def test_preset_validation(client):
    """Test preset field validation."""
    # Preset too long
    response = client.post(
        "/v1/check",
        json={"text": "Test", "kind": "prompt", "preset": "x" * 51},  # Over 50 char limit
    )
    assert response.status_code == 422


@pytest.mark.ci
def test_context_validation(client):
    """Test context field validation."""
    # Context too large
    large_context = {"data": "x" * 10001}  # Over 10KB limit
    response = client.post(
        "/v1/check", json={"text": "Test", "kind": "prompt", "context": large_context}
    )
    assert response.status_code == 422

    # userId too long
    response = client.post(
        "/v1/check",
        json={
            "text": "Test",
            "kind": "prompt",
            "context": {"userId": "x" * 201},  # Over 200 char limit
        },
    )
    assert response.status_code == 422

    # sessionId too long
    response = client.post(
        "/v1/check",
        json={
            "text": "Test",
            "kind": "prompt",
            "context": {"sessionId": "x" * 201},  # Over 200 char limit
        },
    )
    assert response.status_code == 422


@pytest.mark.ci
def test_valid_request_passes(client):
    """Test that valid requests pass validation."""
    response = client.post(
        "/v1/check",
        json={
            "text": "How do I reset my password?",
            "kind": "prompt",
            "preset": "customer_service",
            "context": {
                "userId": "user@example.com",
                "sessionId": "session-123",
                "botId": "assistant",
            },
        },
    )
    assert response.status_code == 200
    assert response.json()["action"] in ["allow", "warn", "block"]
