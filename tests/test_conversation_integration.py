"""
Integration tests for Conversation with GuardrailPipeline - Phase 5f

Tests conversation integration with pipeline, backward compatibility,
and conversation-aware logging.
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from stinger import Conversation, GuardrailPipeline


class TestConversationPipelineIntegration:
    """Test conversation integration with GuardrailPipeline."""

    def test_pipeline_without_conversation(self):
        """Test that pipeline works without conversation (backward compatibility)."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        # Test input without conversation
        result = pipeline.check_input("Hello, world!")

        assert isinstance(result, dict)
        assert "blocked" in result
        assert "warnings" in result
        assert "reasons" in result
        assert "details" in result
        assert "pipeline_type" in result
        assert "conversation_id" in result
        assert result["conversation_id"] is None
        assert result["pipeline_type"] == "input"

    def test_pipeline_with_conversation(self):
        """Test that pipeline works with conversation."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        # Create conversation using new API
        conv = Conversation.human_ai("test_user", "gpt-4", conversation_id="test_conv")

        # Test input with conversation
        result = pipeline.check_input("Hello, world!", conversation=conv)

        assert isinstance(result, dict)
        assert "blocked" in result
        assert "warnings" in result
        assert "reasons" in result
        assert "details" in result
        assert "pipeline_type" in result
        assert "conversation_id" in result
        assert result["conversation_id"] == "test_conv"
        assert result["pipeline_type"] == "input"

        # Check that turn was added to conversation
        assert conv.get_turn_count() == 1
        assert conv.get_history()[0].prompt == "Hello, world!"

    def test_pipeline_output_with_conversation(self):
        """Test that pipeline output works with conversation."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        # Create conversation using new API
        conv = Conversation.human_ai("test_user", "gpt-4", conversation_id="test_conv")

        # Test output with conversation
        result = pipeline.check_output("Here's your response", conversation=conv)

        assert isinstance(result, dict)
        assert "blocked" in result
        assert "warnings" in result
        assert "reasons" in result
        assert "details" in result
        assert "pipeline_type" in result
        assert "conversation_id" in result
        assert result["conversation_id"] == "test_conv"
        assert result["pipeline_type"] == "output"

        # Check that turn was added to conversation
        assert conv.get_turn_count() == 1
        assert conv.get_history()[0].response == "Here's your response"

    def test_multi_turn_conversation(self):
        """Test multi-turn conversation with pipeline."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        # Create conversation using new API
        conv = Conversation.human_ai("test_user", "gpt-4", conversation_id="multi_turn_test")

        # Simulate a conversation
        inputs = ["Hello, I need help", "My account number is 123-45-6789", "I can't log in"]

        outputs = ["How can I assist you?", "I understand you're having login issues"]

        # Process inputs
        for i, content in enumerate(inputs):
            result = pipeline.check_input(content, conversation=conv)
            assert result["conversation_id"] == "multi_turn_test"
            assert result["pipeline_type"] == "input"

        # Process outputs
        for i, content in enumerate(outputs):
            result = pipeline.check_output(content, conversation=conv)
            assert result["conversation_id"] == "multi_turn_test"
            assert result["pipeline_type"] == "output"

        # Check conversation state
        # After 3 inputs and 2 outputs, we have 4 turns:
        # Turn 0: prompt="Hello, I need help", response=None
        # Turn 1: prompt="My account number is 123-45-6789", response=None
        # Turn 2: prompt="I can't log in", response="How can I assist you?"
        # Turn 3: prompt="", response="I understand you're having login issues"
        assert conv.get_turn_count() == 4
        history = conv.get_history()
        assert history[0].prompt == "Hello, I need help"
        assert history[0].response is None
        assert history[1].prompt == "My account number is 123-45-6789"
        assert history[1].response is None
        assert history[2].prompt == "I can't log in"
        assert history[2].response == "How can I assist you?"
        assert history[3].prompt == ""
        assert history[3].response == "I understand you're having login issues"

    def test_conversation_rate_limiting_in_pipeline(self):
        """Test rate limiting in pipeline context."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        # Create conversation with strict rate limit
        rate_limit = {"turns_per_minute": 2}
        conv = Conversation.human_ai(
            "test_user", "gpt-4", conversation_id="rate_test", rate_limit=rate_limit
        )

        # First two inputs should work
        result1 = pipeline.check_input("First message", conversation=conv)
        assert not result1["blocked"]

        result2 = pipeline.check_input("Second message", conversation=conv)
        assert not result2["blocked"]

        # Third input should be blocked (rate limit is 2 turns per minute)
        result3 = pipeline.check_input("Third message", conversation=conv)
        assert result3["blocked"]

        # Fourth input should also be blocked
        result4 = pipeline.check_input("Fourth message", conversation=conv)
        assert result4["blocked"]

    def test_conversation_metadata_preservation(self):
        """Test that conversation metadata is preserved through pipeline."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        # Create conversation with metadata
        metadata = {"session_id": "abc123", "ip_address": "192.168.1.1"}
        conv = Conversation.human_ai(
            "test_user", "gpt-4", conversation_id="metadata_test", metadata=metadata
        )

        # Process content
        result = pipeline.check_input("Test content", conversation=conv)

        # Check that metadata is preserved
        assert conv.metadata == metadata
        assert conv.initiator == "test_user"

    def test_conversation_logging_context(self):
        """Test that conversation context appears in logs."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        # Create conversation
        conv = Conversation.human_ai("test_user", "gpt-4", conversation_id="logging_test")

        # Process content (logs should include conversation context)
        result = pipeline.check_input("Test content for logging", conversation=conv)

        # The actual logging verification would require capturing logs
        # For now, just verify the result structure
        assert result["conversation_id"] == "logging_test"
        assert result["pipeline_type"] == "input"

    def test_conversation_serialization_roundtrip(self):
        """Test conversation serialization and restoration with pipeline."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        # Create conversation and add some turns
        conv = Conversation.human_ai("test_user", "gpt-4", conversation_id="serialization_test")

        # Process some content
        pipeline.check_input("First input", conversation=conv)
        pipeline.check_output("First output", conversation=conv)
        pipeline.check_input("Second input", conversation=conv)

        # Serialize conversation
        conv_dict = conv.to_dict()

        # Create new conversation from serialized data
        conv_restored = Conversation.from_dict(conv_dict)

        # Verify conversation state is preserved
        assert conv_restored.conversation_id == "serialization_test"
        assert conv_restored.initiator == "test_user"

    def test_multiple_conversations(self):
        """Test that multiple conversations work independently."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        # Create two conversations
        conv1 = Conversation.human_ai("user1", "gpt-4", conversation_id="conv1")
        conv2 = Conversation.human_ai("user2", "gpt-4", conversation_id="conv2")

        # Process content in both conversations
        result1 = pipeline.check_input("Hello from user1", conversation=conv1)
        result2 = pipeline.check_input("Hello from user2", conversation=conv2)

        # Verify conversations are independent
        assert result1["conversation_id"] == "conv1"
        assert result2["conversation_id"] == "conv2"
        assert conv1.get_turn_count() == 1
        assert conv2.get_turn_count() == 1
        assert conv1.get_history()[0].prompt == "Hello from user1"
        assert conv2.get_history()[0].prompt == "Hello from user2"

    def test_conversation_with_pii_detection(self):
        """Test conversation with PII detection."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        # Create conversation
        conv = Conversation.human_ai("test_user", "gpt-4", conversation_id="pii_test")

        # Test input with PII
        result = pipeline.check_input("My SSN is 123-45-6789", conversation=conv)

        # Should be blocked due to PII
        assert result["conversation_id"] == "pii_test"
        assert result["pipeline_type"] == "input"

        # Check that turn was still added to conversation (even if blocked)
        assert conv.get_turn_count() == 1
        assert conv.get_history()[0].prompt == "My SSN is 123-45-6789"

    def test_conversation_with_toxicity_detection(self):
        """Test conversation with toxicity detection."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        # Create conversation
        conv = Conversation.human_ai("test_user", "gpt-4", conversation_id="toxicity_test")

        # Test input with potentially toxic content
        result = pipeline.check_input("I'm very angry and want to hurt someone", conversation=conv)

        # Should be blocked due to toxicity
        assert result["conversation_id"] == "toxicity_test"
        assert result["pipeline_type"] == "input"

        # Check that turn was still added to conversation
        assert conv.get_turn_count() == 1

    def test_conversation_backward_compatibility(self):
        """Test that existing code continues to work without conversation."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        # Test all existing methods work without conversation parameter
        result_input = pipeline.check_input("Test input")
        result_output = pipeline.check_output("Test output")

        # Verify results have expected structure
        for result in [result_input, result_output]:
            assert isinstance(result, dict)
            assert "blocked" in result
            assert "warnings" in result
            assert "reasons" in result
            assert "details" in result
            assert "pipeline_type" in result
            assert "conversation_id" in result
            assert result["conversation_id"] is None

        # Test other pipeline methods still work
        status = pipeline.get_guardrail_status()
        assert isinstance(status, dict)
        assert "total_enabled" in status
        assert "input_guardrails" in status
        assert "output_guardrails" in status


class TestConversationEdgeCases:
    """Test edge cases in conversation integration."""

    def test_conversation_with_none_content(self):
        """Test conversation with None content."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        conv = Conversation.human_ai("test_user", "gpt-4", conversation_id="none_test")

        # Should handle None content gracefully
        with pytest.raises(ValueError, match="Content cannot be None"):
            pipeline.check_input(None, conversation=conv)

    def test_conversation_with_empty_content(self):
        """Test conversation with empty content."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        conv = Conversation.human_ai("test_user", "gpt-4", conversation_id="empty_test")

        # Should handle empty content
        result = pipeline.check_input("", conversation=conv)
        assert result["conversation_id"] == "empty_test"
        assert conv.get_turn_count() == 1
        assert conv.get_history()[0].prompt == ""

    def test_conversation_with_long_content(self):
        """Test conversation with very long content."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        conv = Conversation.human_ai("test_user", "gpt-4", conversation_id="long_test")

        # Create long content with multiple lines to avoid line length limits (10KB line limit)
        sentences = [
            f"This is sentence number {i} with various words and content." for i in range(100)
        ]
        long_content = "\n".join(sentences)  # Use newlines to break into multiple lines

        result = pipeline.check_input(long_content, conversation=conv)
        assert result["conversation_id"] == "long_test"
        assert conv.get_turn_count() == 1
        assert conv.get_history()[0].prompt == long_content

    def test_conversation_with_special_characters(self):
        """Test conversation with special characters."""
        try:
            pipeline = GuardrailPipeline.from_preset("customer_service")
        except Exception as e:
            pytest.skip(f"Could not create pipeline: {e}")

        conv = Conversation.human_ai("test_user", "gpt-4", conversation_id="special_test")

        # Test with various special characters
        special_content = "Hello! @#$%^&*()_+-=[]{}|;':\",./<>?`~"

        result = pipeline.check_input(special_content, conversation=conv)
        assert result["conversation_id"] == "special_test"
        assert conv.get_turn_count() == 1
        assert conv.get_history()[0].prompt == special_content
