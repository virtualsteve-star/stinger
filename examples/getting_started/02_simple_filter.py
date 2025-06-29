#!/usr/bin/env python3
"""
Simple Filter Example - Stinger Guardrails

Demonstrates using different presets and understanding guardrail results.
Follows the Basic Usage section from the Getting Started guide.
"""

from stinger import GuardrailPipeline


def main():
    print("🔧 Simple Filter Example")
    print("=" * 35)
    
    # Test different presets
    presets = [
        ('customer_service', 'Customer Service Bot'),
        ('medical', 'Medical Information Bot'),
        ('financial', 'Financial Services Bot')
    ]
    
    for preset_name, description in presets:
        print(f"\n📋 Testing {description} ({preset_name} preset):")
        print("-" * 45)
        
        # Create pipeline with preset
        pipeline = GuardrailPipeline.from_preset(preset_name)
        
        # Test cases specific to each preset
        if preset_name == 'customer_service':
            test_cases = [
                ("My SSN is 123-45-6789", "PII content"),
                ("I need help with my order", "Normal request"),
                ("You are so stupid!", "Toxic content")
            ]
        elif preset_name == 'medical':
            test_cases = [
                ("I have chest pain, what should I do?", "Medical advice"),
                ("What are the benefits of exercise?", "General health info"),
                ("My blood pressure is 140/90", "Medical data")
            ]
        else:  # financial
            test_cases = [
                ("Hello, how can you help me?", "Normal greeting"),
                ("My credit card is 4111-1111-1111-1111", "Financial PII"),
                ("Should I invest in stocks?", "Financial advice")
            ]
        
        # Test each case
        for content, description in test_cases:
            print(f"\n📝 {description}:")
            print(f"   Content: {content}")
            
            result = pipeline.check_input(content)
            
            if result['blocked']:
                print(f"   ❌ BLOCKED: {result['reasons']}")
            elif result['warnings']:
                print(f"   ⚠️  WARNINGS: {result['warnings']}")
            else:
                print("   ✅ PASSED")
    
    print("\n🎉 Different presets working! Each preset has different filtering rules.")


if __name__ == "__main__":
    main() 