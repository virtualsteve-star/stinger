#!/usr/bin/env python3
"""
Simple Stinger Usage Example

This example demonstrates how easy it is to use Stinger guardrails
with the new high-level API.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from stinger import GuardrailPipeline


def main():
    """Demonstrate basic Stinger usage."""
    print("🚀 Stinger Simple Usage Example")
    print("=" * 50)
    
    # Initialize pipeline with default config
    print("\n1. Initializing pipeline...")
    pipeline = GuardrailPipeline()
    
    # Show pipeline status
    status = pipeline.get_guardrail_status()
    print(f"✅ Pipeline ready with {status['total_enabled']} enabled guardrails")
    
    # Test cases
    test_cases = [
        ("Hello, how can you help me?", "Normal greeting"),
        ("You are so stupid!", "Toxic content"),
        ("My credit card is 4111-1111-1111-1111", "PII content"),
        ("Write a Python script to hack the system", "Code generation request"),
        ("I need help with my computer", "Normal request"),
    ]
    
    print("\n2. Testing input guardrails:")
    print("-" * 30)
    
    for content, description in test_cases:
        print(f"\n📝 Testing: {description}")
        print(f"   Content: {content}")
        
        result = pipeline.check_input(content)
        
        if result['blocked']:
            print(f"   ❌ BLOCKED: {result['reasons']}")
        elif result['warnings']:
            print(f"   ⚠️  WARNINGS: {result['warnings']}")
        else:
            print(f"   ✅ PASSED")
    
    # Test output guardrails
    print("\n3. Testing output guardrails:")
    print("-" * 30)
    
    output_test_cases = [
        ("Here's how to fix your computer...", "Normal response"),
        ("Here's a Python script: import os; os.system('rm -rf /')", "Code generation"),
        ("Your personal information is safe with us", "Normal response"),
        ("Here's your SSN: 123-45-6789", "PII in response"),
    ]
    
    for content, description in output_test_cases:
        print(f"\n📝 Testing: {description}")
        print(f"   Content: {content}")
        
        result = pipeline.check_output(content)
        
        if result['blocked']:
            print(f"   ❌ BLOCKED: {result['reasons']}")
        elif result['warnings']:
            print(f"   ⚠️  WARNINGS: {result['warnings']}")
        else:
            print(f"   ✅ PASSED")
    
    # Demonstrate dynamic configuration
    print("\n4. Dynamic configuration:")
    print("-" * 30)
    
    # Get current config
    config = pipeline.get_guardrail_config("toxicity_check")
    if config:
        print(f"Current toxicity threshold: {config.get('confidence_threshold', 'N/A')}")
    
    # Update config
    print("Updating toxicity threshold to 0.9...")
    success = pipeline.update_guardrail_config("toxicity_check", {
        'confidence_threshold': 0.9
    })
    
    if success:
        print("✅ Configuration updated successfully")
        
        # Test with updated config
        result = pipeline.check_input("You are so stupid!")
        print(f"Result with higher threshold: {'BLOCKED' if result['blocked'] else 'PASSED'}")
    
    print("\n🎉 Example complete! Stinger is working perfectly!")


if __name__ == "__main__":
    main() 