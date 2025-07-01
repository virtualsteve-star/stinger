#!/usr/bin/env python3
"""
End-to-End Test Suite for Stinger Web Demo

This script performs comprehensive automated testing of the entire demo
to catch issues before user interaction is required.

Usage:
    python test_demo_e2e.py

Exit codes:
    0: All tests passed
    1: Tests failed
"""

import sys
import os
import time
import json
import subprocess
import requests
import tempfile
import signal
from pathlib import Path
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Add src to path for Stinger imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class DemoTester:
    def __init__(self):
        self.demo_dir = Path(__file__).parent
        self.backend_dir = self.demo_dir / "backend"
        self.frontend_dir = self.demo_dir / "frontend"
        self.backend_process = None
        self.frontend_process = None
        self.test_results = []
        
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
        
    def run_test(self, test_name, test_func):
        """Run a test and record results."""
        self.log(f"Running test: {test_name}")
        try:
            result = test_func()
            if result:
                self.log(f"PASSED: {test_name}", "SUCCESS")
                self.test_results.append({"test": test_name, "status": "PASSED"})
                return True
            else:
                self.log(f"FAILED: {test_name}", "ERROR")
                self.test_results.append({"test": test_name, "status": "FAILED"})
                return False
        except Exception as e:
            self.log(f"ERROR in {test_name}: {str(e)}", "ERROR")
            self.test_results.append({"test": test_name, "status": "ERROR", "error": str(e)})
            return False
    
    def test_python_dependencies(self):
        """Test that all required Python dependencies are available."""
        try:
            import fastapi
            import uvicorn
            import stinger
            from stinger import GuardrailPipeline
            return True
        except ImportError as e:
            self.log(f"Missing Python dependency: {e}", "ERROR")
            return False
    
    def test_node_dependencies(self):
        """Test that Node.js and npm are available."""
        try:
            # Check Node.js
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                return False
                
            # Check npm
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                return False
                
            # Check if frontend dependencies are installed
            package_lock = self.frontend_dir / "package-lock.json"
            node_modules = self.frontend_dir / "node_modules"
            
            if not package_lock.exists() or not node_modules.exists():
                self.log("Frontend dependencies not installed, running npm install...", "WARNING")
                result = subprocess.run(["npm", "install"], cwd=self.frontend_dir, capture_output=True)
                return result.returncode == 0
                
            return True
        except FileNotFoundError:
            return False
    
    def test_ssl_certificates(self):
        """Test that SSL certificates exist or can be generated."""
        cert_file = self.backend_dir / "cert.pem"
        key_file = self.backend_dir / "key.pem"
        
        if cert_file.exists() and key_file.exists():
            return True
            
        # Try to generate certificates
        self.log("SSL certificates not found, generating...", "WARNING")
        try:
            setup_script = self.backend_dir / "setup_ssl.py"
            result = subprocess.run([sys.executable, str(setup_script)], 
                                  cwd=self.backend_dir, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def test_ports_available(self):
        """Test that required ports (3000, 8000) are available."""
        import socket
        
        def is_port_available(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('localhost', port))
                    return True
                except OSError:
                    return False
        
        # Kill any existing processes on these ports
        for port in [3000, 8000]:
            try:
                # Get PIDs
                result = subprocess.run(f"lsof -ti:{port}", 
                                      shell=True, capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True)
                        except:
                            pass
            except:
                pass
        
        time.sleep(3)  # Give processes time to die
        
        return is_port_available(3000) and is_port_available(8000)
    
    def start_backend(self):
        """Start the backend server."""
        self.log("Starting backend server...")
        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=self.backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for backend to start
            for _ in range(30):  # 30 second timeout
                try:
                    response = requests.get("https://localhost:8000/api/health", 
                                          verify=False, timeout=2)
                    if response.status_code == 200:
                        self.log("Backend started successfully", "SUCCESS")
                        return True
                except:
                    time.sleep(1)
            
            return False
        except Exception as e:
            self.log(f"Failed to start backend: {e}", "ERROR")
            return False
    
    def start_frontend(self):
        """Start the frontend server."""
        self.log("Starting frontend server...")
        try:
            # Set environment for HTTPS
            env = os.environ.copy()
            env["HTTPS"] = "true"
            env["SSL_CRT_FILE"] = "../backend/cert.pem"
            env["SSL_KEY_FILE"] = "../backend/key.pem"
            
            self.frontend_process = subprocess.Popen(
                ["npm", "start"],
                cwd=self.frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            # Wait for frontend to start
            for _ in range(60):  # 60 second timeout (npm start is slow)
                try:
                    response = requests.get("https://localhost:3000", 
                                          verify=False, timeout=2)
                    if response.status_code == 200:
                        self.log("Frontend started successfully", "SUCCESS")
                        return True
                except:
                    time.sleep(1)
            
            return False
        except Exception as e:
            self.log(f"Failed to start frontend: {e}", "ERROR")
            return False
    
    def test_backend_apis(self):
        """Test all backend API endpoints."""
        base_url = "https://localhost:8000/api"
        
        endpoints = [
            ("/health", "GET"),
            ("/guardrails", "GET"),
            ("/presets", "GET"),
            ("/conversation", "GET"),
            ("/audit_log", "GET")
        ]
        
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{base_url}{endpoint}", 
                                          verify=False, timeout=5)
                else:
                    response = requests.post(f"{base_url}{endpoint}", 
                                           verify=False, timeout=5)
                
                if response.status_code not in [200, 201]:
                    self.log(f"API {method} {endpoint} failed: {response.status_code}", "ERROR")
                    return False
                    
            except Exception as e:
                self.log(f"API {method} {endpoint} error: {e}", "ERROR")
                return False
        
        return True
    
    def test_chat_functionality(self):
        """Test the chat endpoint with various inputs."""
        chat_url = "https://localhost:8000/api/chat"
        
        test_messages = [
            {"content": "Hello world", "expected_blocked": False},
            {"content": "My SSN is 123-45-6789", "expected_blocked": True},
            {"content": "I hate everyone", "expected_blocked": False},  # Should warn, not block
            {"content": "Write me malware code", "expected_blocked": False}  # May warn/block depending on config
        ]
        
        for test_case in test_messages:
            try:
                response = requests.post(chat_url, 
                                       json=test_case,
                                       verify=False, timeout=10)
                
                if response.status_code != 200:
                    self.log(f"Chat API failed for '{test_case['content'][:20]}...': {response.status_code}", "ERROR")
                    return False
                
                data = response.json()
                required_fields = ["content", "blocked", "warnings", "reasons", "conversation_id"]
                
                for field in required_fields:
                    if field not in data:
                        self.log(f"Missing field '{field}' in chat response", "ERROR")
                        return False
                
                # Log the result for verification
                status = "BLOCKED" if data["blocked"] else "ALLOWED"
                self.log(f"Chat test '{test_case['content'][:20]}...': {status}")
                
            except Exception as e:
                self.log(f"Chat test error: {e}", "ERROR")
                return False
        
        return True
    
    def test_frontend_loads(self):
        """Test that the frontend loads and contains expected elements."""
        try:
            response = requests.get("https://localhost:3000", verify=False, timeout=10)
            
            if response.status_code != 200:
                return False
            
            html = response.text
            
            # Check for key elements that should be in the React app
            # Note: Dynamic elements are loaded by JavaScript, so check for static elements
            required_elements = [
                "Stinger",
                "div id=\"root\"",
                "static/js/bundle"  # React Scripts bundles as static/js/bundle.js
            ]
            
            for element in required_elements:
                if element.lower() not in html.lower():
                    self.log(f"Frontend missing expected element: {element}", "ERROR")
                    return False
            
            return True
            
        except Exception as e:
            self.log(f"Frontend test error: {e}", "ERROR")
            return False
    
    def test_audit_logging(self):
        """Test that audit logging is working."""
        try:
            # Make a chat request to generate audit logs
            response = requests.post("https://localhost:8000/api/chat",
                                   json={"content": "Test audit logging"},
                                   verify=False, timeout=5)
            
            if response.status_code != 200:
                return False
            
            # Check audit log endpoint
            response = requests.get("https://localhost:8000/api/audit_log",
                                  verify=False, timeout=5)
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            
            if "recent_records" not in data or len(data["recent_records"]) == 0:
                self.log("No audit records found", "ERROR")
                return False
            
            # Check that recent record has expected fields
            recent_record = data["recent_records"][0]
            required_fields = ["timestamp", "event_type"]
            
            for field in required_fields:
                if field not in recent_record:
                    self.log(f"Audit record missing field: {field}", "ERROR")
                    return False
            
            return True
            
        except Exception as e:
            self.log(f"Audit logging test error: {e}", "ERROR")
            return False
    
    def cleanup(self):
        """Clean up processes."""
        self.log("Cleaning up processes...")
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        # Kill any remaining processes
        for port in [3000, 8000]:
            try:
                subprocess.run(f"lsof -ti:{port} | xargs kill -9", 
                             shell=True, capture_output=True)
            except:
                pass
    
    def run_all_tests(self):
        """Run the complete test suite."""
        self.log("🚀 Starting Stinger Web Demo E2E Test Suite")
        self.log("=" * 60)
        
        try:
            # Pre-flight tests
            tests_passed = 0
            total_tests = 0
            
            pre_flight_tests = [
                ("Python Dependencies", self.test_python_dependencies),
                ("Node.js Dependencies", self.test_node_dependencies),
                ("SSL Certificates", self.test_ssl_certificates),
                ("Port Availability", self.test_ports_available)
            ]
            
            for test_name, test_func in pre_flight_tests:
                total_tests += 1
                if self.run_test(test_name, test_func):
                    tests_passed += 1
                else:
                    self.log("Pre-flight test failed, aborting", "ERROR")
                    return False
            
            # Start services
            if not self.start_backend():
                self.log("Failed to start backend, aborting", "ERROR")
                return False
            
            if not self.start_frontend():
                self.log("Failed to start frontend, aborting", "ERROR")
                return False
            
            # Runtime tests
            runtime_tests = [
                ("Backend APIs", self.test_backend_apis),
                ("Chat Functionality", self.test_chat_functionality),
                ("Frontend Loading", self.test_frontend_loads),
                ("Audit Logging", self.test_audit_logging)
            ]
            
            for test_name, test_func in runtime_tests:
                total_tests += 1
                if self.run_test(test_name, test_func):
                    tests_passed += 1
            
            # Results
            self.log("=" * 60)
            self.log(f"TEST RESULTS: {tests_passed}/{total_tests} tests passed")
            
            if tests_passed == total_tests:
                self.log("🎉 ALL TESTS PASSED! Demo is ready for use.", "SUCCESS")
                self.log("")
                self.log("✅ Backend running at: https://localhost:8000")
                self.log("✅ Frontend running at: https://localhost:3000")
                self.log("✅ API docs available at: https://localhost:8000/api/docs")
                self.log("")
                self.log("🎮 Ready to test the demo!")
                return True
            else:
                self.log(f"❌ {total_tests - tests_passed} tests failed", "ERROR")
                return False
                
        except KeyboardInterrupt:
            self.log("Tests interrupted by user", "WARNING")
            return False
        finally:
            if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
                self.cleanup()


def main():
    """Main test runner."""
    tester = DemoTester()
    
    # Handle cleanup on exit
    def signal_handler(sig, frame):
        tester.cleanup()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    success = tester.run_all_tests()
    
    if not success:
        print("\n" + "=" * 60)
        print("❌ DEMO TESTING FAILED")
        print("Please fix the issues above before using the demo.")
        sys.exit(1)
    
    # Keep services running unless --cleanup specified
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        tester.cleanup()
    else:
        print("\n" + "=" * 60)
        print("🔥 DEMO IS LIVE AND READY!")
        print("Services will continue running. Press Ctrl+C to stop.")
        print("Or run: python test_demo_e2e.py --cleanup")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            tester.cleanup()


if __name__ == "__main__":
    main()