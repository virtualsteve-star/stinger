"""
Unit tests for Simple Code Generation Filter

Tests pattern matching accuracy, configuration options, and error handling
for the regex-based code generation detection filter.
"""

import pytest

from src.stinger.core.guardrail_interface import GuardrailType
from src.stinger.guardrails.simple_code_generation_guardrail import SimpleCodeGenerationGuardrail


@pytest.mark.ci
class TestSimpleCodeGenerationFilter:
    """Test cases for Simple Code Generation Filter."""

    @pytest.fixture
    def basic_config(self):
        """Basic configuration for code generation filter."""
        return {
            "enabled": True,
            "categories": [
                "code_blocks",
                "programming_keywords",
                "code_injection",
                "file_operations",
                "system_commands",
            ],
            "confidence_threshold": 0.6,
            "min_keywords": 1,  # Lower threshold for testing
            "on_error": "warn",
        }

    @pytest.fixture
    def guardrail_instance(self, basic_config):
        """Create a filter instance for testing."""
        return SimpleCodeGenerationGuardrail("test_code_filter", basic_config)

    @pytest.mark.ci
    def test_filter_initialization(self, basic_config):
        """Test filter initialization with various configurations."""
        # Test basic initialization
        guardrail_instance = SimpleCodeGenerationGuardrail("test_filter", basic_config)
        assert guardrail_instance.name == "test_filter"
        assert guardrail_instance.guardrail_type == GuardrailType.CODE_GENERATION
        assert guardrail_instance.enabled is True
        assert guardrail_instance.confidence_threshold == 0.6
        assert guardrail_instance.min_keywords == 1
        assert guardrail_instance.on_error == "warn"

        # Test with minimal config
        minimal_config = {"enabled": True}
        guardrail_instance = SimpleCodeGenerationGuardrail("minimal_filter", minimal_config)
        assert guardrail_instance.enabled_categories == list(
            guardrail_instance.code_patterns.keys()
        )
        assert guardrail_instance.confidence_threshold == 0.6  # Default
        assert guardrail_instance.min_keywords == 3  # Default
        assert guardrail_instance.on_error == "warn"  # Default

    @pytest.mark.ci
    def test_category_validation(self):
        """Test category validation and unknown category handling."""
        config = {
            "enabled": True,
            "categories": ["code_blocks", "unknown_category", "programming_keywords"],
        }
        guardrail_instance = SimpleCodeGenerationGuardrail("test_filter", config)
        # Should only include valid categories
        assert "code_blocks" in guardrail_instance.enabled_categories
        assert "programming_keywords" in guardrail_instance.enabled_categories
        assert "unknown_category" not in guardrail_instance.enabled_categories

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_code_blocks_detection(self, guardrail_instance):
        """Test code block pattern detection."""
        # Valid code block patterns
        test_cases = [
            ("```python\nprint('hello')\n```", True, 0.9),  # At or above threshold (0.6)
            ("`inline code`", False, 0.4),  # Below threshold (0.6)
            ("<code>function()</code>", False, 0.4),  # Below threshold (0.6)
            ("<pre>code block</pre>", False, 0.4),  # Below threshold (0.6)
        ]

        for content, should_block, expected_confidence in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_block:
                assert result.blocked is True  # At or above threshold
                assert result.confidence >= expected_confidence
                assert "code_blocks" in result.details["detected_code"]
            else:
                assert result.blocked is False  # Below threshold
                assert result.confidence >= expected_confidence
                assert "code_blocks" in result.details["detected_code"]

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_programming_keywords_detection(self, guardrail_instance):
        """Test programming keyword pattern detection."""
        # Valid programming keyword patterns
        test_cases = [
            ("function test() { return true; }", False, 0.2),  # Below threshold (0.6)
            ("class MyClass: def __init__(self): pass", False, 0.2),  # Below threshold (0.6)
            ("if condition: do_something()", False, 0.2),  # Below threshold (0.6)
        ]

        for content, should_block, expected_confidence in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_block:
                assert result.blocked is True  # Above threshold
                assert result.confidence >= expected_confidence
                assert "programming_keywords" in result.details["detected_code"]
            else:
                assert result.blocked is False  # Below threshold
                assert result.confidence >= expected_confidence
                assert "programming_keywords" in result.details["detected_code"]

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_code_injection_detection(self, guardrail_instance):
        """Test code injection pattern detection."""
        # Valid code injection patterns
        test_cases = [
            ("eval('malicious code')", False, 0.2),  # Below threshold (0.6)
            ("system('rm -rf /')", False, 0.2),  # Below threshold (0.6)
            ("console.log('debug')", False, 0.2),  # Below threshold (0.6)
            ("SELECT * FROM users", False, 0.2),  # Below threshold (0.6)
        ]

        for content, should_block, expected_confidence in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_block:
                assert result.blocked is True  # Above threshold
                assert result.confidence >= expected_confidence
                assert "code_injection" in result.details["detected_code"]
            else:
                assert result.blocked is False  # Below threshold
                assert result.confidence >= expected_confidence
                assert "code_injection" in result.details["detected_code"]

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_file_operations_detection(self, guardrail_instance):
        """Test file operation pattern detection."""
        # Valid file operation patterns
        test_cases = [
            ("file.read() and file.write()", True),  # Above threshold (0.6)
            (
                "mkdir directory and chmod 755",
                True,
            ),  # Above threshold (0.6) due to system_commands overlap
            ("copy file.txt to backup.txt", False),  # Below threshold (0.6)
        ]

        for content, should_block in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_block:
                assert result.blocked is True  # At or above threshold
                assert result.confidence == pytest.approx(
                    0.65
                ) or result.confidence == pytest.approx(0.8)
                assert "file_operations" in result.details["detected_code"]
            else:
                assert result.blocked is False  # Below threshold
                assert result.confidence == pytest.approx(0.5)
                assert "file_operations" in result.details["detected_code"]

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_system_commands_detection(self, guardrail_instance):
        """Test system command pattern detection."""
        # Valid system command patterns
        test_cases = [
            ("ls -la and cd /home", False, 0.2),  # Below threshold (0.6)
            ("git commit and npm install", False, 0.2),  # Below threshold (0.6)
            ("bash script.sh", False, 0.2),  # Below threshold (0.6)
        ]

        for content, should_block, expected_confidence in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_block:
                assert result.blocked is True  # Above threshold
                assert result.confidence >= expected_confidence
                assert "system_commands" in result.details["detected_code"]
            else:
                assert result.blocked is False  # Below threshold
                assert result.confidence >= expected_confidence
                assert "system_commands" in result.details["detected_code"]

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_multiple_code_detection(self, guardrail_instance):
        """Test detection of multiple code types in same content."""
        content = "```python\nfunction test() {\n  eval('code');\n  file.read();\n}\n```"
        result = await guardrail_instance.analyze(content)

        assert result.blocked is True
        assert result.confidence >= 0.6  # Higher confidence with multiple matches
        assert "code_blocks" in result.details["detected_code"]
        assert "programming_keywords" in result.details["detected_code"]
        assert "code_injection" in result.details["detected_code"]
        assert "file_operations" in result.details["detected_code"]
        assert len(result.details["detected_code"]) >= 4

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_minimum_keywords_threshold(self):
        """Test minimum keywords threshold behavior."""
        # Below minimum - should not block
        low_keywords_config = {
            "enabled": True,
            "categories": ["programming_keywords"],
            "confidence_threshold": 0.3,
            "min_keywords": 5,
            "on_error": "warn",
        }
        low_filter = SimpleCodeGenerationGuardrail("low_keywords", low_keywords_config)

        result = await low_filter.analyze("function test() { return; }")
        assert result.blocked is False  # Not enough keywords

        # Above minimum - should block
        high_keywords_config = {
            "enabled": True,
            "categories": ["programming_keywords"],
            "confidence_threshold": 0.3,
            "min_keywords": 2,
            "on_error": "warn",
        }
        high_filter = SimpleCodeGenerationGuardrail("high_keywords", high_keywords_config)

        result = await high_filter.analyze("function test() { return; }")
        assert result.blocked is True  # Enough keywords

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_confidence_threshold(self):
        """Test confidence threshold behavior."""
        # Low threshold - should block with single match
        low_threshold_config = {
            "enabled": True,
            "categories": ["code_blocks"],
            "confidence_threshold": 0.3,
            "min_keywords": 1,
            "on_error": "warn",
        }
        low_filter = SimpleCodeGenerationGuardrail("low_threshold", low_threshold_config)

        result = await low_filter.analyze("```code```")
        assert result.blocked is True

        # High threshold - should not block with single match
        high_threshold_config = {
            "enabled": True,
            "categories": ["code_blocks"],
            "confidence_threshold": 0.9,
            "min_keywords": 1,
            "on_error": "warn",
        }
        high_filter = SimpleCodeGenerationGuardrail("high_threshold", high_threshold_config)

        result = await high_filter.analyze("```code```")
        assert result.blocked is False

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_disabled_filter(self):
        """Test disabled filter behavior."""
        config = {"enabled": False}
        guardrail_instance = SimpleCodeGenerationGuardrail("disabled_filter", config)

        result = await guardrail_instance.analyze("```python\nprint('hello')\n```")
        assert result.blocked is False
        assert result.confidence == 0.0
        assert "disabled" in result.reason

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_no_code_detection(self, guardrail_instance):
        """Test content with no code."""
        content = "This is a normal text message without any code."
        result = await guardrail_instance.analyze(content)

        assert result.blocked is False
        assert result.confidence == 0.0
        assert "No code generation detected" in result.reason
        assert result.details["detected_code"] == []

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_false_positive_avoidance(self, guardrail_instance):
        """Test that similar but non-code content is not flagged."""
        # Similar patterns that shouldn't be flagged
        test_cases = [
            "I function well in my job",
            "The class was interesting",
            "If you want to succeed, work hard",
            "This is a file cabinet",
        ]

        for content in test_cases:
            result = await guardrail_instance.analyze(content)
            # These should not be detected as code
            assert result.blocked is False

    @pytest.mark.ci
    def test_configuration_methods(self, guardrail_instance):
        """Test configuration getter and setter methods."""
        # Test get_config
        config = guardrail_instance.get_config()
        assert config["enabled"] is True
        assert "code_blocks" in config["categories"]
        assert config["confidence_threshold"] == 0.6
        assert config["min_keywords"] == 1
        assert config["on_error"] == "warn"

        # Test update_config
        new_config = {
            "enabled": False,
            "confidence_threshold": 0.8,
            "min_keywords": 5,
            "on_error": "block",
        }
        success = guardrail_instance.update_config(new_config)
        assert success is True

        # Verify changes
        assert guardrail_instance.enabled is False
        assert guardrail_instance.confidence_threshold == 0.8
        assert guardrail_instance.min_keywords == 5
        assert guardrail_instance.on_error == "block"

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
        guardrail_instance = SimpleCodeGenerationGuardrail("error_test", config)

        # Test with empty content
        result = await guardrail_instance.analyze("")
        assert result.blocked is False
        assert "No code generation detected" in result.reason


if __name__ == "__main__":
    pytest.main([__file__])
