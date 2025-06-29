#!/usr/bin/env python3
"""
Debug script to check pipeline structure
"""

import sys
from pathlib import Path

# Add src to path for Stinger imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from stinger import GuardrailPipeline

def debug_pipeline():
    """Debug pipeline structure."""
    print("Creating pipeline...")
    
    pipeline = GuardrailPipeline.from_preset("customer_service")
    
    print(f"Pipeline type: {type(pipeline)}")
    print(f"Pipeline attributes: {dir(pipeline)}")
    
    # Check for various attribute names
    attrs_to_check = [
        'input_guardrails', 'output_guardrails', 
        'input_filters', 'output_filters',
        'filters', 'guardrails'
    ]
    
    for attr in attrs_to_check:
        if hasattr(pipeline, attr):
            value = getattr(pipeline, attr)
            print(f"✅ {attr}: {type(value)} = {value}")
        else:
            print(f"❌ {attr}: not found")
    
    # Try to get status
    if hasattr(pipeline, 'get_guardrail_status'):
        status = pipeline.get_guardrail_status()
        print(f"📊 get_guardrail_status(): {status}")
    else:
        print("❌ get_guardrail_status method not found")

if __name__ == "__main__":
    debug_pipeline()