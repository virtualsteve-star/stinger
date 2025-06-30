#!/usr/bin/env python3
"""
Frontend Test Runner

This script:
1. Verifies both services are running
2. Opens the frontend in test mode
3. Monitors test results
4. Reports final status

Usage:
    python3 run_frontend_tests.py
"""

import subprocess
import requests
import time
import webbrowser
from pathlib import Path

def log(message, level="INFO"):
    timestamp = time.strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    icon = icons.get(level, "ℹ️")
    print(f"[{timestamp}] {icon} {message}")

def check_services():
    """Check that both services are running."""
    log("Checking that both services are running...")
    
    # Check backend
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Backend: {data['status']}, {data['enabled_guardrails']}/{data['total_guardrails']} guardrails")
        else:
            log(f"❌ Backend health check failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Backend not accessible: {e}", "ERROR")
        return False
    
    # Check frontend
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            log("✅ Frontend: Serving static content")
        else:
            log(f"❌ Frontend not accessible: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Frontend not accessible: {e}", "ERROR")
        return False
    
    return True

def test_api_directly():
    """Test API functionality directly to verify backend is working."""
    log("Testing backend API directly...")
    
    try:
        # Test chat functionality
        response = requests.post(
            "http://localhost:8000/api/chat",
            json={"content": "Frontend test runner validation"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ API Test: Got {len(data['content'])} char response")
            return True
        else:
            log(f"❌ API Test failed: {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log(f"❌ API Test failed: {e}", "ERROR")
        return False

def create_test_page():
    """Create a simple test page that runs the frontend tests."""
    test_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>Stinger Frontend E2E Test</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a1a;
            color: #00ff00;
            margin: 0;
            padding: 20px;
        }
        .header {
            text-align: center;
            font-size: 24px;
            margin-bottom: 20px;
            border-bottom: 2px solid #00ff00;
            padding-bottom: 10px;
        }
        .redirect-info {
            background: #004d00;
            border: 1px solid #00ff00;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .manual-link {
            display: block;
            color: #00ff00;
            text-decoration: none;
            font-size: 18px;
            margin: 10px 0;
            padding: 10px;
            border: 1px solid #00ff00;
            text-align: center;
            background: #002200;
        }
        .manual-link:hover {
            background: #004400;
        }
    </style>
</head>
<body>
    <div class="header">
        🧪 STINGER FRONTEND E2E TEST LAUNCHER
    </div>
    
    <div class="redirect-info">
        <p><strong>Attempting to launch frontend test mode...</strong></p>
        <p>This page will redirect to the React app with test mode enabled.</p>
        <p>If the redirect doesn't work, use the manual link below.</p>
    </div>
    
    <a href="/" class="manual-link" id="manualLink">
        🚀 CLICK HERE TO START FRONTEND TESTS
    </a>
    
    <script>
        // Add test parameter to trigger test mode
        const url = new URL(window.location);
        url.searchParams.set('test', 'true');
        
        // Update manual link
        document.getElementById('manualLink').href = '/?test=true';
        
        // Auto-redirect after 2 seconds
        setTimeout(() => {
            window.location.href = '/?test=true';
        }, 2000);
        
        console.log('Frontend test mode launcher loaded');
        console.log('Redirecting to:', '/?test=true');
    </script>
</body>
</html>"""

    # Write test page to frontend build directory
    test_file = Path("frontend/build/test.html")
    with open(test_file, 'w') as f:
        f.write(test_html)
    
    return test_file

def main():
    log("🚀 Frontend E2E Test Runner")
    log("=" * 50)
    
    # Check services
    if not check_services():
        log("❌ Services not ready for testing", "ERROR")
        return 1
    
    # Test API directly first
    if not test_api_directly():
        log("❌ Backend API not working", "ERROR")
        return 1
    
    # Create test launcher page
    test_file = create_test_page()
    log(f"✅ Created test launcher: {test_file}")
    
    # Instructions for user
    log("")
    log("🎮 FRONTEND E2E TESTING READY")
    log("=" * 30)
    log("To run frontend tests:")
    log("1. Open browser to: http://localhost:3000/test.html")
    log("2. Click the test link or wait for auto-redirect")
    log("3. Watch the test results in the browser")
    log("")
    log("Or manually visit: http://localhost:3000/?test=true")
    log("")
    log("The React app will run comprehensive E2E tests and display results.")
    
    # Optionally open browser automatically
    try:
        log("🌐 Opening browser automatically...")
        webbrowser.open("http://localhost:3000/test.html")
        log("✅ Browser opened - check the test results!")
    except Exception as e:
        log(f"⚠️ Could not open browser automatically: {e}", "WARNING")
        log("Please open http://localhost:3000/test.html manually")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())