#!/usr/bin/env python3
"""
Simple Filter Example - Stinger Guardrails

Demonstrates using different presets and understanding guardrail results.
Follows the Basic Usage section from the Getting Started guide.
"""

import sys
import os


def check_prerequisites() -> bool:
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    # Check if Stinger is installed
    try:
        import stinger
        print("✅ Stinger is installed")
    except ImportError:
        print("❌ Stinger is not installed")
        print("   Install with: pip install stinger-guardrails-alpha")
        return False
    
    # Check for API key (optional for this example)
    if not os.environ.get('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not found")
        print("   Some guardrails may be limited without an API key")
        print("   Set with: export OPENAI_API_KEY='your-key-here'")
    
    return True


def run_example():
    """Run the main example code."""
    print("\n🔧 Simple Filter Example")
    print("=" * 35)
    
    try:
        from stinger import GuardrailPipeline
        
        # Test different presets
        presets = [
            ('customer_service', 'Customer Service Bot'),
            ('medical', 'Medical Information Bot'),
            ('financial', 'Financial Services Bot')
        ]
        
        for preset_name, description in presets:
            print(f"\n📋 Testing {description} ({preset_name} preset):")
            print("-" * 45)
            
            try:
                # Create pipeline with preset
                pipeline = GuardrailPipeline.from_preset(preset_name)
                
                # Get status to show what's enabled
                status = pipeline.get_guardrail_status()
                print(f"   Guardrails enabled: {status['total_enabled']}")
                
            except Exception as e:
                print(f"   ❌ Failed to create pipeline: {e}")
                print("   Skipping this preset...")
                continue
            
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
                print(f"\n   📝 {description}:")
                print(f"      Content: {content}")
                
                try:
                    result = pipeline.check_input(content)
                    
                    if result['blocked']:
                        print(f"      ❌ BLOCKED: {result['reasons']}")
                    elif result['warnings']:
                        print(f"      ⚠️  WARNINGS: {result['warnings']}")
                    else:
                        print("      ✅ PASSED")
                        
                except Exception as e:
                    print(f"      ❌ Error checking content: {e}")
        
        print("\n✅ Example completed successfully!")
        print("   Different presets have different filtering rules.")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("   Make sure Stinger is properly installed")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Check your Python environment")
        print("   2. Ensure all dependencies are installed")
        print("   3. Try running: stinger setup")
        return False


def main():
    """Main entry point with proper error handling."""
    # Check prerequisites
    if not check_prerequisites():
        print("\n⚠️  Prerequisites not met. Please fix the issues above.")
        return 1
    
    # Run the example
    success = run_example()
    
    if success:
        print("\n🎉 Success! Next steps:")
        print("   - Try different content with each preset")
        print("   - Create your own custom pipelines")
        print("   - Check example 03 for rate limiting")
    else:
        print("\n❌ Example failed. See errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())