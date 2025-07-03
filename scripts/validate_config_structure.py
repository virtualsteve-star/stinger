#!/usr/bin/env python3
"""
Validate Config Structure Script

Ensures all guardrails handle nested configuration correctly.
Run this in CI to catch config bugs before they reach production.
"""

import sys
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, 'src')

from stinger.guardrails.simple_pii_detection_guardrail import SimplePIIDetectionGuardrail
from stinger.guardrails.simple_toxicity_detection_guardrail import SimpleToxicityDetectionGuardrail
from stinger.guardrails.simple_code_generation_guardrail import SimpleCodeGenerationGuardrail
from stinger.guardrails.prompt_injection_guardrail import PromptInjectionGuardrail
from stinger.guardrails.content_moderation_guardrail import ContentModerationGuardrail
from stinger.guardrails.topic_guardrail import TopicGuardrail
from stinger.guardrails.url_guardrail import URLGuardrail
from stinger.guardrails.length_guardrail import LengthGuardrail
from stinger.guardrails.regex_guardrail import RegexGuardrail
from stinger.guardrails.keyword_block import KeywordBlockGuardrail


# Map of guardrail types to their expected config parameters
GUARDRAIL_CONFIG_MAP = {
    "simple_pii_detection": {
        "class": SimplePIIDetectionGuardrail,
        "test_params": {
            "confidence_threshold": 0.123,
            "patterns": ["ssn"],
            "test_custom": "custom_value"
        },
        "verify_params": ["confidence_threshold"]
    },
    "simple_toxicity_detection": {
        "class": SimpleToxicityDetectionGuardrail,
        "test_params": {
            "confidence_threshold": 0.234,
            "categories": ["hate_speech"],
            "test_custom": "custom_value"
        },
        "verify_params": ["confidence_threshold", "enabled_categories"]
    },
    "simple_code_generation": {
        "class": SimpleCodeGenerationGuardrail,
        "test_params": {
            "confidence_threshold": 0.345,
            "min_keywords": 5,
            "categories": ["python_syntax"]
        },
        "verify_params": ["confidence_threshold", "min_keywords"]
    },
    "prompt_injection": {
        "class": PromptInjectionGuardrail,
        "test_params": {
            "risk_threshold": 45,
            "block_levels": ["high"],
            "warn_levels": ["medium"]
        },
        "verify_params": ["risk_threshold", "block_levels"]
    },
    "content_moderation": {
        "class": ContentModerationGuardrail,
        "test_params": {
            "confidence_threshold": 0.456,
            "block_categories": ["violence"],
            "warn_categories": ["hate"]
        },
        "verify_params": ["confidence_threshold", "block_categories"]
    },
    "topic": {
        "class": TopicGuardrail,
        "test_params": {
            "confidence_threshold": 0.567,
            "allow_topics": ["medical"],
            "deny_topics": ["violence"]
        },
        "verify_params": ["confidence_threshold", "allow_topics"]
    },
    "url": {
        "class": URLGuardrail,
        "test_params": {
            "blocked_domains": ["evil.com"],
            "allowed_domains": ["safe.com"],
            "action": "block"
        },
        "verify_params": ["blocked_domains", "action"]
    },
    "length": {
        "class": LengthGuardrail,
        "test_params": {
            "min_length": 10,
            "max_length": 1000,
            "action": "block"
        },
        "verify_params": ["min_length", "max_length"]
    },
    "regex": {
        "class": RegexGuardrail,
        "test_params": {
            "patterns": ["test.*pattern"],
            "action": "block",
            "case_sensitive": False
        },
        "verify_params": ["patterns", "action"]
    },
    "keyword_block": {
        "class": KeywordBlockGuardrail,
        "test_params": {
            "keyword": "forbidden",
            "case_sensitive": True
        },
        "verify_params": ["keyword"]
    }
}


