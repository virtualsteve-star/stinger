#!/usr/bin/env python3
"""
Simple Demo: Guardrail Pipeline

A minimal demonstration of the GuardrailPipeline API.
"""

from stinger import GuardrailPipeline


def main():
    """Run the simple demo."""
    print("🛡️  STINGER: Simple Guardrail Demo")
    print("=" * 50)
    
    # Create pipeline from preset
    print("🔧 Creating pipeline from preset...")
    pipeline = GuardrailPipeline.from_preset("customer_service")
    print("✅ Pipeline ready!")
    
    # Test some content
    test_cases = [
        ("Hello, how can I help you?", "Normal conversation"),
        ("My email is john@example.com", "Contains PII"),
        ("I hate you and want to hurt you!", "Toxic content"),
        ("Here's some code: <script>alert('hack')</script>", "Code generation"),
    ]
    
    for i, (content, description) in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {description}")
        print("-" * 30)
        
        # Check input
        result = pipeline.check_input(content)
        status = "🚫 BLOCKED" if result['blocked'] else "✅ ALLOWED"
        print(f"Input: {status}")
        
        if result['warnings']:
            print(f"   Warnings: {', '.join(result['warnings'])}")
        
        if result['reasons']:
            print(f"   Blocked: {', '.join(result['reasons'])}")
    
    print("\n🎉 Demo complete!")


if __name__ == "__main__":
    main() 