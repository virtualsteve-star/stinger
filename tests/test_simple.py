import asyncio
import sys
import os
import pytest
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.filters.regex_filter import RegexFilter

@pytest.mark.asyncio
async def test_regex_filter():
    print("🧪 Testing RegexFilter...")
    
    # Test configuration
    config = {
        'patterns': [
            r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
        ],
        'action': 'warn',
        'case_sensitive': False
    }
    
    filter_obj = RegexFilter(config)
    
    # Test cases
    test_cases = [
        ("My credit card is 1234-5678-9012-3456", "warn"),
        ("Contact me at test@example.com", "warn"),
        ("Hello world", "allow"),
        ("TEST@EXAMPLE.COM", "warn"),
    ]
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        try:
            result = await filter_obj.run(input_text)
            if result.action == expected:
                print(f"✅ Test {i}: PASS - '{input_text[:30]}...'")
            else:
                print(f"❌ Test {i}: FAIL - '{input_text[:30]}...' -> {result.action} (expected {expected})")
        except Exception as e:
            print(f"💥 Test {i}: ERROR - {str(e)}")
    
    print("✅ RegexFilter test completed!")

if __name__ == "__main__":
    asyncio.run(test_regex_filter()) 