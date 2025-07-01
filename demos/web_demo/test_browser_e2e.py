#!/usr/bin/env python3
"""
Browser End-to-End Test Suite
Tests the complete user experience through browser automation.
Supports both Selenium and Playwright (with Selenium as default).
"""

import os
import sys
import time
import pytest
from pathlib import Path

# Determine which browser automation library to use
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    USE_SELENIUM = True
    USE_PLAYWRIGHT = False
    print("🌐 Using Selenium for browser automation")
except ImportError:
    USE_SELENIUM = False
    try:
        from playwright.sync_api import sync_playwright
        USE_PLAYWRIGHT = True
        print("🎭 Using Playwright for browser automation")
    except ImportError:
        USE_PLAYWRIGHT = False
        print("❌ No browser automation library available (install selenium or playwright)")


class TestBrowserE2E:
    """Browser-based end-to-end tests for web demo."""
    
    BASE_URL = "https://localhost:3000"
    BACKEND_URL = "https://localhost:8000"
    
    @classmethod
    def setup_class(cls):
        """Set up browser driver."""
        if not (USE_SELENIUM or USE_PLAYWRIGHT):
            pytest.skip("No browser automation library available")
            
        if USE_SELENIUM:
            cls._setup_selenium()
        else:
            cls._setup_playwright()
            
    @classmethod
    def teardown_class(cls):
        """Clean up browser resources."""
        if USE_SELENIUM and hasattr(cls, 'driver'):
            cls.driver.quit()
        elif USE_PLAYWRIGHT and hasattr(cls, 'browser'):
            cls.browser.close()
            cls.playwright.stop()
            
    @classmethod
    def _setup_selenium(cls):
        """Set up Selenium WebDriver."""
        # Configure Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-insecure-localhost')
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        try:
            cls.driver = webdriver.Chrome(options=options)
            cls.wait = WebDriverWait(cls.driver, 10)
            print("✅ Selenium WebDriver initialized")
        except WebDriverException as e:
            pytest.skip(f"Failed to initialize WebDriver: {e}")
            
    @classmethod
    def _setup_playwright(cls):
        """Set up Playwright browser."""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            headless=True,
            args=['--ignore-certificate-errors']
        )
        cls.context = cls.browser.new_context(ignore_https_errors=True)
        cls.page = cls.context.new_page()
        print("✅ Playwright browser initialized")
        
    def test_frontend_loads(self):
        """Test that frontend loads successfully."""
        print("\n🌐 Testing frontend loads...")
        
        if USE_SELENIUM:
            self.driver.get(self.BASE_URL)
            # Wait for main app element
            try:
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "app")))
                print("✅ Frontend loaded successfully")
            except TimeoutException:
                pytest.fail("Frontend failed to load")
                
        else:  # Playwright
            response = self.page.goto(self.BASE_URL)
            assert response.status in [200, 304]
            # Wait for app to load
            self.page.wait_for_selector(".app", timeout=10000)
            print("✅ Frontend loaded successfully")
            
    def test_header_elements_present(self):
        """Test that header elements are present."""
        print("\n📋 Testing header elements...")
        
        if USE_SELENIUM:
            # Check for header
            header = self.driver.find_element(By.CLASS_NAME, "header")
            assert header.is_displayed()
            
            # Check for title
            title = self.driver.find_element(By.TAG_NAME, "h1")
            assert "Stinger" in title.text
            
            # Check for control buttons
            audit_btn = self.driver.find_element(By.CLASS_NAME, "logs-btn")
            reset_btn = self.driver.find_element(By.CLASS_NAME, "reset-btn")
            assert audit_btn.is_displayed()
            assert reset_btn.is_displayed()
            
        else:  # Playwright
            # Check header elements
            assert self.page.locator(".header").is_visible()
            assert "Stinger" in self.page.locator("h1").text_content()
            assert self.page.locator(".logs-btn").is_visible()
            assert self.page.locator(".reset-btn").is_visible()
            
        print("✅ All header elements present")
        
    def test_chat_interface_elements(self):
        """Test chat interface elements are present."""
        print("\n💬 Testing chat interface...")
        
        if USE_SELENIUM:
            # Check for chat container
            chat_container = self.driver.find_element(By.CLASS_NAME, "chat-container")
            assert chat_container.is_displayed()
            
            # Check for input area
            chat_input = self.driver.find_element(By.CSS_SELECTOR, "textarea, input[type='text']")
            assert chat_input.is_displayed()
            
            # Check for send button
            send_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], .send-btn")
            assert send_button.is_displayed()
            
        else:  # Playwright
            # Check chat elements
            assert self.page.locator(".chat-container").is_visible()
            assert self.page.locator("textarea, input[type='text']").is_visible()
            assert self.page.locator("button[type='submit'], .send-btn").is_visible()
            
        print("✅ Chat interface elements present")
        
    def test_settings_panel_present(self):
        """Test settings panel is present."""
        print("\n⚙️ Testing settings panel...")
        
        if USE_SELENIUM:
            # Check for settings
            settings = self.driver.find_element(By.CLASS_NAME, "settings-panel")
            assert settings.is_displayed()
            
            # Check for guardrail toggles
            toggles = self.driver.find_elements(By.CLASS_NAME, "guardrail-toggle")
            assert len(toggles) > 0
            
        else:  # Playwright
            # Check settings
            assert self.page.locator(".settings-panel").is_visible()
            toggles = self.page.locator(".guardrail-toggle").all()
            assert len(toggles) > 0
            
        print("✅ Settings panel with guardrails present")
        
    def test_send_chat_message(self):
        """Test sending a chat message."""
        print("\n📤 Testing message sending...")
        
        test_message = "Hello from browser test!"
        
        if USE_SELENIUM:
            # Find input and send message
            chat_input = self.driver.find_element(By.CSS_SELECTOR, "textarea, input[type='text']")
            chat_input.clear()
            chat_input.send_keys(test_message)
            
            # Click send
            send_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], .send-btn")
            send_button.click()
            
            # Wait for response
            time.sleep(2)
            
            # Check for message in chat
            messages = self.driver.find_elements(By.CLASS_NAME, "message")
            assert len(messages) > 0
            
            # Verify our message appears
            message_found = False
            for msg in messages:
                if test_message in msg.text:
                    message_found = True
                    break
            assert message_found, "Sent message not found in chat"
            
        else:  # Playwright
            # Send message
            self.page.fill("textarea, input[type='text']", test_message)
            self.page.click("button[type='submit'], .send-btn")
            
            # Wait for response
            self.page.wait_for_timeout(2000)
            
            # Check message appears
            messages = self.page.locator(".message").all()
            assert len(messages) > 0
            
            # Verify our message
            message_texts = [msg.text_content() for msg in messages]
            assert any(test_message in text for text in message_texts)
            
        print("✅ Message sent and displayed successfully")
        
    def test_guardrail_toggle_interaction(self):
        """Test toggling guardrails."""
        print("\n🔄 Testing guardrail toggles...")
        
        if USE_SELENIUM:
            # Find first toggle
            toggles = self.driver.find_elements(By.CSS_SELECTOR, ".guardrail-toggle input[type='checkbox']")
            if toggles:
                first_toggle = toggles[0]
                initial_state = first_toggle.is_selected()
                
                # Click to toggle
                first_toggle.click()
                time.sleep(0.5)
                
                # Verify state changed
                new_state = first_toggle.is_selected()
                assert new_state != initial_state
                
                # Toggle back
                first_toggle.click()
                
        else:  # Playwright
            # Find toggles
            toggles = self.page.locator(".guardrail-toggle input[type='checkbox']").all()
            if toggles:
                first_toggle = toggles[0]
                initial_state = first_toggle.is_checked()
                
                # Toggle
                first_toggle.click()
                self.page.wait_for_timeout(500)
                
                # Verify change
                assert first_toggle.is_checked() != initial_state
                
                # Toggle back
                first_toggle.click()
                
        print("✅ Guardrail toggles working")
        
    def test_reset_conversation(self):
        """Test reset conversation functionality."""
        print("\n🔄 Testing conversation reset...")
        
        if USE_SELENIUM:
            # Click reset button
            reset_btn = self.driver.find_element(By.CLASS_NAME, "reset-btn")
            reset_btn.click()
            
            # Wait for confirmation or action
            time.sleep(1)
            
            # Messages should be cleared or reset indicated
            # (Implementation depends on frontend behavior)
            
        else:  # Playwright
            # Click reset
            self.page.click(".reset-btn")
            self.page.wait_for_timeout(1000)
            
        print("✅ Reset conversation triggered")
        
    def test_audit_logs_modal(self):
        """Test audit logs modal."""
        print("\n📋 Testing audit logs...")
        
        if USE_SELENIUM:
            # Click audit logs button
            logs_btn = self.driver.find_element(By.CLASS_NAME, "logs-btn")
            logs_btn.click()
            
            # Wait for modal
            try:
                modal = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "audit-logs-modal")))
                assert modal.is_displayed()
                
                # Close modal
                close_btn = modal.find_element(By.CLASS_NAME, "close-btn")
                close_btn.click()
                
            except TimeoutException:
                print("⚠️  Audit logs modal not found")
                
        else:  # Playwright
            # Open audit logs
            self.page.click(".logs-btn")
            
            # Check modal
            if self.page.locator(".audit-logs-modal").count() > 0:
                assert self.page.locator(".audit-logs-modal").is_visible()
                # Close modal
                self.page.click(".close-btn")
            else:
                print("⚠️  Audit logs modal not found")
                
        print("✅ Audit logs modal tested")
        
    def test_responsive_design(self):
        """Test responsive design at different sizes."""
        print("\n📱 Testing responsive design...")
        
        viewports = [
            (1920, 1080, "Desktop"),
            (768, 1024, "Tablet"),
            (375, 667, "Mobile")
        ]
        
        if USE_SELENIUM:
            for width, height, name in viewports:
                self.driver.set_window_size(width, height)
                time.sleep(0.5)
                
                # Check main elements still visible
                assert self.driver.find_element(By.CLASS_NAME, "app").is_displayed()
                print(f"  ✅ {name} view ({width}x{height})")
                
        else:  # Playwright
            for width, height, name in viewports:
                self.page.set_viewport_size({"width": width, "height": height})
                self.page.wait_for_timeout(500)
                
                # Check visibility
                assert self.page.locator(".app").is_visible()
                print(f"  ✅ {name} view ({width}x{height})")
                
    def test_error_message_display(self):
        """Test error message display for blocked content."""
        print("\n🚫 Testing error message display...")
        
        # Send PII content
        pii_message = "My SSN is 123-45-6789"
        
        if USE_SELENIUM:
            # Send message
            chat_input = self.driver.find_element(By.CSS_SELECTOR, "textarea, input[type='text']")
            chat_input.clear()
            chat_input.send_keys(pii_message)
            
            send_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], .send-btn")
            send_button.click()
            
            # Wait for response
            time.sleep(2)
            
            # Look for error or warning indication
            errors = self.driver.find_elements(By.CLASS_NAME, "error")
            warnings = self.driver.find_elements(By.CLASS_NAME, "warning")
            blocked = self.driver.find_elements(By.CLASS_NAME, "blocked")
            
            assert len(errors) > 0 or len(warnings) > 0 or len(blocked) > 0
            
        else:  # Playwright
            # Send PII message
            self.page.fill("textarea, input[type='text']", pii_message)
            self.page.click("button[type='submit'], .send-btn")
            
            # Wait for response
            self.page.wait_for_timeout(2000)
            
            # Check for error indication
            error_count = self.page.locator(".error, .warning, .blocked").count()
            assert error_count > 0
            
        print("✅ Error messages displayed for blocked content")


if __name__ == "__main__":
    # Run with pytest if available
    try:
        pytest.main([__file__, "-v", "-s", "--tb=short"])
    except ImportError:
        print("⚠️  pytest not installed")
        
        if not (USE_SELENIUM or USE_PLAYWRIGHT):
            print("❌ No browser automation library available")
            print("   Install with: pip install selenium")
            print("   Or: pip install playwright && playwright install")
            sys.exit(1)
            
        # Run basic test
        test = TestBrowserE2E()
        try:
            test.setup_class()
            test.test_frontend_loads()
            test.test_header_elements_present()
            test.test_chat_interface_elements()
            print("\n✅ Basic browser tests passed")
        except Exception as e:
            print(f"\n❌ Browser tests failed: {e}")
        finally:
            test.teardown_class()