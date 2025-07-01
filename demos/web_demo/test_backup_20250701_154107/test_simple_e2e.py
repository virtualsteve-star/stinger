#!/usr/bin/env python3
"""
Simple E2E Test - Verify the demo actually works

This tests the working demo:
- Backend serving APIs on HTTP
- Frontend serving static files  
- API communication working
- Real user workflows functional
"""

import requests
import time

def log(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_services():
    """Test both services are running and responding."""
    
    # Test backend
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Backend: {data['status']}, {data['enabled_guardrails']}/{data['total_guardrails']} guardrails")
        else:
            log(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Backend not accessible: {e}")
        return False
    
    # Test frontend
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200 and "Stinger Guardrails Demo" in response.text:
            log("✅ Frontend: Serving React app correctly")
        else:
            log(f"❌ Frontend not serving correctly: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Frontend not accessible: {e}")
        return False
        
    return True

def test_chat_workflow():
    """Test complete chat workflow."""
    log("Testing chat workflow...")
    
    messages = [
        "Hello, I'm testing the demo",
        "How do guardrails work?", 
        "Can you help me with coding?"
    ]
    
    conversation_id = None
    
    for i, message in enumerate(messages, 1):
        try:
            payload = {"content": message}
            if conversation_id:
                payload["conversation_id"] = conversation_id
                
            response = requests.post(
                "http://localhost:8000/api/chat",
                json=payload,
                timeout=15
            )
            
            if response.status_code != 200:
                log(f"❌ Chat message {i} failed: {response.status_code}")
                return False
                
            data = response.json()
            if not conversation_id:
                conversation_id = data["conversation_id"]
                
            log(f"✅ Message {i}: Got {len(data['content'])} char response")
            
        except Exception as e:
            log(f"❌ Chat test failed: {e}")
            return False
            
    return True

def test_settings():
    """Test settings management."""
    log("Testing settings...")
    
    try:
        response = requests.get("http://localhost:8000/api/guardrails", timeout=5)
        if response.status_code == 200:
            settings = response.json()
            input_count = len(settings["input_guardrails"])
            output_count = len(settings["output_guardrails"])
            log(f"✅ Settings: {input_count} input, {output_count} output guardrails")
            return True
        else:
            log(f"❌ Settings failed: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Settings test failed: {e}")
        return False

def main():
    log("🚀 Simple E2E Test - Verifying Working Demo")
    log("=" * 50)
    
    tests = [
        ("Services Running", test_services),
        ("Chat Workflow", test_chat_workflow),
        ("Settings Management", test_settings)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        log(f"\nTesting: {test_name}")
        if test_func():
            passed += 1
        else:
            break
    
    log("\n" + "=" * 50)
    log(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        log("🎉 DEMO IS WORKING END-TO-END!")
        log("✅ Backend: http://localhost:8000/api/docs")
        log("✅ Frontend: http://localhost:3000")
        log("✅ All user workflows functional")
        return True
    else:
        log("❌ Demo has issues")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)