#!/usr/bin/env python3
"""
Global Rate Limiting Example - Stinger Guardrails

Demonstrates global rate limiting features and monitoring.
Follows the Rate Limiting section from the Getting Started guide.
"""

from stinger.core.rate_limiter import get_global_rate_limiter


def main():
    print("⏱️  Global Rate Limiting Example")
    print("=" * 35)
    
    # Step 1: Get the global rate limiter
    print("\n1. Setting up global rate limiter...")
    limiter = get_global_rate_limiter()
    print(f"   Global rate limiter ready")
    
    # Step 2: Test basic rate limiting
    print("\n2. Testing basic rate limiting:")
    print("-" * 30)
    
    api_key = "test_user_123"
    
    # Test multiple requests
    for i in range(1, 6):
        print(f"\n📝 Request {i}:")
        
        # Check rate limit before making request
        result = limiter.check_rate_limit(api_key)
        
        if not result['exceeded']:
            remaining = result.get('remaining', {})
            minute_remaining = remaining.get('minute', 'N/A')
            print(f"   ✅ Allowed - {minute_remaining} requests remaining this minute")
            # Record the request
            limiter.record_request(api_key)
        else:
            print(f"   ❌ Blocked - Rate limit exceeded")
            print(f"      Reason: {result.get('reason', 'N/A')}")
            break
    
    # Step 3: Check rate limit status
    print("\n3. Rate limit status:")
    print("-" * 20)
    
    status = limiter.get_status(api_key)
    print(f"   API Key: {api_key}")
    
    details = status.get('details', {})
    if 'requests_per_minute' in details:
        minute_info = details['requests_per_minute']
        print(f"   Requests in last minute: {minute_info.get('current', 0)}")
        print(f"   Remaining this minute: {minute_info.get('remaining', 0)}")
    
    if 'requests_per_hour' in details:
        hour_info = details['requests_per_hour']
        print(f"   Requests in last hour: {hour_info.get('current', 0)}")
        print(f"   Remaining this hour: {hour_info.get('remaining', 0)}")
    
    # Step 4: Show all tracked keys
    print("\n4. All tracked API keys:")
    print("-" * 25)
    
    all_keys = limiter.get_all_keys()
    print(f"   Total tracked keys: {len(all_keys)}")
    for key in all_keys[:3]:  # Show first 3
        print(f"   - {key}")
    if len(all_keys) > 3:
        print(f"   ... and {len(all_keys) - 3} more")
    
    print("\n🎉 Global rate limiting working! Requests are automatically tracked and limited.")


if __name__ == "__main__":
    main() 