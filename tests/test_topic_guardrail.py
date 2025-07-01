import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

"""
Tests for Topic Filter

This module tests the topic filtering capabilities including allow/deny lists,
different modes, regex support, and edge cases.
"""

import pytest
import asyncio
from stinger.guardrails.topic_guardrail import TopicGuardrail


class TestTopicFilter:
    """Test the TopicGuardrail class."""
    
    def test_filter_creation(self):
        """Test basic filter creation."""
        config = {
            'name': 'test_topic_filter',
            'enabled': True,
            'allow_topics': ['allowed1', 'allowed2'],
            'deny_topics': ['denied1', 'denied2'],
            'mode': 'deny'
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        assert guardrail_obj.name == 'test_topic_filter'
        assert guardrail_obj.enabled is True
        assert guardrail_obj.allow_topics == ['allowed1', 'allowed2']
        assert guardrail_obj.deny_topics == ['denied1', 'denied2']
        assert guardrail_obj.mode == 'deny'
    
    def test_filter_creation_with_defaults(self):
        """Test filter creation with default values."""
        config = {'name': 'test_filter'}
        
        guardrail_obj = TopicGuardrail(config)
        
        assert guardrail_obj.allow_topics == []
        assert guardrail_obj.deny_topics == []
        assert guardrail_obj.mode == 'deny'
        assert guardrail_obj.case_sensitive is False
        assert guardrail_obj.use_regex is False
        assert guardrail_obj.confidence_threshold == 0.5
    
    @pytest.mark.asyncio
    async def test_deny_mode_blocked(self):
        """Test deny mode when content should be blocked."""
        config = {
            'name': 'deny_test',
            'mode': 'deny',
            'deny_topics': ['politics', 'religion']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        result = await guardrail_obj.analyze("I want to discuss politics and religion")
        
        assert result.blocked == True
        assert 'politics' in result.reason
        assert result.confidence > 0
    
    @pytest.mark.asyncio
    async def test_deny_mode_allowed(self):
        """Test deny mode when content should be allowed."""
        config = {
            'name': 'deny_test',
            'mode': 'deny',
            'deny_topics': ['politics', 'religion']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        result = await guardrail_obj.analyze("I need help with my account")
        
        assert result.blocked == False
        assert 'denied topics' not in result.reason
    
    @pytest.mark.asyncio
    async def test_allow_mode_blocked(self):
        """Test allow mode when content should be blocked."""
        config = {
            'name': 'allow_test',
            'mode': 'allow',
            'allow_topics': ['customer service', 'billing']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        result = await guardrail_obj.analyze("I want to discuss politics")
        
        assert result.blocked == True
        assert 'allowed topics' in result.reason
        assert result.confidence == 1.0
    
    @pytest.mark.asyncio
    async def test_allow_mode_allowed(self):
        """Test allow mode when content should be allowed."""
        config = {
            'name': 'allow_test',
            'mode': 'allow',
            'allow_topics': ['customer service', 'billing']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        result = await guardrail_obj.analyze("I need customer service help")
        
        assert result.blocked == False
        assert 'customer service' in result.reason
    
    @pytest.mark.asyncio
    async def test_both_mode_deny_priority(self):
        """Test both mode with deny taking priority."""
        config = {
            'name': 'both_test',
            'mode': 'both',
            'allow_topics': ['customer service', 'billing'],
            'deny_topics': ['politics']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        result = await guardrail_obj.analyze("I need customer service but also want to discuss politics")
        
        assert result.blocked == True
        assert 'politics' in result.reason
    
    @pytest.mark.asyncio
    async def test_both_mode_allow_check(self):
        """Test both mode with allow list check."""
        config = {
            'name': 'both_test',
            'mode': 'both',
            'allow_topics': ['customer service', 'billing'],
            'deny_topics': []
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        result = await guardrail_obj.analyze("I want to discuss sports")
        
        assert result.blocked == True
        assert 'allowed topics' in result.reason
    
    @pytest.mark.asyncio
    async def test_both_mode_allowed(self):
        """Test both mode when content should be allowed."""
        config = {
            'name': 'both_test',
            'mode': 'both',
            'allow_topics': ['customer service', 'billing'],
            'deny_topics': ['politics']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        result = await guardrail_obj.analyze("I need customer service help")
        
        assert result.blocked == False
        assert 'Content matches allowed topics' in result.reason
    
    @pytest.mark.asyncio
    async def test_case_sensitive_matching(self):
        """Test case sensitive matching."""
        config = {
            'name': 'case_test',
            'mode': 'deny',
            'case_sensitive': True,
            'deny_topics': ['POLITICS']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        # Should not match due to case sensitivity
        result = await guardrail_obj.analyze("I want to discuss politics")
        assert result.blocked == False
        
        # Should match
        result = await guardrail_obj.analyze("I want to discuss POLITICS")
        assert result.blocked == True
    
    @pytest.mark.asyncio
    async def test_case_insensitive_matching(self):
        """Test case insensitive matching."""
        config = {
            'name': 'case_test',
            'mode': 'deny',
            'case_sensitive': False,
            'deny_topics': ['politics']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        # Should match regardless of case
        result = await guardrail_obj.analyze("I want to discuss POLITICS")
        assert result.blocked == True
        
        result = await guardrail_obj.analyze("I want to discuss Politics")
        assert result.blocked == True
    
    @pytest.mark.asyncio
    async def test_regex_matching(self):
        """Test regex pattern matching."""
        config = {
            'name': 'regex_test',
            'mode': 'deny',
            'use_regex': True,
            'deny_topics': [r'\b(spam|scam)\b']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        # Should match
        result = await guardrail_obj.analyze("This is spam content")
        assert result.blocked == True
        
        # Should not match (word boundary)
        result = await guardrail_obj.analyze("This is spammy content")
        assert result.blocked == False
    
    @pytest.mark.asyncio
    async def test_confidence_threshold(self):
        """Test confidence threshold filtering."""
        config = {
            'name': 'confidence_test',
            'mode': 'deny',
            'deny_topics': ['politics', 'religion', 'gambling'],
            'confidence_threshold': 0.8
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        # One match out of three topics = 0.33 confidence, below threshold
        result = await guardrail_obj.analyze("I want to discuss politics")
        assert result.blocked == False
        assert 'Confidence' in result.reason
    
    @pytest.mark.asyncio
    async def test_disabled_filter(self):
        """Test disabled filter behavior."""
        config = {
            'name': 'disabled_test',
            'enabled': False,
            'mode': 'deny',
            'deny_topics': ['politics']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        result = await guardrail_obj.analyze("I want to discuss politics")
        assert result.blocked == False
        assert 'disabled' in result.reason
    
    @pytest.mark.asyncio
    async def test_empty_content(self):
        """Test behavior with empty content."""
        config = {
            'name': 'empty_test',
            'mode': 'deny',
            'deny_topics': ['politics']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        result = await guardrail_obj.analyze("")
        assert result.blocked == False
        assert 'Empty content' in result.reason
    
    def test_guardrail_interface_compatibility(self):
        """Test GuardrailInterface compatibility."""
        config = {
            'name': 'interface_test',
            'mode': 'deny',
            'deny_topics': ['politics']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        # Test check method
        result = guardrail_obj.check("I want to discuss politics")
        assert result['blocked'] is True
        assert 'politics' in result['reasons'][0]
    
    def test_get_config(self):
        """Test configuration retrieval."""
        config = {
            'name': 'config_test',
            'mode': 'both',
            'allow_topics': ['allowed'],
            'deny_topics': ['denied'],
            'case_sensitive': True,
            'use_regex': True,
            'confidence_threshold': 0.8
        }
        
        guardrail_obj = TopicGuardrail(config)
        retrieved_config = guardrail_obj.get_config()
        
        assert retrieved_config['type'] == 'topic_filter'
        assert retrieved_config['name'] == 'config_test'
        assert retrieved_config['mode'] == 'both'
        assert retrieved_config['allow_topics'] == ['allowed']
        assert retrieved_config['deny_topics'] == ['denied']
        assert retrieved_config['case_sensitive'] is True
        assert retrieved_config['use_regex'] is True
        assert retrieved_config['confidence_threshold'] == 0.8
    
    def test_update_config(self):
        """Test configuration updates."""
        config = {
            'name': 'update_test',
            'mode': 'deny',
            'deny_topics': ['old_topic']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        # Update configuration
        new_config = {
            'deny_topics': ['new_topic'],
            'mode': 'allow',
            'allow_topics': ['allowed_topic']
        }
        
        success = guardrail_obj.update_config(new_config)
        assert success is True
        
        assert guardrail_obj.deny_topics == ['new_topic']
        assert guardrail_obj.mode == 'allow'
        assert guardrail_obj.allow_topics == ['allowed_topic']
    
    def test_get_guardrail_type(self):
        """Test guardrail type."""
        config = {'name': 'type_test'}
        guardrail_obj = TopicGuardrail(config)
        
        guardrail_type = guardrail_obj.get_guardrail_type()
        assert guardrail_type.value == 'content_moderation'
    
    def test_is_available(self):
        """Test availability check."""
        config = {'name': 'available_test'}
        guardrail_obj = TopicGuardrail(config)
        
        assert guardrail_obj.is_available() is True
    
    def test_get_health_status(self):
        """Test health status."""
        config = {
            'name': 'health_test',
            'allow_topics': ['topic1', 'topic2'],
            'deny_topics': ['topic3']
        }
        
        guardrail_obj = TopicGuardrail(config)
        health = guardrail_obj.get_health_status()
        
        assert health['name'] == 'health_test'
        assert health['type'] == 'topic_filter'
        assert health['enabled'] is True
        assert health['available'] is True
        assert health['allow_topics_count'] == 2
        assert health['deny_topics_count'] == 1
        assert health['compiled_patterns'] == 3


class TestTopicFilterEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_invalid_regex_pattern(self):
        """Test handling of invalid regex patterns."""
        config = {
            'name': 'invalid_regex_test',
            'mode': 'deny',
            'use_regex': True,
            'deny_topics': ['[invalid', 'valid_pattern']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        # Should still work with valid patterns
        result = await guardrail_obj.analyze("This contains valid_pattern")
        assert result.blocked == True
    
    @pytest.mark.asyncio
    async def test_empty_topic_lists(self):
        """Test behavior with empty topic lists."""
        config = {
            'name': 'empty_lists_test',
            'mode': 'both',
            'allow_topics': [],
            'deny_topics': []
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        result = await guardrail_obj.analyze("Any content")
        assert result.blocked == False
        assert 'No topic restrictions' in result.reason
    
    @pytest.mark.asyncio
    async def test_duplicate_topics(self):
        """Test behavior with duplicate topics."""
        config = {
            'name': 'duplicate_test',
            'mode': 'deny',
            'deny_topics': ['politics', 'politics', 'religion']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        result = await guardrail_obj.analyze("I want to discuss politics")
        assert result.blocked == True
    
    @pytest.mark.asyncio
    async def test_very_long_content(self):
        """Test behavior with very long content."""
        config = {
            'name': 'long_content_test',
            'mode': 'deny',
            'deny_topics': ['politics']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        # Create very long content
        long_content = "This is a very long content. " * 1000 + "I want to discuss politics"
        
        result = await guardrail_obj.analyze(long_content)
        assert result.blocked == True
    
    @pytest.mark.asyncio
    async def test_special_characters(self):
        """Test behavior with special characters."""
        config = {
            'name': 'special_chars_test',
            'mode': 'deny',
            'deny_topics': ['politics']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        result = await guardrail_obj.analyze("I want to discuss politics! @#$%^&*()")
        assert result.blocked == True
    
    @pytest.mark.asyncio
    async def test_unicode_content(self):
        """Test behavior with unicode content."""
        config = {
            'name': 'unicode_test',
            'mode': 'deny',
            'deny_topics': ['politics']
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        result = await guardrail_obj.analyze("I want to discuss politics 🗳️")
        assert result.blocked == True


class TestTopicFilterPerformance:
    """Test performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_many_topics_performance(self):
        """Test performance with many topics."""
        # Create many topics
        allow_topics = [f"topic_{i}" for i in range(100)]
        deny_topics = [f"deny_{i}" for i in range(100)]
        
        config = {
            'name': 'performance_test',
            'mode': 'both',
            'allow_topics': allow_topics,
            'deny_topics': deny_topics
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        # Test performance
        import time
        start_time = time.time()
        
        for i in range(10):
            await guardrail_obj.analyze(f"This is content with topic_{i}")
        
        end_time = time.time()
        
        # Should complete quickly
        assert end_time - start_time < 1.0  # Less than 1 second
    
    @pytest.mark.asyncio
    async def test_complex_regex_performance(self):
        """Test performance with complex regex patterns."""
        config = {
            'name': 'complex_regex_test',
            'mode': 'deny',
            'use_regex': True,
            'deny_topics': [
                r'\b(spam|scam|phishing|malware|virus)\b',
                r'\b(click here|free money|lottery|winner)\b',
                r'\b(viagra|cialis|weight loss|diet)\b'
            ]
        }
        
        guardrail_obj = TopicGuardrail(config)
        
        # Test performance
        import time
        start_time = time.time()
        
        for i in range(50):
            await guardrail_obj.analyze(f"This is test content {i} with various words")
        
        end_time = time.time()
        
        # Should complete quickly
        assert end_time - start_time < 1.0  # Less than 1 second 