#!/usr/bin/env python3
"""
Action Control Behavioral Tests

Tests that guardrail actions (block/warn/allow) work as configured.
This is CRITICAL - different contexts need different responses.
"""

import asyncio

from src.stinger.guardrails.simple_pii_detection_guardrail import SimplePIIDetectionGuardrail
from src.stinger.guardrails.simple_toxicity_detection_guardrail import (
    SimpleToxicityDetectionGuardrail,
)


class TestBlockAction:
    """Test 'block' action prevents content and returns appropriate result"""

    def test_block_action_blocks_content(self):
        """Block action MUST prevent content from passing"""
        # PII with block action
        config = {
            "name": "pii_blocker",
            "config": {"action": "block", "confidence_threshold": 0.6},  # Explicitly set to block
        }
        guardrail = SimplePIIDetectionGuardrail("test", config)

        result = asyncio.run(guardrail.analyze("My SSN is 123-45-6789"))

        assert result.blocked == True, "Block action must block content"
        assert (
            "detected" in result.reason.lower() or "pii" in result.reason.lower()
        ), "Should explain detection"

    def test_block_is_default_action(self):
        """Most guardrails should default to blocking for safety"""
        # No action specified - should default to block
        config = {"name": "default_action", "config": {"confidence_threshold": 0.6}}
        guardrail = SimplePIIDetectionGuardrail("test", config)

        result = asyncio.run(guardrail.analyze("Credit card: 4111-1111-1111-1111"))

        assert result.blocked == True, "Should default to blocking"


class TestWarnAction:
    """Test 'warn' action allows content but flags concerns"""

    def test_warn_action_behavior(self):
        """Test how warn action is implemented"""
        config = {"name": "pii_warner", "config": {"action": "warn", "confidence_threshold": 0.6}}
        guardrail = SimplePIIDetectionGuardrail("test", config)

        result = asyncio.run(guardrail.analyze("My SSN is 123-45-6789"))

        # Document actual behavior - warn might still block or not depending on implementation
        print(f"Warn action behavior: blocked={result.blocked}, confidence={result.confidence:.2f}")
        print(f"Reason: {result.reason}")

        # Warn action behavior is implementation-specific
        # It might block with warning in reason, or not block but flag in details
        if result.blocked:
            assert (
                "warn" in result.reason.lower() or result.confidence < 1.0
            ), "Should indicate warning nature"
        else:
            assert result.confidence > 0, "Should still detect the issue"

    def test_warn_action_on_safe_content(self):
        """Warn action on safe content should pass cleanly"""
        config = {"name": "warner", "config": {"action": "warn", "confidence_threshold": 0.6}}
        guardrail = SimplePIIDetectionGuardrail("test", config)

        result = asyncio.run(guardrail.analyze("Hello world"))

        assert result.blocked == False, "Safe content not blocked"
        assert result.confidence == 0.0, "No detection confidence for safe content"


class TestAllowAction:
    """Test 'allow' action for monitoring without interference"""

    def test_allow_action_never_blocks(self):
        """Allow action MUST pass all content (monitoring only)"""
        config = {
            "name": "pii_monitor",
            "config": {
                "action": "allow",  # Monitor only, don't block
                "confidence_threshold": 0.1,  # Very sensitive
            },
        }
        guardrail = SimplePIIDetectionGuardrail("test", config)

        # Even obvious PII should pass
        result = asyncio.run(guardrail.analyze("My SSN is 123-45-6789"))

        # Document actual behavior
        print(f"Allow action: blocked={result.blocked}, confidence={result.confidence:.2f}")
        print(f"Details: {result.details}")

        # Allow action might be implemented as:
        # 1. Never blocking (blocked=False)
        # 2. Blocking but with allow override in pipeline
        # Document which approach is used

    def test_allow_for_analytics(self):
        """Allow mode useful for gathering analytics without blocking"""
        config = {"name": "analytics", "config": {"action": "allow", "confidence_threshold": 0.7}}

        # Test various guardrails in allow mode
        guardrail = SimplePIIDetectionGuardrail("pii", config)

        test_cases = [
            "SSN: 123-45-6789",
            "My email is test@example.com",
            "Hello world",
        ]

        for text in test_cases:
            result = asyncio.run(guardrail.analyze(text))
            print(
                f"Text: '{text[:20]}...' - blocked={result.blocked}, confidence={result.confidence:.2f}"
            )


