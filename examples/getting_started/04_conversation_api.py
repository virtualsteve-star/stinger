#!/usr/bin/env python3
"""
Conversation API Example - Stinger Guardrails

Demonstrates using the Conversation API with automatic guardrail application.
Follows the Conversation section from the Getting Started guide.
"""

from stinger import Conversation, GuardrailPipeline


def main():
    print("💬 Conversation API Example")
    print("=" * 35)
    
    # Step 1: Create conversation with rate limiting
    print("\n1. Creating conversation with rate limiting...")
    conv = Conversation.human_ai("user123", "assistant")
    # Optionally set a rate limit for demonstration
    conv.set_rate_limit({"turns_per_minute": 3})
    print(f"   Rate limit config: {conv.rate_limit}")
    
    # Step 2: Add exchanges (automatically rate limited)
    print("\n2. Adding exchanges (rate limit checked after each):")
    print("-" * 45)
    
    exchanges = [
        ("Hello", "Hi there! How can I help you today?"),
        ("How are you?", "I'm doing well, thanks for asking!"),
        ("I need help with my account", "I'd be happy to help with your account."),
        ("Can you reset my password?", "Sure, I can help with that.")
    ]
    
    for i, (prompt, response) in enumerate(exchanges, 1):
        print(f"\n📝 Exchange {i}:")
        print(f"   User: {prompt}")
        print(f"   Assistant: {response}")
        
        # Add exchange to conversation
        conv.add_exchange(prompt, response)
        
        # Check if rate limit exceeded
        exceeded = conv.check_rate_limit()
        if exceeded:
            print("   ⚠️  Rate limit exceeded! No more exchanges allowed in this window.")
            break
        else:
            print("   ✅ Rate limit OK")
    
    # Step 3: Check conversation history
    print("\n3. Conversation history:")
    print("-" * 25)
    
    history = conv.get_history()
    for i, turn in enumerate(history, 1):
        print(f"   Turn {i}: {turn.speaker} → {turn.listener}")
        print(f"      Prompt: {turn.prompt}")
        if turn.response:
            print(f"      Response: {turn.response}")
    
    # Step 4: Test conversation with guardrails
    print("\n4. Testing conversation with guardrails:")
    print("-" * 40)
    
    # Create pipeline for conversation context
    pipeline = GuardrailPipeline.from_preset('customer_service')
    
    # Test a conversation that should be blocked
    test_conv = Conversation.human_ai("user456", "assistant")
    test_conv.add_exchange("Hello", "Hi! How can I help?")
    
    # This should be blocked (PII in conversation context)
    result = pipeline.check_input("My SSN is 123-45-6789", conversation=test_conv)
    
    print(f"📝 Testing with conversation context:")
    print(f"   Content: My SSN is 123-45-6789")
    print(f"   Blocked: {result['blocked']}")
    if result['blocked']:
        print(f"   Reasons: {result['reasons']}")
    
    print("\n🎉 Conversation API working! Rate limiting and guardrails applied automatically.")


if __name__ == "__main__":
    main() 