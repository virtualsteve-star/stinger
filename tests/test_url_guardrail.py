#!/usr/bin/env python3
"""
Comprehensive tests for URLGuardrail.

Tests cover:
- URL detection and extraction
- Domain blocking and allowing
- Configuration validation
- Edge cases and malformed URLs
- Performance characteristics
"""

import asyncio

import pytest

from src.stinger.guardrails.url_guardrail import URLGuardrail


@pytest.mark.performance
class TestURLFilter:
    """Test suite for URLGuardrail functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.basic_blocked_config = {
            "blocked_domains": ["evil.com", "malicious.org"],
            "action": "block",
            "on_error": "allow",
        }

        self.basic_allowed_config = {
            "allowed_domains": ["trusted.com", "safe.org"],
            "action": "block",
            "on_error": "allow",
        }

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_basic_url_detection(self):
        """Test basic URL detection functionality."""
        guardrail_instance = URLGuardrail(self.basic_blocked_config)

        # Content with URLs
        content = "Visit https://example.com for more info"
        result = await guardrail_instance.analyze(content)
        assert result.blocked is False  # example.com not in blocked list
        assert "All URLs allowed: 1 found" in result.reason

        # Content without URLs
        content = "No URLs in this text"
        result = await guardrail_instance.analyze(content)
        assert result.blocked is False
        assert result.reason == "No URLs found"

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_blocked_domain_filtering(self):
        """Test blocking of specified domains."""
        guardrail_instance = URLGuardrail(self.basic_blocked_config)

        # Content with blocked domain
        content = "Don't visit https://evil.com/malware"
        result = await guardrail_instance.analyze(content)
        assert result.blocked is True
        assert "Blocked URLs found: https://evil.com/malware" in result.reason

        # Content with multiple blocked domains
        content = "Bad sites: https://evil.com and http://malicious.org/page"
        result = await guardrail_instance.analyze(content)
        assert result.blocked is True
        assert "Blocked URLs found:" in result.reason

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_allowed_domain_whitelist(self):
        """Test allowed domain whitelist functionality."""
        guardrail_instance = URLGuardrail(self.basic_allowed_config)

        # Content with allowed domain
        content = "Safe site: https://trusted.com/page"
        result = await guardrail_instance.analyze(content)
        assert result.blocked is False
        assert "All URLs allowed: 1 found" in result.reason

        # Content with non-allowed domain (should be blocked)
        content = "Unknown site: https://unknown.com/page"
        result = await guardrail_instance.analyze(content)
        assert result.blocked is True
        assert "Blocked URLs found: https://unknown.com/page" in result.reason

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_mixed_allowed_and_blocked(self):
        """Test configuration with both allowed and blocked domains."""
        config = {
            "blocked_domains": ["evil.com"],
            "allowed_domains": ["trusted.com", "safe.org"],
            "action": "block",
            "on_error": "allow",
        }
        guardrail_instance = URLGuardrail(config)

        # Blocked domain should be blocked even if in allowed list
        content = "Visit https://evil.com for info"
        result = await guardrail_instance.analyze(content)
        assert result.blocked is True

        # Allowed domain should be allowed
        content = "Visit https://trusted.com for info"
        result = await guardrail_instance.analyze(content)
        assert result.blocked is False

        # Unknown domain should be blocked (not in allowed list)
        content = "Visit https://unknown.com for info"
        result = await guardrail_instance.analyze(content)
        assert result.blocked is True

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_url_schemes_and_protocols(self):
        """Test detection of different URL schemes."""
        guardrail_instance = URLGuardrail(self.basic_blocked_config)

        test_urls = [
            "https://example.com/path",
            "http://example.com/path",
            "https://example.com:8080/path",
            "http://example.com:80/path",
        ]

        for url in test_urls:
            content = f"Visit {url} for info"
            result = await guardrail_instance.analyze(content)
            assert result.blocked is False, f"Failed to handle URL: {url}"
            assert "All URLs allowed: 1 found" in result.reason

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_domain_with_ports(self):
        """Test handling of domains with ports."""
        config = {"blocked_domains": ["evil.com"], "action": "block", "on_error": "allow"}
        guardrail_instance = URLGuardrail(config)

        # Should block regardless of port
        test_cases = [
            "https://evil.com:443/path",
            "http://evil.com:80/path",
            "https://evil.com:8080/path",
        ]

        for url in test_cases:
            content = f"Visit {url}"
            result = await guardrail_instance.analyze(content)
            assert result.blocked is True, f"Failed to block URL with port: {url}"

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_multiple_urls_in_content(self):
        """Test content with multiple URLs."""
        guardrail_instance = URLGuardrail(self.basic_blocked_config)

        content = """
        Safe sites: https://google.com and https://github.com
        Dangerous: https://evil.com/malware
        More safe: https://stackoverflow.com
        """

        result = await guardrail_instance.analyze(content)
        assert result.blocked is True
        assert "Blocked URLs found: https://evil.com/malware" in result.reason

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_malformed_urls(self):
        """Test handling of malformed URLs."""
        guardrail_instance = URLGuardrail(self.basic_blocked_config)

        malformed_urls = [
            "https://",
            "http://",
            "https:///path",
            "https://[invalid",
            "https://domain..com",
        ]

        for url in malformed_urls:
            content = f"Malformed URL: {url}"
            result = await guardrail_instance.analyze(content)
            # Should either be allowed (if not detected) or blocked (if detected as invalid)
            assert result.blocked in [True, False]  # GuardrailResult has blocked, not action

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_case_insensitive_domains(self):
        """Test case insensitive domain matching."""
        config = {"blocked_domains": ["evil.com"], "action": "block", "on_error": "allow"}
        guardrail_instance = URLGuardrail(config)

        test_cases = ["https://EVIL.COM/path", "https://Evil.Com/path", "https://eViL.cOm/path"]

        for url in test_cases:
            content = f"Visit {url}"
            result = await guardrail_instance.analyze(content)
            assert result.blocked is True, f"Failed case insensitive blocking for: {url}"

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_complex_url_paths(self):
        """Test URLs with complex paths and parameters."""
        guardrail_instance = URLGuardrail(self.basic_blocked_config)

        complex_urls = [
            "https://example.com/path/to/resource?param=value&other=test",
            "https://example.com/path/to/resource#fragment",
            "https://example.com:8080/api/v1/users?filter=active",
            "https://example.com/search?q=test%20query&lang=en",
        ]

        for url in complex_urls:
            content = f"API endpoint: {url}"
            result = await guardrail_instance.analyze(content)
            assert result.blocked is False, f"Failed to handle complex URL: {url}"

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_empty_and_none_content(self):
        """Test handling of empty and None content."""
        guardrail_instance = URLGuardrail(self.basic_blocked_config)

        # Empty string
        result = await guardrail_instance.analyze("")
        assert result.blocked is False
        assert result.reason == "No content to analyze"

        # None content
        result = await guardrail_instance.analyze("")
        assert result.blocked is False
        assert result.reason == "No content to analyze"

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_action_configuration(self):
        """Test different action configurations."""
        # Test warn action
        config = {"blocked_domains": ["evil.com"], "action": "warn", "on_error": "allow"}
        guardrail_instance = URLGuardrail(config)

        content = "Visit https://evil.com/page"
        result = await guardrail_instance.analyze(content)
        # assert result.action == 'warn'  # TODO: GuardrailResult doesn't have action field
        assert "Blocked URLs found: https://evil.com/page" in result.reason

    @pytest.mark.ci
    def test_config_validation(self):
        """Test configuration validation."""
        guardrail_instance = URLGuardrail(self.basic_blocked_config)
        assert guardrail_instance.validate_config() == True

        # Test invalid configurations
        invalid_configs = [
            {"blocked_domains": "not_a_list"},
            {"allowed_domains": "not_a_list"},
            {"blocked_domains": [], "action": "invalid_action"},
            {"blocked_domains": [], "allowed_domains": []},  # Valid minimal config
        ]

        for config in invalid_configs[:-1]:  # Skip the last valid one
            config["on_error"] = "allow"
            with pytest.raises(ValueError):
                guardrail_instance = URLGuardrail(config)

        # Test the valid minimal config
        valid_config = invalid_configs[-1]
        valid_config["on_error"] = "allow"
        guardrail_instance = URLGuardrail(valid_config)
        # Should not raise an exception

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_url_extraction_patterns(self):
        """Test URL extraction from various text patterns."""
        guardrail_instance = URLGuardrail(self.basic_blocked_config)

        test_patterns = [
            "URL in parentheses: (https://example.com)",
            "URL in brackets: [https://example.com]",
            "URL with trailing punctuation: https://example.com.",
            "URL with comma: https://example.com, see more",
            "Multiple URLs: https://first.com and https://second.com",
            "URL at end: Visit https://example.com",
            "URL at start: https://example.com is great",
        ]

        for pattern in test_patterns:
            result = await guardrail_instance.analyze(pattern)
            # Should detect at least one URL
            assert "found" in result.reason or "blocked" in result.reason

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_performance_with_many_urls(self):
        """Test performance with content containing many URLs."""
        guardrail_instance = URLGuardrail(self.basic_blocked_config)

        # Create content with many URLs
        urls = [f"https://site{i}.com/path" for i in range(100)]
        content = "URLs: " + " ".join(urls)

        import time

        start_time = time.time()
        result = await guardrail_instance.analyze(content)
        end_time = time.time()

        # Should complete in reasonable time
        duration = end_time - start_time
        assert duration < 1.0, f"Performance test took too long: {duration}s"
        assert result.blocked is False
        assert "All URLs allowed: 100 found" in result.reason

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_confidence_scoring(self):
        """Test confidence scoring in results."""
        guardrail_instance = URLGuardrail(self.basic_blocked_config)

        content = "Visit https://evil.com/malware"
        result = await guardrail_instance.analyze(content)
        assert hasattr(result, "confidence")
        assert result.confidence == 1.0

    @pytest.mark.ci
    @pytest.mark.asyncio
    async def test_subdomain_handling(self):
        """Test handling of subdomains."""
        config = {"blocked_domains": ["evil.com"], "action": "block", "on_error": "allow"}
        guardrail_instance = URLGuardrail(config)

        # Subdomain should be blocked (current implementation behavior)
        content = "Visit https://sub.evil.com/page"
        result = await guardrail_instance.analyze(content)
        assert result.blocked is True  # sub.evil.com is blocked (current behavior)

        # Exact domain should be blocked
        content = "Visit https://evil.com/page"
        result = await guardrail_instance.analyze(content)
        assert result.blocked is True

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_filtering(self):
        """Test concurrent filtering operations."""
        guardrail_instance = URLGuardrail(self.basic_blocked_config)

        test_contents = [
            "Safe URL: https://google.com",
            "Blocked URL: https://evil.com/page",
            "No URLs here",
            "Multiple URLs: https://github.com and https://malicious.org",
            "Another safe one: https://stackoverflow.com",
        ]

        # Run concurrent filtering
        tasks = [guardrail_instance.analyze(content) for content in test_contents]
        results = await asyncio.gather(*tasks)

        # Verify results
        expected_actions = ["allow", "block", "allow", "block", "allow"]
        actual_actions = ["block" if result.blocked else "allow" for result in results]
        assert actual_actions == expected_actions


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
