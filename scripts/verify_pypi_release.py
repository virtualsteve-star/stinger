#!/usr/bin/env python3
"""
Comprehensive verification script for PyPI releases.
Tests all major functionality after pip installation.
"""

import subprocess
import sys
import tempfile
import os
import json
from pathlib import Path


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def run_test(test_name, test_func):
    """Run a single test and report results."""
    print(f"\n{Colors.YELLOW}Testing: {test_name}{Colors.NC}")
    try:
        result, message = test_func()
        if result:
            print(f"{Colors.GREEN}✅ {message}{Colors.NC}")
            return True
        else:
            print(f"{Colors.RED}❌ {message}{Colors.NC}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Exception: {str(e)}{Colors.NC}")
        return False


def test_cli_commands():
    """Test all CLI commands."""
    commands = [
        ("stinger --version", "Version check"),
        ("stinger --help", "Help command"),
        ("stinger health", "Health check"),
        ("stinger check-prompt 'Hello world'", "Check prompt command"),
        ("stinger check-response 'Safe response'", "Check response command"),
        # Note: Can't test demo as it's interactive
    ]
    
    all_passed = True
    for cmd, desc in commands:
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ {desc}: {cmd}")
            else:
                print(f"  ❌ {desc}: {cmd}")
                print(f"     Error: {result.stderr}")
                all_passed = False
        except Exception as e:
            print(f"  ❌ {desc}: {cmd} - {str(e)}")
            all_passed = False
    
    return all_passed, "CLI commands test completed"


def test_presets():
    """Test all available presets."""
    from stinger import GuardrailPipeline
    
    presets = ['basic', 'customer_service', 'medical', 'educational', 'financial', 'content_moderation']
    all_passed = True
    
    for preset in presets:
        try:
            pipeline = GuardrailPipeline.from_preset(preset)
            print(f"  ✅ Preset '{preset}' loads successfully")
        except Exception as e:
            print(f"  ❌ Preset '{preset}' failed: {str(e)}")
            all_passed = False
    
    return all_passed, f"Tested {len(presets)} presets"


def test_guardrail_functionality():
    """Test actual guardrail functionality."""
    from stinger import GuardrailPipeline
    
    pipeline = GuardrailPipeline.from_preset('customer_service')
    
    # Test both INPUT and OUTPUT guardrails with positive/negative cases
    input_test_cases = [
        # Negative cases (should block)
        ("My SSN is 123-45-6789", True, "Input: PII detection (SSN)"),
        ("My email is test@example.com", True, "Input: PII detection (email)"),
        ("Call me at 555-123-4567", True, "Input: PII detection (phone)"),
        # Positive cases (should pass)
        ("Hello, how can I help?", False, "Input: Safe greeting"),
        ("I need help with my order", False, "Input: Normal request"),
        ("What are your business hours?", False, "Input: Safe question"),
    ]
    
    output_test_cases = [
        # Negative cases (should block)
        ("Your SSN 123-45-6789 is on file", True, "Output: PII leak (SSN)"),
        ("Here's the code: import os; os.system('rm -rf /')", True, "Output: Code generation"),
        # Positive cases (should pass)  
        ("Thank you for contacting support", False, "Output: Safe response"),
        ("Our business hours are 9-5 EST", False, "Output: Normal information"),
    ]
    
    all_passed = True
    
    # Test input guardrails
    print("  Testing INPUT guardrails:")
    for content, should_block, desc in input_test_cases:
        result = pipeline.check_input(content)
        if result['blocked'] == should_block:
            print(f"    ✅ {desc}: {'Blocked' if should_block else 'Passed'} as expected")
        else:
            print(f"    ❌ {desc}: Expected {'blocked' if should_block else 'passed'}, got {'blocked' if result['blocked'] else 'passed'}")
            if result.get('reasons'):
                print(f"       Reasons: {result['reasons']}")
            all_passed = False
    
    # Test output guardrails
    print("  Testing OUTPUT guardrails:")
    for content, should_block, desc in output_test_cases:
        result = pipeline.check_output(content)
        if result['blocked'] == should_block:
            print(f"    ✅ {desc}: {'Blocked' if should_block else 'Passed'} as expected")
        else:
            print(f"    ❌ {desc}: Expected {'blocked' if should_block else 'passed'}, got {'blocked' if result['blocked'] else 'passed'}")
            if result.get('reasons'):
                print(f"       Reasons: {result['reasons']}")
            all_passed = False
    
    return all_passed, "Input/Output guardrail tests completed"


