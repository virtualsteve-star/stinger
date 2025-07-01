#!/usr/bin/env python3
"""
Comprehensive tests for RegexGuardrail.

Tests cover:
- Basic pattern matching
- Case sensitivity options
- Multiple patterns
- Complex regex patterns
- Configuration validation
- Performance characteristics
"""

import pytest
import asyncio
import re
from unittest.mock import Mock

from src.stinger.guardrails.regex_guardrail import RegexGuardrail


class TestRegexFilter:
    """Test suite for RegexGuardrail functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.basic_config = {
            'patterns': [r'\d{3}-\d{2}-\d{4}', r'password'],
            'action': 'block',
            'case_sensitive': True,
            'on_error': 'allow'
        }

    @pytest.mark.asyncio
    async def test_basic_pattern_matching(self):
        """Test basic pattern matching functionality."""
        guardrail_instance = RegexGuardrail(self.basic_config)
        
        # Content matching SSN pattern
        content = "My SSN is 123-45-6789"
        result = await guardrail_instance.analyze(content)
        assert result.blocked == True
        assert 'Matched patterns:' in result.reason
        assert '\\d{3}-\\d{2}-\\d{4}' in result.reason
        
        # Content matching password pattern
        content = "My password is secret123"
        result = await guardrail_instance.analyze(content)
        assert result.blocked == True
        assert 'password' in result.reason
        
        # Content not matching any pattern
        content = "This is safe content"
        result = await guardrail_instance.analyze(content)
        assert result.blocked == False
        assert result.reason == 'No pattern matches found'

    @pytest.mark.asyncio
    async def test_case_sensitivity(self):
        """Test case sensitive and insensitive matching."""
        # Case sensitive (default)
        sensitive_config = {
            'patterns': ['Password'],
            'action': 'block',
            'case_sensitive': True,
            'on_error': 'allow'
        }
        guardrail_instance = RegexGuardrail(sensitive_config)
        
        # Exact case match
        result = await guardrail_instance.analyze("My Password is secret")
        assert result.blocked == True
        
        # Different case - should not match
        result = await guardrail_instance.analyze("My password is secret")
        assert result.blocked == False
        
        # Case insensitive
        insensitive_config = {
            'patterns': ['Password'],
            'action': 'block',
            'case_sensitive': False,
            'on_error': 'allow'
        }
        guardrail_instance = RegexGuardrail(insensitive_config)
        
        # Different cases should all match
        test_cases = [
            "My Password is secret",
            "My password is secret", 
            "My PASSWORD is secret",
            "My PaSSwoRd is secret"
        ]
        
        for test_case in test_cases:
            result = await guardrail_instance.analyze(test_case)
            assert result.blocked == True, f"Failed case insensitive match: {test_case}"

    @pytest.mark.asyncio
    async def test_multiple_pattern_matches(self):
        """Test content matching multiple patterns."""
        config = {
            'patterns': [r'\d{3}-\d{2}-\d{4}', r'password', r'\b\w+@\w+\.\w+\b'],
            'action': 'block',
            'on_error': 'allow'
        }
        guardrail_instance = RegexGuardrail(config)
        
        # Content matching multiple patterns
        content = "SSN: 123-45-6789, password: secret, email: test@example.com"
        result = await guardrail_instance.analyze(content)
        assert result.blocked == True
        assert 'Matched patterns:' in result.reason
        # Should report all matched patterns
        reason_patterns = result.reason.split(': ')[1]
        assert '\\d{3}-\\d{2}-\\d{4}' in reason_patterns
        assert 'password' in reason_patterns
        assert '\\b\\w+@\\w+\\.\\w+\\b' in reason_patterns

    @pytest.mark.asyncio
    async def test_complex_regex_patterns(self):
        """Test complex regex patterns."""
        complex_patterns = [
            r'(?i)\b(?:visa|mastercard|amex)\b',  # Credit card types
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  # IP addresses
            r'(?:https?|ftp)://[^\s/$.?#].[^\s]*',  # URLs
            r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b'  # IBAN
        ]
        
        config = {
            'patterns': complex_patterns,
            'action': 'block',
            'on_error': 'allow'
        }
        guardrail_instance = RegexGuardrail(config)
        
        test_cases = [
            ("I have a visa card", True),
            ("Card number: 1234 5678 9012 3456", True),
            ("Email me at user@domain.com", True),
            ("Server IP: 192.168.1.1", True),
            ("Visit https://example.com/path", True),
            ("Safe text with no patterns", False)
        ]
        
        for content, should_match in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_match:
                assert result.blocked == True, f"Should have matched: {content}"
            else:
                assert result.blocked == False, f"Should not have matched: {content}"

    @pytest.mark.asyncio
    async def test_regex_flags(self):
        """Test regex flags configuration."""
        # Test multiline flag
        config = {
            'patterns': [r'^password'],
            'action': 'block',
            'flags': re.MULTILINE,
            'on_error': 'allow'
        }
        guardrail_instance = RegexGuardrail(config)
        
        multiline_content = "Line 1\npassword on line 2\nLine 3"
        result = await guardrail_instance.analyze(multiline_content)
        assert result.blocked == True
        
        # Test dotall flag
        config = {
            'patterns': [r'start.*end'],
            'action': 'block',
            'flags': re.DOTALL,
            'on_error': 'allow'
        }
        guardrail_instance = RegexGuardrail(config)
        
        dotall_content = "start\nsome text\nend"
        result = await guardrail_instance.analyze(dotall_content)
        assert result.blocked == True

    @pytest.mark.asyncio
    async def test_empty_and_none_content(self):
        """Test handling of empty and None content."""
        guardrail_instance = RegexGuardrail(self.basic_config)
        
        # Empty string
        result = await guardrail_instance.analyze("")
        assert result.blocked == False
        assert result.reason == 'No content or patterns to match'
        
        # None content
        result = await guardrail_instance.analyze(None)
        assert result.blocked == False
        assert result.reason == 'No content or patterns to match'

    @pytest.mark.asyncio
    async def test_no_patterns_configured(self):
        """Test behavior when no patterns are configured."""
        config = {
            'patterns': [],
            'action': 'block',
            'on_error': 'allow'
        }
        guardrail_instance = RegexGuardrail(config)
        
        result = await guardrail_instance.analyze("Any content should be allowed")
        assert result.blocked == False
        assert result.reason == 'No content or patterns to match'

    @pytest.mark.asyncio
    async def test_different_actions(self):
        """Test different action configurations."""
        # Test warn action
        config = {
            'patterns': ['test'],
            'action': 'warn',
            'on_error': 'allow'
        }
        guardrail_instance = RegexGuardrail(config)
        
        result = await guardrail_instance.analyze("This is a test")
        # assert result.action == 'warn'  # TODO: GuardrailResult doesn't have action field
        assert 'Matched patterns: test' in result.reason
        
        # Test allow action (unusual but valid)
        config['action'] = 'allow'
        guardrail_instance = RegexGuardrail(config)
        
        result = await guardrail_instance.analyze("This is a test")
        assert result.blocked == True  # analyze always blocks when patterns match
        assert 'Matched patterns: test' in result.reason

    def test_invalid_regex_patterns(self):
        """Test handling of invalid regex patterns."""
        invalid_patterns = [
            r'[unclosed',
            r'(?P<name>invalid group',
            r'*invalid quantifier',
            r'(?invalid)',
            r'\x'  # Invalid escape
        ]
        
        for pattern in invalid_patterns:
            config = {
                'patterns': [pattern],
                'action': 'block',
                'on_error': 'allow'
            }
            
            with pytest.raises(ValueError, match="Invalid regex pattern"):
                RegexGuardrail(config)

    def test_config_validation_success(self):
        """Test successful configuration validation."""
        valid_configs = [
            {'patterns': [r'\d+'], 'action': 'block'},
            {'patterns': ['simple'], 'action': 'warn'},
            {'patterns': [r'\w+@\w+\.\w+'], 'action': 'allow'},
            {'patterns': [], 'action': 'block'},  # Empty patterns list
        ]
        
        for config in valid_configs:
            config['on_error'] = 'allow'
            guardrail_instance = RegexGuardrail(config)
            # Should not raise an exception during initialization

    def test_config_validation_failure(self):
        """Test configuration validation failures."""
        # Test patterns type validation
        with pytest.raises(ValueError, match="patterns must be of type list"):
            RegexGuardrail({'patterns': 'not_a_list', 'action': 'block', 'on_error': 'allow'})
        
        # Test action validation
        with pytest.raises(ValueError, match="action must be one of"):
            RegexGuardrail({'patterns': [r'\d+'], 'action': 'invalid_action', 'on_error': 'allow'})
        
        # Test invalid regex pattern
        with pytest.raises(ValueError, match="Invalid or unsafe regex pattern"):
            RegexGuardrail({'patterns': [r'[invalid'], 'action': 'block', 'on_error': 'allow'})

    @pytest.mark.asyncio
    async def test_unicode_content(self):
        """Test regex matching with unicode content."""
        config = {
            'patterns': [r'[émöjïs]', r'🚀'],
            'action': 'block',
            'on_error': 'allow'
        }
        guardrail_instance = RegexGuardrail(config)
        
        # Unicode character class
        result = await guardrail_instance.analyze("Content with émojis")
        assert result.blocked == True
        
        # Emoji pattern
        result = await guardrail_instance.analyze("Rocket emoji: 🚀")
        assert result.blocked == True
        
        # No unicode matches
        result = await guardrail_instance.analyze("Regular ASCII content")
        assert result.blocked == False

    @pytest.mark.asyncio
    async def test_anchored_patterns(self):
        """Test anchored regex patterns (^ and $)."""
        config = {
            'patterns': [r'^START', r'END$', r'^WHOLE_LINE$'],
            'action': 'block',
            'on_error': 'allow'
        }
        guardrail_instance = RegexGuardrail(config)
        
        test_cases = [
            ("START of line", True),   # Matches ^START
            ("End of line END", True), # Matches END$
            ("WHOLE_LINE", True),      # Matches ^WHOLE_LINE$
            ("Not START here", False), # Doesn't match ^START
            ("Not END here", False),   # Doesn't match END$
            ("Not WHOLE_LINE here", False)  # Doesn't match ^WHOLE_LINE$
        ]
        
        for content, should_match in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_match:
                assert result.blocked == True, f"Should have matched: {content}"
            else:
                assert result.blocked == False, f"Should not have matched: {content}"

    @pytest.mark.asyncio
    async def test_word_boundaries(self):
        """Test word boundary patterns (\\b)."""
        config = {
            'patterns': [r'\btest\b'],
            'action': 'block',
            'on_error': 'allow'
        }
        guardrail_instance = RegexGuardrail(config)
        
        test_cases = [
            ("This is a test", True),      # Word boundary match
            ("Testing code", False),       # Part of word, no boundary
            ("contest results", False),    # Part of word, no boundary  
            ("test-case", True),          # Word boundary with hyphen
            ("test.file", True),          # Word boundary with period
        ]
        
        for content, should_match in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_match:
                assert result.blocked == True, f"Should have matched: {content}"
            else:
                assert result.blocked == False, f"Should not have matched: {content}"

    @pytest.mark.asyncio
    async def test_lookahead_lookbehind(self):
        """Test lookahead and lookbehind assertions."""
        config = {
            'patterns': [
                r'password(?=\s*:)',      # Positive lookahead
                r'(?<=user\s)admin',      # Positive lookbehind
                r'secret(?!\s*key)'       # Negative lookahead
            ],
            'action': 'block',
            'on_error': 'allow'
        }
        guardrail_instance = RegexGuardrail(config)
        
        test_cases = [
            ("password: secret123", True),    # Matches password(?=\s*:)
            ("user admin access", True),      # Matches (?<=user\s)admin
            ("secret data", True),            # Matches secret(?!\s*key)
            ("password field", False),        # No colon after password
            ("admin user", False),            # admin not after "user "
            ("secret key", False),            # secret followed by key
        ]
        
        for content, should_match in test_cases:
            result = await guardrail_instance.analyze(content)
            if should_match:
                assert result.blocked == True, f"Should have matched: {content}"
            else:
                assert result.blocked == False, f"Should not have matched: {content}"

    @pytest.mark.asyncio
    async def test_performance_with_complex_patterns(self):
        """Test performance with complex patterns and large content."""
        complex_patterns = [
            r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'(?:https?|ftp)://(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?(?::\d+)?(?:/?|[/?]\S+)$',
            r'\b(?:\d[ -]*?){13,16}\b'
        ]
        
        config = {
            'patterns': complex_patterns,
            'action': 'block',
            'on_error': 'allow'
        }
        guardrail_instance = RegexGuardrail(config)
        
        # Large content for performance testing
        large_content = "Safe content. " * 1000 + "No patterns here."
        
        import time
        start_time = time.time()
        result = await guardrail_instance.analyze(large_content)
        end_time = time.time()
        
        # Should complete in reasonable time
        duration = end_time - start_time
        assert duration < 1.0, f"Performance test took too long: {duration}s"
        assert result.blocked == False

    @pytest.mark.asyncio
    async def test_concurrent_filtering(self):
        """Test concurrent filtering operations."""
        guardrail_instance = RegexGuardrail(self.basic_config)
        
        test_contents = [
            "Safe content",
            "SSN: 123-45-6789",
            "password: secret",
            "More safe content",
            "Both SSN 555-66-7777 and password"
        ]
        
        # Run concurrent filtering
        tasks = [guardrail_instance.analyze(content) for content in test_contents]
        results = await asyncio.gather(*tasks)
        
        # Verify results
        expected_actions = ['allow', 'block', 'block', 'allow', 'block']
        actual_actions = ['block' if result.blocked else 'allow' for result in results]
        assert actual_actions == expected_actions

    @pytest.mark.asyncio
    async def test_confidence_scoring(self):
        """Test confidence scoring in results."""
        guardrail_instance = RegexGuardrail(self.basic_config)
        
        content = "password: secret123"  # Lowercase to match pattern
        result = await guardrail_instance.analyze(content)
        assert hasattr(result, 'confidence')
        assert result.confidence == 1.0

    @pytest.mark.asyncio
    async def test_pattern_order_independence(self):
        """Test that pattern order doesn't affect results."""
        patterns = [r'\d{3}-\d{2}-\d{4}', r'password', r'\w+@\w+\.\w+']
        
        # Test with different pattern orders
        for i in range(3):
            rotated_patterns = patterns[i:] + patterns[:i]
            config = {
                'patterns': rotated_patterns,
                'action': 'block',
                'on_error': 'allow'
            }
            guardrail_instance = RegexGuardrail(config)
            
            content = "SSN: 123-45-6789, password: secret, email: test@example.com"
            result = await guardrail_instance.analyze(content)
            assert result.blocked == True
            assert 'Matched patterns:' in result.reason


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])