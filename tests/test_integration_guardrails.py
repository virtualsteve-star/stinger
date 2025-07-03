"""
Integration tests for Phase 5a: Additional Classifier Filters

Tests integration of all Phase 5a filters with the universal guardrail interface,
factory registration, and pipeline integration.
"""

import asyncio

import pytest

from src.stinger.core.guardrail_factory import create_guardrail_from_config, register_all_factories
from src.stinger.core.guardrail_interface import GuardrailRegistry, GuardrailType
from src.stinger.guardrails.simple_code_generation_guardrail import SimpleCodeGenerationGuardrail
from src.stinger.guardrails.simple_pii_detection_guardrail import SimplePIIDetectionGuardrail
from src.stinger.guardrails.simple_toxicity_detection_guardrail import (
    SimpleToxicityDetectionGuardrail,
)


class TestPhase5aIntegration:
    """Integration tests for Phase 5a filters."""

    @pytest.fixture
    def registry(self):
        """Create a guardrail registry for testing."""
        registry = GuardrailRegistry()
        register_all_factories(registry)
        return registry

    def test_factory_registration(self, registry):
        """Test that all Phase 5a filter types are registered."""
        # Check that all new filter types are registered
        assert GuardrailType.PII_DETECTION in registry._factories
        assert GuardrailType.TOXICITY_DETECTION in registry._factories
        assert GuardrailType.CODE_GENERATION in registry._factories

        # Check that factory functions exist
        assert registry._factories[GuardrailType.PII_DETECTION] is not None
        assert registry._factories[GuardrailType.TOXICITY_DETECTION] is not None
        assert registry._factories[GuardrailType.CODE_GENERATION] is not None

    def test_filter_creation_from_config(self, registry):
        """Test creating filters from configuration."""
        # Test PII detection filter creation
        pii_config = {
            "name": "test_pii",
            "type": "pii_detection",
            "enabled": True,
            "patterns": ["ssn"],
            "confidence_threshold": 0.5,
        }
        pii_filter = create_guardrail_from_config(pii_config, registry)
        assert pii_filter is not None
        assert isinstance(pii_filter, SimplePIIDetectionGuardrail)
        assert pii_filter.name == "test_pii"
        assert pii_filter.guardrail_type == GuardrailType.PII_DETECTION

        # Test toxicity detection filter creation
        toxicity_config = {
            "name": "test_toxicity",
            "type": "toxicity_detection",
            "enabled": True,
            "categories": ["hate_speech"],
            "confidence_threshold": 0.4,
        }
        toxicity_filter = create_guardrail_from_config(toxicity_config, registry)
        assert toxicity_filter is not None
        assert isinstance(toxicity_filter, SimpleToxicityDetectionGuardrail)
        assert toxicity_filter.name == "test_toxicity"
        assert toxicity_filter.guardrail_type == GuardrailType.TOXICITY_DETECTION

        # Test code generation filter creation
        code_config = {
            "name": "test_code",
            "type": "code_generation",
            "enabled": True,
            "categories": ["code_blocks"],
            "confidence_threshold": 0.3,
        }
        code_filter = create_guardrail_from_config(code_config, registry)
        assert code_filter is not None
        assert isinstance(code_filter, SimpleCodeGenerationGuardrail)
        assert code_filter.name == "test_code"
        assert code_filter.guardrail_type == GuardrailType.CODE_GENERATION

    @pytest.mark.asyncio
    async def test_filter_interface_compliance(self, registry):
        """Test that all filters implement the universal interface correctly."""
        # Create all filter types
        guardrails = []

        # PII detection filter
        pii_config = {
            "name": "test_pii",
            "type": "pii_detection",
            "enabled": True,
            "patterns": ["ssn"],
        }
        pii_filter = create_guardrail_from_config(pii_config, registry)
        guardrails.append(pii_filter)

        # Toxicity detection filter
        toxicity_config = {
            "name": "test_toxicity",
            "type": "toxicity_detection",
            "enabled": True,
            "categories": ["hate_speech"],
        }
        toxicity_filter = create_guardrail_from_config(toxicity_config, registry)
        guardrails.append(toxicity_filter)

        # Code generation filter
        code_config = {
            "name": "test_code",
            "type": "code_generation",
            "enabled": True,
            "categories": ["code_blocks"],
        }
        code_filter = create_guardrail_from_config(code_config, registry)
        guardrails.append(code_filter)

        # Test interface compliance for each filter
        for guardrail_instance in guardrails:
            # Test basic interface methods
            assert hasattr(guardrail_instance, "analyze")
            assert hasattr(guardrail_instance, "is_available")
            assert hasattr(guardrail_instance, "get_config")
            assert hasattr(guardrail_instance, "update_config")
            assert hasattr(guardrail_instance, "get_name")
            assert hasattr(guardrail_instance, "get_type")
            assert hasattr(guardrail_instance, "is_enabled")
            assert hasattr(guardrail_instance, "enable")
            assert hasattr(guardrail_instance, "disable")

            # Test analyze method returns GuardrailResult
            result = await guardrail_instance.analyze("test content")
            assert hasattr(result, "blocked")
            assert hasattr(result, "confidence")
            assert hasattr(result, "reason")
            assert hasattr(result, "details")
            assert hasattr(result, "guardrail_name")
            assert hasattr(result, "guardrail_type")

            # Test configuration methods
            config = guardrail_instance.get_config()
            assert isinstance(config, dict)

            # Test enable/disable
            original_enabled = guardrail_instance.is_enabled()
            guardrail_instance.disable()
            assert guardrail_instance.is_enabled() is False
            guardrail_instance.enable()
            assert guardrail_instance.is_enabled() is True

    @pytest.mark.asyncio
    async def test_filter_independence(self, registry):
        """Test that filters don't interfere with each other."""
        # Create multiple filters
        pii_config = {
            "name": "test_pii",
            "type": "pii_detection",
            "enabled": True,
            "patterns": ["ssn"],
            "confidence_threshold": 0.5,
        }
        pii_filter = create_guardrail_from_config(pii_config, registry)

        toxicity_config = {
            "name": "test_toxicity",
            "type": "toxicity_detection",
            "enabled": True,
            "categories": ["hate_speech"],
            "confidence_threshold": 0.4,
        }
        toxicity_filter = create_guardrail_from_config(toxicity_config, registry)

        code_config = {
            "name": "test_code",
            "type": "code_generation",
            "enabled": True,
            "categories": ["code_blocks"],
            "confidence_threshold": 0.3,
        }
        code_filter = create_guardrail_from_config(code_config, registry)

        # Test content that should only trigger PII detection
        pii_content = "My SSN is 123-45-6789"
        pii_result = await pii_filter.analyze(pii_content) if pii_filter else None
        toxicity_result = await toxicity_filter.analyze(pii_content) if toxicity_filter else None
        code_result = await code_filter.analyze(pii_content) if code_filter else None

        assert pii_result and pii_result.blocked is True
        assert toxicity_result and toxicity_result.blocked is False
        assert code_result and code_result.blocked is False

        # Test content that should only trigger toxicity detection
        toxicity_content = "You are a racist bigot"
        pii_result = await pii_filter.analyze(toxicity_content) if pii_filter else None
        toxicity_result = (
            await toxicity_filter.analyze(toxicity_content) if toxicity_filter else None
        )
        code_result = await code_filter.analyze(toxicity_content) if code_filter else None

        assert pii_result and pii_result.blocked is False
        assert toxicity_result and toxicity_result.blocked is True
        assert code_result and code_result.blocked is False

        # Test content that should only trigger code detection
        code_content = "```python\nprint('hello')\n```"
        pii_result = await pii_filter.analyze(code_content) if pii_filter else None
        toxicity_result = await toxicity_filter.analyze(code_content) if toxicity_filter else None
        code_result = await code_filter.analyze(code_content) if code_filter else None

        assert pii_result and pii_result.blocked is False
        assert toxicity_result and toxicity_result.blocked is False
        assert code_result and code_result.blocked is True

    @pytest.mark.asyncio
    async def test_multiple_filters_same_type(self, registry):
        """Test that multiple filters of the same type work independently."""
        # Create two PII filters with different configurations
        pii_config1 = {
            "name": "pii_filter_1",
            "type": "pii_detection",
            "enabled": True,
            "patterns": ["ssn"],
            "confidence_threshold": 0.5,
        }
        pii_filter1 = create_guardrail_from_config(pii_config1, registry)

        pii_config2 = {
            "name": "pii_filter_2",
            "type": "pii_detection",
            "enabled": True,
            "patterns": ["email"],
            "confidence_threshold": 0.9,
        }
        pii_filter2 = create_guardrail_from_config(pii_config2, registry)

        # Test content that should trigger both filters differently
        content = "My SSN is 123-45-6789 and email is test@example.com"

        result1 = await pii_filter1.analyze(content) if pii_filter1 else None
        result2 = await pii_filter2.analyze(content) if pii_filter2 else None

        # First filter should block (low threshold)
        assert result1 and result1.blocked is True
        assert "ssn" in result1.details["detected_pii"]

        # Second filter should not block (high threshold)
        assert result2 and result2.blocked is False
        assert "email" in result2.details["detected_pii"]

    def test_configuration_validation(self, registry):
        """Test configuration validation and error handling."""
        # Test invalid filter type
        invalid_config = {"name": "invalid_filter", "type": "invalid_type", "enabled": True}
        from src.stinger.utils.exceptions import InvalidGuardrailTypeError

        with pytest.raises(InvalidGuardrailTypeError):
            create_guardrail_from_config(invalid_config, registry)

        # Test missing required fields
        incomplete_config = {
            "name": "incomplete_filter"
            # Missing 'type' field
        }
        from src.stinger.utils.exceptions import ConfigurationError

        with pytest.raises(ConfigurationError):
            create_guardrail_from_config(incomplete_config, registry)

        # Test valid configuration with unknown patterns/categories
        valid_config = {
            "name": "valid_filter",
            "type": "pii_detection",
            "enabled": True,
            "patterns": ["ssn", "unknown_pattern"],
        }
        valid_filter = create_guardrail_from_config(valid_config, registry)
        assert valid_filter is not None
        # Should only include valid patterns
        if isinstance(valid_filter, SimplePIIDetectionGuardrail):
            assert "ssn" in valid_filter.enabled_patterns
            assert "unknown_pattern" not in valid_filter.enabled_patterns

    @pytest.mark.asyncio
    async def test_filter_performance(self, registry):
        """Test filter performance characteristics."""
        import time

        # Create a filter for performance testing
        config = {
            "name": "perf_test",
            "type": "pii_detection",
            "enabled": True,
            "patterns": ["ssn", "email", "phone", "credit_card"],
            "confidence_threshold": 0.5,  # Lower threshold so it will block
        }
        guardrail_instance = create_guardrail_from_config(config, registry)

        # Test simple content performance
        simple_content = "This is a normal message without PII."
        start_time = time.time()
        result = await guardrail_instance.analyze(simple_content) if guardrail_instance else None
        end_time = time.time()

        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert execution_time < 10  # Should be under 10ms for simple filters
        assert result and result.blocked is False

        # Test complex content performance
        complex_content = "My SSN is 123-45-6789, email is test@example.com, phone is (555) 123-4567, and credit card is 1234-5678-9012-3456"
        start_time = time.time()
        result = await guardrail_instance.analyze(complex_content) if guardrail_instance else None
        end_time = time.time()

        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert execution_time < 10  # Should still be under 10ms
        assert result and result.blocked is True

    def test_registry_management(self, registry):
        """Test registry management with Phase 5a filters."""
        # Test getting filters by type
        pii_filters = registry.get_guardrails_by_type(GuardrailType.PII_DETECTION)
        toxicity_filters = registry.get_guardrails_by_type(GuardrailType.TOXICITY_DETECTION)
        code_filters = registry.get_guardrails_by_type(GuardrailType.CODE_GENERATION)

        # Initially should be empty (no filters registered yet)
        assert len(pii_filters) == 0
        assert len(toxicity_filters) == 0
        assert len(code_filters) == 0

        # Create and register filters
        pii_config = {"name": "test_pii", "type": "pii_detection", "enabled": True}
        pii_filter = create_guardrail_from_config(pii_config, registry)
        registry.register_guardrail(pii_filter)

        # Check that filter is now in registry
        pii_filters = registry.get_guardrails_by_type(GuardrailType.PII_DETECTION)
        assert len(pii_filters) == 1
        assert pii_filters[0].name == "test_pii"

        # Test unregistering
        success = registry.unregister_guardrail("test_pii")
        assert success is True

        pii_filters = registry.get_guardrails_by_type(GuardrailType.PII_DETECTION)
        assert len(pii_filters) == 0


if __name__ == "__main__":
    pytest.main([__file__])
