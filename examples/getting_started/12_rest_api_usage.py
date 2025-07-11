#!/usr/bin/env python3
"""
Example 12: Using Stinger via REST API

This example shows how to use Stinger through its REST API service
instead of directly importing the Python library.

Use the REST API when:
- Building non-Python applications
- Creating browser extensions
- Need centralized guardrail management
- Want language-agnostic integration

Prerequisites:
1. Install API dependencies: pip install stinger-guardrails-alpha[api]
2. Start the API server: stinger-api
3. Run this example: python 12_rest_api_usage.py
"""

import requests
import json
from typing import Dict, Any


def check_api_health(base_url: str = "http://localhost:8888") -> Dict[str, Any]:
    """Check if the API server is running and healthy."""
    try:
        response = requests.get(f"{base_url}/health")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: Cannot connect to API at {base_url}")
        print(f"   Make sure the server is running: stinger-api")
        raise SystemExit(1)


def main():
    """Demonstrate using Stinger through the REST API."""
    
    print("=" * 70)
    print("Stinger REST API Example")
    print("=" * 70)
    print()
    
    # API configuration
    BASE_URL = "http://localhost:8888"
    
    # 1. Check API health
    print("1. Checking API health...")
    health = check_api_health(BASE_URL)
    print(f"   ✅ API Status: {health['status']}")
    print(f"   Guardrails loaded: {health['guardrail_count']}")
    print(f"   API key configured: {health['api_key_configured']}")
    print()
    
    # 2. Get active guardrail rules
    print("2. Getting active guardrail rules...")
    rules_response = requests.get(f"{BASE_URL}/v1/rules", params={"preset": "customer_service"})
    rules = rules_response.json()
    print(f"   Preset: {rules['preset']}")
    print(f"   Version: {rules['version']}")
    print(f"   Input guardrails: {list(rules['guardrails']['input_guardrails'].keys())}")
    print(f"   Output guardrails: {list(rules['guardrails']['output_guardrails'].keys())}")
    print()
    
    # 3. Check various types of content
    print("3. Checking different types of content...")
    print()
    
    test_cases = [
        {
            "name": "Safe user input",
            "request": {
                "text": "Hello, can you help me with my order?",
                "kind": "prompt",
                "preset": "customer_service"
            }
        },
        {
            "name": "User input with PII",
            "request": {
                "text": "My email is john@example.com and SSN is 123-45-6789",
                "kind": "prompt",
                "preset": "customer_service"
            }
        },
        {
            "name": "Toxic user input",
            "request": {
                "text": "You stupid bot, you're worthless!",
                "kind": "prompt",
                "preset": "customer_service"
            }
        },
        {
            "name": "Safe LLM response",
            "request": {
                "text": "I'd be happy to help you with your order. Can you provide your order number?",
                "kind": "response",  # Note: checking LLM output
                "preset": "customer_service"
            }
        },
        {
            "name": "LLM response with PII leak",
            "request": {
                "text": "I see your SSN is 123-45-6789. Let me look that up for you.",
                "kind": "response",
                "preset": "customer_service"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"   Test: {test_case['name']}")
        print(f"   Text: '{test_case['request']['text']}'")
        
        # Make API request
        response = requests.post(
            f"{BASE_URL}/v1/check",
            headers={"Content-Type": "application/json"},
            json=test_case['request']
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Display result
            action_symbol = {
                "allow": "✅",
                "warn": "⚠️",
                "block": "❌"
            }.get(result['action'], "?")
            
            print(f"   Result: {action_symbol} {result['action'].upper()}")
            
            if result.get('reasons'):
                print(f"   Reasons: {', '.join(result['reasons'])}")
            
            if result.get('warnings'):
                print(f"   Warnings: {', '.join(result['warnings'])}")
            
            # Show processing time
            if 'metadata' in result and 'processing_time_ms' in result['metadata']:
                print(f"   Processing time: {result['metadata']['processing_time_ms']}ms")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
        
        print()
    
    # 4. Using conversation context
    print("4. Using conversation context...")
    contextual_request = {
        "text": "What was my previous question about?",
        "kind": "prompt",
        "preset": "customer_service",
        "context": {
            "sessionId": "session-123",
            "userId": "user-456"
        }
    }
    
    response = requests.post(f"{BASE_URL}/v1/check", json=contextual_request)
    result = response.json()
    print(f"   With context: {result['action'].upper()}")
    print(f"   Session ID: {contextual_request['context']['sessionId']}")
    print()
    
    # 5. Comparing different presets
    print("5. Comparing different presets...")
    test_text = "I need help with my medical prescription"
    
    for preset in ["customer_service", "medical", "financial"]:
        response = requests.post(
            f"{BASE_URL}/v1/check",
            json={
                "text": test_text,
                "kind": "prompt",
                "preset": preset
            }
        )
        result = response.json()
        print(f"   Preset '{preset}': {result['action'].upper()}")
    
    print()
    print("✅ REST API example complete!")
    print()
    print("💡 Tips:")
    print("   - The API server must be running: stinger-api")
    print("   - Default port is 8888 (customize with --port)")
    print("   - API supports CORS for browser extensions")
    print("   - See /docs endpoint for interactive API documentation")
    print()
    print("📚 Next steps:")
    print("   - Try different presets and content types")
    print("   - Integrate the API into your application")
    print("   - Create a browser extension using the API")


if __name__ == "__main__":
    main()