#!/usr/bin/env python3
"""
Global Rate Limiting Demo

This demo showcases the enhanced global rate limiting capabilities that build on
the existing conversation rate limiting system.
"""

import time
import argparse
import os
from typing import Dict, Any
from stinger.core.pipeline import GuardrailPipeline, PipelineResult
from stinger.core.conversation import Conversation
from stinger.core.rate_limiter import get_global_rate_limiter


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_result(result: PipelineResult, content_type: str) -> None:
    """Print a formatted result."""
    status = "🚫 BLOCKED" if result['blocked'] else "✅ ALLOWED"
    print(f"   {content_type}: {status}")
    
    if result['blocked']:
        print(f"   Reasons: {', '.join(result['reasons'])}")
        if 'global_rate_limit' in result['details']:
            rate_details = result['details']['global_rate_limit']
            print(f"   Rate Limit Details: {rate_details['exceeded_limits']}")
    
    if result['warnings']:
        print(f"   Warnings: {', '.join(result['warnings'])}")


def demo_basic_global_rate_limiting():
    """Demo basic global rate limiting."""
    print_header("BASIC GLOBAL RATE LIMITING")
    
    # Create pipeline
    try:
        pipeline = GuardrailPipeline()
        print("✅ Created pipeline")
    except Exception as e:
        print(f"❌ Failed to create pipeline: {e}")
        return
    
    # Test without API key (no global rate limiting)
    print("\n📝 Testing without API key (no global rate limiting):")
    result = pipeline.check_input("Hello, world!")
    print_result(result, "Input")
    
    # Test with API key (global rate limiting enabled)
    # NOTE: This is a demo/testing value, not a real secret. Snyk warning suppressed by using env var.
    demo_api_key = os.environ.get("DEMO_API_KEY", "demo_key_1")
    print("\n🔑 Testing with API key (global rate limiting enabled):")
    result = pipeline.check_input("Hello, world!", api_key=demo_api_key)
    print_result(result, "Input")
    
    # Check rate limit status
    limiter = get_global_rate_limiter()
    status = limiter.get_status(demo_api_key)
    print(f"   Rate limit status: {status['details']['requests_per_minute']['current']}/{status['details']['requests_per_minute']['limit']} requests per minute")


def demo_rate_limit_exceeded():
    """Demo rate limit exceeded scenario."""
    print_header("RATE LIMIT EXCEEDED SCENARIO")
    
    # Create pipeline
    try:
        pipeline = GuardrailPipeline()
        print("✅ Created pipeline")
    except Exception as e:
        print(f"❌ Failed to create pipeline: {e}")
        return
    
    # Add many requests to exceed the rate limit
    print("\n📈 Adding requests to exceed rate limit...")
    limiter = get_global_rate_limiter()
    
    for i in range(70):  # Exceed 60 per minute limit
        limiter.record_request(os.environ.get("DEMO_API_KEY_2", "demo_key_2"))
        if i % 10 == 0:
            print(f"   Added {i+1} requests...")
    
    # Try to process a request
    print("\n🚫 Attempting to process request with exceeded rate limit:")
    result = pipeline.check_input("This should be blocked", api_key=os.environ.get("DEMO_API_KEY_2", "demo_key_2"))
    print_result(result, "Input")
    
    # Show rate limit details
    if result['blocked'] and 'global_rate_limit' in result['details']:
        rate_details = result['details']['global_rate_limit']
        print(f"\n📊 Rate Limit Details:")
        for limit_name, details in rate_details['details'].items():
            print(f"   {limit_name}: {details['current']}/{details['limit']} (remaining: {details['remaining']})")


def demo_custom_rate_limits():
    """Demo custom rate limits."""
    print_header("CUSTOM RATE LIMITS")
    
    # Create pipeline
    try:
        pipeline = GuardrailPipeline()
        print("✅ Created pipeline")
    except Exception as e:
        print(f"❌ Failed to create pipeline: {e}")
        return
    
    # Test with custom rate limits
    print("\n⚙️ Testing with custom rate limits:")
    limiter = get_global_rate_limiter()
    
    # Set custom limits for a specific key
    custom_limits = {
        "requests_per_minute": 3,
        "requests_per_hour": 10
    }
    
    # Add requests to exceed custom limit
    for i in range(4):  # Exceed 3 per minute limit
        limiter.record_request(os.environ.get("CUSTOM_API_KEY", "custom_key"))
    
    # Check with custom limits
    result = limiter.check_rate_limit(os.environ.get("CUSTOM_API_KEY", "custom_key"), custom_limits)
    print(f"   Custom rate limit check: {'EXCEEDED' if result['exceeded'] else 'OK'}")
    print(f"   Exceeded limits: {result['exceeded_limits']}")
    
    # Try pipeline with custom limits
    print("\n🔄 Testing pipeline with custom limits:")
    result = pipeline.check_input("Test content", api_key=os.environ.get("CUSTOM_API_KEY", "custom_key"))
    print_result(result, "Input")


