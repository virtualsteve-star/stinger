"""
Test the simplified Conversation API - Phase 5f

Tests the new factory methods and simplified constructor while ensuring
backward compatibility with the old API.
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from stinger import Conversation


class TestConversationAPISimplification:
    """Test the simplified Conversation API."""

    def test_factory_methods(self):
        """Test all factory methods work correctly."""

        # Test human_ai factory method
        human_ai = Conversation.human_ai("user_123", "gpt-4")
        assert human_ai.initiator == "user_123"
        assert human_ai.responder == "gpt-4"
        assert human_ai.initiator_type == "human"
        assert human_ai.responder_type == "ai_model"
        assert human_ai.model_info.get("model_id") == "gpt-4"
        assert human_ai.model_info.get("provider") == "openai"

        # Test bot_to_bot factory method
        bot_bot = Conversation.bot_to_bot("service_bot", "billing_bot")
        assert bot_bot.initiator == "service_bot"
        assert bot_bot.responder == "billing_bot"
        assert bot_bot.initiator_type == "bot"
        assert bot_bot.responder_type == "bot"

        # Test agent_to_agent factory method
        agent_agent = Conversation.agent_to_agent("orchestrator", "specialist")
        assert agent_agent.initiator == "orchestrator"
        assert agent_agent.responder == "specialist"
        assert agent_agent.initiator_type == "agent"
        assert agent_agent.responder_type == "agent"

        # Test human_to_human factory method
        human_human = Conversation.human_to_human("user1", "user2")
        assert human_human.initiator == "user1"
        assert human_human.responder == "user2"
        assert human_human.initiator_type == "human"
        assert human_human.responder_type == "human"

    def test_simplified_constructor(self):
        """Test the simplified constructor works correctly."""

        conv = Conversation(
            initiator="user_123",
            responder="gpt-4",
            initiator_type="human",
            responder_type="ai_model",
        )

        assert conv.initiator == "user_123"
        assert conv.responder == "gpt-4"
        assert conv.initiator_type == "human"
        assert conv.responder_type == "ai_model"

        # Test with custom model info
        conv_with_model = Conversation(
            initiator="user_123",
            responder="gpt-4",
            initiator_type="human",
            responder_type="ai_model",
            model_info={"model_version": "gpt-4-1106-preview", "provider": "openai"},
        )

        assert conv_with_model.model_info.get("model_version") == "gpt-4-1106-preview"
        assert conv_with_model.model_info.get("provider") == "openai"

    def test_backward_compatibility(self):
        """Test that the old API still works."""

        # Test legacy participants parameter
        conv = Conversation(
            participants={
                "initiator": "user_123",
                "responder": "gpt-4",
                "initiator_type": "human",
                "responder_type": "ai_model",
            },
            model_info={
                "model_id": "gpt-4",
                "model_version": "gpt-4-1106-preview",
                "provider": "openai",
            },
        )

        assert conv.initiator == "user_123"
        assert conv.responder == "gpt-4"
        assert conv.initiator_type == "human"
        assert conv.responder_type == "ai_model"
        assert conv.model_info.get("model_id") == "gpt-4"

    def test_add_exchange_method(self):
        """Test the new add_exchange method."""

        conv = Conversation.human_ai("user_123", "gpt-4")

        # Test add_exchange
        turn = conv.add_exchange("Hello", "Hi there!")
        assert turn.prompt == "Hello"
        assert turn.response == "Hi there!"
        assert turn.speaker == "user_123"
        assert turn.listener == "gpt-4"
        assert conv.get_turn_count() == 1
        assert conv.get_complete_turn_count() == 1

        # Test that add_exchange is equivalent to add_turn
        conv2 = Conversation.human_ai("user_123", "gpt-4")
        turn2 = conv2.add_turn("Hello", "Hi there!")
        assert turn2.prompt == turn.prompt
        assert turn2.response == turn.response
        assert turn2.speaker == turn.speaker
        assert turn2.listener == turn.listener

    def test_factory_methods_with_kwargs(self):
        """Test factory methods work with additional kwargs."""

        # Test with rate limits
        conv = Conversation.human_ai("user_123", "gpt-4", rate_limit={"turns_per_minute": 10})
        assert conv.rate_limit == {"turns_per_minute": 10}

        # Test with metadata
        conv = Conversation.human_ai("user_123", "gpt-4", metadata={"session_id": "abc123"})
        assert conv.metadata == {"session_id": "abc123"}

        # Test with conversation_id
        conv = Conversation.human_ai("user_123", "gpt-4", conversation_id="test_conv_123")
        assert conv.conversation_id == "test_conv_123"

    def test_model_info_in_factory_methods(self):
        """Test that model_info is handled correctly in factory methods."""

        # Test with custom model_info
        custom_model_info = {
            "model_version": "gpt-4-1106-preview",
            "provider": "anthropic",  # Override default
            "temperature": 0.7,
        }

        conv = Conversation.human_ai("user_123", "gpt-4", model_info=custom_model_info)

        assert conv.model_info.get("model_id") == "gpt-4"
        assert conv.model_info.get("provider") == "anthropic"
        assert conv.model_info.get("temperature") == 0.7

    def test_serialization_with_new_api(self):
        """Test that conversations created with new API serialize correctly."""

        # Create conversation with factory method
        conv = Conversation.human_ai(
            "user_123",
            "gpt-4",
            model_info={"model_version": "gpt-4-1106-preview", "provider": "openai"},
        )

        conv.add_exchange("Hello", "Hi there!")

        # Serialize and deserialize
        conv_dict = conv.to_dict()
        conv_restored = Conversation.from_dict(conv_dict)

        # Verify all properties are preserved
        assert conv_restored.initiator == conv.initiator
        assert conv_restored.responder == conv.responder
        assert conv_restored.initiator_type == conv.initiator_type
        assert conv_restored.responder_type == conv.responder_type
        assert conv_restored.model_info == conv.model_info
        assert conv_restored.get_turn_count() == conv.get_turn_count()

        # Verify history is preserved
        original_history = [(turn.prompt, turn.response) for turn in conv.get_history()]
        restored_history = [(turn.prompt, turn.response) for turn in conv_restored.get_history()]
        assert original_history == restored_history


class TestConversationAPIBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_old_constructor_still_works(self):
        """Test that the old constructor format still works."""

        # This should work exactly as before
        conv = Conversation(
            conversation_id="test_123",
            participants={
                "initiator": "user_123",
                "responder": "gpt-4",
                "initiator_type": "human",
                "responder_type": "ai_model",
            },
            model_info={"model_id": "gpt-4", "provider": "openai"},
            metadata={"test": "data"},
            rate_limit={"turns_per_minute": 10},
        )

        assert conv.conversation_id == "test_123"
        assert conv.initiator == "user_123"
        assert conv.responder == "gpt-4"
        assert conv.initiator_type == "human"
        assert conv.responder_type == "ai_model"
        assert conv.model_info.get("model_id") == "gpt-4"
        assert conv.metadata == {"test": "data"}
        assert conv.rate_limit == {"turns_per_minute": 10}

    def test_old_methods_still_work(self):
        """Test that old methods still work as expected."""

        conv = Conversation.human_ai("user_123", "gpt-4")

        # Test old add_turn method
        turn = conv.add_turn("Hello", "Hi there!")
        assert turn.prompt == "Hello"
        assert turn.response == "Hi there!"

        # Test add_prompt and add_response
        conv.add_prompt("How are you?")
        assert conv.get_incomplete_turns()[0].prompt == "How are you?"

        conv.add_response("I'm good!")
        assert conv.get_complete_turns()[-1].response == "I'm good!"

    def test_mixed_usage(self):
        """Test mixing old and new API methods."""

        conv = Conversation.human_ai("user_123", "gpt-4")

        # Mix old and new methods
        conv.add_exchange("Hello", "Hi there!")  # New method - 1 complete turn
        conv.add_turn("How are you?", "I'm good!")  # Old method - 1 complete turn
        conv.add_prompt("What's the weather?")  # Old method - 1 incomplete turn
        conv.add_response("It's sunny!")  # Old method - completes the previous turn

        assert conv.get_turn_count() == 3  # 3 total turns
        assert conv.get_complete_turn_count() == 3  # All 3 are complete
        assert len(conv.get_incomplete_turns()) == 0  # No incomplete turns


if __name__ == "__main__":
    pytest.main([__file__])
