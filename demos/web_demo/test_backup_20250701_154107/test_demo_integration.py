#!/usr/bin/env python3
"""
End-to-End Integration Tests for Stinger Web Demo

This test suite validates the complete Super Demo functionality,
including backend API, frontend integration, and core guardrail features.
"""

import sys
import os
import time
import json
import subprocess
import tempfile
import signal
from pathlib import Path
from threading import Thread
import requests
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add src to path for Stinger imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest

class DemoIntegrationTest:
    """Integration test suite for the Super Demo."""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.backend_url = "https://localhost:8000"
        self.frontend_url = "https://localhost:3000"
        
    def setup(self):
        """Set up the test environment."""
        print("🚀 Setting up integration test environment...")
        
        # Start backend
        self.start_backend()
        
        # Wait for backend to be ready
        self.wait_for_backend()
        
        # Validate backend is working
        self.validate_backend()
        
        # Start frontend (optional - can test API directly)
        # self.start_frontend()
        
        print("✅ Test environment ready!")
    
    def teardown(self):
        """Clean up the test environment."""
        print("🧹 Cleaning up test environment...")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
            except Exception as e:
                print(f"Warning: Error stopping frontend: {e}")
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except Exception as e:
                print(f"Warning: Error stopping backend: {e}")
        
        print("✅ Cleanup completed!")
    
    def start_backend(self):
        """Start the FastAPI backend."""
        print("🔧 Starting backend server...")
        
        backend_dir = Path(__file__).parent / "backend"
        
        # Change to backend directory and start server
        self.backend_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "PYTHONPATH": str(Path(__file__).parent.parent.parent / "src")}
        )
        
        print(f"✅ Backend process started (PID: {self.backend_process.pid})")
    
    def wait_for_backend(self, timeout=30):
        """Wait for backend to be ready."""
        print("⏳ Waiting for backend to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Disable SSL verification for self-signed cert
                response = requests.get(
                    f"{self.backend_url}/api/health",
                    verify=False,
                    timeout=5
                )
                if response.status_code == 200:
                    print("✅ Backend is ready!")
                    return
            except requests.exceptions.RequestException:
                time.sleep(1)
                continue
        
        raise TimeoutError("Backend failed to start within timeout period")
    
    def validate_backend(self):
        """Validate backend functionality."""
        print("🔍 Validating backend functionality...")
        
        # Test health endpoint
        health_response = requests.get(
            f"{self.backend_url}/api/health",
            verify=False
        )
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["status"] == "healthy"
        assert health_data["pipeline_loaded"] is True
        print("✅ Health endpoint working")
        
        # Test guardrails endpoint
        guardrails_response = requests.get(
            f"{self.backend_url}/api/guardrails",
            verify=False
        )
        assert guardrails_response.status_code == 200
        guardrail_data = guardrails_response.json()
        assert "input_guardrails" in guardrail_data
        assert "output_guardrails" in guardrail_data
        print("✅ Guardrails endpoint working")
        
        # Test presets endpoint
        presets_response = requests.get(
            f"{self.backend_url}/api/presets",
            verify=False
        )
        assert presets_response.status_code == 200
        presets_data = presets_response.json()
        assert "presets" in presets_data
        assert len(presets_data["presets"]) > 0
        print("✅ Presets endpoint working")
        
        print("✅ Backend validation completed!")
    
    def test_chat_functionality(self):
        """Test the chat functionality end-to-end."""
        print("💬 Testing chat functionality...")
        
        # Test normal message
        normal_message = {
            "content": "Hello, how are you today?"
        }
        
        chat_response = requests.post(
            f"{self.backend_url}/api/chat",
            json=normal_message,
            verify=False
        )
        
        assert chat_response.status_code == 200
        chat_data = chat_response.json()
        assert "content" in chat_data
        assert "blocked" in chat_data
        assert chat_data["blocked"] is False
        assert "conversation_id" in chat_data
        print("✅ Normal chat message working")
        
        # Test message that should trigger guardrails
        pii_message = {
            "content": "My social security number is 123-45-6789"
        }
        
        pii_response = requests.post(
            f"{self.backend_url}/api/chat",
            json=pii_message,
            verify=False
        )
        
        assert pii_response.status_code == 200
        pii_data = pii_response.json()
        # Should be blocked or have warnings due to PII
        assert pii_data["blocked"] is True or len(pii_data["warnings"]) > 0
        print("✅ PII detection working")
        
        # Test toxic content
        toxic_message = {
            "content": "I hate everyone and want to hurt people"
        }
        
        toxic_response = requests.post(
            f"{self.backend_url}/api/chat",
            json=toxic_message,
            verify=False
        )
        
        assert toxic_response.status_code == 200
        toxic_data = toxic_response.json()
        # Should be blocked or have warnings due to toxicity
        assert toxic_data["blocked"] is True or len(toxic_data["warnings"]) > 0
        print("✅ Toxicity detection working")
        
        print("✅ Chat functionality tests completed!")
    
    def test_guardrail_settings(self):
        """Test guardrail settings functionality."""
        print("⚙️ Testing guardrail settings...")
        
        # Get current settings
        settings_response = requests.get(
            f"{self.backend_url}/api/guardrails",
            verify=False
        )
        assert settings_response.status_code == 200
        original_settings = settings_response.json()
        
        # Toggle a guardrail
        modified_settings = original_settings.copy()
        if modified_settings["input_guardrails"]:
            first_guardrail = modified_settings["input_guardrails"][0]
            original_state = first_guardrail["enabled"]
            first_guardrail["enabled"] = not original_state
            
            # Update settings
            update_response = requests.post(
                f"{self.backend_url}/api/guardrails",
                json=modified_settings,
                verify=False
            )
            assert update_response.status_code == 200
            
            # Verify the change
            verify_response = requests.get(
                f"{self.backend_url}/api/guardrails",
                verify=False
            )
            assert verify_response.status_code == 200
            verify_data = verify_response.json()
            assert verify_data["input_guardrails"][0]["enabled"] == (not original_state)
            print("✅ Guardrail toggle working")
            
            # Restore original settings
            restore_response = requests.post(
                f"{self.backend_url}/api/guardrails",
                json=original_settings,
                verify=False
            )
            assert restore_response.status_code == 200
            print("✅ Settings restored")
        
        print("✅ Guardrail settings tests completed!")
    
    def test_preset_switching(self):
        """Test preset switching functionality."""
        print("🔄 Testing preset switching...")
        
        # Get available presets
        presets_response = requests.get(
            f"{self.backend_url}/api/presets",
            verify=False
        )
        assert presets_response.status_code == 200
        presets_data = presets_response.json()
        presets = presets_data["presets"]
        
        if len(presets) > 1:
            # Try switching to a different preset
            preset_names = list(presets.keys())
            target_preset = preset_names[0] if preset_names[0] != "customer_service" else preset_names[1]
            
            switch_response = requests.post(
                f"{self.backend_url}/api/preset",
                json={"preset": target_preset},
                verify=False
            )
            assert switch_response.status_code == 200
            
            # Verify the preset was loaded
            settings_response = requests.get(
                f"{self.backend_url}/api/guardrails",
                verify=False
            )
            assert settings_response.status_code == 200
            settings_data = settings_response.json()
            assert settings_data["preset"] == target_preset
            print(f"✅ Preset switching to '{target_preset}' working")
            
            # Switch back to customer_service
            restore_response = requests.post(
                f"{self.backend_url}/api/preset",
                json={"preset": "customer_service"},
                verify=False
            )
            assert restore_response.status_code == 200
            print("✅ Preset restored")
        
        print("✅ Preset switching tests completed!")
    
    def test_conversation_management(self):
        """Test conversation management functionality."""
        print("💭 Testing conversation management...")
        
        # Send a message to create a conversation
        message = {"content": "Hello, this is a test conversation"}
        chat_response = requests.post(
            f"{self.backend_url}/api/chat",
            json=message,
            verify=False
        )
        assert chat_response.status_code == 200
        
        # Get conversation info
        conv_response = requests.get(
            f"{self.backend_url}/api/conversation",
            verify=False
        )
        assert conv_response.status_code == 200
        conv_data = conv_response.json()
        assert conv_data["active"] is True
        assert "conversation_id" in conv_data
        print("✅ Conversation creation working")
        
        # Reset conversation
        reset_response = requests.post(
            f"{self.backend_url}/api/conversation/reset",
            verify=False
        )
        assert reset_response.status_code == 200
        
        # Verify conversation was reset
        verify_response = requests.get(
            f"{self.backend_url}/api/conversation",
            verify=False
        )
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["active"] is False
        print("✅ Conversation reset working")
        
        print("✅ Conversation management tests completed!")
    
    def test_audit_logging(self):
        """Test audit logging functionality."""
        print("📊 Testing audit logging...")
        
        # Send a message to generate audit logs
        message = {"content": "This is an audit test message"}
        chat_response = requests.post(
            f"{self.backend_url}/api/chat",
            json=message,
            verify=False
        )
        assert chat_response.status_code == 200
        
        # Get audit logs
        audit_response = requests.get(
            f"{self.backend_url}/api/audit_log",
            verify=False
        )
        assert audit_response.status_code == 200
        audit_data = audit_response.json()
        assert "status" in audit_data
        assert "recent_records" in audit_data
        
        if audit_data["status"] == "enabled":
            print("✅ Audit logging is enabled")
            # Could have records depending on timing
        else:
            print("⚠️ Audit logging is disabled (may be expected)")
        
        print("✅ Audit logging tests completed!")
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        print("🚨 Testing error handling...")
        
        # Test invalid endpoint
        invalid_response = requests.get(
            f"{self.backend_url}/api/nonexistent",
            verify=False
        )
        assert invalid_response.status_code == 404
        print("✅ 404 error handling working")
        
        # Test invalid chat message
        invalid_chat = requests.post(
            f"{self.backend_url}/api/chat",
            json={},  # Missing content
            verify=False
        )
        assert invalid_chat.status_code == 422  # Validation error
        print("✅ Validation error handling working")
        
        # Test invalid preset
        invalid_preset = requests.post(
            f"{self.backend_url}/api/preset",
            json={"preset": "nonexistent_preset"},
            verify=False
        )
        assert invalid_preset.status_code == 500  # Server error
        print("✅ Invalid preset error handling working")
        
        print("✅ Error handling tests completed!")
    
    def run_all_tests(self):
        """Run all integration tests."""
        print("🎯 Starting Stinger Web Demo Integration Tests")
        print("=" * 60)
        
        try:
            self.setup()
            
            # Run test suites
            self.test_chat_functionality()
            print()
            
            self.test_guardrail_settings()
            print()
            
            self.test_preset_switching()
            print()
            
            self.test_conversation_management()
            print()
            
            self.test_audit_logging()
            print()
            
            self.test_error_handling()
            print()
            
            print("🎉 All integration tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            self.teardown()


def main():
    """Main test runner."""
    test_suite = DemoIntegrationTest()
    
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✅ Stinger Web Demo Integration Tests - ALL PASSED")
        sys.exit(0)
    else:
        print("\n❌ Stinger Web Demo Integration Tests - FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()