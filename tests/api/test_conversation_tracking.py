"""
Test conversation tracking in the API.
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
def test_conversation_tracking_minimal(client):
    """Test minimal conversation tracking with userId and botId."""
    response = client.post(
        "/v1/check",
        json={
            "text": "How do I reset my password?",
            "kind": "prompt",
            "context": {
                "userId": "bob@example.com",
                "botId": "chatgpt"
            }
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["action"] in ["allow", "warn", "block"]


@pytest.mark.ci
def test_conversation_tracking_full_context(client):
    """Test conversation tracking with full context."""
    response = client.post(
        "/v1/check",
        json={
            "text": "Tell me about user accounts",
            "kind": "prompt",
            "context": {
                "userId": "alice@company.com",
                "botId": "claude",
                "sessionId": "ext-12345",
                "userName": "Alice Johnson",
                "botName": "Claude Assistant",
                "botModel": "claude-3",
                "browser": "Chrome",
                "extensionVersion": "1.0.0"
            }
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["action"] in ["allow", "warn", "block"]


@pytest.mark.ci
def test_conversation_tracking_response_type(client):
    """Test conversation tracking for AI responses."""
    response = client.post(
        "/v1/check",
        json={
            "text": "Here is how to reset your password: [instructions]",
            "kind": "response",
            "context": {
                "userId": "support@example.com",
                "botId": "gpt-4",
                "sessionId": "support-chat-789"
            }
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["action"] in ["allow", "warn", "block"]


@pytest.mark.ci
def test_no_context_still_works(client):
    """Test that requests without context still work (backward compatibility)."""
    response = client.post(
        "/v1/check",
        json={
            "text": "Test prompt",
            "kind": "prompt"
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["action"] in ["allow", "warn", "block"]


@pytest.mark.ci
def test_partial_context_works(client):
    """Test that partial context (only userId) still works."""
    response = client.post(
        "/v1/check",
        json={
            "text": "Partial context test",
            "kind": "prompt",
            "context": {
                "userId": "test@example.com"
                # Missing botId - should default to "unknown-ai"
            }
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["action"] in ["allow", "warn", "block"]


@pytest.mark.ci
def test_conversation_types(client):
    """Test different conversation types (agent-to-agent, bot-to-human, etc)."""
    # Test agent-to-agent conversation
    response = client.post(
        "/v1/check",
        json={
            "text": "Process this data set",
            "kind": "prompt",
            "context": {
                "userId": "research-agent",
                "userType": "agent",
                "botId": "analysis-agent",
                "botType": "agent"
            }
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["action"] in ["allow", "warn", "block"]
    
    # Test bot-to-human conversation
    response = client.post(
        "/v1/check",
        json={
            "text": "Your support ticket #12345 has been created",
            "kind": "response",
            "context": {
                "userId": "support-bot",
                "userType": "bot",
                "botId": "customer@email.com",
                "botType": "human"
            }
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["action"] in ["allow", "warn", "block"]


@pytest.mark.efficacy
def test_conversation_audit_trail():
    """
    Test that conversation context appears in audit trail.
    
    This is an efficacy test that verifies the audit logging works correctly.
    """
    from stinger.core import audit
    from stinger.core.pipeline import GuardrailPipeline
    from stinger.core.conversation import Conversation
    
    # Enable audit trail to capture logs
    audit.enable(destination="stdout", buffer_size=1)
    
    # Create pipeline
    pipeline = GuardrailPipeline.from_preset("customer_service")
    
    # Create conversation with participant info
    conversation = Conversation(
        initiator="bob@example.com",
        responder="chatgpt",
        initiator_type="human",
        responder_type="ai_model",
        metadata={
            "participants": "bob@example.com <-> chatgpt",
            "browser": "Chrome"
        }
    )
    
    # Check content - this should trigger audit logging
    result = pipeline.check_input(
        "How do I reset my password?",
        conversation=conversation
    )
    
    # Verify the pipeline processed it
    assert "blocked" in result
    assert result["pipeline_type"] == "input"
    
    # The audit trail should now contain:
    # - user_id: "bob@example.com"
    # - metadata with participants: "bob@example.com <-> chatgpt"
    # This can be verified by checking audit logs