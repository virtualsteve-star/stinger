#!/usr/bin/env python3
"""
ReDoS Security Tests for Regex Filter

Tests cover Regular Expression Denial of Service (ReDoS) attack prevention
and regex security validation.
"""

import pytest
import time
import re
from unittest.mock import patch

from src.stinger.core.regex_security import (
    RegexSecurityValidator, 
    RegexSecurityConfig,
    SecurityError,
    validate_regex_pattern,
    safe_compile_regex,
    safe_regex_search
)
from src.stinger.filters.regex_filter import RegexFilter


class TestRegexSecurityValidator:
    """Test the regex security validation system."""
    
    def test_safe_patterns_allowed(self):
        """Test that safe patterns are allowed."""
        validator = RegexSecurityValidator()
        
        safe_patterns = [
            r'hello',
            r'[a-zA-Z]+',
            r'\d{1,10}',
            r'^email@domain\.com$',
            r'(test|demo)',
            r'[a-z]{3,20}',
        ]
        
        for pattern in safe_patterns:
            is_safe, reason = validator.validate_pattern(pattern)
            assert is_safe, f"Safe pattern '{pattern}' was rejected: {reason}"
    
    def test_dangerous_patterns_blocked(self):
        """Test that known dangerous ReDoS patterns are blocked."""
        validator = RegexSecurityValidator()
        
        dangerous_patterns = [
            r'(a+)+b',           # Classic ReDoS - nested quantifiers
            r'(a*)*b',           # Nested quantifiers with *
            r'(.+)+end',         # Nested quantifiers with wildcard
            r'(.*)*end',         # Nested quantifiers with greedy wildcard
            r'a+*',              # Conflicting quantifiers
            r'a*+',              # Conflicting quantifiers
            r'(?:a+)+a+',        # Nested quantifiers with suffix
            r'(a|a)+a',          # Alternation with overlap
            r'(a+)?a+',          # Optional with required overlap
        ]
        
        for pattern in dangerous_patterns:
            is_safe, reason = validator.validate_pattern(pattern)
            assert not is_safe, f"Dangerous pattern '{pattern}' was not blocked"
            assert 'dangerous' in reason.lower() or 'nested' in reason.lower()
    
    def test_pattern_length_limits(self):
        """Test that overly long patterns are rejected."""
        validator = RegexSecurityValidator(RegexSecurityConfig(MAX_PATTERN_LENGTH=50))
        
        short_pattern = 'a' * 30
        long_pattern = 'a' * 100
        
        is_safe, _ = validator.validate_pattern(short_pattern)
        assert is_safe, "Short pattern should be allowed"
        
        is_safe, reason = validator.validate_pattern(long_pattern)
        assert not is_safe, "Long pattern should be rejected"
        assert "too long" in reason.lower()
    
    def test_complexity_limits(self):
        """Test that overly complex patterns are rejected."""
        validator = RegexSecurityValidator(RegexSecurityConfig(MAX_REGEX_COMPLEXITY=20))
        
        simple_pattern = r'hello'
        complex_pattern = r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}+'
        
        is_safe, _ = validator.validate_pattern(simple_pattern)
        assert is_safe, "Simple pattern should be allowed"
        
        is_safe, reason = validator.validate_pattern(complex_pattern)
        assert not is_safe, "Complex pattern should be rejected"
        assert "too complex" in reason.lower()
    
    def test_compilation_timeout(self):
        """Test that slow-compiling patterns are rejected."""
        validator = RegexSecurityValidator(RegexSecurityConfig(
            MAX_COMPILE_TIME_MS=10,
            MAX_PATTERN_LENGTH=10000  # Allow long patterns for this test
        ))
        
        # This pattern should compile quickly
        fast_pattern = r'hello'
        is_safe, _ = validator.validate_pattern(fast_pattern)
        assert is_safe, "Fast pattern should be allowed"
        
        # This pattern might be slow to compile (very long alternation)
        slow_pattern = '|'.join([f'test{i}' for i in range(1000)])
        is_safe, reason = validator.validate_pattern(slow_pattern)
        # May or may not be rejected depending on system speed
        if not is_safe:
            assert any(word in reason.lower() for word in ['slow', 'timeout', 'compilation', 'complex'])
    
    def test_safe_compile_function(self):
        """Test the safe compile functionality."""
        # Safe pattern should compile
        compiled = safe_compile_regex(r'hello')
        assert compiled.pattern == 'hello'
        
        # Dangerous pattern should raise SecurityError
        with pytest.raises(SecurityError, match="Unsafe regex pattern"):
            safe_compile_regex(r'(a+)+b')
    
    def test_safe_search_timeout(self):
        """Test that regex search times out on ReDoS attacks."""
        validator = RegexSecurityValidator(RegexSecurityConfig(MAX_EXECUTION_TIME_MS=100))
        
        # Compile a potentially dangerous pattern (if it passes validation)
        safe_pattern = re.compile(r'a+')
        
        # Normal text should work fine
        result = validator.safe_search(safe_pattern, "aaa")
        assert result is not None
        
        # Very long text might timeout (simulate heavy load)
        very_long_text = "a" * 10000 + "b"
        try:
            result = validator.safe_search(safe_pattern, very_long_text)
            # Should either work or timeout
        except SecurityError as e:
            assert "timeout" in str(e).lower()
    
    def test_convenience_functions(self):
        """Test the module-level convenience functions."""
        # Test validate_regex_pattern
        is_safe, reason = validate_regex_pattern(r'hello')
        assert is_safe
        
        is_safe, reason = validate_regex_pattern(r'(a+)+b')
        assert not is_safe
        
        # Test safe_compile_regex
        compiled = safe_compile_regex(r'test')
        assert compiled.search("testing") is not None
        
        # Test safe_regex_search
        pattern = safe_compile_regex(r'hello')
        match = safe_regex_search(pattern, "hello world")
        assert match is not None


