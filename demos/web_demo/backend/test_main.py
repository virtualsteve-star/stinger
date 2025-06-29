#!/usr/bin/env python3
"""
Basic tests for Stinger Web Demo backend.

This file provides simple validation tests for the FastAPI backend
to ensure all endpoints are working correctly.
"""

import sys
import os
import pytest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
import yaml

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
    """Test updating guardrail settings."""
    # First get current settings
    response = client.get("/api/guardrails")
    assert response.status_code == 200
    current_settings = response.json()
    
    # Try to update settings (toggle first guardrail)
    if current_settings["input_guardrails"]:
        updated_settings = current_settings.copy()
        first_guardrail = updated_settings["input_guardrails"][0]
        first_guardrail["enabled"] = not first_guardrail["enabled"]
        
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


if __name__ == "__main__":
    print("🧪 Running Stinger Web Demo Backend Tests")
    print("=" * 50)
    
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
    
    # Run all tests
    pytest.main([__file__, "-v"])