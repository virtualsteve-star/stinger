#!/usr/bin/env python3
"""
End-to-End Integration Tests for Stinger Web Demo

This script performs comprehensive integration testing that covers
the full user workflow from frontend to backend to guardrails.

Dependencies:
    pip install playwright pytest-asyncio
    playwright install
    
Usage:
    python test_integration_e2e.py
    
Exit codes:
    0: All tests passed
    1: Tests failed
"""

import sys
import os
import asyncio
import json
import time
import subprocess
import requests
import signal
from pathlib import Path
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Add src to path for Stinger imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class IntegrationTester:
    def __init__(self):
        self.demo_dir = Path(__file__).parent
        self.backend_dir = self.demo_dir / "backend"
        self.frontend_dir = self.demo_dir / "frontend"
        self.backend_process = None
        self.frontend_process = None
        self.browser = None
        self.page = None
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
        
    async def run_test(self, test_name, test_func):
        """Run a test and record results."""
        self.log(f"Running integration test: {test_name}")
        try:
            await test_func()
            self.log(f"PASSED: {test_name}", "SUCCESS")
            self.test_results.append({"test": test_name, "status": "PASSED"})
            return True
        except Exception as e:
            self.log(f"FAILED: {test_name} - {str(e)}", "ERROR")
            self.test_results.append({"test": test_name, "status": "FAILED", "error": str(e)})
            return False
    
    def start_services(self):
        """Start backend and frontend services."""
        self.log("Starting services for integration testing...")
        
        # Kill any existing processes
        for port in [3000, 8000]:
            try:
                subprocess.run(f"lsof -ti:{port} | xargs kill -9", 
                             shell=True, capture_output=True)
            except:
                pass
        
        time.sleep(3)
        
        # Start backend
        self.log("Starting backend server...")
        self.backend_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=self.backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for backend to start
        for _ in range(30):
            try:
                response = requests.get("https://localhost:8000/api/health", 
                                      verify=False, timeout=2)
                if response.status_code == 200:
                    self.log("Backend started", "SUCCESS")
                    break
            except:
                time.sleep(1)
        else:
            raise Exception("Backend failed to start")
        
        # Start frontend
        self.log("Starting frontend server...")
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
        for _ in range(60):
            try:
                response = requests.get("https://localhost:3000", verify=False, timeout=2)
                if response.status_code == 200:
                    self.log("Frontend started", "SUCCESS")
                    break
            except:
                time.sleep(1)
        else:
            raise Exception("Frontend failed to start")
    
    async def setup_browser(self):
        """Setup browser for testing."""
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright not available. Install with: pip install playwright && playwright install")
        
        self.log("Setting up browser...")
        self.playwright = await async_playwright().start()
        
        # Launch browser with options to handle self-signed certificates
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--ignore-certificate-errors', '--ignore-ssl-errors', '--allow-running-insecure-content']
        )
        
        # Create context that ignores HTTPS errors
        self.context = await self.browser.new_context(
            ignore_https_errors=True,
            viewport={'width': 1280, 'height': 720}
        )
        
        self.page = await self.context.new_page()
        
        # Set up console logging
        self.page.on("console", lambda msg: self.log(f"Browser console: {msg.text}"))
        self.page.on("pageerror", lambda error: self.log(f"Browser error: {error}", "ERROR"))
    
    async def test_page_loads(self):
        """Test that the main page loads correctly."""
        await self.page.goto("https://localhost:3000")
        
        # Wait for React app to load
        await self.page.wait_for_selector('[data-testid="app-container"], .App, #root > div', timeout=10000)
        
        # Check for main elements
        title = await self.page.text_content('h1, [data-testid="header-title"]')
        assert "Stinger" in title, f"Expected 'Stinger' in title, got: {title}"
        
        # Check for chat interface
        chat_input = self.page.locator('textarea, input[placeholder*="message"]').first
        assert await chat_input.is_visible(), "Chat input not visible"
        
        # Check for settings panel
        settings_panel = self.page.locator('[data-testid="settings-panel"], .settings, [class*="Settings"]').first
        assert await settings_panel.is_visible(), "Settings panel not visible"
    
    async def test_system_status_display(self):
        """Test that system status is displayed correctly."""
        await self.page.goto("https://localhost:3000")
        
        # Wait for status to load
        await self.page.wait_for_selector('[data-testid="status-bar"], [class*="Status"]', timeout=10000)
        
        # Check for pipeline status
        status_text = await self.page.text_content('[data-testid="status-bar"], [class*="Status"]')
        assert "Pipeline" in status_text or "guardrails" in status_text.lower(), f"Status not showing pipeline info: {status_text}"
    
    async def test_basic_chat_flow(self):
        """Test basic chat functionality."""
        await self.page.goto("https://localhost:3000")
        
        # Wait for page to be ready
        await self.page.wait_for_load_state('networkidle')
        
        # Find chat input
        chat_input = self.page.locator('textarea, input[placeholder*="message"]').first
        await chat_input.wait_for(state='visible', timeout=10000)
        
        # Type a simple message
        test_message = "Hello, this is a test message!"
        await chat_input.fill(test_message)
        
        # Find and click send button
        send_button = self.page.locator('button[type="submit"], button:has-text("Send"), [data-testid="send-button"]').first
        await send_button.click()
        
        # Wait for response
        await self.page.wait_for_timeout(3000)  # Wait for processing
        
        # Check that message appears in chat
        chat_messages = self.page.locator('[data-testid="chat-messages"], [class*="message"], [class*="Message"]')
        message_count = await chat_messages.count()
        assert message_count > 0, "No messages appeared after sending"
        
        # Check input is cleared
        input_value = await chat_input.input_value()
        assert input_value == "", "Input not cleared after sending"
    
    async def test_pii_detection_blocking(self):
        """Test that PII detection blocks sensitive content."""
        await self.page.goto("https://localhost:3000")
        await self.page.wait_for_load_state('networkidle')
        
        # Send message with PII
        chat_input = self.page.locator('textarea, input[placeholder*="message"]').first
        await chat_input.wait_for(state='visible')
        
        pii_message = "My social security number is 123-45-6789"
        await chat_input.fill(pii_message)
        
        send_button = self.page.locator('button[type="submit"], button:has-text("Send")').first
        await send_button.click()
        
        # Wait for processing
        await self.page.wait_for_timeout(5000)
        
        # Look for blocking indicators
        page_content = await self.page.content()
        assert "blocked" in page_content.lower() or "warning" in page_content.lower() or "pii" in page_content.lower(), \
            "No blocking/warning indicators found for PII content"
    
    async def test_guardrail_settings_toggle(self):
        """Test guardrail settings can be toggled."""
        await self.page.goto("https://localhost:3000")
        await self.page.wait_for_load_state('networkidle')
        
        # Look for guardrail toggles
        toggles = self.page.locator('input[type="checkbox"], [role="switch"], [data-testid*="toggle"]')
        toggle_count = await toggles.count()
        
        if toggle_count > 0:
            # Click first toggle
            first_toggle = toggles.first
            initial_state = await first_toggle.is_checked()
            await first_toggle.click()
            
            # Wait for state change
            await self.page.wait_for_timeout(1000)
            
            # Check state changed
            new_state = await first_toggle.is_checked()
            assert new_state != initial_state, "Toggle state did not change"
        else:
            # Just verify settings panel exists
            settings_elements = self.page.locator('[data-testid="settings"], [class*="Settings"]')
            assert await settings_elements.count() > 0, "No settings panel found"
    
    async def test_audit_log_display(self):
        """Test that audit log displays activity."""
        await self.page.goto("https://localhost:3000")
        await self.page.wait_for_load_state('networkidle')
        
        # Send a message to generate audit activity
        chat_input = self.page.locator('textarea, input[placeholder*="message"]').first
        if await chat_input.is_visible():
            await chat_input.fill("Test message for audit log")
            send_button = self.page.locator('button[type="submit"], button:has-text("Send")').first
            await send_button.click()
            await self.page.wait_for_timeout(3000)
        
        # Look for audit log section
        audit_elements = self.page.locator('[data-testid="audit-log"], [class*="audit"], [class*="Audit"]')
        audit_count = await audit_elements.count()
        assert audit_count > 0, "No audit log section found"
        
        # Check for audit entries (might be in collapsed state)
        page_content = await self.page.content()
        assert "audit" in page_content.lower() or "log" in page_content.lower(), "No audit-related content found"
    
    async def test_error_handling(self):
        """Test that errors are handled gracefully."""
        await self.page.goto("https://localhost:3000")
        await self.page.wait_for_load_state('networkidle')
        
        # Test with empty message
        chat_input = self.page.locator('textarea, input[placeholder*="message"]').first
        await chat_input.fill("")
        
        send_button = self.page.locator('button[type="submit"], button:has-text("Send")').first
        await send_button.click()
        
        # Should not send empty message, or handle gracefully
        await self.page.wait_for_timeout(1000)
        
        # Test with very long message
        long_message = "A" * 10000
        await chat_input.fill(long_message)
        await send_button.click()
        await self.page.wait_for_timeout(5000)
        
        # Should handle without crashing
        page_errors = []
        self.page.on("pageerror", lambda error: page_errors.append(error))
        await self.page.wait_for_timeout(1000)
        
        # No critical errors should occur
        assert len(page_errors) == 0, f"Page errors occurred: {page_errors}"
    
    async def test_responsive_design(self):
        """Test responsive design works on different screen sizes."""
        await self.page.goto("https://localhost:3000")
        
        # Test desktop size
        await self.page.set_viewport_size({"width": 1280, "height": 720})
        await self.page.wait_for_load_state('networkidle')
        
        desktop_content = await self.page.content()
        assert "Stinger" in desktop_content, "Desktop layout not loading"
        
        # Test tablet size
        await self.page.set_viewport_size({"width": 768, "height": 1024})
        await self.page.wait_for_timeout(1000)
        
        tablet_content = await self.page.content()
        assert "Stinger" in tablet_content, "Tablet layout not loading"
        
        # Test mobile size
        await self.page.set_viewport_size({"width": 375, "height": 667})
        await self.page.wait_for_timeout(1000)
        
        mobile_content = await self.page.content()
        assert "Stinger" in mobile_content, "Mobile layout not loading"
    
    async def test_full_user_workflow(self):
        """Test complete user workflow from start to finish."""
        await self.page.goto("https://localhost:3000")
        await self.page.wait_for_load_state('networkidle')
        
        # 1. Check initial page load
        title = await self.page.title()
        assert "Stinger" in title or title != "", f"Page title issue: {title}"
        
        # 2. Send normal message
        chat_input = self.page.locator('textarea, input[placeholder*="message"]').first
        await chat_input.fill("Hello, how are you today?")
        
        send_button = self.page.locator('button[type="submit"], button:has-text("Send")').first
        await send_button.click()
        await self.page.wait_for_timeout(3000)
        
        # 3. Send message with potential issues
        await chat_input.fill("I'm feeling quite angry about this service")
        await send_button.click()
        await self.page.wait_for_timeout(3000)
        
        # 4. Check that conversation is maintained
        chat_area = self.page.locator('[data-testid="chat-messages"], [class*="message"]')
        message_count = await chat_area.count()
        assert message_count >= 2, "Not maintaining conversation properly"
        
        # 5. Verify system is still responsive
        await chat_input.fill("Final test message")
        await send_button.click()
        await self.page.wait_for_timeout(3000)
        
        # Should still be functional
        input_value = await chat_input.input_value()
        assert input_value == "", "System not responding after workflow"
    
    def cleanup(self):
        """Clean up processes and browser."""
        self.log("Cleaning up integration test environment...")
        
        # Close browser
        if self.browser:
            try:
                asyncio.create_task(self.browser.close())
            except:
                pass
        
        if hasattr(self, 'playwright'):
            try:
                asyncio.create_task(self.playwright.stop())
            except:
                pass
        
        # Kill processes
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
        
        # Kill any remaining processes on ports
        for port in [3000, 8000]:
            try:
                subprocess.run(f"lsof -ti:{port} | xargs kill -9", 
                             shell=True, capture_output=True)
            except:
                pass
    
    async def run_all_tests(self):
        """Run the complete integration test suite."""
        self.log("🚀 Starting Stinger Web Demo Integration Test Suite")
        self.log("=" * 70)
        
        if not PLAYWRIGHT_AVAILABLE:
            self.log("❌ Playwright not available. Install with: pip install playwright && playwright install", "ERROR")
            return False
        
        try:
            # Start services
            self.start_services()
            
            # Setup browser
            await self.setup_browser()
            
            # Run all integration tests
            tests = [
                ("Page Loading", self.test_page_loads),
                ("System Status Display", self.test_system_status_display),
                ("Basic Chat Flow", self.test_basic_chat_flow),
                ("PII Detection Blocking", self.test_pii_detection_blocking),
                ("Guardrail Settings Toggle", self.test_guardrail_settings_toggle),
                ("Audit Log Display", self.test_audit_log_display),
                ("Error Handling", self.test_error_handling),
                ("Responsive Design", self.test_responsive_design),
                ("Full User Workflow", self.test_full_user_workflow)
            ]
            
            tests_passed = 0
            total_tests = len(tests)
            
            for test_name, test_func in tests:
                if await self.run_test(test_name, test_func):
                    tests_passed += 1
            
            # Results
            self.log("=" * 70)
            self.log(f"INTEGRATION TEST RESULTS: {tests_passed}/{total_tests} tests passed")
            
            if tests_passed == total_tests:
                self.log("🎉 ALL INTEGRATION TESTS PASSED!", "SUCCESS")
                return True
            else:
                self.log(f"❌ {total_tests - tests_passed} integration tests failed", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Integration test suite failed: {e}", "ERROR")
            return False
        finally:
            self.cleanup()

async def main():
    """Main test runner."""
    tester = IntegrationTester()
    
    # Handle cleanup on exit
    def signal_handler(sig, frame):
        tester.cleanup()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    success = await tester.run_all_tests()
    
    if not success:
        print("\n" + "=" * 70)
        print("❌ INTEGRATION TESTING FAILED")
        print("Please fix the issues above before deploying the demo.")
        sys.exit(1)
    else:
        print("\n" + "=" * 70)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("Demo is ready for production use.")

if __name__ == "__main__":
    asyncio.run(main())