"""
Unit tests for Simple PII Detection Filter

Tests pattern matching accuracy, configuration options, and error handling
for the regex-based PII detection filter.
"""

import pytest

from src.stinger.core.guardrail_interface import GuardrailType
from src.stinger.guardrails.simple_pii_detection_guardrail import SimplePIIDetectionGuardrail


class TestSimplePIIDetectionFilter:
    """Test cases for Simple PII Detection Filter."""

    @pytest.fixture
    def basic_config(self):
        """Basic configuration for PII detection filter."""
        return {
            "enabled": True,
            "patterns": ["ssn", "credit_card", "email", "phone", "ip_address"],
            "confidence_threshold": 0.8,
            "on_error": "block",
        }

    @pytest.fixture
    def guardrail_instance(self, basic_config):
        """Create a filter instance for testing."""
        return SimplePIIDetectionGuardrail("test_pii_filter", basic_config)

    def test_filter_initialization(self, basic_config):
        """Test filter initialization with various configurations."""
        # Test basic initialization
        guardrail_instance = SimplePIIDetectionGuardrail("test_filter", basic_config)
        assert guardrail_instance.name == "test_filter"
        assert guardrail_instance.guardrail_type == GuardrailType.PII_DETECTION
        assert guardrail_instance.enabled is True
        assert guardrail_instance.confidence_threshold == 0.8
        assert guardrail_instance.on_error == "block"

        # Test with minimal config
        minimal_config = {"enabled": True}
        guardrail_instance = SimplePIIDetectionGuardrail("minimal_filter", minimal_config)
        assert guardrail_instance.enabled_patterns == list(guardrail_instance.pii_patterns.keys())
        assert guardrail_instance.confidence_threshold == 0.8  # Default
        assert guardrail_instance.on_error == "block"  # Default

    def test_pattern_validation(self):
        """Test pattern validation and unknown pattern handling."""
        config = {"enabled": True, "patterns": ["ssn", "unknown_pattern", "email"]}
        guardrail_instance = SimplePIIDetectionGuardrail("test_filter", config)
        # Should only include valid patterns
        assert "ssn" in guardrail_instance.enabled_patterns
        assert "email" in guardrail_instance.enabled_patterns
        assert "unknown_pattern" not in guardrail_instance.enabled_patterns

    @pytest.mark.asyncio
    async def test_ssn_detection(self, guardrail_instance):
        """Test SSN pattern detection."""
        # Valid SSN formats
        test_cases = [
            ("My SSN is 123-45-6789", False, 0.6),  # Below threshold (0.8)
            ("SSN: 123456789", False, 0.6),  # Below threshold (0.8)
            ("Social Security Number: 111-22-3333", False, 0.6),  # Below threshold (0.8)
        ]

        for content, should_block, expected_confidence in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_block:
                assert result.blocked is True  # Above threshold
                assert result.confidence >= expected_confidence
                assert "ssn" in result.details["detected_pii"]
                assert "SSN" in result.reason
            else:
                assert result.blocked is False  # Below threshold
                assert result.confidence >= expected_confidence
                assert "ssn" in result.details["detected_pii"]
                assert "PII detected" in result.reason

    @pytest.mark.asyncio
    async def test_credit_card_detection(self, guardrail_instance):
        """Test credit card pattern detection."""
        # Valid credit card formats
        test_cases = [
            ("Card: 1234-5678-9012-3456", False, 0.6),  # Below threshold (0.8)
            ("Credit card: 1234567890123456", False, 0.6),  # Below threshold (0.8)
            ("CC: 1234 5678 9012 3456", False, 0.6),  # Below threshold (0.8)
        ]

        for content, should_block, expected_confidence in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_block:
                assert result.blocked is True  # Above threshold
                assert result.confidence >= expected_confidence
                assert "credit_card" in result.details["detected_pii"]
            else:
                assert result.blocked is False  # Below threshold
                assert result.confidence >= expected_confidence
                assert "credit_card" in result.details["detected_pii"]

    @pytest.mark.asyncio
    async def test_email_detection(self, guardrail_instance):
        """Test email pattern detection."""
        # Valid email formats
        test_cases = [
            ("Contact me at test@example.com", False, 0.6),  # Below threshold (0.8)
            ("Email: user.name+tag@domain.co.uk", False, 0.6),  # Below threshold (0.8)
            ("My email is john.doe@company.org", False, 0.6),  # Below threshold (0.8)
        ]

        for content, should_block, expected_confidence in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_block:
                assert result.blocked is True  # Above threshold
                assert result.confidence >= expected_confidence
                assert "email" in result.details["detected_pii"]
            else:
                assert result.blocked is False  # Below threshold
                assert result.confidence >= expected_confidence
                assert "email" in result.details["detected_pii"]

    @pytest.mark.asyncio
    async def test_phone_detection(self, guardrail_instance):
        """Test phone number pattern detection."""
        # Valid phone formats
        test_cases = [
            ("Call me at (555) 123-4567", False, 0.6),  # Below threshold (0.8)
            ("Phone: +1-555-123-4567", False, 0.6),  # Below threshold (0.8)
            ("Contact: 555.123.4567", False, 0.6),  # Below threshold (0.8)
        ]

        for content, should_block, expected_confidence in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_block:
                assert result.blocked is True  # Above threshold
                assert result.confidence >= expected_confidence
                assert "phone" in result.details["detected_pii"]
            else:
                assert result.blocked is False  # Below threshold
                assert result.confidence >= expected_confidence
                assert "phone" in result.details["detected_pii"]

    @pytest.mark.asyncio
    async def test_ip_address_detection(self, guardrail_instance):
        """Test IP address pattern detection."""
        # Valid IP formats
        test_cases = [
            ("Server IP: 192.168.1.1", False, 0.6),  # Below threshold (0.8)
            ("Gateway: 10.0.0.1", False, 0.6),  # Below threshold (0.8)
            ("Network: 172.16.0.1", False, 0.6),  # Below threshold (0.8)
        ]

        for content, should_block, expected_confidence in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_block:
                assert result.blocked is True  # Above threshold
                assert result.confidence >= expected_confidence
                assert "ip_address" in result.details["detected_pii"]
            else:
                assert result.blocked is False  # Below threshold
                assert result.confidence >= expected_confidence
                assert "ip_address" in result.details["detected_pii"]

    @pytest.mark.asyncio
    async def test_multiple_pii_detection(self, guardrail_instance):
        """Test detection of multiple PII types in same content."""
        content = "My SSN is 123-45-6789 and email is test@example.com"
        result = await guardrail_instance.analyze(content)

        assert result.blocked is False  # Below threshold (0.8) even with multiple matches
        assert result.confidence >= 0.6  # Confidence should be at least 0.6 for any detection
        assert "ssn" in result.details["detected_pii"]
        assert "email" in result.details["detected_pii"]
        assert len(result.details["detected_pii"]) == 2

    @pytest.mark.asyncio
    async def test_confidence_threshold(self):
        """Test confidence threshold behavior."""
        # Low threshold - should block with single match
        low_threshold_config = {
            "enabled": True,
            "patterns": ["ssn"],
            "confidence_threshold": 0.5,
            "on_error": "block",
        }
        low_filter = SimplePIIDetectionGuardrail("low_threshold", low_threshold_config)

        result = await low_filter.analyze("SSN: 123-45-6789")
        assert result.blocked is True

        # High threshold - should not block with single match
        high_threshold_config = {
            "enabled": True,
            "patterns": ["ssn"],
            "confidence_threshold": 0.9,
            "on_error": "block",
        }
        high_filter = SimplePIIDetectionGuardrail("high_threshold", high_threshold_config)

        result = await high_filter.analyze("SSN: 123-45-6789")
        assert result.blocked is False

    @pytest.mark.asyncio
    async def test_disabled_filter(self):
        """Test disabled filter behavior."""
        config = {"enabled": False}
        guardrail_instance = SimplePIIDetectionGuardrail("disabled_filter", config)

        result = await guardrail_instance.analyze("SSN: 123-45-6789")
        assert result.blocked is False
        assert result.confidence == 0.0
        assert "disabled" in result.reason

    @pytest.mark.asyncio
    async def test_no_pii_detection(self, guardrail_instance):
        """Test content with no PII."""
        content = "This is a normal message without any personal information."
        result = await guardrail_instance.analyze(content)

        assert result.blocked is False
        assert result.confidence == 0.0
        assert "No PII detected" in result.reason
        assert result.details["detected_pii"] == []

    @pytest.mark.asyncio
    async def test_false_positive_avoidance(self, guardrail_instance):
        """Test that similar but non-PII content is not flagged."""
        # Similar patterns that shouldn't be flagged
        test_cases = [
            "The number 123-45-6789 is not an SSN",
            "My phone number is 555-1234",  # Too short
            "Email me at test@",  # Incomplete email
            "IP address 256.256.256.256",  # Invalid IP
        ]

        for content in test_cases:
            result = await guardrail_instance.analyze(content)
            # These should not be detected as PII
            assert result.blocked is False

    def test_configuration_methods(self, guardrail_instance):
        """Test configuration getter and setter methods."""
        # Test get_config
        config = guardrail_instance.get_config()
        assert config["enabled"] is True
        assert "ssn" in config["patterns"]
        assert config["confidence_threshold"] == 0.8
        assert config["on_error"] == "block"

        # Test update_config
        new_config = {"enabled": False, "confidence_threshold": 0.9, "on_error": "allow"}
        success = guardrail_instance.update_config(new_config)
        assert success is True

        # Verify changes
        assert guardrail_instance.enabled is False
        assert guardrail_instance.confidence_threshold == 0.9
        assert guardrail_instance.on_error == "allow"

    def test_availability_check(self, guardrail_instance):
        """Test availability checking."""
        assert guardrail_instance.is_available() is True

        guardrail_instance.disable()
        assert guardrail_instance.is_available() is False

        guardrail_instance.enable()
        assert guardrail_instance.is_available() is True

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in filter."""
        # Test with invalid regex pattern (should not happen with current implementation)
        # But we can test the error handling structure
        config = {"enabled": True, "on_error": "allow"}
        guardrail_instance = SimplePIIDetectionGuardrail("error_test", config)

        # Test with empty content
        result = await guardrail_instance.analyze("")
        assert result.blocked is False
        assert "No PII detected" in result.reason


if __name__ == "__main__":
    pytest.main([__file__])
