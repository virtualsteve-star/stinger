#!/usr/bin/env python3
"""
One-Liner Demo: Guardrail Pipeline

The simplest possible demonstration - just two lines of code!
"""

from stinger import GuardrailPipeline


def main():
    """Run the one-liner demo."""
    print("🛡️  STINGER: One-Liner Demo")
    print("=" * 40)
    print("Just two lines of code to protect your AI!")
    print()
    
    # 🎯 THE TWO LINES THAT MATTER
    pipeline = GuardrailPipeline.from_preset("basic")
    result = pipeline.check_input("Hello, my SSN is 123-45-6789")
    
    # Show the result
    print("📝 Input: 'Hello, my SSN is 123-45-6789'")
    print(f"🔍 Result: {'🚫 BLOCKED' if result['blocked'] else '✅ ALLOWED'}")
    
    if result['warnings']:
        print(f"⚠️  Warnings: {', '.join(result['warnings'])}")
    
    if result['reasons']:
        print(f"🚫 Blocked: {', '.join(result['reasons'])}")
    
    print("\n🎉 That's it! Two lines to protect your AI!")


if __name__ == "__main__":
    main() 