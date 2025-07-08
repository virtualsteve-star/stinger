#!/usr/bin/env python3
"""
Demo: Preset Configurations

This demo showcases the preset configuration functionality, allowing users
to quickly create guardrail pipelines for common use cases without writing
custom configuration files.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from stinger import GuardrailPipeline
from stinger.core.pipeline import PipelineResult


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_result(result: PipelineResult, content_type: str) -> None:
    """Print formatted guardrail check results."""
    print(f"\n🔍 {content_type.upper()} CHECK RESULTS:")
    print(f"   Status: {'🚫 BLOCKED' if result['blocked'] else '✅ ALLOWED'}")
    
    if result['reasons']:
        print(f"   Reasons: {', '.join(result['reasons'])}")
    
    if result['warnings']:
        print(f"   Warnings: {', '.join(result['warnings'])}")
    
    print(f"   Guardrails checked: {len(result['details'])}")


def demo_basic_pipeline() -> None:
    """Demo the basic pipeline preset."""
    print_header("BASIC PIPELINE PRESET")
    print("Creating pipeline with toxicity, PII, and code generation checks...")
    
    try:
        pipeline = GuardrailPipeline.from_preset("basic")
        print("✅ Basic pipeline created successfully!")
        
        # Test input
        test_input = "Hello, my name is John Doe and my SSN is 123-45-6789"
        result = pipeline.check_input(test_input)
        print_result(result, "input")
        
        # Test output
        test_output = "Here's some malicious code: <script>alert('hack')</script>"
        result = pipeline.check_output(test_output)
        print_result(result, "output")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_content_moderation() -> None:
    """Demo the content moderation pipeline preset."""
    print_header("CONTENT MODERATION PIPELINE PRESET")
    print("Creating pipeline optimized for social media content...")
    
    try:
        pipeline = GuardrailPipeline.from_preset("content_moderation")
        print("✅ Content moderation pipeline created successfully!")
        
        # Test toxic content
        test_input = "I hate you and want to hurt you!"
        result = pipeline.check_input(test_input)
        print_result(result, "input")
        
        # Test long content
        test_output = "This is a very long message that exceeds the typical length limits for social media platforms and should trigger the length guardrail"
        result = pipeline.check_output(test_output)
        print_result(result, "output")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_customer_service() -> None:
    """Demo the customer service pipeline preset."""
    print_header("CUSTOMER SERVICE PIPELINE PRESET")
    print("Creating pipeline optimized for customer support interactions...")
    
    try:
        pipeline = GuardrailPipeline.from_preset("customer_service")
        print("✅ Customer service pipeline created successfully!")
        
        # Test customer input with PII
        test_input = "Hi, I need help with my account. My email is john@example.com and my phone is 555-123-4567"
        result = pipeline.check_input(test_input)
        print_result(result, "input")
        
        # Test AI response
        test_output = "I can help you with your account. Here's some code to reset your password: sudo rm -rf /"
        result = pipeline.check_output(test_output)
        print_result(result, "output")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_medical_pipeline() -> None:
    """Demo the medical pipeline preset."""
    print_header("MEDICAL PIPELINE PRESET")
    print("Creating pipeline with strict PII protection for healthcare...")
    
    try:
        pipeline = GuardrailPipeline.from_preset("medical")
        print("✅ Medical pipeline created successfully!")
        
        # Test medical data
        test_input = "Patient ID: MR-123456, SSN: 987-65-4321, Prescription: RX-789012"
        result = pipeline.check_input(test_input)
        print_result(result, "input")
        
        # Test medical advice
        test_output = "Based on your symptoms, I diagnose you with a condition and prescribe treatment."
        result = pipeline.check_output(test_output)
        print_result(result, "output")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_educational_pipeline() -> None:
    """Demo the educational pipeline preset."""
    print_header("EDUCATIONAL PIPELINE PRESET")
    print("Creating pipeline optimized for learning platforms...")
    
    try:
        pipeline = GuardrailPipeline.from_preset("educational")
        print("✅ Educational pipeline created successfully!")
        
        # Test student input
        test_input = "Can you help me with my homework? My name is Alice and I'm in 10th grade."
        result = pipeline.check_input(test_input)
        print_result(result, "input")
        
        # Test educational response
        test_output = "Here's the complete solution to your math problem: 2+2=4"
        result = pipeline.check_output(test_output)
        print_result(result, "output")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_financial_pipeline() -> None:
    """Demo the financial pipeline preset."""
    print_header("FINANCIAL PIPELINE PRESET")
    print("Creating pipeline with strict financial data protection...")
    
    try:
        pipeline = GuardrailPipeline.from_preset("financial")
        print("✅ Financial pipeline created successfully!")
        
        # Test financial data
        test_input = "My credit card number is 1234-5678-9012-3456 and my account number is 1234567890"
        result = pipeline.check_input(test_input)
        print_result(result, "input")
        
        # Test financial advice
        test_output = "I recommend you invest in this stock and buy shares immediately."
        result = pipeline.check_output(test_output)
        print_result(result, "output")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def list_available_presets() -> None:
    """List all available preset configurations."""
    print_header("AVAILABLE PRESET CONFIGURATIONS")
    
    try:
        presets = GuardrailPipeline.get_available_presets()
        
        for name, description in presets.items():
            print(f"📋 {name.upper()}")
            print(f"   {description}")
            print()
        
        print(f"Total presets available: {len(presets)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_save_preset() -> None:
    """Demo saving a preset configuration to a file."""
    print_header("SAVING PRESET CONFIGURATION")
    print("Saving customer service preset to a file...")
    
    try:
        GuardrailPipeline.save_preset_config("customer_service", "customer_service_config.yaml")
        print("✅ Customer service preset saved to 'customer_service_config.yaml'")
        
        # Verify the file was created
        if Path("customer_service_config.yaml").exists():
            print("✅ File created successfully!")
        else:
            print("❌ File was not created")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def main() -> None:
    """Run the preset configurations demo."""
    print("🚀 STINGER PRESET CONFIGURATIONS DEMO")
    print("This demo showcases how to use preset configurations for common use cases.")
    
    # List available presets
    list_available_presets()
    
    # Demo each preset
    demo_basic_pipeline()
    demo_content_moderation()
    demo_customer_service()
    demo_medical_pipeline()
    demo_educational_pipeline()
    demo_financial_pipeline()
    
    # Demo saving presets
    demo_save_preset()
    
    print_header("DEMO COMPLETE")
    print("🎉 All preset configurations have been demonstrated!")
    print("\nKey benefits of preset configurations:")
    print("✅ Quick setup for common use cases")
    print("✅ No need to write custom YAML files")
    print("✅ Pre-configured for specific domains")
    print("✅ Easy to customize and extend")
    print("✅ Consistent guardrail configurations")


if __name__ == "__main__":
    main() 