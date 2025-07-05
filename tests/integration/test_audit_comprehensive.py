import pytest

"""
Comprehensive end-to-end tests for security audit trail system.

This test validates all major requirements from the test plan.
"""

import json
import os
import sys
import tempfile

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import stinger
from stinger.core import audit
from stinger.core.conversation import Conversation


@pytest.mark.efficacy
def test_comprehensive_security_audit_trail():
    """Comprehensive test of the complete security audit trail system."""
    with tempfile.TemporaryDirectory() as temp_dir:
        audit_file = os.path.join(temp_dir, "comprehensive_audit.log")

        # 1. Test zero-config enable
        audit.enable()
        assert audit.is_enabled() == True
        audit.disable()

        # 2. Test easy destination configuration
        audit.enable(audit_file, redact_pii=True)
        assert audit.is_enabled() == True

        # 3. Create pipeline and conversation for complete flow testing
        pipeline = stinger.create_pipeline()
        conversation = Conversation(
            "forensic_user", "ai_assistant", conversation_id="forensic_conv"
        )

        # 4. Test complete conversation flow with all security events

        # Input 1: Normal prompt
        input_result1 = pipeline.check_input("What is machine learning?", conversation=conversation)
        assert input_result1 is not None

        # Output 1: Normal response
        output_result1 = pipeline.check_output(
            "Machine learning is a subset of AI that enables computers to learn.",
            conversation=conversation,
        )
        assert output_result1 is not None

        # Input 2: Prompt with PII (should be redacted)
        input_result2 = pipeline.check_input(
            "My email is john@company.com, can you help?", conversation=conversation
        )
        assert input_result2 is not None

        # Output 2: Response
        output_result2 = pipeline.check_output(
            "I can help, but I won't store your email.", conversation=conversation
        )
        assert output_result2 is not None

        # 5. Disable audit and analyze the complete trail
        audit.disable()

        # Read all audit records
        with open(audit_file, "r") as f:
            lines = f.readlines()

        # Should have substantial number of events
        assert (
            len(lines) >= 8
        )  # enable + prompt + decisions + response + prompt + decisions + response

        # Parse all records
        records = [json.loads(line) for line in lines]

        # 6. Validate audit trail completeness

        # Check for audit trail enabled event
        enable_events = [r for r in records if r["event_type"] == "audit_trail_enabled"]
        assert len(enable_events) == 1
        assert enable_events[0]["redact_pii"] == True

        # Check for user prompts (2 expected)
        prompt_events = [r for r in records if r["event_type"] == "user_prompt"]
        assert len(prompt_events) == 2

        # Validate first prompt
        prompt1 = prompt_events[0]
        assert prompt1["prompt"] == "What is machine learning?"
        assert prompt1["user_id"] == "forensic_user"
        assert prompt1["conversation_id"] == "forensic_conv"
        assert "timestamp" in prompt1

        # Validate second prompt has PII redacted
        prompt2 = prompt_events[1]
        assert "[EMAIL_REDACTED]" in prompt2["prompt"]
        assert "john@company.com" not in prompt2["prompt"]
        assert prompt2["user_id"] == "forensic_user"
        assert prompt2["conversation_id"] == "forensic_conv"

        # Check for LLM responses (2 expected)
        response_events = [r for r in records if r["event_type"] == "llm_response"]
        assert len(response_events) == 2

        # Validate responses
        response1 = response_events[0]
        assert "Machine learning" in response1["response"]
        assert response1["user_id"] == "forensic_user"
        assert response1["conversation_id"] == "forensic_conv"

        response2 = response_events[1]
        assert "help" in response2["response"]
        assert response2["user_id"] == "forensic_user"
        assert response2["conversation_id"] == "forensic_conv"

        # Check for guardrail decisions (should have multiple)
        decision_events = [r for r in records if r["event_type"] == "guardrail_decision"]
        assert len(decision_events) >= 4  # At least 2 input + 2 output guardrails

        # Validate guardrail decision format
        for decision in decision_events:
            assert "guardrail_name" in decision
            assert "decision" in decision
            assert decision["decision"] in ["block", "allow", "warn", "error"]
            assert "reason" in decision
            assert "user_id" in decision
            assert "conversation_id" in decision
            assert decision["user_id"] == "forensic_user"
            assert decision["conversation_id"] == "forensic_conv"

        # 7. Test forensic analysis capabilities using query tools

        # Query by conversation ID
        conv_events = audit.query(conversation_id="forensic_conv", destination=audit_file)
        conversation_specific = [
            e for e in conv_events if e.get("conversation_id") == "forensic_conv"
        ]
        assert len(conversation_specific) >= 6  # 2 prompts + 2 responses + 4+ decisions

        # Query by user ID
        user_events = audit.query(user_id="forensic_user", destination=audit_file)
        user_specific = [e for e in user_events if e.get("user_id") == "forensic_user"]
        assert len(user_specific) >= 6

        # Query by event type
        prompt_query = audit.query(event_type="user_prompt", destination=audit_file)
        assert len(prompt_query) == 2

        response_query = audit.query(event_type="llm_response", destination=audit_file)
        assert len(response_query) == 2

        decision_query = audit.query(event_type="guardrail_decision", destination=audit_file)
        assert len(decision_query) >= 4

        # 8. Validate timeline consistency (all events should be in chronological order)
        timestamps = [r["timestamp"] for r in records[1:]]  # Skip enable event
        for i in range(1, len(timestamps)):
            assert timestamps[i] >= timestamps[i - 1], "Events should be in chronological order"

        # 9. Validate conversation flow reconstruction
        conv_events_sorted = sorted(conversation_specific, key=lambda x: x["timestamp"])

        # Should be able to reconstruct: prompt1 -> decisions -> response1 -> prompt2 -> decisions -> response2
        event_types = [e["event_type"] for e in conv_events_sorted]

        # Should start with prompt
        assert event_types[0] == "user_prompt"

        # Should contain both prompts and responses
        assert event_types.count("user_prompt") == 2
        assert event_types.count("llm_response") == 2
        assert event_types.count("guardrail_decision") >= 4

        # 10. Validate all required fields are present
        required_fields = ["timestamp", "event_type"]
        for record in records:
            for field in required_fields:
                assert field in record, f"Required field {field} missing from record"

        # Validate conversation context fields for conversation events
        conv_specific_records = [r for r in records if r.get("conversation_id") == "forensic_conv"]
        for record in conv_specific_records:
            assert record["user_id"] == "forensic_user"
            assert record["conversation_id"] == "forensic_conv"

        print(f"✅ Comprehensive test passed! Analyzed {len(records)} audit records")
        print(f"   - {len(prompt_events)} user prompts logged")
        print(f"   - {len(response_events)} LLM responses logged")
        print(f"   - {len(decision_events)} guardrail decisions logged")
        print(f"   - Complete conversation flow reconstructed")
        print(f"   - PII redaction working correctly")
        print(f"   - Forensic query tools working correctly")