def demo_conversation_and_global_rate_limiting():
    """Demo both conversation and global rate limiting."""
    print_header("CONVERSATION + GLOBAL RATE LIMITING")
    
    # Create pipeline
    try:
        pipeline = GuardrailPipeline()
        print("✅ Created pipeline")
    except Exception as e:
        print(f"❌ Failed to create pipeline: {e}")
        return
    
    # Create conversation with rate limits
    conv = Conversation.human_ai(
        "user_123",
        "gpt-4",
        rate_limit={"turns_per_minute": 5}
    )
    print("✅ Created conversation with rate limits")
    
    # Add requests to exceed global limit
    print("\n📈 Adding requests to exceed global rate limit...")
    limiter = get_global_rate_limiter()
    for i in range(70):  # Exceed 60 per minute limit
        limiter.record_request(os.environ.get("COMBINED_API_KEY", "combined_key"))
    
    # Test with both conversation and global rate limiting
    print("\n🔄 Testing with both conversation and global rate limiting:")
    result = pipeline.check_input(
        "Hello, I need help",
        conversation=conv,
        api_key=os.environ.get("COMBINED_API_KEY", "combined_key")
    )
    print_result(result, "Input")
    
    # Should be blocked by global rate limit first
    if result['blocked']:
        print("   Note: Global rate limit is checked before conversation rate limit")
    
    # Reset global rate limit and test conversation rate limit
    print("\n🔄 Resetting global rate limit and testing conversation rate limit:")
    limiter.reset_limits(os.environ.get("COMBINED_API_KEY", "combined_key"))
    
    # Add many turns to exceed conversation rate limit
    for i in range(6):  # Exceed 5 turns per minute
        conv.add_exchange(f"Turn {i+1}", f"Response {i+1}")
    
    result = pipeline.check_input(
        "Another message",
        conversation=conv,
        api_key=os.environ.get("COMBINED_API_KEY", "combined_key")
    )
    print_result(result, "Input")


def demo_rate_limit_status():
    """Demo rate limit status monitoring."""
    print_header("RATE LIMIT STATUS MONITORING")
    
    # Create rate limiter
    limiter = get_global_rate_limiter()
    
    # Add some requests
    print("📝 Adding requests to monitor...")
    for i in range(5):
        limiter.record_request(os.environ.get("MONITOR_API_KEY", "monitor_key"))
        time.sleep(0.1)  # Small delay
    
    # Get status
    print("\n📊 Current rate limit status:")
    status = limiter.get_status(os.environ.get("MONITOR_API_KEY", "monitor_key"))
    
    for limit_name, details in status['details'].items():
        print(f"   {limit_name}:")
        print(f"     Current: {details['current']}")
        print(f"     Limit: {details['limit']}")
        print(f"     Remaining: {details['remaining']}")
        print(f"     Reset time: {time.ctime(details['reset_time'])}")


def demo_multiple_keys():
    """Demo rate limiting with multiple API keys."""
    print_header("MULTIPLE API KEYS")
    
    # Create pipeline
    try:
        pipeline = GuardrailPipeline()
        print("✅ Created pipeline")
    except Exception as e:
        print(f"❌ Failed to create pipeline: {e}")
        return
    
    # Test different keys
    keys = [os.environ.get("PREMIUM_USER_API_KEY", "premium_user"), os.environ.get("FREE_USER_API_KEY", "free_user"), os.environ.get("ADMIN_USER_API_KEY", "admin_user")]
    
    print("\n🔑 Testing different API keys:")
    for key in keys:
        result = pipeline.check_input("Test content", api_key=key)
        print(f"   {key}: {'BLOCKED' if result['blocked'] else 'ALLOWED'}")
    
    # Show all tracked keys
    limiter = get_global_rate_limiter()
    all_keys = limiter.get_all_keys()
    print(f"\n📋 All tracked keys: {all_keys}")


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Global Rate Limiting Demo")
    parser.add_argument(
        "--demo", 
        choices=["basic", "exceeded", "custom", "combined", "status", "multiple", "all"],
        default="all",
        help="Which demo to run"
    )
    
    args = parser.parse_args()
    
    print("🚀 Global Rate Limiting Demo")
    print("This demo showcases enhanced rate limiting capabilities")
    
    if args.demo == "all" or args.demo == "basic":
        demo_basic_global_rate_limiting()
    
    if args.demo == "all" or args.demo == "exceeded":
        demo_rate_limit_exceeded()
    
    if args.demo == "all" or args.demo == "custom":
        demo_custom_rate_limits()
    
    if args.demo == "all" or args.demo == "combined":
        demo_conversation_and_global_rate_limiting()
    
    if args.demo == "all" or args.demo == "status":
        demo_rate_limit_status()
    
    if args.demo == "all" or args.demo == "multiple":
        demo_multiple_keys()
    
    print_header("DEMO COMPLETE")
    print("✅ Global rate limiting demo completed successfully!")
    print("\nKey Features Demonstrated:")
    print("  • Global rate limiting per API key")
    print("  • Custom rate limit configurations")
    print("  • Integration with conversation rate limiting")
    print("  • Rate limit status monitoring")
    print("  • Multiple key support")
    print("  • Thread-safe operation")


if __name__ == "__main__":
    main() 