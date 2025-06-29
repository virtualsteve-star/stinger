#!/usr/bin/env python3
"""
CLI and YAML Config Example - Stinger Guardrails

Demonstrates CLI usage and YAML configuration files.
Follows the CLI Commands and Configuration sections from the Getting Started guide.
"""

import subprocess
import sys
import yaml
from pathlib import Path
from stinger import GuardrailPipeline, ConfigLoader


def main():
    print("🔧 CLI and YAML Config Example")
    print("=" * 35)
    
    # Step 1: Show CLI commands
    print("\n1. CLI Commands:")
    print("-" * 15)
    
    cli_commands = [
        ("python -m stinger.cli health", "Basic health check"),
        ("python -m stinger.cli health --detailed", "Detailed health information"),
        ("python -m stinger.cli check-prompt 'Hello world'", "Check a prompt"),
        ("python -m stinger.cli check-response 'This is a response'", "Check a response"),
        ("python -m stinger.cli demo", "Run interactive demo")
    ]
    
    for command, description in cli_commands:
        print(f"   {command}")
        print(f"      → {description}")
    
    # Step 2: Create a custom YAML config
    print("\n2. Creating custom YAML config:")
    print("-" * 30)
    
    custom_config = {
        "version": "1.0",
        "pipeline": {
            "input": [
                {
                    "name": "toxicity_check",
                    "type": "simple_toxicity_detection",
                    "enabled": True,
                    "on_error": "block",
                    "config": {
                        "categories": ["hate_speech", "harassment"],
                        "confidence_threshold": 0.8
                    }
                },
                {
                    "name": "pii_check",
                    "type": "simple_pii_detection",
                    "enabled": True,
                    "on_error": "warn"
                },
                {
                    "name": "length_check",
                    "type": "length_filter",
                    "enabled": True,
                    "on_error": "warn",
                    "config": {
                        "max_length": 1000,
                        "min_length": 1
                    }
                }
            ],
            "output": [
                {
                    "name": "content_moderation",
                    "type": "content_moderation",
                    "enabled": True,
                    "on_error": "block"
                }
            ]
        }
    }
    
    # Save config to file
    config_path = Path("configs/custom_example.yaml")
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w') as f:
        yaml.dump(custom_config, f, default_flow_style=False, indent=2)
    
    print(f"   ✅ Created: {config_path}")
    print(f"   Config includes: toxicity, PII, length, and content moderation filters")
    
    # Step 3: Load and use custom config
    print("\n3. Loading and using custom config:")
    print("-" * 35)
    
    try:
        # Load config using GuardrailPipeline
        pipeline = GuardrailPipeline(str(config_path))
        
        print(f"   ✅ Config loaded successfully")
        
        # Test the custom pipeline
        test_cases = [
            ("Hello, how are you?", "Normal greeting"),
            ("You are so stupid!", "Toxic content"),
            ("My SSN is 123-45-6789", "PII content"),
            ("This is a very long message that exceeds the maximum length limit...", "Long content")
        ]
        
        for content, description in test_cases:
            print(f"\n📝 Testing: {description}")
            print(f"   Content: {content[:50]}{'...' if len(content) > 50 else ''}")
            
            result = pipeline.check_input(content)
            
            if result['blocked']:
                print(f"   ❌ BLOCKED: {result['reasons']}")
            elif result['warnings']:
                print(f"   ⚠️  WARNINGS: {result['warnings']}")
            else:
                print("   ✅ PASSED")
                
    except Exception as e:
        print(f"   ❌ Error loading config: {e}")
    
    # Step 4: Show config structure
    print("\n4. YAML Config Structure:")
    print("-" * 25)
    
    print("   Basic structure:")
    print("   ├── version: Config version")
    print("   └── pipeline:")
    print("       ├── input: Input guardrails")
    print("       └── output: Output guardrails")
    print("")
    print("   Each guardrail has:")
    print("   ├── name: Unique identifier")
    print("   ├── type: Filter type")
    print("   ├── enabled: True/False")
    print("   ├── on_error: block/warn/log")
    print("   └── config: Filter-specific settings")
    
    # Step 5: Demonstrate CLI simulation
    print("\n5. CLI Command Simulation:")
    print("-" * 30)
    
    # Simulate CLI check-prompt
    print("   Simulating: python -m stinger.cli check-prompt 'Test content'")
    
    test_content = "This is a test prompt with some content"
    result = pipeline.check_input(test_content)
    
    print(f"   Input: {test_content}")
    print(f"   Result: {'BLOCKED' if result['blocked'] else 'PASSED'}")
    if result['reasons']:
        print(f"   Reasons: {result['reasons']}")
    if result['warnings']:
        print(f"   Warnings: {result['warnings']}")
    
    # Clean up
    if config_path.exists():
        config_path.unlink()
        print(f"\n   🧹 Cleaned up: {config_path}")
    
    print("\n🎉 CLI and YAML config working! You can now create custom configurations.")


if __name__ == "__main__":
    main() 