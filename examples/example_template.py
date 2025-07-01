#!/usr/bin/env python3
"""
Example Template - Stinger Guardrails

This template provides the standard structure for Stinger examples.
Copy this template when creating new examples.
"""

import sys
import os
from typing import Optional


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
    
    # Check for API key if needed (for AI-powered examples)
    # Uncomment if your example needs AI features
    # if not os.environ.get('OPENAI_API_KEY'):
    #     print("⚠️  OPENAI_API_KEY not found")
    #     print("   AI-powered guardrails will not work without an API key")
    #     print("   Set with: export OPENAI_API_KEY='your-key-here'")
    #     # Don't fail - allow example to run with limited functionality
    
    return True


def run_example():
    """Run the main example code."""
    print("\n📚 Example Name Here")
    print("=" * 50)
    
    try:
        # Import Stinger components
        from stinger import GuardrailPipeline
        
        # Example code here
        print("\n1️⃣ Step 1: Description...")
        # ... your code ...
        
        print("\n2️⃣ Step 2: Description...")
        # ... your code ...
        
        print("\n✅ Example completed successfully!")
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("   Make sure Stinger is properly installed")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Check your API key (if using AI features)")
        print("   2. Ensure all dependencies are installed")
        print("   3. Check the error message above")
        return False
    
    return True


def main():
    """Main entry point."""
    # Check prerequisites
    if not check_prerequisites():
        print("\n⚠️  Prerequisites not met. Please fix the issues above.")
        return 1
    
    # Run the example
    success = run_example()
    
    if success:
        print("\n🎉 Success! You can now:")
        print("   - Modify this example for your needs")
        print("   - Check other examples in this directory")
        print("   - Read the full documentation")
    else:
        print("\n❌ Example failed. See errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())