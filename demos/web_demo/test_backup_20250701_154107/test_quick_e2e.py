#!/usr/bin/env python3
"""
Quick End-to-End Test for Stinger Web Demo

Tests the core functionality quickly without waiting for frontend build:
1. Backend starts without API key errors
2. Chat functionality works (the main use case)
3. Guardrails are functioning
4. Settings management works

This runs in under 30 seconds to confirm the demo is working.
"""

import sys
import os
import time
import subprocess
import requests
import signal
from pathlib import Path
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class QuickE2ETest:
    def __init__(self):
        self.demo_dir = Path(__file__).parent
        self.backend_dir = self.demo_dir / "backend"
        self.backend_process = None
        self.api_key_available = bool(os.getenv('OPENAI_API_KEY'))
        
    def log(self, message, level="INFO"):
        """Log a message with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        prefix = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}.get(level, "ℹ️")
        print(f"[{timestamp}] {prefix} {message}")
        
    def cleanup_backend_port(self):
        """Kill any existing backend process."""
        try:
            result = subprocess.run("lsof -ti:8000", shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True)
                    self.log(f"Killed existing backend process {pid}")
                time.sleep(2)
        except:
            pass
            
    def start_backend(self):
        """Start backend and wait for it to be ready."""
        self.log("Starting backend...")
        
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent / "src")
        
        self.backend_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=self.backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        # Wait for backend to be ready (max 30 seconds)
        for attempt in range(30):
            try:
                response = requests.get("https://localhost:8000/api/health", verify=False, timeout=2)
                if response.status_code == 200:
                    self.log("✅ Backend ready!")
                    return True
            except:
                time.sleep(1)
        
        self.log("❌ Backend failed to start", "ERROR")
        return False
        
    def test_no_api_key_error(self):
        """Test that backend starts without the old 'demo_key' error."""
        self.log("Testing API key handling...")
        
        try:
            response = requests.get("https://localhost:8000/api/health", verify=False)
            data = response.json()
            
            assert response.status_code == 200, "Health check failed"
            assert data["status"] == "healthy", "Backend not healthy"
            
            self.log("✅ No API key errors - backend healthy")
            return True
            
        except Exception as e:
            self.log(f"❌ API key test failed: {e}", "ERROR")
            return False
            
    def test_chat_works(self):
        """Test the main chat functionality."""
        self.log("Testing chat functionality...")
        
        try:
            # Test simple message
            response = requests.post("https://localhost:8000/api/chat",
                                   json={"content": "Hello, test message"},
                                   verify=False, timeout=10)
            
            assert response.status_code == 200, f"Chat failed: {response.status_code}"
            
            data = response.json()
            required_fields = ["content", "blocked", "warnings", "conversation_id"]
            for field in required_fields:
                assert field in data, f"Missing field: {field}"
            
            if self.api_key_available:
                assert len(data["content"]) > 0, "Empty response with API key"
                self.log("✅ Chat works with real LLM")
            else:
                assert "OpenAI API not configured" in data["content"], "Missing setup instructions"
                self.log("✅ Chat works in mock mode with setup instructions")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Chat test failed: {e}", "ERROR")
            return False
            
    def test_guardrails_work(self):
        """Test that guardrails are functioning."""
        self.log("Testing guardrails...")
        
        try:
            # Test PII detection
            response = requests.post("https://localhost:8000/api/chat",
                                   json={"content": "My email is test@example.com"},
                                   verify=False, timeout=10)
            
            assert response.status_code == 200, "Guardrail test failed"
            
            data = response.json()
            # Should either block or warn about PII
            has_protection = data["blocked"] or len(data["warnings"]) > 0
            assert has_protection, "PII not detected by guardrails"
            
            self.log("✅ Guardrails detecting PII correctly")
            return True
            
        except Exception as e:
            self.log(f"❌ Guardrail test failed: {e}", "ERROR")
            return False
            
    def test_settings_work(self):
        """Test settings management."""
        self.log("Testing settings management...")
        
        try:
            # Get settings
            response = requests.get("https://localhost:8000/api/guardrails", verify=False)
            assert response.status_code == 200, "Failed to get settings"
            
            settings = response.json()
            assert "input_guardrails" in settings, "Missing input_guardrails"
            assert "output_guardrails" in settings, "Missing output_guardrails"
            
            self.log(f"✅ Settings available: {len(settings['input_guardrails'])} input, {len(settings['output_guardrails'])} output")
            return True
            
        except Exception as e:
            self.log(f"❌ Settings test failed: {e}", "ERROR")
            return False
            
    def cleanup(self):
        """Clean up backend process."""
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                self.log("Backend process terminated")
            except:
                try:
                    self.backend_process.kill()
                    self.log("Backend process killed")
                except:
                    pass
                    
    def run_quick_test(self):
        """Run the quick test suite."""
        self.log("🚀 Quick E2E Test for Stinger Web Demo")
        self.log("=" * 50)
        
        if self.api_key_available:
            self.log("✅ OpenAI API key detected")
        else:
            self.log("⚠️ No OpenAI API key - testing mock mode")
        
        try:
            # Setup
            self.cleanup_backend_port()
            
            if not self.start_backend():
                return False
            
            # Run tests
            tests = [
                ("No API Key Errors", self.test_no_api_key_error),
                ("Chat Functionality", self.test_chat_works),
                ("Guardrails Working", self.test_guardrails_work),
                ("Settings Management", self.test_settings_work)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                if test_func():
                    passed += 1
                else:
                    break  # Stop on first failure
            
            # Results
            self.log("=" * 50)
            self.log(f"📊 Results: {passed}/{total} tests passed")
            
            if passed == total:
                self.log("🎉 ALL CORE TESTS PASSED!", "SUCCESS")
                self.log("✅ Demo is ready for manual testing")
                self.log("🌐 Backend running at: https://localhost:8000")
                self.log("📚 API docs at: https://localhost:8000/api/docs")
                
                if not self.api_key_available:
                    self.log("\n💡 To enable real LLM responses:")
                    self.log("   export OPENAI_API_KEY='your-key-here'")
                
                return True
            else:
                self.log("❌ Core functionality broken", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Test error: {e}", "ERROR")
            return False
        finally:
            self.cleanup()

def main():
    tester = QuickE2ETest()
    
    def signal_handler(sig, frame):
        tester.cleanup()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    success = tester.run_quick_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()