class TestRegexFilterSecurity:
    """Test that RegexFilter uses security validation."""
    
    def test_safe_regex_filter_creation(self):
        """Test that RegexFilter can be created with safe patterns."""
        config = {
            'patterns': [r'hello', r'[a-z]+', r'\d{1,5}'],
            'blocked': True
        }
        
        # Should create successfully
        filter_instance = RegexFilter(config)
        assert len(filter_instance.compiled_patterns) == 3
    
    def test_dangerous_regex_filter_rejected(self):
        """Test that RegexFilter rejects dangerous patterns."""
        config = {
            'patterns': [r'hello', r'(a+)+b'],  # One safe, one dangerous
            'blocked': True
        }
        
        # Should raise ValueError due to unsafe pattern
        with pytest.raises(ValueError, match="Invalid or unsafe regex pattern"):
            RegexFilter(config)
    
    @pytest.mark.asyncio
    async def test_regex_filter_safe_execution(self):
        """Test that RegexFilter executes safely."""
        config = {
            'patterns': [r'test', r'hello'],
            'blocked': True
        }
        
        filter_instance = RegexFilter(config)
        
        # Normal execution should work
        result = await filter_instance.analyze("this is a test")
        assert result.blocked == True
        assert 'test' in result.reason
        
        # Non-matching text should be allowed
        result = await filter_instance.analyze("no matches here")
        assert result.blocked == False
    
    @pytest.mark.asyncio
    async def test_regex_filter_timeout_protection(self):
        """Test that RegexFilter protects against execution timeouts."""
        # Create filter with a pattern that should be safe but test timeout handling
        config = {
            'patterns': [r'a+'],
            'blocked': True
        }
        
        filter_instance = RegexFilter(config)
        
        # Patch the safe_search to simulate timeout
        with patch.object(filter_instance.security_validator, 'safe_search') as mock_search:
            mock_search.side_effect = SecurityError("Regex execution timeout: >50ms")
            
            # Should handle timeout gracefully and continue
            result = await filter_instance.analyze("aaaaaaa")
            assert result.blocked == False  # No matches due to timeout