def test_conversation_api():
    """Test conversation API."""
    from stinger import Conversation
    
    try:
        conv = Conversation.human_ai("test_user", "assistant")
        conv.add_exchange("Hello", "Hi there!")
        conv.add_exchange("How are you?", "I'm doing well!")
        
        history = conv.get_history()
        if len(history) == 2:
            print(f"  ✅ Conversation tracking works: {len(history)} exchanges")
            return True, "Conversation API functional"
        else:
            return False, f"Expected 2 exchanges, got {len(history)}"
    except Exception as e:
        return False, f"Conversation API error: {str(e)}"


def test_audit_trail():
    """Test audit trail functionality."""
    from stinger import audit
    
    try:
        # Enable audit trail
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            audit_file = f.name
        
        audit.enable(audit_file)
        audit.log_prompt("Test prompt", user_id="test_user")
        audit.disable()
        
        # Check if file was created and has content
        if os.path.exists(audit_file) and os.path.getsize(audit_file) > 0:
            os.unlink(audit_file)
            return True, "Audit trail logging works"
        else:
            return False, "Audit trail file not created or empty"
    except Exception as e:
        return False, f"Audit trail error: {str(e)}"


def test_yaml_config():
    """Test YAML configuration loading."""
    from stinger import GuardrailPipeline
    
    # Create a temporary config file
    config_content = """
version: "1.0"
pipeline:
  input:
    - name: pii_check
      type: simple_pii_detection
      enabled: true
      on_error: block
  output:
    - name: toxicity_check
      type: simple_toxicity_detection
      enabled: true
      on_error: block
"""
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            config_file = f.name
        
        pipeline = GuardrailPipeline(config_file)
        os.unlink(config_file)
        
        return True, "YAML configuration loading works"
    except Exception as e:
        return False, f"YAML config error: {str(e)}"


def test_package_data():
    """Test that package data files are included."""
    import stinger
    import os
    
    package_dir = os.path.dirname(stinger.__file__)
    
    # Check for important data files
    data_checks = [
        ('data', 'Data directory'),
        ('guardrails/configs', 'Guardrail configs'),
    ]
    
    all_found = True
    for subdir, desc in data_checks:
        path = os.path.join(package_dir, subdir)
        if os.path.exists(path):
            print(f"  ✅ {desc} found: {subdir}")
        else:
            print(f"  ❌ {desc} missing: {subdir}")
            all_found = False
    
    return all_found, "Package data verification completed"


def main():
    """Run all verification tests."""
    print(f"{Colors.BLUE}🧪 Stinger PyPI Release Verification{Colors.NC}")
    print("=" * 40)
    
    # Check if package is installed
    try:
        import stinger
        print(f"\n{Colors.GREEN}✅ Package installed: stinger-guardrails-alpha{Colors.NC}")
        print(f"   Version: {stinger.__version__}")
    except ImportError:
        print(f"\n{Colors.RED}❌ Package not installed!{Colors.NC}")
        print("   Run: pip install stinger-guardrails-alpha")
        sys.exit(1)
    
    # Run all tests
    tests = [
        ("CLI Commands", test_cli_commands),
        ("Preset Loading", test_presets),
        ("Guardrail Functionality", test_guardrail_functionality),
        ("Conversation API", test_conversation_api),
        ("Audit Trail", test_audit_trail),
        ("YAML Configuration", test_yaml_config),
        ("Package Data Files", test_package_data),
    ]
    
    results = []
    for test_name, test_func in tests:
        passed = run_test(test_name, test_func)
        results.append((test_name, passed))
    
    # Summary
    print(f"\n{Colors.BLUE}========== Test Summary =========={Colors.NC}")
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = f"{Colors.GREEN}PASSED{Colors.NC}" if passed else f"{Colors.RED}FAILED{Colors.NC}"
        print(f"{test_name}: {status}")
    
    print(f"\n{Colors.BLUE}Total: {passed_count}/{total_count} tests passed{Colors.NC}")
    
    if passed_count == total_count:
        print(f"{Colors.GREEN}🎉 All tests passed! Release verified.{Colors.NC}")
        return 0
    else:
        print(f"{Colors.RED}❌ Some tests failed. Please investigate.{Colors.NC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())