@pytest.mark.performance
def test_performance_requirements():
    """Test that audit trail meets performance requirements."""
    with tempfile.TemporaryDirectory() as temp_dir:
        audit_file = os.path.join(temp_dir, "performance_audit.log")

        # Enable audit trail
        audit.enable(audit_file)

        # Create pipeline
        pipeline = stinger.create_pipeline()

        import time

        # Test multiple operations to ensure performance
        start_time = time.time()

        for i in range(10):  # Test with multiple operations
            conversation = Conversation(f"user_{i}", "assistant", conversation_id=f"conv_{i}")

            # Test input and output processing
            input_result = pipeline.check_input(f"Test message {i}", conversation=conversation)
            output_result = pipeline.check_output(f"Test response {i}", conversation=conversation)

            assert input_result is not None
            assert output_result is not None

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete 20 operations (10 input + 10 output) reasonably quickly
        # Each operation should add minimal overhead
        assert total_time < 5.0, f"Performance test took too long: {total_time}s"

        audit.disable()

        # Verify all events were logged
        with open(audit_file, "r") as f:
            lines = f.readlines()

        # Should have logged many events
        assert len(lines) >= 30  # enable + 10 prompts + 10 responses + guardrail decisions

        print(f"✅ Performance test passed! Processed 20 operations in {total_time:.2f}s")


if __name__ == "__main__":
    # Run the comprehensive test
    test_comprehensive_security_audit_trail()
    test_performance_requirements()
    print("\n🎉 All comprehensive tests passed! Security audit trail is ready for production.")
