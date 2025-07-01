#!/usr/bin/env python3
"""Test the startup detection logic."""

import requests
import time

def test_detection():
    print("🧪 Testing startup detection logic...")
    
    for attempt in range(10):
        try:
            print(f"   Attempt {attempt + 1}: Testing http://127.0.0.1:8000/api/health")
            response = requests.get("http://127.0.0.1:8000/api/health", timeout=2)
            if response.status_code == 200:
                data = response.json()
                enabled = data.get('enabled_guardrails', 0)
                total = data.get('total_guardrails', 0)
                print(f"   ✅ Backend ready - {enabled}/{total} guardrails active")
                print(f"   📊 Full response: {data}")
                return True
        except Exception as e:
            print(f"   ❌ Attempt {attempt + 1} failed: {e}")
        time.sleep(1)
    
    print("   ❌ Detection failed after 10 attempts")
    return False

if __name__ == "__main__":
    success = test_detection()
    print(f"\n🎯 Result: {'SUCCESS' if success else 'FAILED'}")