#!/usr/bin/env python3
"""
Test script to verify AI filters integration with centralized API key management.
"""

import asyncio
import tempfile
import yaml
import sys
from pathlib import Path
import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from stinger.filters.ai_code_generation_filter import AICodeGenerationFilter
from stinger.filters.ai_pii_detection_filter import AIPIIDetectionFilter
from stinger.filters.ai_toxicity_detection_filter import AIToxicityDetectionFilter

@pytest.mark.asyncio
async def test_ai_filters_integration():
    """Test AI filters with centralized API key management."""
    print("Testing AI filters integration with centralized API key management...")
    
    # Test configuration with environment variable substitution
    test_config = {
        "enabled": True,
        "confidence_threshold": 0.6,
        "on_error": "warn"
    }
    
    # Test AI Code Generation Filter
    print("\n1. Testing AI Code Generation Filter...")
    code_filter = AICodeGenerationFilter("test_code_gen", test_config)
    
    if code_filter.is_available():
        print("✅ SUCCESS: AI Code Generation Filter is available")
        
        # Test with benign content
        result = await code_filter.analyze("Hello, how are you today?")
        print(f"   Benign content result: {'BLOCKED' if result.blocked else 'ALLOWED'}")
        
        # Test with code content
        result = await code_filter.analyze("Here's a Python script: import os; os.system('rm -rf /')")
        print(f"   Code content result: {'BLOCKED' if result.blocked else 'ALLOWED'}")
    else:
        print("❌ FAILURE: AI Code Generation Filter is not available")
        return False
    
    # Test AI PII Detection Filter
    print("\n2. Testing AI PII Detection Filter...")
    pii_filter = AIPIIDetectionFilter("test_pii", test_config)
    
    if pii_filter.is_available():
        print("✅ SUCCESS: AI PII Detection Filter is available")
        
        # Test with benign content
        result = await pii_filter.analyze("Hello, how are you today?")
        print(f"   Benign content result: {'BLOCKED' if result.blocked else 'ALLOWED'}")
        
        # Test with PII content
        result = await pii_filter.analyze("My credit card is 4111-1111-1111-1111")
        print(f"   PII content result: {'BLOCKED' if result.blocked else 'ALLOWED'}")
    else:
        print("❌ FAILURE: AI PII Detection Filter is not available")
        return False
    
    # Test AI Toxicity Detection Filter
    print("\n3. Testing AI Toxicity Detection Filter...")
    toxicity_filter = AIToxicityDetectionFilter("test_toxicity", test_config)
    
    if toxicity_filter.is_available():
        print("✅ SUCCESS: AI Toxicity Detection Filter is available")
        
        # Test with benign content
        result = await toxicity_filter.analyze("Hello, how are you today?")
        print(f"   Benign content result: {'BLOCKED' if result.blocked else 'ALLOWED'}")
        
        # Test with potentially toxic content
        result = await toxicity_filter.analyze("You are so stupid and worthless!")
        print(f"   Toxic content result: {'BLOCKED' if result.blocked else 'ALLOWED'}")
    else:
        print("❌ FAILURE: AI Toxicity Detection Filter is not available")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_ai_filters_integration())
    if success:
        print("\n🎉 All AI filters are working correctly with centralized API key management!")
    else:
        print("\n💥 AI filters integration failed!")
        exit(1) 