#!/usr/bin/env python3
"""
Comprehensive tests for KeywordBlockFilter.

Tests cover:
- Basic keyword blocking functionality
- Case sensitivity handling
- Configuration validation
- Edge cases and error handling
- Performance characteristics
"""

import pytest
import asyncio
from unittest.mock import Mock

from src.stinger.filters.keyword_block import KeywordBlockFilter


class TestKeywordBlockFilter:
    """Test suite for KeywordBlockFilter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.basic_config = {
            'keyword': 'blocked_word',
            'on_error': 'allow'
        }

    @pytest.mark.asyncio
    async def test_basic_keyword_blocking(self):
        """Test basic keyword blocking functionality."""
        filter_instance = KeywordBlockFilter(self.basic_config)
        
        # Test blocking
        result = await filter_instance.analyze("This contains blocked_word in text")
        assert result.blocked == True
        assert 'Blocked keyword found: blocked_word' in result.reason
        
        # Test allowing
        result = await filter_instance.analyze("This contains safe content")
        assert result.blocked == False
        assert result.reason == 'No keyword match found'

    @pytest.mark.asyncio
    async def test_case_insensitive_matching(self):
        """Test that keyword matching is case insensitive."""
        filter_instance = KeywordBlockFilter(self.basic_config)
        
        test_cases = [
            "Text with BLOCKED_WORD in caps",
            "Text with Blocked_Word in mixed case", 
            "Text with blocked_word in lowercase",
            "Text with BlOcKeD_wOrD in random case"
        ]
        
        for test_case in test_cases:
            result = await filter_instance.analyze(test_case)
            assert result.blocked == True, f"Failed to block: {test_case}"
            assert 'Blocked keyword found: blocked_word' in result.reason

    @pytest.mark.asyncio
    async def test_partial_word_matching(self):
        """Test that partial words are matched."""
        filter_instance = KeywordBlockFilter({'keyword': 'test', 'on_error': 'allow'})
        
        # Should match partial words
        result = await filter_instance.analyze("This is a testing example")
        assert result.blocked == True
        
        result = await filter_instance.analyze("Contest results are here")
        assert result.blocked == True

    @pytest.mark.asyncio
    async def test_empty_and_none_content(self):
        """Test handling of empty and None content."""
        filter_instance = KeywordBlockFilter(self.basic_config)
        
        # Empty string
        result = await filter_instance.analyze("")
        assert result.blocked == False
        assert result.reason == 'No content to analyze'
        
        # None content
        result = await filter_instance.analyze(None)
        assert result.blocked == False
        assert result.reason == 'No content to analyze'

    @pytest.mark.asyncio
    async def test_no_keyword_configured(self):
        """Test behavior when no keyword is configured."""
        config = {'on_error': 'allow'}  # No keyword
        filter_instance = KeywordBlockFilter(config)
        
        result = await filter_instance.analyze("Any content should be allowed")
        assert result.blocked == False
        assert result.reason == 'No keyword configured'

    @pytest.mark.asyncio
    async def test_empty_keyword_configured(self):
        """Test behavior when empty keyword is configured."""
        config = {'keyword': '', 'on_error': 'allow'}
        filter_instance = KeywordBlockFilter(config)
        
        result = await filter_instance.analyze("Any content should be allowed")
        assert result.blocked == False
        assert result.reason == 'No keyword configured'

    @pytest.mark.asyncio
    async def test_whitespace_keyword(self):
        """Test behavior with whitespace-only keyword."""
        config = {'keyword': '   ', 'on_error': 'allow'}
        filter_instance = KeywordBlockFilter(config)
        
        result = await filter_instance.analyze("Content with   spaces")
        assert result.blocked == True
        assert 'Blocked keyword found:' in result.reason

    @pytest.mark.asyncio
    async def test_special_characters_in_keyword(self):
        """Test keywords with special characters."""
        special_keywords = [
            'test@example.com',
            'user-name',
            'key_value',
            'test.domain',
            'user+tag',
            'file.txt',
            '$variable',
            '#hashtag'
        ]
        
        for keyword in special_keywords:
            config = {'keyword': keyword, 'on_error': 'allow'}
            filter_instance = KeywordBlockFilter(config)
            
            result = await filter_instance.analyze(f"Text containing {keyword} should be blocked")
            assert result.blocked == True, f"Failed to block keyword: {keyword}"
            assert f'Blocked keyword found: {keyword.lower()}' in result.reason

    @pytest.mark.asyncio
    async def test_unicode_content(self):
        """Test handling of unicode content."""
        config = {'keyword': 'test', 'on_error': 'allow'}
        filter_instance = KeywordBlockFilter(config)
        
        # Unicode content without keyword
        result = await filter_instance.analyze("Content with émojis 🚀 and spëcial chars")
        assert result.blocked == False
        
        # Unicode content with keyword
        result = await filter_instance.analyze("test with émojis 🚀 and spëcial chars")
        assert result.blocked == True

    @pytest.mark.asyncio
    async def test_very_long_content(self):
        """Test performance with very long content."""
        config = {'keyword': 'needle', 'on_error': 'allow'}
        filter_instance = KeywordBlockFilter(config)
        
        # Long content without keyword
        long_content = "haystack " * 10000
        result = await filter_instance.analyze(long_content)
        assert result.blocked == False
        
        # Long content with keyword at the end
        long_content_with_keyword = long_content + " needle"
        result = await filter_instance.analyze(long_content_with_keyword)
        assert result.blocked == True

    @pytest.mark.asyncio
    async def test_multiple_keyword_occurrences(self):
        """Test content with multiple occurrences of keyword."""
        filter_instance = KeywordBlockFilter(self.basic_config)
        
        content = "blocked_word appears multiple times: blocked_word and BLOCKED_WORD"
        result = await filter_instance.analyze(content)
        assert result.blocked == True
        assert 'Blocked keyword found: blocked_word' in result.reason

    @pytest.mark.asyncio
    async def test_concurrent_filtering(self):
        """Test concurrent filtering operations."""
        filter_instance = KeywordBlockFilter(self.basic_config)
        
        test_contents = [
            "Safe content 1",
            "Content with blocked_word",
            "More safe content",
            "Another blocked_word occurrence",
            "Final safe content"
        ]
        
        # Run concurrent filtering
        tasks = [filter_instance.analyze(content) for content in test_contents]
        results = await asyncio.gather(*tasks)
        
        # Verify results
        expected_actions = ['allow', 'block', 'allow', 'block', 'allow']
        actual_actions = ['block' if result.blocked else 'allow' for result in results]
        assert actual_actions == expected_actions

    def test_filter_initialization(self):
        """Test filter initialization with various configurations."""
        # Valid configuration
        valid_config = {'keyword': 'test', 'on_error': 'allow'}
        filter_instance = KeywordBlockFilter(valid_config)
        assert filter_instance.config['keyword'] == 'test'
        
        # Configuration with extra fields
        config_with_extras = {
            'keyword': 'test',
            'on_error': 'allow',
            'extra_field': 'ignored'
        }
        filter_instance = KeywordBlockFilter(config_with_extras)
        assert filter_instance.config['keyword'] == 'test'
        assert filter_instance.config.get('extra_field') == 'ignored'

    @pytest.mark.asyncio
    async def test_edge_case_keywords(self):
        """Test edge case keywords."""
        edge_cases = [
            ('\\n', 'Content with\\nnewlines'),  # Newline character
            ('\\t', 'Content with\\ttabs'),      # Tab character  
            (' ', 'Content with spaces'),        # Single space
            ('a', 'Any content with letter a'),  # Single character
            ('🚀', 'Content with 🚀 emoji'),     # Emoji keyword
        ]
        
        for keyword, test_content in edge_cases:
            config = {'keyword': keyword, 'on_error': 'allow'}
            filter_instance = KeywordBlockFilter(config)
            
            result = await filter_instance.analyze(test_content)
            assert result.blocked == True, f"Failed to block keyword: {repr(keyword)}"

    @pytest.mark.asyncio
    async def test_filter_result_structure(self):
        """Test that FilterResult has correct structure."""
        filter_instance = KeywordBlockFilter(self.basic_config)
        
        result = await filter_instance.analyze("Content with blocked_word")
        
        # Check FilterResult structure
        assert hasattr(result, 'blocked')
        assert hasattr(result, 'reason')
        assert isinstance(result.blocked, bool)
        assert isinstance(result.reason, str)
        assert len(result.reason) > 0

    @pytest.mark.asyncio 
    async def test_performance_benchmarking(self):
        """Test performance characteristics of the filter."""
        import time
        
        filter_instance = KeywordBlockFilter(self.basic_config)
        
        # Test multiple runs for performance
        start_time = time.time()
        for _ in range(1000):
            await filter_instance.analyze("Test content without keyword")
        end_time = time.time()
        
        # Should complete 1000 runs in reasonable time (< 1 second)
        duration = end_time - start_time
        assert duration < 1.0, f"Performance test took too long: {duration}s"

if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])