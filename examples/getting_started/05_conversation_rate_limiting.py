#!/usr/bin/env python3
"""
Rate Limiting Example - Stinger Guardrails

Demonstrates rate limiting features and monitoring.
Follows the Rate Limiting section from the Getting Started guide.
"""

from stinger import Conversation, GuardrailPipeline


def main():
    print("⏱️  Rate Limiting Example")
    print("=" * 30)
    
    # Step 1: Create conversation with rate limiting
    print("\n1. Creating conversation with rate limiting...")
    conv = Conversation.human_ai("user123", "assistant")
    
    # Step 2: Add multiple exchanges to test rate limiting
    print("\n2. Adding exchanges (testing rate limits):")
    print("-" * 40)
    
    exchanges = [
        ("Hello", "Hi there!"),
        ("How are you?", "I'm doing well, thanks!"),
        ("What's the weather?", "I can't check the weather, but I can help with other things."),
        ("Tell me a joke", "Why don't scientists trust atoms? Because they make up everything!"),
        ("Another joke", "What do you call a fake noodle? An impasta!"),
        ("One more joke", "Why did the scarecrow win an award? He was outstanding in his field!")
    ]
    
    for i, (prompt, response) in enumerate(exchanges, 1):
        print(f"\n📝 Exchange {i}:")
        print(f"   User: {prompt}")
        print(f"   Assistant: {response}")
        
        # Add exchange to conversation
        conv.add_exchange(prompt, response)
        
        # Check rate limit status
        status = conv.check_rate_limit(action="warn")
        print(f"   Rate limit exceeded: {status}")
        
        # Show if rate limited
        if status:
            print("   ⚠️  Rate limit reached!")
            break
    
    # Step 3: Check conversation duration and stats
    print("\n3. Conversation statistics:")
    print("-" * 25)
    
    duration = conv.get_duration()
    turn_count = conv.get_turn_count()
    complete_count = conv.get_complete_turn_count()
    
    print(f"   Duration: {duration:.2f} seconds")
    print(f"   Total turns: {turn_count}")
    print(f"   Complete exchanges: {complete_count}")
    
    # Step 4: Test rate limit reset
    print("\n4. Rate limit information:")
    print("-" * 25)
    
    # Check if rate limit is configured
    if conv.rate_limit:
        print(f"   Rate limit config: {conv.rate_limit}")
        exceeded = conv.check_rate_limit(action="log")
        print(f"   Currently exceeded: {exceeded}")
    else:
        print("   No rate limit configured")
    
    print("\n🎉 Rate limiting working! Conversations are automatically rate limited.")


if __name__ == "__main__":
    main() 