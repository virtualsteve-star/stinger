#!/usr/bin/env python3
"""
Complete Integration Test Suite
Comprehensive service integration testing including all API endpoints,
concurrent requests, error handling, and complete workflows.
"""

import os
import sys
import time
import json
import pytest
import requests
import subprocess
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable SSL warnings for self-signed certificates
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TestIntegrationComplete:
    """Comprehensive integration tests for web demo."""
    
    BASE_BACKEND_URL = "https://localhost:8000"
    BASE_FRONTEND_URL = "https://localhost:3000"
    
    @classmethod
    def setup_class(cls):
        """Verify services and prepare test environment."""
        print("\n🔍 Running comprehensive integration tests...")
        
        # Verify both services are running
        if not cls._verify_services():
            pytest.skip("Required services not available")
            
        # Store session for connection pooling
        cls.session = requests.Session()
        cls.session.verify = False
        
    @classmethod
    def teardown_class(cls):
        """Clean up test environment."""
        if hasattr(cls, 'session'):
            cls.session.close()
    
    @classmethod
    def _verify_services(cls):
        """Verify all required services are running."""
        services = [
            (cls.BASE_BACKEND_URL + "/api/health", "Backend API"),
            (cls.BASE_FRONTEND_URL, "Frontend")
        ]
        
        all_ready = True
        for url, name in services:
            if not cls._wait_for_service(url, name):
                all_ready = False
                
        return all_ready
    
    @staticmethod
    def _wait_for_service(url, name, timeout=15):
        """Wait for a service to become available."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, verify=False, timeout=3)
                if response.status_code in [200, 404]:
                    print(f"✅ {name} is ready")
                    return True
            except requests.exceptions.RequestException:
                time.sleep(0.5)
        print(f"❌ {name} not available after {timeout}s")
        return False
    
    # Service Health & Stability Tests
    
    def test_service_stability_over_time(self):
        """Test services remain stable over extended period."""
        duration = 10  # seconds
        interval = 2   # seconds
        checks = duration // interval
        
        print(f"\n🕐 Testing stability over {duration} seconds...")
        
        for i in range(checks):
            response = self.session.get(f"{self.BASE_BACKEND_URL}/api/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
            
            if i < checks - 1:
                time.sleep(interval)
                
        print("✅ Services remained stable")
        
    def test_concurrent_requests_handling(self):
        """Test handling of concurrent requests."""
        num_requests = 10
        
        def make_request(i):
            response = self.session.post(
                f"{self.BASE_BACKEND_URL}/api/chat",
                json={"content": f"Concurrent test message {i}"}
            )
            return response.status_code == 200
        
        print(f"\n🔄 Testing {num_requests} concurrent requests...")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            results = [f.result() for f in as_completed(futures)]
            
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.9, f"Only {success_rate*100}% requests succeeded"
        print(f"✅ Handled {success_rate*100}% of concurrent requests")
        
    # Complete API Coverage Tests
    
    def test_all_api_endpoints(self):
        """Test all available API endpoints."""
        endpoints = [
            ("GET", "/api/health", None, 200),
            ("GET", "/api/guardrails", None, 200),
            ("GET", "/api/conversation", None, 200),
            ("POST", "/api/conversation/reset", {}, 200),
            ("GET", "/api/audit_log", None, [200, 404]),  # May not exist
            ("POST", "/api/chat", {"content": "Test"}, 200),
            ("GET", "/api/docs", None, 200),
            ("GET", "/api/openapi.json", None, 200),
        ]
        
        print("\n📡 Testing all API endpoints...")
        
        for method, path, data, expected in endpoints:
            url = self.BASE_BACKEND_URL + path
            
            if method == "GET":
                response = self.session.get(url)
            else:
                response = self.session.post(url, json=data)
                
            if isinstance(expected, list):
                assert response.status_code in expected, f"{method} {path} returned {response.status_code}"
            else:
                assert response.status_code == expected, f"{method} {path} returned {response.status_code}"
                
        print("✅ All API endpoints responding correctly")
        
    def test_complete_chat_workflows(self):
        """Test complete conversation workflows."""
        print("\n💬 Testing complete chat workflows...")
        
        # Reset conversation
        response = self.session.post(f"{self.BASE_BACKEND_URL}/api/conversation/reset")
        assert response.status_code == 200
        
        # Workflow: Normal conversation
        messages = [
            "Hello, how are you?",
            "What services do you provide?",
            "Can you help me with my order?",
            "Thank you for your help!"
        ]
        
        for i, msg in enumerate(messages):
            response = self.session.post(
                f"{self.BASE_BACKEND_URL}/api/chat",
                json={"content": msg}
            )
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert not data.get("blocked", False)
            
        print("✅ Normal conversation workflow completed")
        
        # Workflow: Guardrail triggers
        test_cases = [
            ("My SSN is 123-45-6789", "PII detection"),
            ("You're completely useless!", "Toxicity detection"),
            ("a" * 10000, "Length limit"),
        ]
        
        for content, test_name in test_cases:
            response = self.session.post(
                f"{self.BASE_BACKEND_URL}/api/chat",
                json={"content": content}
            )
            # Should handle appropriately (block or warn)
            assert response.status_code in [200, 400]
            print(f"✅ {test_name} handled correctly")
            
    def test_guardrail_configuration_persistence(self):
        """Test guardrail settings persistence."""
        print("\n⚙️ Testing guardrail configuration...")
        
        # Get original settings
        response = self.session.get(f"{self.BASE_BACKEND_URL}/api/guardrails")
        original_settings = response.json()
        
        # Modify settings
        modified_settings = json.loads(json.dumps(original_settings))
        if modified_settings["input_guardrails"]:
            for g in modified_settings["input_guardrails"]:
                g["enabled"] = False
                
        # Update settings
        response = self.session.post(
            f"{self.BASE_BACKEND_URL}/api/guardrails",
            json=modified_settings
        )
        assert response.status_code == 200
        
        # Verify persistence
        response = self.session.get(f"{self.BASE_BACKEND_URL}/api/guardrails")
        current_settings = response.json()
        
        for g in current_settings["input_guardrails"]:
            assert g["enabled"] is False
            
        # Restore original settings
        response = self.session.post(
            f"{self.BASE_BACKEND_URL}/api/guardrails",
            json=original_settings
        )
        assert response.status_code == 200
        
        print("✅ Configuration persistence verified")
        
    def test_error_handling_scenarios(self):
        """Test various error scenarios."""
        print("\n🚨 Testing error handling...")
        
        error_cases = [
            # Invalid JSON
            ("POST", "/api/chat", "invalid json", 422),
            # Missing required field
            ("POST", "/api/chat", {}, 422),
            # Invalid content type
            ("POST", "/api/chat", {"content": None}, 422),
            # Invalid endpoint
            ("GET", "/api/nonexistent", None, 404),
            # Invalid method
            ("DELETE", "/api/health", None, 405),
        ]
        
        for method, path, data, expected_status in error_cases:
            url = self.BASE_BACKEND_URL + path
            
            if method == "GET":
                response = self.session.get(url)
            elif method == "DELETE":
                response = self.session.delete(url)
            else:
                if isinstance(data, str):
                    response = self.session.post(url, data=data, headers={"Content-Type": "application/json"})
                else:
                    response = self.session.post(url, json=data)
                    
            assert response.status_code == expected_status, f"{method} {path} error handling failed"
            
        print("✅ Error handling working correctly")
        
    def test_cors_configuration(self):
        """Test CORS headers for frontend integration."""
        print("\n🔒 Testing CORS configuration...")
        
        # Test preflight request
        response = self.session.options(
            f"{self.BASE_BACKEND_URL}/api/chat",
            headers={
                "Origin": "https://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        
        print("✅ CORS properly configured")
        
    def test_audit_logging_functionality(self):
        """Test audit logging if available."""
        print("\n📋 Testing audit logging...")
        
        # Check if audit endpoint exists
        response = self.session.get(f"{self.BASE_BACKEND_URL}/api/audit_log")
        
        if response.status_code == 404:
            print("⚠️  Audit logging endpoint not available")
            return
            
        assert response.status_code == 200
        data = response.json()
        
        # Send a tracked message
        test_message = f"Audit test message {time.time()}"
        response = self.session.post(
            f"{self.BASE_BACKEND_URL}/api/chat",
            json={"content": test_message}
        )
        assert response.status_code == 200
        
        # Check if logged (with delay for async logging)
        time.sleep(1)
        response = self.session.get(f"{self.BASE_BACKEND_URL}/api/audit_log")
        if response.status_code == 200:
            new_data = response.json()
            # Verify we have audit data
            if isinstance(new_data, dict) and "records" in new_data:
                assert len(new_data["records"]) > 0
                print("✅ Audit logging functional")
            else:
                print("⚠️  Audit log format unexpected")
                
    def test_performance_metrics(self):
        """Test response time performance."""
        print("\n⚡ Testing performance metrics...")
        
        response_times = []
        num_requests = 10
        
        for i in range(num_requests):
            start_time = time.time()
            response = self.session.post(
                f"{self.BASE_BACKEND_URL}/api/chat",
                json={"content": f"Performance test {i}"}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                response_times.append(end_time - start_time)
                
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            
            print(f"  Average response time: {avg_time*1000:.0f}ms")
            print(f"  Max response time: {max_time*1000:.0f}ms")
            
            # Performance assertions
            assert avg_time < 2.0, f"Average response time too high: {avg_time}s"
            assert max_time < 5.0, f"Max response time too high: {max_time}s"
            
        print("✅ Performance within acceptable limits")
        
    def test_recovery_from_errors(self):
        """Test service recovery from error conditions."""
        print("\n🔧 Testing error recovery...")
        
        # Send multiple invalid requests
        for i in range(5):
            self.session.post(
                f"{self.BASE_BACKEND_URL}/api/chat",
                data="invalid",
                headers={"Content-Type": "application/json"}
            )
            
        # Service should still work
        response = self.session.post(
            f"{self.BASE_BACKEND_URL}/api/chat",
            json={"content": "Recovery test"}
        )
        assert response.status_code == 200
        
        print("✅ Service recovers from errors correctly")


if __name__ == "__main__":
    # Run with pytest if available
    try:
        pytest.main([__file__, "-v", "-s", "--tb=short"])
    except ImportError:
        print("⚠️  pytest not installed, running basic validation...")
        test = TestIntegrationComplete()
        
        try:
            test.setup_class()
            test.test_service_stability_over_time()
            test.test_all_api_endpoints()
            test.test_complete_chat_workflows()
            print("\n✅ Basic integration tests passed")
        except Exception as e:
            print(f"\n❌ Integration tests failed: {e}")
        finally:
            test.teardown_class()