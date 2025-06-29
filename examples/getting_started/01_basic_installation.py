#!/usr/bin/env python3
"""
Basic Installation Example - Stinger Guardrails

Demonstrates basic installation and your first guardrail check.
Follows the Quick Start section from the Getting Started guide.
"""

from stinger import GuardrailPipeline


def main():
    print("🚀 Basic Installation Example")
    print("=" * 40)
    
    # Step 1: Create pipeline with customer service preset
    print("\n1. Creating pipeline with customer service preset...")
    pipeline = GuardrailPipeline.from_preset('customer_service')
    
    # Show pipeline status
    status = pipeline.get_guardrail_status()
    print(f"✅ Pipeline ready with {status['total_enabled']} enabled guardrails")
    
    # Step 2: Your first guardrail check
    print("\n2. Testing your first guardrail check:")
    print("-" * 35)
    
    test_content = "My credit card is 1234-5678-9012-3456"
    print(f"📝 Testing: {test_content}")
    
    result = pipeline.check_input(test_content)
    
    print(f"   Blocked: {result['blocked']}")
    print(f"   Reasons: {result['reasons']}")
    
    # Step 3: Test a safe message
    print("\n3. Testing a safe message:")
    print("-" * 25)
    
    safe_content = "I need help with my order"
    print(f"📝 Testing: {safe_content}")
    
    result = pipeline.check_input(safe_content)
    
    print(f"   Blocked: {result['blocked']}")
    if result['warnings']:
        print(f"   Warnings: {result['warnings']}")
    else:
        print("   ✅ Content approved")
    
    print("\n🎉 Basic installation working! Stinger is protecting your content.")


if __name__ == "__main__":
    main() 