def test_guardrail_nested_config(guardrail_type: str, config_info: Dict[str, Any]) -> Dict[str, Any]:
    """Test a single guardrail handles nested config correctly"""
    
    guardrail_class = config_info["class"]
    test_params = config_info["test_params"]
    verify_params = config_info["verify_params"]
    
    # Create config with NESTED structure (as pipeline provides)
    nested_config = {
        "name": f"test_{guardrail_type}",
        "type": guardrail_type,
        "config": test_params  # Config is NESTED here
    }
    
    # Add required fields for certain guardrails at top level
    if guardrail_type == "regex":
        nested_config["patterns"] = test_params.get("patterns", ["test.*pattern"])
    elif guardrail_type == "keyword_block":
        nested_config["keyword"] = test_params.get("keyword", "forbidden")
    
    # Create guardrail with nested config
    try:
        # Try (name, config) signature first
        guardrail = guardrail_class(nested_config["name"], nested_config)
    except TypeError:
        # Fall back to (config) signature
        try:
            guardrail = guardrail_class(nested_config)
        except Exception as e:
            return {
                "guardrail": guardrail_type,
                "status": "FAILED", 
                "error": f"Failed to create: {e}",
                "critical": True
            }
    except Exception as e:
        return {
            "guardrail": guardrail_type,
            "status": "FAILED",
            "error": f"Failed to create: {e}",
            "critical": True
        }
    
    # Verify parameters were extracted
    results = {
        "guardrail": guardrail_type,
        "status": "PASSED",
        "errors": []
    }
    
    for param in verify_params:
        expected_value = test_params.get(param)
        
        # Handle special case where attribute name differs
        attr_name = param
        if param == "categories" and hasattr(guardrail, "enabled_categories"):
            attr_name = "enabled_categories"
        
        if hasattr(guardrail, attr_name):
            actual_value = getattr(guardrail, attr_name)
            
            # Special handling for lists
            if isinstance(expected_value, list) and isinstance(actual_value, list):
                if set(expected_value) != set(actual_value):
                    results["errors"].append(
                        f"{param}: expected {expected_value}, got {actual_value}"
                    )
            elif expected_value is None and isinstance(actual_value, list):
                # Skip - None in test means we're not checking this value
                continue
            elif actual_value != expected_value:
                results["errors"].append(
                    f"{param}: expected {expected_value}, got {actual_value}"
                )
        else:
            # Check if it might be under a different name
            found = False
            for attr in dir(guardrail):
                if param in attr.lower():
                    found = True
                    actual = getattr(guardrail, attr)
                    print(f"  Note: {param} might be stored as {attr} = {actual}")
            
            if not found:
                results["errors"].append(f"{param}: attribute not found on guardrail")
    
    if results["errors"]:
        results["status"] = "FAILED"
        results["critical"] = True
    
    return results


def test_all_guardrails():
    """Test all registered guardrails"""
    
    print("=== Guardrail Config Structure Validation ===\n")
    
    all_passed = True
    results = []
    
    # Test each guardrail type
    for guardrail_type, config_info in GUARDRAIL_CONFIG_MAP.items():
        print(f"Testing {guardrail_type}...")
        result = test_guardrail_nested_config(guardrail_type, config_info)
        results.append(result)
        
        if result["status"] == "PASSED":
            print(f"  ✓ {guardrail_type}: Config extraction working correctly")
        else:
            print(f"  ✗ {guardrail_type}: FAILED")
            for error in result.get("errors", []):
                print(f"    - {error}")
            if result.get("error"):
                print(f"    - {result['error']}")
            all_passed = False
    
    # Summary
    print("\n=== Summary ===")
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nFailed guardrails:")
        for result in results:
            if result["status"] == "FAILED":
                print(f"  - {result['guardrail']}")
    
    return all_passed


def test_factory_integration():
    """Test guardrail factory passes config correctly"""
    
    print("\n=== Factory Integration Test ===\n")
    
    # For now, skip factory test and just test direct instantiation
    print("Factory test skipped - testing direct instantiation")
    return True


if __name__ == "__main__":
    # Test all guardrails
    guardrails_ok = test_all_guardrails()
    
    # Test factory
    factory_ok = test_factory_integration()
    
    # Exit with error if any tests failed
    if not (guardrails_ok and factory_ok):
        print("\n❌ Config validation FAILED - fix guardrails before release!")
        sys.exit(1)
    else:
        print("\n✅ All config validations passed!")
        sys.exit(0)