#!/usr/bin/env python3
"""
Core Functionality Test Suite - Quick Smoke Test
Consolidates basic functionality tests for rapid validation.
Target runtime: <30 seconds
"""

import os
import sys
import time
import json
import pytest
import requests
from pathlib import Path

# Disable SSL warnings for self-signed certificates
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TestCoreFunctionality:
    """Quick smoke tests for core web demo functionality."""
    
    BASE_BACKEND_URL = "https://localhost:8000"
    BASE_FRONTEND_URL = "https://localhost:3000"
    
    @classmethod
    def setup_class(cls):
        """Verify services are running before tests."""
        print("\n🔍 Checking service availability...")
        
        # Check backend
        backend_ready = cls._wait_for_service(cls.BASE_BACKEND_URL + "/api/health", "Backend")
        if not backend_ready:
            pytest.skip("Backend service not available")
            
        # Check frontend (optional for core tests)
        cls.frontend_available = cls._wait_for_service(cls.BASE_FRONTEND_URL, "Frontend", timeout=5)
        
    @staticmethod
    def _wait_for_service(url, name, timeout=10):
        """Wait for a service to become available."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, verify=False, timeout=2)
                if response.status_code in [200, 404]:  # 404 is OK for base URL
                    print(f"✅ {name} is ready at {url}")
                    return True
            except requests.exceptions.RequestException:
                time.sleep(0.5)
        print(f"⚠️  {name} not available at {url}")
        return False
    
    def test_backend_health(self):
        """Test backend health endpoint."""
        response = requests.get(f"{self.BASE_BACKEND_URL}/api/health", verify=False)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["pipeline_loaded"] is True
        assert "total_guardrails" in data
        assert data["total_guardrails"] > 0
        
    def test_api_key_handling(self):
        """Test API key management and mock mode."""
        # Test without API key (should work in mock mode)
        test_message = "Hello, test message"
        response = requests.post(
            f"{self.BASE_BACKEND_URL}/api/chat",
            json={"content": test_message},
            verify=False
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # In mock mode or with API key
        assert "response" in data
        assert len(data["response"]) > 0
        
    def test_basic_chat_functionality(self):
        """Test basic chat API with safe content."""
        # Test safe message
        safe_message = "What is the weather like today?"
        response = requests.post(
            f"{self.BASE_BACKEND_URL}/api/chat",
            json={"content": safe_message},
            verify=False
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "error" not in data
        assert data.get("blocked") is False
        
    def test_pii_detection(self):
        """Test PII detection guardrail."""
        # Test message with PII
        pii_message = "My credit card number is 4111-1111-1111-1111"
        response = requests.post(
            f"{self.BASE_BACKEND_URL}/api/chat",
            json={"content": pii_message},
            verify=False
        )
        
        # Should either block or warn
        assert response.status_code in [200, 400]
        data = response.json()
        
        # Check for blocking or warning
        if response.status_code == 400:
            assert "error" in data
        else:
            # May have warnings or be blocked
            assert data.get("blocked") is True or data.get("warnings")
            
    def test_toxic_content_handling(self):
        """Test toxic content detection."""
        toxic_message = "You are so stupid and worthless!"
        response = requests.post(
            f"{self.BASE_BACKEND_URL}/api/chat",
            json={"content": toxic_message},
            verify=False
        )
        
        # Should handle toxic content appropriately
        assert response.status_code in [200, 400]
        data = response.json()
        
        if response.status_code == 200:
            # Either blocked or has warnings
            assert data.get("blocked") is True or data.get("warnings")
            
    def test_guardrail_settings_retrieval(self):
        """Test guardrail settings API."""
        response = requests.get(f"{self.BASE_BACKEND_URL}/api/guardrails", verify=False)
        assert response.status_code == 200
        
        data = response.json()
        assert "input_guardrails" in data
        assert "output_guardrails" in data
        assert isinstance(data["input_guardrails"], list)
        assert isinstance(data["output_guardrails"], list)
        
        # Should have at least one guardrail
        total_guardrails = len(data["input_guardrails"]) + len(data["output_guardrails"])
        assert total_guardrails > 0
        
    def test_guardrail_settings_update(self):
        """Test updating guardrail settings."""
        # First get current settings
        response = requests.get(f"{self.BASE_BACKEND_URL}/api/guardrails", verify=False)
        current_settings = response.json()
        
        # Toggle a guardrail
        if current_settings["input_guardrails"]:
            guardrail = current_settings["input_guardrails"][0]
            guardrail["enabled"] = not guardrail.get("enabled", True)
            
            # Update settings
            response = requests.post(
                f"{self.BASE_BACKEND_URL}/api/guardrails",
                json=current_settings,
                verify=False
            )
            assert response.status_code == 200
            
            # Verify update
            response = requests.get(f"{self.BASE_BACKEND_URL}/api/guardrails", verify=False)
            updated_settings = response.json()
            assert updated_settings["input_guardrails"][0]["enabled"] == guardrail["enabled"]
            
    def test_conversation_management(self):
        """Test conversation tracking."""
        # Get initial conversation status
        response = requests.get(f"{self.BASE_BACKEND_URL}/api/conversation", verify=False)
        assert response.status_code == 200
        initial_data = response.json()
        
        # Send a message
        response = requests.post(
            f"{self.BASE_BACKEND_URL}/api/chat",
            json={"content": "Test message for conversation"},
            verify=False
        )
        assert response.status_code == 200
        
        # Check conversation was updated
        response = requests.get(f"{self.BASE_BACKEND_URL}/api/conversation", verify=False)
        updated_data = response.json()
        
        # Message count should increase
        if "message_count" in initial_data and "message_count" in updated_data:
            assert updated_data["message_count"] >= initial_data["message_count"]
            
    def test_conversation_reset(self):
        """Test conversation reset functionality."""
        response = requests.post(f"{self.BASE_BACKEND_URL}/api/conversation/reset", verify=False)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "success" or "reset" in str(data).lower()
        
    def test_api_documentation(self):
        """Test API documentation availability."""
        response = requests.get(f"{self.BASE_BACKEND_URL}/api/docs", verify=False)
        assert response.status_code == 200
        # Should return HTML documentation
        assert "text/html" in response.headers.get("content-type", "")


if __name__ == "__main__":
    # Run with pytest if available, otherwise run basic validation
    try:
        pytest.main([__file__, "-v", "-s"])
    except ImportError:
        print("⚠️  pytest not installed, running basic validation...")
        test = TestCoreFunctionality()
        test.setup_class()
        
        # Run basic tests
        tests = [
            test.test_backend_health,
            test.test_basic_chat_functionality,
            test.test_guardrail_settings_retrieval
        ]
        
        passed = 0
        for test_func in tests:
            try:
                test_func()
                print(f"✅ {test_func.__name__}")
                passed += 1
            except Exception as e:
                print(f"❌ {test_func.__name__}: {e}")
                
        print(f"\n{'✅' if passed == len(tests) else '❌'} {passed}/{len(tests)} tests passed")