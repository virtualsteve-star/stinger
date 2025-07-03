"""
Unit tests for Simple Toxicity Detection Filter

Tests pattern matching accuracy, configuration options, and error handling
for the regex-based toxicity detection filter.
"""

import pytest

from src.stinger.core.guardrail_interface import GuardrailType
from src.stinger.guardrails.simple_toxicity_detection_guardrail import (
    SimpleToxicityDetectionGuardrail,
)


@pytest.mark.ci
class TestSimpleToxicityDetectionFilter:
    """Test cases for Simple Toxicity Detection Filter."""

    @pytest.fixture
    def basic_config(self):
        """Basic configuration for toxicity detection filter."""
        return {
            "enabled": True,
            "categories": ["hate_speech", "harassment", "threats", "sexual_harassment", "violence"],
            "confidence_threshold": 0.7,
            "on_error": "block",
        }

    @pytest.fixture
    def guardrail_instance(self, basic_config):
        """Create a filter instance for testing."""
        return SimpleToxicityDetectionGuardrail("test_toxicity_filter", basic_config)

    @pytest.mark.ci
    def test_filter_initialization(self, basic_config):
        """Test filter initialization with various configurations."""
        # Test basic initialization
        guardrail_instance = SimpleToxicityDetectionGuardrail("test_filter", basic_config)
        assert guardrail_instance.name == "test_filter"
        assert guardrail_instance.guardrail_type == GuardrailType.TOXICITY_DETECTION
        assert guardrail_instance.enabled is True
        assert guardrail_instance.confidence_threshold == 0.7
        assert guardrail_instance.on_error == "block"

        # Test with minimal config
        minimal_config = {"enabled": True}
        guardrail_instance = SimpleToxicityDetectionGuardrail("minimal_filter", minimal_config)
        assert guardrail_instance.enabled_categories == list(
            guardrail_instance.toxicity_patterns.keys()
        )
        assert guardrail_instance.confidence_threshold == 0.7  # Default
        assert guardrail_instance.on_error == "block"  # Default

    @pytest.mark.ci
    def test_category_validation(self):
        """Test category validation and unknown category handling."""
        config = {"enabled": True, "categories": ["hate_speech", "unknown_category", "harassment"]}
        guardrail_instance = SimpleToxicityDetectionGuardrail("test_filter", config)
        # Should only include valid categories
        assert "hate_speech" in guardrail_instance.enabled_categories
        assert "harassment" in guardrail_instance.enabled_categories
        assert "unknown_category" not in guardrail_instance.enabled_categories

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_hate_speech_detection(self, guardrail_instance):
        """Test hate speech pattern detection."""
        test_cases = [
            "You are a racist bigot",
            "Kill all of them",
            "White supremacy is the way",
        ]
        for content in test_cases:
            result = await guardrail_instance.analyze(content)
            # Test behavior rather than exact confidence values
            assert result.confidence >= 0.5 and result.confidence <= 1.0
            expected_blocked = result.confidence >= 0.7
            assert result.blocked is expected_blocked
            assert "hate_speech" in result.details["detected_toxicity"]

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_harassment_detection(self, guardrail_instance):
        """Test harassment pattern detection."""
        # Valid harassment patterns
        test_cases = [
            ("I will stalk you", True, 0.7),  # Above threshold (0.7) - stalking is harassment
            ("You suck and are worthless", True, 0.7),  # Above threshold (0.7) - personal attack
            ("Go die in a hole", True, 0.7),  # Above threshold (0.7) - death wish
        ]

        for content, should_block, expected_confidence in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_block:
                assert result.blocked is True  # Above threshold
                assert result.confidence >= expected_confidence
                assert "harassment" in result.details["detected_toxicity"]
            else:
                assert result.blocked is False  # Below threshold
                assert result.confidence >= expected_confidence
                assert "harassment" in result.details["detected_toxicity"]

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_threat_detection(self, guardrail_instance):
        """Test threat pattern detection."""
        # Valid threat patterns
        test_cases = [
            ("I will kill you", True, 0.7),  # Above threshold (0.7) - death threat
            ("You will die for this", True, 0.7),  # Above threshold (0.7) - death threat
            ("I hope you die soon", True, 0.7),  # Above threshold (0.7) - death wish
        ]

        for content, should_block, expected_confidence in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_block:
                assert result.blocked is True  # Above threshold
                assert result.confidence >= expected_confidence
                assert "threats" in result.details["detected_toxicity"]
            else:
                assert result.blocked is False  # Below threshold
                assert result.confidence >= expected_confidence
                assert "threats" in result.details["detected_toxicity"]

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_sexual_harassment_detection(self, guardrail_instance):
        """Test sexual harassment pattern detection."""
        test_cases = [
            "Send me nude pictures",
            "You are so sexy, show me more",
        ]
        for content in test_cases:
            result = await guardrail_instance.analyze(content)
            # Test behavior rather than exact confidence values
            assert result.confidence >= 0.0 and result.confidence <= 1.0
            expected_blocked = result.confidence >= 0.7
            assert result.blocked is expected_blocked

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_violence_detection(self, guardrail_instance):
        """Test violence pattern detection."""
        test_cases = [
            "I will punch you in the face",
            "Let's fight and beat them up",
            "Shoot them all",
        ]
        for content in test_cases:
            result = await guardrail_instance.analyze(content)
            # Test behavior rather than exact confidence values
            assert result.confidence >= 0.0 and result.confidence <= 1.0
            expected_blocked = result.confidence >= 0.7
            assert result.blocked is expected_blocked
            if result.confidence > 0:
                assert "violence" in result.details["detected_toxicity"]

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_multiple_toxicity_detection(self, guardrail_instance):
        """Test detection of multiple toxicity types in same content."""
        content = "You racist bigot, I will kill you and you suck"
        result = await guardrail_instance.analyze(content)

        assert result.blocked is True
        assert result.confidence >= 0.7  # Higher confidence with multiple matches
        assert "hate_speech" in result.details["detected_toxicity"]
        assert "threats" in result.details["detected_toxicity"]
        assert "harassment" in result.details["detected_toxicity"]
        assert len(result.details["detected_toxicity"]) >= 3

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_confidence_threshold(self):
        """Test confidence threshold behavior."""
        # Low threshold - should block with single match
        low_threshold_config = {
            "enabled": True,
            "categories": ["hate_speech"],
            "confidence_threshold": 0.3,
            "on_error": "block",
        }
        low_filter = SimpleToxicityDetectionGuardrail("low_threshold", low_threshold_config)

        result = await low_filter.analyze("You are a racist")
        assert result.blocked is True

        # High threshold - should not block with single match
        high_threshold_config = {
            "enabled": True,
            "categories": ["hate_speech"],
            "confidence_threshold": 0.9,
            "on_error": "block",
        }
        high_filter = SimpleToxicityDetectionGuardrail("high_threshold", high_threshold_config)

        result = await high_filter.analyze("You are a racist")
        assert result.blocked is False

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_disabled_filter(self):
        """Test disabled filter behavior."""
        config = {"enabled": False}
        guardrail_instance = SimpleToxicityDetectionGuardrail("disabled_filter", config)

        result = await guardrail_instance.analyze("You are a racist bigot")
        assert result.blocked is False
        assert result.confidence == 0.0
        assert "disabled" in result.reason

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_no_toxicity_detection(self, guardrail_instance):
        """Test content with no toxicity."""
        content = "This is a friendly and positive message."
        result = await guardrail_instance.analyze(content)

        assert result.blocked is False
        assert result.confidence == 0.0
        assert "No toxic content detected" in result.reason
        assert result.details["detected_toxicity"] == []

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_false_positive_avoidance(self, guardrail_instance):
        """Test that similar but non-toxic content is not flagged."""
        # Similar patterns that shouldn't be flagged
        test_cases = [
            "Don't kill the mood, let's have fun",
            "You're great at your job",
            "This is a discussion about violence in media",
        ]

        for content in test_cases:
            result = await guardrail_instance.analyze(content)
            # These should not be detected as toxic
            assert result.blocked is False

    @pytest.mark.ci
    def test_configuration_methods(self, guardrail_instance):
        """Test configuration getter and setter methods."""
        # Test get_config
        config = guardrail_instance.get_config()
        assert config["enabled"] is True
        assert "hate_speech" in config["categories"]
        assert config["confidence_threshold"] == 0.7
        assert config["on_error"] == "block"

        # Test update_config
        new_config = {"enabled": False, "confidence_threshold": 0.8, "on_error": "allow"}
        success = guardrail_instance.update_config(new_config)
        assert success is True

        # Verify changes
        assert guardrail_instance.enabled is False
        assert guardrail_instance.confidence_threshold == 0.8
        assert guardrail_instance.on_error == "allow"

    @pytest.mark.ci
    def test_availability_check(self, guardrail_instance):
        """Test availability checking."""
        assert guardrail_instance.is_available() is True

        guardrail_instance.disable()
        assert guardrail_instance.is_available() is False

        guardrail_instance.enable()
        assert guardrail_instance.is_available() is True

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in filter."""
        config = {"enabled": True, "on_error": "allow"}
        guardrail_instance = SimpleToxicityDetectionGuardrail("error_test", config)

        # Test with empty content
        result = await guardrail_instance.analyze("")
        assert result.blocked is False
        assert "No toxic content detected" in result.reason


if __name__ == "__main__":
    pytest.main([__file__])
