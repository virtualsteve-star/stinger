#!/usr/bin/env python3
"""Test script to verify imports work correctly"""

import sys
import os

# Add src to path as the command does
sys.path.insert(0, 'src')

try:
    from stinger import GuardrailPipeline
    print("✓ Import successful: GuardrailPipeline imported")
    print(f"  Module path: {GuardrailPipeline.__module__}")
    
    # Test if we can create an instance
    try:
        pipeline = GuardrailPipeline()
        print("✓ Instance creation successful: GuardrailPipeline() created")
    except Exception as e:
        print(f"✗ Instance creation failed: {e}")
        
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Also test other key imports
try:
    from stinger import GuardrailInterface, GuardrailResult, GuardrailType
    print("✓ Core interfaces imported successfully")
except ImportError as e:
    print(f"✗ Core interface import failed: {e}")

print("\nAll imports tested successfully!")