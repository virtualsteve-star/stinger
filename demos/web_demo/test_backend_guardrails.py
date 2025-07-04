#!/usr/bin/env python3
"""
Test script to verify backend guardrail configuration
"""

import requests
import json
import sys
from pathlib import Path

# Disable SSL warnings for self-signed cert
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_backend():
    base_url = "https://localhost:8000"
    
    print("🧪 Testing Backend Guardrails Configuration")
    print("=" * 50)
    
    # Test 1: Check health
    try:
        resp = requests.get(f"{base_url}/health", verify=False)
        if resp.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("   Make sure backend is running: cd backend && python main.py")
        return False
    
    # Test 2: Get guardrail details
    try:
        resp = requests.get(f"{base_url}/api/guardrails/details", verify=False)
        if resp.status_code == 200:
            data = resp.json()
            input_count = len(data.get("input_guardrails", []))
            output_count = len(data.get("output_guardrails", []))
            total_count = input_count + output_count
            
            print(f"✅ Guardrails loaded: {total_count} total ({input_count} input, {output_count} output)")
            
            # List all guardrails
            print("\n📋 Input Guardrails:")
            for g in data.get("input_guardrails", []):
                status = "✅" if g.get("enabled") else "⭕"
                print(f"   {status} {g.get('display_name', g['name'])} - {g.get('description', 'No description')}")
            
            print("\n📋 Output Guardrails:")
            for g in data.get("output_guardrails", []):
                status = "✅" if g.get("enabled") else "⭕"
                print(f"   {status} {g.get('display_name', g['name'])} - {g.get('description', 'No description')}")
            
            if total_count >= 14:
                print(f"\n✅ All 14+ guardrails available!")
            else:
                print(f"\n⚠️  Only {total_count} guardrails loaded (expected 14+)")
        else:
            print(f"❌ Failed to get guardrail details: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting guardrail details: {e}")
        return False
    
    # Test 3: Check system status
    try:
        resp = requests.get(f"{base_url}/api/status", verify=False)
        if resp.status_code == 200:
            data = resp.json()
            print(f"\n📊 System Status:")
            print(f"   Pipeline: {'✅ Loaded' if data.get('pipeline_loaded') else '❌ Not loaded'}")
            print(f"   Audit: {'✅ Enabled' if data.get('audit_enabled') else '⭕ Disabled'}")
            print(f"   Enabled guardrails: {data.get('enabled_guardrails', 0)}/{data.get('total_guardrails', 0)}")
        else:
            print(f"⚠️  Could not get system status: {resp.status_code}")
    except Exception as e:
        print(f"⚠️  Error getting system status: {e}")
    
    print("\n✅ Backend test complete!")
    return True

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)