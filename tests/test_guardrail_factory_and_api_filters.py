"""
Guardrail Factory, Registry, and API-based Filter Tests

Tests for the extensible guardrail/filter system, including legacy adapters and OpenAI-based filters.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from src.stinger.core.guardrail_interface import GuardrailType, GuardrailRegistry, GuardrailFactory
from src.stinger.core.guardrail_factory import register_all_factories
from src.stinger.core.api_key_manager import APIKeyManager


# Use the actual register_all_factories from the module


class TestGuardrailInterface:
    """Test the universal guardrail interface system."""

    def test_guardrail_type_enum(self):
        """Test that all guardrail types are defined."""
        types = list(GuardrailType)
        assert len(types) >= 7  # Should have at least 7 types
        assert GuardrailType.CONTENT_MODERATION in types
        assert GuardrailType.PROMPT_INJECTION in types
        assert GuardrailType.KEYWORD_BLOCK in types
        assert GuardrailType.REGEX_FILTER in types

    def test_guardrail_registry(self):
        """Test guardrail registry functionality."""
        registry = GuardrailRegistry()

        # Test empty registry
        assert len(registry.get_all_guardrails()) == 0
        assert registry.get_guardrail("nonexistent") is None

        # Test factory registration
        mock_factory = Mock(return_value=None)
        registry.register_factory(GuardrailType.KEYWORD_BLOCK, mock_factory)

        # Test guardrail creation
        result = registry.create_guardrail(GuardrailType.KEYWORD_BLOCK, "test", {})
        assert result is None  # Mock returns None

        # Test clearing
        registry.clear()
        assert len(registry.get_all_guardrails()) == 0


class TestGuardrailFactory:
    """Test the guardrail factory system."""

    def test_factory_registration(self):
        """Test that all factories can be registered."""
        registry = GuardrailRegistry()
        register_all_factories(registry)

        # Check that factories are registered
        assert GuardrailType.KEYWORD_BLOCK in registry._factories
        assert GuardrailType.REGEX_FILTER in registry._factories
        assert GuardrailType.LENGTH_FILTER in registry._factories
        assert GuardrailType.URL_FILTER in registry._factories
        assert GuardrailType.PASS_THROUGH in registry._factories

    def test_factory_creation(self):
        """Test creating guardrails from configuration."""
        registry = GuardrailRegistry()
        register_all_factories(registry)
        factory = GuardrailFactory(registry)

        # Test valid configuration
        config = {
            "name": "test_filter",
            "type": "keyword_block",
            "enabled": True,
            "keyword": "test",
        }

        guardrail = factory.create_from_config(config)
        assert guardrail is not None
        assert guardrail.get_name() == "test_filter"
        assert guardrail.get_type() == GuardrailType.KEYWORD_BLOCK

    def test_factory_invalid_config(self):
        """Test factory with invalid configuration."""
        registry = GuardrailRegistry()
        register_all_factories(registry)
        factory = GuardrailFactory(registry)

        # Test missing name - should raise ConfigurationError
        from src.stinger.utils.exceptions import ConfigurationError

        config = {"type": "keyword_block"}
        with pytest.raises(ConfigurationError):
            factory.create_from_config(config)

        # Test missing type - should raise ConfigurationError
        config = {"name": "test"}
        with pytest.raises(ConfigurationError):
            factory.create_from_config(config)

        # Test invalid type - should raise InvalidGuardrailTypeError
        from src.stinger.utils.exceptions import InvalidGuardrailTypeError

        config = {"name": "test", "type": "invalid_type"}
        with pytest.raises(InvalidGuardrailTypeError):
            factory.create_from_config(config)


class TestAPIKeyManager:
    """Test the API key management system."""

    def test_api_key_manager_initialization(self):
        """Test API key manager initialization."""
        manager = APIKeyManager()
        assert manager is not None
        assert isinstance(manager._keys, dict)

    def test_environment_variable_loading(self):
        """Test loading API keys from environment variables."""
        with patch.dict(
            "os.environ", {"OPENAI_API_KEY": "sk-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}
        ):
            manager = APIKeyManager()
            key = manager.get_openai_key()
            assert key == "sk-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    def test_key_validation(self):
        """Test API key validation."""
        manager = APIKeyManager()

        # Test valid OpenAI key (48 characters after sk-)
        valid_key = "sk-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        assert manager.validate_key("openai", valid_key) is True

        # Test invalid OpenAI key
        invalid_key = "invalid-key"
        assert manager.validate_key("openai", invalid_key) is False

        # Test key that's too short
        short_key = "sk-test"
        assert manager.validate_key("openai", short_key) is False

    def test_health_check(self):
        """Test health check functionality."""
        manager = APIKeyManager()
        health = manager.health_check()
        assert isinstance(health, dict)


# Legacy filter adapters removed - all filters now use GuardrailInterface directly


class TestGuardrailFactoryAndAPIFilters:
    """Test the Guardrail Factory and API-based Filters."""

    @pytest.mark.asyncio
    async def test_content_moderation_filter_unavailable(self):
        """Test content moderation filter when OpenAI is unavailable."""
        try:
            from src.stinger.guardrails.content_moderation_guardrail import (
                ContentModerationGuardrail,
            )

            config = {
                "name": "test_moderation",
                "type": "content_moderation",
                "enabled": True,
                "confidence_threshold": 0.7,
                "on_error": "allow",
            }

            # Mock the OpenAI adapter to simulate unavailability
            with patch(
                "src.stinger.guardrails.content_moderation_guardrail.OpenAIAdapter"
            ) as mock_adapter_class:
                mock_adapter = MagicMock()
                mock_adapter.moderate_content = AsyncMock(side_effect=Exception("API unavailable"))
                mock_adapter_class.return_value = mock_adapter

                # Recreate the filter with mocked adapter
                guardrail_instance = ContentModerationGuardrail("test_moderation", config)

                # Test when API is unavailable
                result = await guardrail_instance.analyze("test content")
                assert result.blocked is False  # Should allow when unavailable
                assert "unavailable" in result.reason.lower() or "error" in result.reason.lower()

        except ImportError:
            pytest.skip("Guardrail Factory and API-based Filters not available")

    @pytest.mark.asyncio
    async def test_content_moderation_filter_available(self):
        """Test content moderation filter when OpenAI is available."""
        try:
            from src.stinger.guardrails.content_moderation_guardrail import (
                ContentModerationGuardrail,
            )
            from src.stinger.adapters.openai_adapter import ModerationResult

            config = {
                "name": "test_moderation",
                "type": "content_moderation",
                "enabled": True,
                "confidence_threshold": 0.7,
                "on_error": "allow",
            }

            # Mock the OpenAI adapter to simulate successful response
            with patch(
                "src.stinger.guardrails.content_moderation_guardrail.OpenAIAdapter"
            ) as mock_adapter_class:
                mock_adapter = MagicMock()
                mock_result = ModerationResult(
                    flagged=False,
                    categories={"hate": False, "harassment": False},
                    category_scores={"hate": 0.1, "harassment": 0.2},
                    confidence=0.2,
                )
                # Make the method async
                mock_adapter.moderate_content = AsyncMock(return_value=mock_result)
                mock_adapter_class.return_value = mock_adapter

                # Recreate the filter with mocked adapter
                guardrail_instance = ContentModerationGuardrail("test_moderation", config)

                # Test when API is available
                result = await guardrail_instance.analyze("test content")
                assert result.blocked is False  # Should allow safe content
                assert "passed" in result.reason.lower() or "safe" in result.reason.lower()

        except ImportError:
            pytest.skip("Guardrail Factory and API-based Filters not available")

    @pytest.mark.asyncio
    async def test_prompt_injection_filter_unavailable(self):
        """Test prompt injection filter when OpenAI is unavailable."""
        try:
            from src.stinger.guardrails.prompt_injection_guardrail import PromptInjectionGuardrail

            config = {
                "name": "test_injection",
                "type": "prompt_injection",
                "enabled": True,
                "risk_threshold": 70,
                "on_error": "allow",
            }

            # Mock the OpenAI adapter to simulate unavailability
            with patch(
                "src.stinger.guardrails.prompt_injection_guardrail.OpenAIAdapter"
            ) as mock_adapter_class:
                mock_adapter = MagicMock()
                mock_adapter.complete = AsyncMock(side_effect=Exception("API unavailable"))
                mock_adapter_class.return_value = mock_adapter

                # Recreate the filter with mocked adapter
                guardrail_instance = PromptInjectionGuardrail("test_injection", config)

                # Test when API is unavailable
                result = await guardrail_instance.analyze("test content")
                assert result.blocked is False  # Should allow when unavailable
                assert "unavailable" in result.reason.lower() or "error" in result.reason.lower()

        except ImportError:
            pytest.skip("Guardrail Factory and API-based Filters not available")

    @pytest.mark.asyncio
    async def test_prompt_injection_filter_available(self):
        """Test prompt injection filter when OpenAI is available."""
        try:
            from src.stinger.guardrails.prompt_injection_guardrail import (
                PromptInjectionGuardrail,
                InjectionResult,
            )

            config = {
                "name": "test_injection",
                "type": "prompt_injection",
                "enabled": True,
                "risk_threshold": 70,
                "on_error": "allow",
            }

            # Mock the OpenAI adapter to simulate successful response
            with patch(
                "src.stinger.guardrails.prompt_injection_guardrail.OpenAIAdapter"
            ) as mock_adapter_class:
                from src.stinger.adapters.openai_adapter import CompletionResult

                mock_adapter = MagicMock()
                mock_completion = CompletionResult(
                    content='{"detected": false, "risk_percent": 10, "level": "low", "indicators": [], "comment": "No injection detected"}',
                    model="gpt-4o-mini",
                    usage={},
                    finish_reason="stop",
                )
                # Make the method async
                mock_adapter.complete = AsyncMock(return_value=mock_completion)
                mock_adapter_class.return_value = mock_adapter

                # Recreate the filter with mocked adapter
                guardrail_instance = PromptInjectionGuardrail("test_injection", config)

                # Test when API is available
                result = await guardrail_instance.analyze("test content")
                assert result.blocked is False  # Should allow safe content
                assert (
                    "no prompt injection" in result.reason.lower()
                    or "safe" in result.reason.lower()
                )

        except ImportError:
            pytest.skip("Guardrail Factory and API-based Filters not available")


if __name__ == "__main__":
    pytest.main([__file__])
