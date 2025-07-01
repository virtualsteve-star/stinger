#!/usr/bin/env python3
"""
Comprehensive End-to-End Test for Stinger Web Demo

This test starts both backend and frontend from scratch and runs through
real user scenarios to ensure the demo works completely.

Specifically tests:
1. Backend starts without API key errors
2. Frontend loads correctly 
3. Chat functionality works (with/without OpenAI)
4. Guardrails are functioning
5. Settings management works
6. Conversation management works
"""

import sys
import os
import time
import json
import subprocess
import requests
import signal
import threading
from pathlib import Path
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Add src to path for Stinger imports  
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class ComprehensiveE2ETest:
    def __init__(self):
        self.demo_dir = Path(__file__).parent
        self.backend_dir = self.demo_dir / "backend"
        self.frontend_dir = self.demo_dir / "frontend"
        self.backend_process = None
        self.frontend_process = None
        self.test_results = []
        self.api_key_available = bool(os.getenv('OPENAI_API_KEY'))
        
    def log(self, message, level="INFO"):
        """Log a message with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "WARNING": "⚠️"
        }.get(level, "ℹ️")
        print(f"[{timestamp}] {prefix} {message}")
        
    def cleanup_ports(self):
        """Kill any existing processes on our ports."""
        for port in [3000, 8000]:
            try:
                result = subprocess.run(f"lsof -ti:{port}", 
                                      shell=True, capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True)
                        self.log(f"Killed process {pid} on port {port}")
            except:
                pass
        time.sleep(2)  # Give processes time to die
        
    def start_backend(self):
        """Start the backend server from scratch."""
        self.log("Starting backend server...")
        
        # Ensure we're in the right directory
        os.chdir(self.backend_dir)
        
        # Set up environment
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent / "src")
        
        # Start backend
        self.backend_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=self.backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        self.log(f"Backend process started (PID: {self.backend_process.pid})")
        
        # Wait for backend to be ready
        for attempt in range(30):  # 30 second timeout
            try:
                response = requests.get("https://localhost:8000/api/health", 
                                      verify=False, timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"Backend ready: {data['status']}")
                    return True
            except:
                time.sleep(1)
        
        # If we get here, backend didn't start
        self.log("Backend failed to start within timeout", "ERROR")
        self.get_backend_logs()
        return False
        
    def start_frontend(self):
        """Start the frontend server from scratch."""
        self.log("Starting frontend server...")
        
        # Check if dependencies are installed
        node_modules = self.frontend_dir / "node_modules"
        if not node_modules.exists():
            self.log("Installing frontend dependencies...")
            result = subprocess.run(["npm", "install"], 
                                  cwd=self.frontend_dir, 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.log(f"npm install failed: {result.stderr}", "ERROR")
                return False
        
        # Set up environment for HTTPS
        env = os.environ.copy()
        env["HTTPS"] = "true"
        env["SSL_CRT_FILE"] = "../backend/cert.pem"
        env["SSL_KEY_FILE"] = "../backend/key.pem"
        
        # Start frontend
        self.frontend_process = subprocess.Popen(
            ["npm", "start"],
            cwd=self.frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        self.log(f"Frontend process started (PID: {self.frontend_process.pid})")
        
        # Wait for frontend to be ready (React dev server takes longer)
        for attempt in range(60):  # 60 second timeout
            try:
                response = requests.get("https://localhost:3000", 
                                      verify=False, timeout=2)
                if response.status_code == 200:
                    self.log("Frontend ready")
                    return True
            except:
                time.sleep(1)
        
        self.log("Frontend failed to start within timeout", "ERROR")
        return False
        
    def test_backend_health(self):
        """Test backend health and API key status."""
        self.log("Testing backend health...")
        
        try:
            response = requests.get("https://localhost:8000/api/health", verify=False)
            data = response.json()
            
            # Check basic health
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            assert data["status"] == "healthy", f"Backend not healthy: {data['status']}"
            assert data["pipeline_loaded"] is True, "Pipeline not loaded"
            
            self.log(f"Backend health: {data['status']}")
            self.log(f"Guardrails: {data['enabled_guardrails']}/{data['total_guardrails']} active")
            self.log(f"Audit: {'enabled' if data['audit_enabled'] else 'disabled'}")
            
            return True
            
        except Exception as e:
            self.log(f"Backend health test failed: {e}", "ERROR")
            return False
            
    def test_chat_basic_functionality(self):
        """Test basic chat functionality - the core use case."""
        self.log("Testing basic chat functionality...")
        
        test_cases = [
            {
                "name": "Simple greeting", 
                "content": "Hello, how are you?",
                "should_block": False
            },
            {
                "name": "PII content",
                "content": "My email is test@example.com and my phone is 555-123-4567", 
                "should_warn_or_block": True
            },
            {
                "name": "Toxic content",
                "content": "I hate everyone and want to hurt people",
                "should_warn_or_block": True  
            }
        ]
        
        conversation_id = None
        
        for test_case in test_cases:
            try:
                self.log(f"Testing: {test_case['name']}")
                
                payload = {"content": test_case["content"]}
                if conversation_id:
                    payload["conversation_id"] = conversation_id
                
                response = requests.post("https://localhost:8000/api/chat",
                                       json=payload,
                                       verify=False, timeout=15)
                
                assert response.status_code == 200, f"Chat API failed: {response.status_code}"
                
                data = response.json()
                
                # Verify response structure
                required_fields = ["content", "blocked", "warnings", "reasons", "conversation_id"]
                for field in required_fields:
                    assert field in data, f"Missing field: {field}"
                
                # Store conversation ID for subsequent tests
                if not conversation_id:
                    conversation_id = data["conversation_id"]
                
                # Check API key handling
                if not self.api_key_available:
                    # Should get mock response with setup instructions
                    assert "OpenAI API not configured" in data["content"], "Missing setup instructions in mock mode"
                    assert "OpenAI API key not configured" in data["warnings"], "Missing API key warning"
                else:
                    # Should get real LLM response
                    assert len(data["content"]) > 0, "Empty response with API key"
                
                # Check guardrail behavior
                if test_case.get("should_block"):
                    assert data["blocked"], f"Expected blocking for: {test_case['name']}"
                elif test_case.get("should_warn_or_block"):
                    assert data["blocked"] or len(data["warnings"]) > 0, f"Expected warning/blocking for: {test_case['name']}"
                
                status = "BLOCKED" if data["blocked"] else "ALLOWED" 
                warnings = f" ({len(data['warnings'])} warnings)" if data["warnings"] else ""
                self.log(f"  Result: {status}{warnings}")
                
            except Exception as e:
                self.log(f"Chat test failed for '{test_case['name']}': {e}", "ERROR")
                return False
                
        return True
        
    def test_guardrail_settings(self):
        """Test guardrail settings management."""
        self.log("Testing guardrail settings...")
        
        try:
            # Get current settings
            response = requests.get("https://localhost:8000/api/guardrails", verify=False)
            assert response.status_code == 200, "Failed to get guardrail settings"
            
            original_settings = response.json()
            assert "input_guardrails" in original_settings, "Missing input_guardrails"
            assert "output_guardrails" in original_settings, "Missing output_guardrails"
            
            self.log(f"Current settings: {len(original_settings['input_guardrails'])} input, {len(original_settings['output_guardrails'])} output")
            
            # Try to toggle a guardrail
            if original_settings["input_guardrails"]:
                modified_settings = original_settings.copy()
                first_guardrail = modified_settings["input_guardrails"][0]
                original_state = first_guardrail["enabled"]
                first_guardrail["enabled"] = not original_state
                
                # Update settings
                response = requests.post("https://localhost:8000/api/guardrails",
                                       json=modified_settings,
                                       verify=False)
                assert response.status_code == 200, "Failed to update settings"
                
                self.log(f"Toggled '{first_guardrail['name']}' from {original_state} to {not original_state}")
                
                # Restore original settings
                response = requests.post("https://localhost:8000/api/guardrails",
                                       json=original_settings,
                                       verify=False)
                assert response.status_code == 200, "Failed to restore settings"
                
                self.log("Settings restored successfully")
            
            return True
            
        except Exception as e:
            self.log(f"Guardrail settings test failed: {e}", "ERROR")
            return False
            
    def test_conversation_management(self):
        """Test conversation management."""
        self.log("Testing conversation management...")
        
        try:
            # Start a conversation
            response = requests.post("https://localhost:8000/api/chat",
                                   json={"content": "Start conversation test"},
                                   verify=False)
            assert response.status_code == 200, "Failed to start conversation"
            
            # Get conversation info
            response = requests.get("https://localhost:8000/api/conversation", verify=False)
            assert response.status_code == 200, "Failed to get conversation info"
            
            data = response.json()
            assert data["active"] is True, "Conversation not active"
            assert "conversation_id" in data, "Missing conversation_id"
            
            self.log(f"Conversation active: {data['conversation_id']}")
            
            # Reset conversation
            response = requests.post("https://localhost:8000/api/conversation/reset", verify=False)
            assert response.status_code == 200, "Failed to reset conversation"
            
            # Verify reset
            response = requests.get("https://localhost:8000/api/conversation", verify=False)
            data = response.json()
            assert data["active"] is False, "Conversation still active after reset"
            
            self.log("Conversation reset successfully")
            return True
            
        except Exception as e:
            self.log(f"Conversation management test failed: {e}", "ERROR")
            return False
            
    def test_frontend_basic_load(self):
        """Test that frontend loads with expected elements."""
        self.log("Testing frontend basic load...")
        
        try:
            response = requests.get("https://localhost:3000", verify=False, timeout=10)
            assert response.status_code == 200, f"Frontend failed to load: {response.status_code}"
            
            html = response.text.lower()
            
            # Check for key elements
            required_elements = [
                "stinger",
                "div id=\"root\"",
                "static/js/"  # React bundles
            ]
            
            for element in required_elements:
                assert element.lower() in html, f"Frontend missing: {element}"
                
            self.log("Frontend loaded with all required elements")
            return True
            
        except Exception as e:
            self.log(f"Frontend test failed: {e}", "ERROR")
            return False
            
    def get_backend_logs(self):
        """Get backend logs for debugging."""
        if self.backend_process:
            try:
                stdout, stderr = self.backend_process.communicate(timeout=1)
                if stdout:
                    self.log("Backend stdout:", "INFO")
                    print(stdout)
                if stderr:
                    self.log("Backend stderr:", "ERROR") 
                    print(stderr)
            except:
                pass
                
    def cleanup(self):
        """Clean up processes."""
        self.log("Cleaning up...")
        
        processes = [
            ("Frontend", self.frontend_process),
            ("Backend", self.backend_process)
        ]
        
        for name, process in processes:
            if process:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    self.log(f"{name} process terminated")
                except subprocess.TimeoutExpired:
                    process.kill()
                    self.log(f"{name} process killed")
                except Exception as e:
                    self.log(f"Error stopping {name}: {e}", "WARNING")
        
        # Kill any remaining processes on our ports
        self.cleanup_ports()
        
    def run_comprehensive_test(self):
        """Run the complete test suite."""
        self.log("🚀 Starting Comprehensive E2E Test for Stinger Web Demo")
        self.log("=" * 70)
        
        if self.api_key_available:
            self.log("✅ OpenAI API key detected - testing with real LLM", "SUCCESS")
        else:
            self.log("⚠️ No OpenAI API key - testing in mock mode", "WARNING")
        
        try:
            # Clean up any existing processes
            self.cleanup_ports()
            
            # Start services
            self.log("\n🔧 Starting Services...")
            if not self.start_backend():
                return False
            
            if not self.start_frontend():
                return False
                
            # Run tests
            tests = [
                ("Backend Health", self.test_backend_health),
                ("Chat Basic Functionality", self.test_chat_basic_functionality),
                ("Guardrail Settings", self.test_guardrail_settings),
                ("Conversation Management", self.test_conversation_management),
                ("Frontend Basic Load", self.test_frontend_basic_load)
            ]
            
            self.log("\n🧪 Running Tests...")
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                self.log(f"\n--- {test_name} ---")
                try:
                    if test_func():
                        self.log(f"✅ PASSED: {test_name}", "SUCCESS")
                        passed += 1
                    else:
                        self.log(f"❌ FAILED: {test_name}", "ERROR")
                except Exception as e:
                    self.log(f"❌ ERROR in {test_name}: {e}", "ERROR")
            
            # Results
            self.log("\n" + "=" * 70)
            self.log(f"📊 TEST RESULTS: {passed}/{total} tests passed")
            
            if passed == total:
                self.log("🎉 ALL TESTS PASSED! Demo is fully functional.", "SUCCESS")
                self.log("\n🎮 Demo is ready for manual testing:")
                self.log("   Frontend: https://localhost:3000")
                self.log("   Backend:  https://localhost:8000/api/docs") 
                
                if not self.api_key_available:
                    self.log("\n💡 To enable real LLM responses:")
                    self.log("   export OPENAI_API_KEY='your-key-here'")
                    self.log("   Then restart the backend")
                
                return True
            else:
                self.log(f"❌ {total - passed} tests failed", "ERROR")
                return False
                
        except KeyboardInterrupt:
            self.log("Tests interrupted by user", "WARNING")
            return False
        except Exception as e:
            self.log(f"Test suite error: {e}", "ERROR")
            return False
        finally:
            # Keep services running for manual testing
            self.log("\n🔥 Services are still running for manual testing")
            self.log("Press Ctrl+C to stop all services")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.cleanup()

def main():
    """Main test runner."""
    tester = ComprehensiveE2ETest()
    
    # Handle cleanup on exit
    def signal_handler(sig, frame):
        tester.cleanup()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()