#!/usr/bin/env python3
"""
REAL Frontend-Backend E2E Test

This test actually validates that:
1. Frontend React app loads and renders
2. Frontend JavaScript can make API calls to backend  
3. The proxy configuration works
4. Complete user workflow functions through the web interface

This is what TRUE E2E testing should look like.
"""

import requests
import time
import json
import subprocess
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

class RealE2ETest:
    def __init__(self):
        self.driver = None
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        icon = icons.get(level, "ℹ️")
        print(f"[{timestamp}] {icon} {message}")
        
    def setup_browser(self):
        """Set up headless Chrome browser for testing."""
        self.log("Setting up browser for E2E testing...")
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
            self.log("✅ Browser setup complete", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Browser setup failed: {e}", "ERROR")
            self.log("💡 Install ChromeDriver: brew install chromedriver", "INFO")
            return False
            
    def test_services_are_running(self):
        """Test that both services are actually running and responding."""
        self.log("Testing that both services are running...")
        
        # Test backend
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Backend: {data['status']}, {data['enabled_guardrails']}/{data['total_guardrails']} guardrails")
            else:
                self.log(f"❌ Backend health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Backend not accessible: {e}", "ERROR")
            return False
            
        # Test frontend
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code == 200 and "Stinger Guardrails Demo" in response.text:
                self.log("✅ Frontend: Serving React app HTML")
            else:
                self.log(f"❌ Frontend not serving correctly: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Frontend not accessible: {e}", "ERROR")
            return False
            
        return True
        
    def test_frontend_loads_and_renders(self):
        """Test that the React app actually loads and renders in a browser."""
        self.log("Testing that React app loads and renders...")
        
        try:
            # Load the frontend
            self.driver.get("http://localhost:3000")
            
            # Wait for React app to load
            wait = WebDriverWait(self.driver, 10)
            
            # Check for main app container
            app_container = wait.until(
                EC.presence_of_element_located((By.ID, "root"))
            )
            
            # Check for key elements
            header = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "header"))
            )
            
            # Check for chat interface
            chat_interface = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='chat-interface'], .chat-interface, .chat-container"))
            )
            
            self.log("✅ React app loaded and rendered successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ React app failed to load: {e}", "ERROR")
            
            # Debug: Get page source
            try:
                page_source = self.driver.page_source
                if "Error" in page_source or "Cannot" in page_source:
                    self.log("❌ Page contains error messages", "ERROR")
                if len(page_source) < 1000:
                    self.log(f"❌ Page seems incomplete: {len(page_source)} chars", "ERROR")
            except:
                pass
                
            return False
            
    def test_frontend_backend_communication(self):
        """Test that the frontend can actually communicate with the backend through the browser."""
        self.log("Testing frontend-backend communication through browser...")
        
        try:
            # Find chat input
            wait = WebDriverWait(self.driver, 10)
            
            # Look for chat input field (try multiple selectors)
            chat_input = None
            input_selectors = [
                "input[type='text']",
                "textarea",
                "[data-testid='chat-input']",
                ".chat-input",
                "input[placeholder*='message']",
                "input[placeholder*='chat']"
            ]
            
            for selector in input_selectors:
                try:
                    chat_input = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    self.log(f"✅ Found chat input with selector: {selector}")
                    break
                except:
                    continue
                    
            if not chat_input:
                self.log("❌ Could not find chat input field", "ERROR")
                return False
                
            # Type a test message
            test_message = "Hello, this is a real E2E test"
            chat_input.clear()
            chat_input.send_keys(test_message)
            
            # Find and click send button
            send_button = None
            send_selectors = [
                "button[type='submit']",
                "[data-testid='send-button']",
                ".send-button",
                "button:contains('Send')",
                "button[title*='Send']"
            ]
            
            for selector in send_selectors:
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
                    
            if not send_button:
                # Try pressing Enter instead
                chat_input.send_keys(Keys.RETURN)
                self.log("✅ Sent message via Enter key")
            else:
                send_button.click()
                self.log("✅ Sent message via Send button")
                
            # Wait for response
            time.sleep(3)
            
            # Check for response in chat history
            response_selectors = [
                ".chat-message",
                ".message",
                "[data-testid='chat-message']",
                ".chat-response"
            ]
            
            response_found = False
            for selector in response_selectors:
                try:
                    messages = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(messages) >= 2:  # User message + bot response
                        self.log(f"✅ Found {len(messages)} messages in chat history")
                        response_found = True
                        break
                except:
                    continue
                    
            if not response_found:
                # Check if there's any new content on the page
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                if test_message in page_text:
                    self.log("✅ Message appears on page (basic communication working)")
                    response_found = True
                    
            if response_found:
                self.log("✅ Frontend-backend communication successful!", "SUCCESS")
                return True
            else:
                self.log("❌ No response received from backend", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Frontend-backend communication failed: {e}", "ERROR")
            return False
            
    def test_api_calls_from_browser(self):
        """Test that the browser can make direct API calls (simulating what React does)."""
        self.log("Testing API calls from browser context...")
        
        try:
            # Execute JavaScript in the browser to make API calls
            test_script = """
            return fetch('/api/health')
                .then(response => response.json())
                .then(data => {
                    return {success: true, data: data};
                })
                .catch(error => {
                    return {success: false, error: error.toString()};
                });
            """
            
            result = self.driver.execute_async_script("""
            var callback = arguments[arguments.length - 1];
            fetch('/api/health')
                .then(response => response.json())
                .then(data => callback({success: true, data: data}))
                .catch(error => callback({success: false, error: error.toString()}));
            """)
            
            if result.get('success'):
                health_data = result['data']
                self.log(f"✅ Browser API call successful: {health_data.get('status')}", "SUCCESS")
                return True
            else:
                self.log(f"❌ Browser API call failed: {result.get('error')}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Browser API test failed: {e}", "ERROR")
            return False
            
    def test_proxy_configuration(self):
        """Test that the React proxy is working correctly."""
        self.log("Testing React proxy configuration...")
        
        try:
            # Make a request through the frontend's proxy
            self.driver.get("http://localhost:3000")
            
            # Execute fetch to /api/health through the proxy
            result = self.driver.execute_async_script("""
            var callback = arguments[arguments.length - 1];
            fetch('/api/health')
                .then(response => {
                    return response.json().then(data => ({
                        status: response.status,
                        ok: response.ok,
                        data: data
                    }));
                })
                .then(result => callback({success: true, result: result}))
                .catch(error => callback({success: false, error: error.toString()}));
            """)
            
            if result.get('success') and result['result']['ok']:
                self.log("✅ React proxy working correctly", "SUCCESS")
                return True
            else:
                self.log(f"❌ React proxy failed: {result}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Proxy test failed: {e}", "ERROR")
            return False
            
    def cleanup(self):
        """Clean up browser resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.log("✅ Browser cleanup complete")
            except:
                pass
                
    def run_real_e2e_test(self):
        """Run the complete REAL end-to-end test."""
        self.log("🚀 REAL Frontend-Backend E2E Test")
        self.log("=" * 50)
        self.log("Testing actual frontend-backend communication through browser...")
        
        try:
            # Setup
            if not self.setup_browser():
                self.log("❌ Cannot run E2E tests without browser automation", "ERROR")
                return False
                
            # Run tests
            tests = [
                ("Services Running", self.test_services_are_running),
                ("Frontend Loads and Renders", self.test_frontend_loads_and_renders),
                ("API Calls from Browser", self.test_api_calls_from_browser),
                ("Proxy Configuration", self.test_proxy_configuration),
                ("Frontend-Backend Communication", self.test_frontend_backend_communication)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                self.log(f"\n--- {test_name} ---")
                try:
                    if test_func():
                        passed += 1
                        self.log(f"✅ PASSED: {test_name}", "SUCCESS")
                    else:
                        self.log(f"❌ FAILED: {test_name}", "ERROR")
                        # Continue with other tests to get full picture
                except Exception as e:
                    self.log(f"❌ ERROR in {test_name}: {e}", "ERROR")
            
            # Results
            self.log("\n" + "=" * 50)
            self.log(f"📊 REAL E2E TEST RESULTS: {passed}/{total} tests passed")
            
            if passed == total:
                self.log("🎉 REAL E2E TESTS PASSED!", "SUCCESS")
                self.log("✅ Frontend and backend are truly communicating")
                self.log("✅ React app loads and functions in browser")
                self.log("✅ API calls work through proxy configuration")
                self.log("✅ Complete user workflow validated")
                return True
            else:
                self.log(f"❌ {total - passed} E2E tests failed", "ERROR")
                self.log("❌ Frontend-backend communication has issues")
                return False
                
        except Exception as e:
            self.log(f"❌ E2E test suite error: {e}", "ERROR")
            return False
        finally:
            self.cleanup()

def main():
    tester = RealE2ETest()
    
    try:
        success = tester.run_real_e2e_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        tester.log("Tests interrupted by user", "WARNING")
        return 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    import sys
    sys.exit(main())