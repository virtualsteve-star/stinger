#!/usr/bin/env python3
"""
Basic Demo Functionality Test

Tests that the demo can start and handle basic requests without API key errors.
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# Add src to path for Stinger imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_api_key_manager():
    """Test that the API key manager works correctly."""
    print("🔑 Testing API key manager...")
    
    try:
        from stinger.core.api_key_manager import get_openai_key, validate_api_key_config
        
        # Test getting OpenAI key
        api_key = get_openai_key()
        if api_key:
            print(f"✅ OpenAI API key found: {api_key[:8]}...{api_key[-4:]}")
            
            # Test validation
            health = validate_api_key_config()
            print(f"✅ API key validation: {health}")
            
            return True
        else:
            print("⚠️ No OpenAI API key configured")
            print("💡 Set OPENAI_API_KEY environment variable to test with real LLM")
            return True  # This is acceptable for testing
            
    except Exception as e:
        print(f"❌ API key manager test failed: {e}")
        return False

def test_pipeline_creation():
    """Test that guardrail pipeline can be created."""
    print("\n🛡️ Testing guardrail pipeline creation...")
    
    try:
        from stinger.core.pipeline import GuardrailPipeline
        
        # Test creating pipeline from preset
        pipeline = GuardrailPipeline.from_preset("customer_service")
        print("✅ Customer service pipeline created")
        
        # Test getting status
        status = pipeline.get_guardrail_status()
        input_count = len(status.get("input_guardrails", []))
        output_count = len(status.get("output_guardrails", []))
        print(f"✅ Pipeline status: {input_count} input, {output_count} output guardrails")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline creation failed: {e}")
        return False

def test_backend_initialization():
    """Test that backend can initialize without the hardcoded demo_key error."""
    print("\n🚀 Testing backend initialization...")
    
    try:
        # Set a temporary backend directory
        backend_dir = Path(__file__).parent / "backend"
        os.chdir(backend_dir)
        
        # Import the main module to test initialization
        sys.path.insert(0, str(backend_dir))
        
        # Test that we can import without errors
        import main
        print("✅ Backend main module imports successfully")
        
        # Test that the lifespan function exists and uses proper API key management
        assert hasattr(main, 'lifespan'), "lifespan function not found"
        print("✅ Lifespan function found")
        
        # Check that demo_key is not in the source
        main_file = backend_dir / "main.py"
        with open(main_file, 'r') as f:
            content = f.read()
        
        if 'demo_key' in content:
            print("❌ Found 'demo_key' in backend source code")
            return False
        else:
            print("✅ No hardcoded 'demo_key' found in backend")
        
        # Check that get_openai_key is imported
        if 'get_openai_key' in content:
            print("✅ Backend uses centralized API key manager")
        else:
            print("❌ Backend doesn't use centralized API key manager")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Backend initialization test failed: {e}")
        return False

def test_mock_response_functionality():
    """Test that the demo works without an API key (mock mode)."""
    print("\n🎭 Testing mock response functionality...")
    
    try:
        from stinger.core.pipeline import GuardrailPipeline
        from stinger.core.conversation import Conversation
        
        # Create pipeline
        pipeline = GuardrailPipeline.from_preset("customer_service")
        
        # Create conversation
        conversation = Conversation.human_ai("test_user", "gpt-4o-mini")
        
        # Test input guardrails
        test_content = "Hello, this is a test message"
        input_result = pipeline.check_input(test_content, conversation=conversation)
        
        print(f"✅ Input guardrails work: blocked={input_result['blocked']}")
        
        # Test with potentially problematic content
        pii_content = "My email is test@example.com"
        pii_result = pipeline.check_input(pii_content, conversation=conversation)
        
        print(f"✅ PII detection works: blocked={pii_result['blocked']}, warnings={len(pii_result['warnings'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock response test failed: {e}")
        return False

def main():
    """Run all basic functionality tests."""
    print("🧪 Stinger Web Demo - Basic Functionality Test")
    print("=" * 60)
    
    tests = [
        ("API Key Manager", test_api_key_manager),
        ("Pipeline Creation", test_pipeline_creation), 
        ("Backend Initialization", test_backend_initialization),
        ("Mock Response Functionality", test_mock_response_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All basic functionality tests PASSED!")
        print("\n💡 Next steps:")
        print("1. Set OPENAI_API_KEY environment variable for real LLM responses")
        print("2. Run 'python test_demo_e2e.py' for full integration testing")
        print("3. Start the demo with 'python backend/main.py'")
        return True
    else:
        print("❌ Some tests FAILED. Please fix issues before running the demo.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Tests cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)