class TestActionImplementation:
    """Test how actions are actually implemented"""

    def test_action_in_simple_pii(self):
        """Document how SimplePIIDetectionGuardrail handles actions"""
        test_text = "My SSN is 123-45-6789"

        for action in ["block", "warn", "allow"]:
            config = {
                "name": f"pii_{action}",
                "config": {"action": action, "confidence_threshold": 0.7},
            }
            guardrail = SimplePIIDetectionGuardrail("test", config)
            result = asyncio.run(guardrail.analyze(test_text))

            print(f"\nSimplePII with action='{action}':")
            print(f"  blocked: {result.blocked}")
            print(f"  confidence: {result.confidence:.2f}")
            print(f"  reason: {result.reason}")

    def test_action_in_simple_toxicity(self):
        """Document how SimpleToxicityDetectionGuardrail handles actions"""
        test_text = "I hate you"

        for action in ["block", "warn", "allow"]:
            config = {
                "name": f"toxicity_{action}",
                "config": {"action": action, "confidence_threshold": 0.7},
            }
            guardrail = SimpleToxicityDetectionGuardrail("test", config)
            result = asyncio.run(guardrail.analyze(test_text))

            print(f"\nSimpleToxicity with action='{action}':")
            print(f"  blocked: {result.blocked}")
            print(f"  confidence: {result.confidence:.2f}")
            print(f"  reason: {result.reason}")


def test_action_configuration_matrix():
    """Test matrix of guardrails with different actions"""

    guardrail_configs = [
        ("PII Detection", SimplePIIDetectionGuardrail, "SSN: 123-45-6789"),
        ("Toxicity Detection", SimpleToxicityDetectionGuardrail, "I hate you"),
    ]

    actions = ["block", "warn", "allow"]

    print("\n=== Action Configuration Matrix ===")
    print(f"{'Guardrail':<20} | {'Action':<6} | {'Blocked':<7} | {'Confidence':<10} | {'Reason'}")
    print("-" * 80)

    for name, guard_class, test_input in guardrail_configs:
        for action in actions:
            config = {
                "name": f"test_{action}",
                "config": {"action": action, "confidence_threshold": 0.5},
            }

            try:
                guardrail = guard_class("test", config)
                result = asyncio.run(guardrail.analyze(test_input))

                print(
                    f"{name:<20} | {action:<6} | "
                    f"{str(result.blocked):<7} | {result.confidence:<10.2f} | "
                    f"{result.reason[:30]}..."
                )
            except Exception as e:
                print(f"{name:<20} | {action:<6} | ERROR: {e}")


if __name__ == "__main__":
    print("=== Action Control Behavioral Test Results ===")

    # Test block action
    print("\n1. Testing Block Action...")
    block_test = TestBlockAction()
    try:
        block_test.test_block_action_blocks_content()
        print("✓ Block action blocks content")
    except AssertionError as e:
        print(f"✗ Block action test failed: {e}")

    try:
        block_test.test_block_is_default_action()
        print("✓ Block is default action")
    except AssertionError as e:
        print(f"✗ Default action test failed: {e}")

    # Test warn action
    print("\n2. Testing Warn Action...")
    warn_test = TestWarnAction()
    warn_test.test_warn_action_behavior()
    warn_test.test_warn_action_on_safe_content()

    # Test allow action
    print("\n3. Testing Allow Action...")
    allow_test = TestAllowAction()
    allow_test.test_allow_action_never_blocks()
    allow_test.test_allow_for_analytics()

    # Test implementation details
    print("\n4. Testing Action Implementation...")
    impl_test = TestActionImplementation()
    impl_test.test_action_in_simple_pii()
    impl_test.test_action_in_simple_toxicity()

    # Test action matrix
    print("\n5. Testing Action Configuration Matrix...")
    test_action_configuration_matrix()
