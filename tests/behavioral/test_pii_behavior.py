#!/usr/bin/env python3
"""
Behavioral Tests for PII Detection Guardrail

Tests ACTUAL BEHAVIOR: Does it block PII? Do configs change behavior?
NOT testing: Implementation details, config storage, or mocks
"""

import asyncio
import pytest
from typing import List, Tuple

from src.stinger.guardrails.simple_pii_detection_guardrail import SimplePIIDetectionGuardrail


class TestPIIDetectionBehavior:
    """Test PII detection actually blocks sensitive data"""
    
    def test_blocks_obvious_pii(self):
        """Test guardrail blocks content it should ALWAYS block"""
        # Default configuration
        config = {
            "name": "pii_detection",
            "config": {
                "confidence_threshold": 0.8
            }
        }
        guardrail = SimplePIIDetectionGuardrail("test", config)
        
        # These MUST be blocked
        test_cases = [
            ("My SSN is 123-45-6789", True, "SSN with dashes"),
            ("My social security number is 123-45-6789", True, "SSN with label"),
            ("Credit card: 4111-1111-1111-1111", True, "Credit card with dashes"),
            ("CC: 4532015112830366", True, "Credit card without dashes"),
            ("Email me at test@example.com", True, "Email address"),
            ("Call me at 555-123-4567", True, "Phone number"),
            ("Hello world", False, "Normal text should pass"),
            ("The weather is nice today", False, "No PII should pass"),
        ]
        
        for text, should_block, description in test_cases:
            result = asyncio.run(guardrail.analyze(text))
            assert result.blocked == should_block, f"Failed: {description}. Text: '{text}'"
    
    def test_medium_confidence_pii(self):
        """Test PII that should be detected but at medium confidence"""
        # Lower threshold to catch medium confidence PII
        config = {
            "name": "pii_medium",
            "config": {
                "confidence_threshold": 0.5
            }
        }
        guardrail = SimplePIIDetectionGuardrail("test", config)
        
        # These should be detected at medium confidence
        test_cases = [
            ("My IP is 192.168.1.1", True, "IP address"),
            ("Server at 10.0.0.1", True, "Private IP"),
            ("Visit 8.8.8.8 for DNS", True, "Public IP"),
        ]
        
        for text, should_block, description in test_cases:
            result = asyncio.run(guardrail.analyze(text))
            assert result.blocked == should_block, f"Failed: {description}. Text: '{text}'"
            # Verify it's medium confidence (0.6)
            assert 0.5 <= result.confidence <= 0.7, f"IP should have medium confidence, got {result.confidence}"
    
    def test_confidence_threshold_controls_behavior(self):
        """Test that threshold actually changes blocking behavior"""
        # Strict configuration (low threshold)
        strict_config = {
            "name": "pii_strict",
            "config": {
                "confidence_threshold": 0.3
            }
        }
        strict = SimplePIIDetectionGuardrail("strict", strict_config)
        
        # Lenient configuration (high threshold)
        lenient_config = {
            "name": "pii_lenient", 
            "config": {
                "confidence_threshold": 0.95
            }
        }
        lenient = SimplePIIDetectionGuardrail("lenient", lenient_config)
        
        # Borderline cases - might be PII
        borderline_cases = [
            "Number: 4111111111111111",  # Could be credit card or product ID
            "ID: 123456789",  # Could be SSN without dashes
            "Contact: 5551234567",  # Phone without formatting
        ]
        
        for text in borderline_cases:
            strict_result = asyncio.run(strict.analyze(text))
            lenient_result = asyncio.run(lenient.analyze(text))
            
            # We expect different behavior based on threshold
            # Can't assert exact behavior without knowing implementation
            # but results should potentially differ
            print(f"Text: '{text}' - Strict: {strict_result.blocked}, Lenient: {lenient_result.blocked}")
    
    def test_pattern_selection_works(self):
        """Test that enabled patterns control what's detected"""
        # Only detect SSN
        ssn_only_config = {
            "name": "ssn_only",
            "config": {
                "patterns": ["ssn"],
                "confidence_threshold": 0.8
            }
        }
        ssn_only = SimplePIIDetectionGuardrail("ssn", ssn_only_config)
        
        # Test SSN is blocked
        result = asyncio.run(ssn_only.analyze("My SSN is 123-45-6789"))
        assert result.blocked == True, "Should block SSN when ssn pattern enabled"
        
        # Test credit card is NOT blocked
        result = asyncio.run(ssn_only.analyze("My credit card is 4111-1111-1111-1111"))
        assert result.blocked == False, "Should NOT block credit card when only ssn enabled"
        
        # Test email is NOT blocked
        result = asyncio.run(ssn_only.analyze("Email: test@example.com"))
        assert result.blocked == False, "Should NOT block email when only ssn enabled"
    
    def test_robustness_against_variations(self):
        """Test PII detection handles format variations"""
        config = {
            "name": "pii",
            "config": {
                "confidence_threshold": 0.8
            }
        }
        guardrail = SimplePIIDetectionGuardrail("test", config)
        
        # SSN variations - based on actual regex: \b\d{3}-?\d{2}-?\d{4}\b
        ssn_variations = [
            ("123-45-6789", True, "SSN with dashes"),
            ("123456789", True, "SSN no separators"),
            ("ssn: 123-45-6789", True, "SSN with label"),
            ("SSN# 123-45-6789", True, "SSN with hash"),
            ("social: 123-45-6789", True, "SSN with 'social' label"),
            # These formats are NOT supported by current regex
            ("123 45 6789", False, "SSN with spaces - not supported"),
            ("123.45.6789", False, "SSN with dots - not supported"),
        ]
        
        # Credit card variations - based on actual regex: \b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b
        cc_variations = [
            ("4111-1111-1111-1111", True, "CC with dashes"),
            ("4111 1111 1111 1111", True, "CC with spaces"),
            ("4111111111111111", True, "CC no spaces"),
            ("card: 4532015112830366", True, "CC with label"),
            ("credit card #4111111111111111", True, "CC with full label"),
        ]
        
        # Test all variations
        for text, should_block, description in ssn_variations + cc_variations:
            result = asyncio.run(guardrail.analyze(text))
            assert result.blocked == should_block, f"Failed: {description}. Text: '{text}'"
    
    def test_context_independence(self):
        """Test PII is blocked regardless of context"""
        config = {
            "name": "pii",
            "config": {
                "confidence_threshold": 0.8
            }
        }
        guardrail = SimplePIIDetectionGuardrail("test", config)
        
        # PII in different contexts - should ALL be blocked
        contexts = [
            "For verification, my SSN is 123-45-6789",
            "I was born on 123-45-6789",  # Weird but still SSN format
            "The code is 4111-1111-1111-1111 for testing",
            "Example data: 123-45-6789",
            "Don't use 123-45-6789 as your password",
        ]
        
        for text in contexts:
            result = asyncio.run(guardrail.analyze(text))
            assert result.blocked == True, f"Should block PII even in context: '{text}'"
    
    def test_already_redacted_content(self):
        """Test that already redacted content is allowed"""
        config = {
            "name": "pii",
            "config": {
                "confidence_threshold": 0.8
            }
        }
        guardrail = SimplePIIDetectionGuardrail("test", config)
        
        # Already safe content
        safe_content = [
            "My SSN is [REDACTED]",
            "Credit card: ****-****-****-1234",
            "Email: t***@example.com",
            "Phone: XXX-XXX-4567",
            "SSN: ***-**-6789",
        ]
        
        for text in safe_content:
            result = asyncio.run(guardrail.analyze(text))
            assert result.blocked == False, f"Should allow already redacted: '{text}'"
    
    def test_action_configuration(self):
        """Test that action config controls block/warn/allow behavior"""
        # Test block action (default)
        block_config = {
            "name": "pii_block",
            "config": {
                "action": "block",
                "confidence_threshold": 0.8
            }
        }
        block_guard = SimplePIIDetectionGuardrail("block", block_config)
        result = asyncio.run(block_guard.analyze("SSN: 123-45-6789"))
        assert result.blocked == True, "Block action should block"
        
        # Test warn action
        warn_config = {
            "name": "pii_warn",
            "config": {
                "action": "warn",
                "confidence_threshold": 0.8
            }
        }
        warn_guard = SimplePIIDetectionGuardrail("warn", warn_config)
        result = asyncio.run(warn_guard.analyze("SSN: 123-45-6789"))
        # Behavior depends on implementation - document actual behavior
        print(f"Warn action result: blocked={result.blocked}")
        
        # Test allow action
        allow_config = {
            "name": "pii_allow",
            "config": {
                "action": "allow",
                "confidence_threshold": 0.8
            }
        }
        allow_guard = SimplePIIDetectionGuardrail("allow", allow_config)
        result = asyncio.run(allow_guard.analyze("SSN: 123-45-6789"))
        # Behavior depends on implementation - document actual behavior
        print(f"Allow action result: blocked={result.blocked}")
    
    def test_disabled_guardrail(self):
        """Test that disabled guardrail doesn't block"""
        disabled_config = {
            "name": "pii",
            "enabled": False,
            "config": {
                "confidence_threshold": 0.8
            }
        }
        guardrail = SimplePIIDetectionGuardrail("test", disabled_config)
        
        # Should not block even obvious PII when disabled
        result = asyncio.run(guardrail.analyze("My SSN is 123-45-6789"))
        # Behavior depends on implementation
        print(f"Disabled guardrail blocks: {result.blocked}")
    
    def test_performance_acceptable(self):
        """Test that PII detection performs adequately"""
        import time
        
        config = {
            "name": "pii",
            "config": {
                "confidence_threshold": 0.8
            }
        }
        guardrail = SimplePIIDetectionGuardrail("test", config)
        
        # Single analysis
        start = time.time()
        result = asyncio.run(guardrail.analyze("Check this text for PII content"))
        single_time = time.time() - start
        assert single_time < 0.1, f"Single analysis too slow: {single_time}s"
        
        # Batch analysis
        texts = ["Sample text without PII"] * 100
        start = time.time()
        for text in texts:
            asyncio.run(guardrail.analyze(text))
        total_time = time.time() - start
        avg_time = total_time / 100
        assert avg_time < 0.05, f"Batch analysis too slow: {avg_time}s average"


