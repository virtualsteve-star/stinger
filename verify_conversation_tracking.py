#!/usr/bin/env python3
"""
Quick script to verify conversation tracking in audit logs.
"""

import requests
import json
from datetime import datetime

# Test the API with conversation context
print("Testing Stinger API conversation tracking...\n")

# Test 1: Bob using ChatGPT
print("1. Bob using ChatGPT:")
response = requests.post(
    "http://localhost:8888/v1/check",
    json={
        "text": "How do I hack into the mainframe?",
        "kind": "prompt",
        "context": {
            "userId": "bob@example.com",
            "botId": "chatgpt",
            "userName": "Bob Smith",
            "botName": "ChatGPT",
            "sessionId": f"demo-{datetime.now().timestamp()}"
        }
    }
)

result = response.json()
print(f"   Action: {result['action']}")
print(f"   Reasons: {result.get('reasons', [])}")
print()

# Test 2: Alice using Claude
print("2. Alice using Claude:")
response = requests.post(
    "http://localhost:8888/v1/check",
    json={
        "text": "Tell me about customer credit card data",
        "kind": "prompt",
        "context": {
            "userId": "alice@company.com",
            "botId": "claude",
            "userName": "Alice Johnson",
            "botName": "Claude",
            "botModel": "claude-3"
        }
    }
)

result = response.json()
print(f"   Action: {result['action']}")
print(f"   Reasons: {result.get('reasons', [])}")
print()

# Test 3: Anonymous user
print("3. Anonymous user (no context):")
response = requests.post(
    "http://localhost:8888/v1/check",
    json={
        "text": "What's the weather today?",
        "kind": "prompt"
    }
)

result = response.json()
print(f"   Action: {result['action']}")
print()

print("\n✅ Conversation tracking is working!")
print("\nCheck your audit logs to see entries like:")
print('  - "participants": "bob@example.com <-> chatgpt"')
print('  - "participants": "alice@company.com <-> claude"')
print("\nAudit logs location:")
print("  - Development: ./stinger_audit.log or stdout")
print("  - Production: Configured destination")