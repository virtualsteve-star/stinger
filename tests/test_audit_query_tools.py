"""
Tests for audit trail query tools.

Tests the development query and analysis tools.
"""

import os
import sys
import tempfile

import pytest

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import stinger
from stinger.core import audit


class TestAuditQueryTools:
    """Test audit trail query tools."""

    def setup_method(self):
        """Setup for each test."""
        # Disable audit trail before each test
        if audit.is_enabled():
            try:
                audit.disable()
            except RuntimeError:
                # Can't disable in production - reset the global instance
                audit._audit_trail = audit.AuditTrail()

    def test_query_by_conversation_id(self):
        """Test querying audit trail by conversation ID."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "audit.log")

            # Enable audit trail
            audit.enable(audit_file)

            # Log some events with different conversation IDs
            audit.log_prompt("Hello from conv1", user_id="user1", conversation_id="conv_123")
            audit.log_prompt("Hello from conv2", user_id="user2", conversation_id="conv_456")
            audit.log_response("Response from conv1", user_id="user1", conversation_id="conv_123")

            audit.disable()

            # Query for specific conversation
            results = audit.query(conversation_id="conv_123", destination=audit_file)

            # Should find 2 events for conv_123
            assert len(results) == 2

            # All results should be for conv_123
            for result in results:
                assert result["conversation_id"] == "conv_123"

            # Should have prompt and response
            event_types = [r["event_type"] for r in results]
            assert "user_prompt" in event_types
            assert "llm_response" in event_types

    def test_query_by_user_id(self):
        """Test querying audit trail by user ID."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "audit.log")

            # Enable audit trail
            audit.enable(audit_file)

            # Log some events with different user IDs
            audit.log_prompt("Hello from user1", user_id="user_123", conversation_id="conv1")
            audit.log_prompt("Hello from user2", user_id="user_456", conversation_id="conv2")
            audit.log_response("Response to user1", user_id="user_123", conversation_id="conv1")

            audit.disable()

            # Query for specific user
            results = audit.query(user_id="user_123", destination=audit_file)

            # Should find 2 events for user_123
            assert len(results) == 2

            # All results should be for user_123
            for result in results:
                assert result["user_id"] == "user_123"

    def test_query_by_event_type(self):
        """Test querying audit trail by event type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "audit.log")

            # Enable audit trail
            audit.enable(audit_file)

            # Log different types of events
            audit.log_prompt("Test prompt", user_id="user1", conversation_id="conv1")
            audit.log_response("Test response", user_id="user1", conversation_id="conv1")
            audit.log_guardrail_decision(
                "test_filter", "allow", "Test reason", user_id="user1", conversation_id="conv1"
            )

            audit.disable()

            # Query for prompts only
            prompt_results = audit.query(event_type="user_prompt", destination=audit_file)
            assert len(prompt_results) == 1
            assert prompt_results[0]["event_type"] == "user_prompt"

            # Query for guardrail decisions only
            decision_results = audit.query(event_type="guardrail_decision", destination=audit_file)
            assert len(decision_results) == 1
            assert decision_results[0]["event_type"] == "guardrail_decision"

    def test_query_nonexistent_file(self):
        """Test querying non-existent audit file."""
        results = audit.query(destination="/nonexistent/audit.log")
        assert results == []

    def test_print_query_results(self):
        """Test printing query results in human-readable format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "audit.log")

            # Enable audit trail
            audit.enable(audit_file)

            # Log some events
            audit.log_prompt("What is AI?", user_id="user_123", conversation_id="conv_456")
            audit.log_guardrail_decision(
                "content_filter",
                "allow",
                "Content is safe",
                user_id="user_123",
                conversation_id="conv_456",
            )
            audit.log_response(
                "AI is artificial intelligence.", user_id="user_123", conversation_id="conv_456"
            )

            audit.disable()

            # Query and print results
            results = audit.query(conversation_id="conv_456", destination=audit_file)

            # Should be able to print without errors
            import contextlib
            import io

            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                audit.print_query_results(results)

            output = f.getvalue()

            # Check that output contains expected information
            assert "Found 3 matching audit records" in output
            assert "user_prompt" in output
            assert "guardrail_decision" in output
            assert "llm_response" in output
            assert "What is AI?" in output
            assert "AI is artificial intelligence." in output

    def test_print_query_results_empty(self):
        """Test printing empty query results."""
        import contextlib
        import io

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            audit.print_query_results([])

        output = f.getvalue()
        assert "No matching audit records found" in output

    def test_pipeline_integration_with_query(self):
        """Test end-to-end pipeline integration with query tools."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = os.path.join(temp_dir, "audit.log")

            # Enable audit trail
            audit.enable(audit_file)

            # Create pipeline and conversation
            pipeline = stinger.create_pipeline()
            conversation = stinger.Conversation(
                "test_user", "assistant", conversation_id="test_conv"
            )

            # Process some content through pipeline
            input_result = pipeline.check_input(
                "Hello, can you help me?", conversation=conversation
            )
            output_result = pipeline.check_output(
                "Of course! I'm here to help.", conversation=conversation
            )

            audit.disable()

            # Query the audit trail
            all_events = audit.query(conversation_id="test_conv", destination=audit_file)
            prompt_events = audit.query(event_type="user_prompt", destination=audit_file)
            response_events = audit.query(event_type="llm_response", destination=audit_file)
            decision_events = audit.query(event_type="guardrail_decision", destination=audit_file)

            # Should have multiple events
            assert len(all_events) >= 4  # prompt + decisions + response + more decisions
            assert len(prompt_events) == 1
            assert len(response_events) == 1
            assert len(decision_events) >= 2  # At least input and output guardrails

            # Check event content
            prompt_event = prompt_events[0]
            assert prompt_event["prompt"] == "Hello, can you help me?"
            assert prompt_event["user_id"] == "test_user"
            assert prompt_event["conversation_id"] == "test_conv"

            response_event = response_events[0]
            assert response_event["response"] == "Of course! I'm here to help."
            assert response_event["user_id"] == "test_user"
            assert response_event["conversation_id"] == "test_conv"


if __name__ == "__main__":
    pytest.main([__file__])