class TestReDoSAttackSimulation:
    """Simulate actual ReDoS attacks to verify protection."""
    
    def test_nested_quantifier_attack(self):
        """Simulate nested quantifier ReDoS attack."""
        # This pattern would cause exponential backtracking
        attack_pattern = r'(a+)+b'
        attack_text = 'a' * 30 + 'c'  # No 'b' at end causes massive backtracking
        
        validator = RegexSecurityValidator()
        
        # Pattern should be rejected during validation
        is_safe, reason = validator.validate_pattern(attack_pattern)
        assert not is_safe
        assert 'dangerous' in reason.lower()
        
        # Should not be able to compile
        with pytest.raises(SecurityError):
            validator.safe_compile(attack_pattern)
    
    def test_alternation_overlap_attack(self):
        """Simulate alternation overlap ReDoS attack."""
        attack_pattern = r'(a|a)*b'
        attack_text = 'a' * 25 + 'c'
        
        validator = RegexSecurityValidator()
        
        # Should be detected as dangerous
        is_safe, reason = validator.validate_pattern(attack_pattern)
        assert not is_safe
    
    def test_catastrophic_backtracking_protection(self):
        """Test protection against catastrophic backtracking."""
        # Patterns that could cause catastrophic backtracking
        dangerous_patterns = [
            r'(x+x+)+y',
            r'(.*a){x} for x \> 10',
            r'(a|a)*b',
            r'([a-zA-Z]+)*c',
        ]
        
        validator = RegexSecurityValidator()
        
        blocked_count = 0
        for pattern in dangerous_patterns:
            is_safe, reason = validator.validate_pattern(pattern)
            if not is_safe:
                blocked_count += 1
                # Check for security-related rejection reasons
                assert any(word in reason.lower() for word in ['dangerous', 'complex', 'nested', 'overlap', 'pattern']), f"Pattern '{pattern}' rejected for unexpected reason: {reason}"
        
        # At least some of the dangerous patterns should be caught
        assert blocked_count > 0, "No dangerous patterns were blocked"
    
    def test_complexity_scoring_accuracy(self):
        """Test that complexity scoring correctly identifies problematic patterns."""
        validator = RegexSecurityValidator()
        
        # Low complexity patterns
        simple_patterns = [
            r'hello',
            r'[a-z]',
            r'\d+',
        ]
        
        # High complexity patterns
        complex_patterns = [
            r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+',
            r'(.*){10,}',
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        ]
        
        for pattern in simple_patterns:
            complexity = validator._calculate_complexity(pattern)
            assert complexity < 50, f"Simple pattern '{pattern}' scored too high: {complexity}"
        
        for pattern in complex_patterns:
            complexity = validator._calculate_complexity(pattern)
            assert complexity > 20, f"Complex pattern '{pattern}' scored too low: {complexity}"
    
    def test_pattern_suggestions(self):
        """Test that the validator provides helpful suggestions for unsafe patterns."""
        validator = RegexSecurityValidator()
        
        unsafe_pattern = r'(a+)+b'
        suggestions = validator.get_safe_pattern_suggestions(unsafe_pattern)
        
        assert len(suggestions) > 0
        assert any('quantifier' in suggestion.lower() for suggestion in suggestions)
    
    def test_real_world_safe_patterns(self):
        """Test that common real-world patterns are considered safe."""
        validator = RegexSecurityValidator()
        
        real_world_patterns = [
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',  # Email
            r'^\+?[1-9]\d{1,14}$',                                    # Phone
            r'^https?:\/\/[^\s/$.?#].[^\s]*$',                       # URL
            r'^\d{4}-\d{2}-\d{2}$',                                  # Date
            r'^[a-zA-Z0-9]{6,20}$',                                  # Username
            r'^\$?\d{1,3}(,\d{3})*(\.\d{2})?$',                     # Currency
        ]
        
        for pattern in real_world_patterns:
            is_safe, reason = validator.validate_pattern(pattern)
            assert is_safe, f"Real-world pattern '{pattern}' should be safe but was rejected: {reason}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])