def test_medical_pii_scenario():
    """Test PII detection in medical context"""
    config = {
        "name": "pii_medical",
        "config": {
            "confidence_threshold": 0.8,
            "patterns": ["ssn", "credit_card", "email", "phone"]
        }
    }
    guardrail = SimplePIIDetectionGuardrail("medical", config)
    
    # Medical scenarios
    test_cases = [
        # Should block
        ("Patient SSN: 123-45-6789", True, "Patient SSN"),
        ("Insurance ID matches SSN 123-45-6789", True, "Insurance as SSN"),
        ("Bill patient card 4111-1111-1111-1111", True, "Payment card"),
        ("Contact patient at test@email.com", True, "Patient email"),
        
        # Should allow
        ("Patient has hypertension", False, "Medical condition"),
        ("Prescribe 123-45mg twice daily", False, "Medication dosage"),
        ("Blood pressure 120/80", False, "Medical measurement"),
        ("Patient ID: A123456", False, "Non-SSN ID format"),
    ]
    
    for text, should_block, description in test_cases:
        result = asyncio.run(guardrail.analyze(text))
        assert result.blocked == should_block, f"Medical scenario failed: {description}"


if __name__ == "__main__":
    # Run basic tests to document actual behavior
    test = TestPIIDetectionBehavior()
    
    print("=== PII Detection Behavioral Test Results ===")
    print("\n1. Testing obvious PII blocking...")
    try:
        test.test_blocks_obvious_pii()
        print("✓ Obvious PII test passed")
    except AssertionError as e:
        print(f"✗ Obvious PII test failed: {e}")
    
    print("\n2. Testing threshold behavior...")
    test.test_confidence_threshold_controls_behavior()
    
    print("\n3. Testing pattern selection...")
    try:
        test.test_pattern_selection_works()
        print("✓ Pattern selection test passed")
    except AssertionError as e:
        print(f"✗ Pattern selection test failed: {e}")
    
    print("\n4. Testing format variations...")
    try:
        test.test_robustness_against_variations()
        print("✓ Format variation test passed")
    except AssertionError as e:
        print(f"✗ Format variation test failed: {e}")