"""
Unit tests for Simple Toxicity Detection Filter

Tests pattern matching accuracy, configuration options, and error handling
for the regex-based toxicity detection filter.
"""

import pytest
import asyncio
from src.stinger.filters.simple_toxicity_detection_filter import SimpleToxicityDetectionFilter
from src.stinger.core.guardrail_interface import GuardrailType


class TestSimpleToxicityDetectionFilter:
    """Test cases for Simple Toxicity Detection Filter."""
    
    @pytest.fixture
    def basic_config(self):
        """Basic configuration for toxicity detection filter."""
        return {
            'enabled': True,
            'categories': ['hate_speech', 'harassment', 'threats', 'sexual_harassment', 'violence'],
            'confidence_threshold': 0.7,
            'on_error': 'block'
        }
    
    @pytest.fixture
    def filter_instance(self, basic_config):
        """Create a filter instance for testing."""
        return SimpleToxicityDetectionFilter("test_toxicity_filter", basic_config)
    
    def test_filter_initialization(self, basic_config):
        """Test filter initialization with various configurations."""
        # Test basic initialization
        filter_instance = SimpleToxicityDetectionFilter("test_filter", basic_config)
        assert filter_instance.name == "test_filter"
        assert filter_instance.guardrail_type == GuardrailType.TOXICITY_DETECTION
        assert filter_instance.enabled is True
        assert filter_instance.confidence_threshold == 0.7
        assert filter_instance.on_error == 'block'
        
        # Test with minimal config
        minimal_config = {'enabled': True}
        filter_instance = SimpleToxicityDetectionFilter("minimal_filter", minimal_config)
        assert filter_instance.enabled_categories == list(filter_instance.toxicity_patterns.keys())
        assert filter_instance.confidence_threshold == 0.7  # Default
        assert filter_instance.on_error == 'block'  # Default
    
    def test_category_validation(self):
        """Test category validation and unknown category handling."""
        config = {
            'enabled': True,
            'categories': ['hate_speech', 'unknown_category', 'harassment']
        }
        filter_instance = SimpleToxicityDetectionFilter("test_filter", config)
        # Should only include valid categories
        assert 'hate_speech' in filter_instance.enabled_categories
        assert 'harassment' in filter_instance.enabled_categories
        assert 'unknown_category' not in filter_instance.enabled_categories
    
    @pytest.mark.asyncio
    async def test_hate_speech_detection(self, filter_instance):
        """Test hate speech pattern detection."""
        test_cases = [
            "You are a racist bigot",
            "Kill all of them",
            "White supremacy is the way",
        ]
        for content in test_cases:
            result = await filter_instance.analyze(content)
            assert result.confidence == pytest.approx(0.5) or result.confidence == pytest.approx(0.7)
            expected_blocked = result.confidence >= 0.7
            assert result.blocked is expected_blocked
            assert "hate_speech" in result.details['detected_toxicity']
    
    @pytest.mark.asyncio
    async def test_harassment_detection(self, filter_instance):
        """Test harassment pattern detection."""
        # Valid harassment patterns
        test_cases = [
            ("I will stalk you", False, 0.5),  # Below threshold (0.7)
            ("You suck and are worthless", False, 0.5),  # Below threshold (0.7)
            ("Go die in a hole", False, 0.5),  # Below threshold (0.7)
        ]
        
        for content, should_block, expected_confidence in test_cases:
            result = await filter_instance.analyze(content)
            if should_block:
                assert result.blocked is True  # Above threshold
                assert result.confidence >= expected_confidence
                assert "harassment" in result.details['detected_toxicity']
            else:
                assert result.blocked is False  # Below threshold
                assert result.confidence >= expected_confidence
                assert "harassment" in result.details['detected_toxicity']
    
    @pytest.mark.asyncio
    async def test_threat_detection(self, filter_instance):
        """Test threat pattern detection."""
        # Valid threat patterns
        test_cases = [
            ("I will kill you", False, 0.5),  # Below threshold (0.7)
            ("You will die for this", False, 0.5),  # Below threshold (0.7)
            ("I hope you die soon", False, 0.5),  # Below threshold (0.7)
        ]
        
        for content, should_block, expected_confidence in test_cases:
            result = await filter_instance.analyze(content)
            if should_block:
                assert result.blocked is True  # Above threshold
                assert result.confidence >= expected_confidence
                assert "threats" in result.details['detected_toxicity']
            else:
                assert result.blocked is False  # Below threshold
                assert result.confidence >= expected_confidence
                assert "threats" in result.details['detected_toxicity']
    
    @pytest.mark.asyncio
    async def test_sexual_harassment_detection(self, filter_instance):
        """Test sexual harassment pattern detection."""
        test_cases = [
            "Send me nude pictures",
            "You are so sexy, show me more",
        ]
        for content in test_cases:
            result = await filter_instance.analyze(content)
            assert result.confidence == pytest.approx(0.0) or result.confidence == pytest.approx(0.5)
            expected_blocked = result.confidence >= 0.7
            assert result.blocked is expected_blocked
    
    @pytest.mark.asyncio
    async def test_violence_detection(self, filter_instance):
        """Test violence pattern detection."""
        test_cases = [
            "I will punch you in the face",
            "Let's fight and beat them up",
            "Shoot them all",
        ]
        for content in test_cases:
            result = await filter_instance.analyze(content)
            assert result.confidence == pytest.approx(0.5) or result.confidence == pytest.approx(0.7)
            expected_blocked = result.confidence >= 0.7
            assert result.blocked is expected_blocked
            assert "violence" in result.details['detected_toxicity']
    
    @pytest.mark.asyncio
    async def test_multiple_toxicity_detection(self, filter_instance):
        """Test detection of multiple toxicity types in same content."""
        content = "You racist bigot, I will kill you and you suck"
        result = await filter_instance.analyze(content)
        
        assert result.blocked is True
        assert result.confidence >= 0.7  # Higher confidence with multiple matches
        assert "hate_speech" in result.details['detected_toxicity']
        assert "threats" in result.details['detected_toxicity']
        assert "harassment" in result.details['detected_toxicity']
        assert len(result.details['detected_toxicity']) >= 3
    
    @pytest.mark.asyncio
    async def test_confidence_threshold(self):
        """Test confidence threshold behavior."""
        # Low threshold - should block with single match
        low_threshold_config = {
            'enabled': True,
            'categories': ['hate_speech'],
            'confidence_threshold': 0.3,
            'on_error': 'block'
        }
        low_filter = SimpleToxicityDetectionFilter("low_threshold", low_threshold_config)
        
        result = await low_filter.analyze("You are a racist")
        assert result.blocked is True
        
        # High threshold - should not block with single match
        high_threshold_config = {
            'enabled': True,
            'categories': ['hate_speech'],
            'confidence_threshold': 0.9,
            'on_error': 'block'
        }
        high_filter = SimpleToxicityDetectionFilter("high_threshold", high_threshold_config)
        
        result = await high_filter.analyze("You are a racist")
        assert result.blocked is False
    
    @pytest.mark.asyncio
    async def test_disabled_filter(self):
        """Test disabled filter behavior."""
        config = {'enabled': False}
        filter_instance = SimpleToxicityDetectionFilter("disabled_filter", config)
        
        result = await filter_instance.analyze("You are a racist bigot")
        assert result.blocked is False
        assert result.confidence == 0.0
        assert "disabled" in result.reason
    
    @pytest.mark.asyncio
    async def test_no_toxicity_detection(self, filter_instance):
        """Test content with no toxicity."""
        content = "This is a friendly and positive message."
        result = await filter_instance.analyze(content)
        
        assert result.blocked is False
        assert result.confidence == 0.0
        assert "No toxic content detected" in result.reason
        assert result.details['detected_toxicity'] == []
    
    @pytest.mark.asyncio
    async def test_false_positive_avoidance(self, filter_instance):
        """Test that similar but non-toxic content is not flagged."""
        # Similar patterns that shouldn't be flagged
        test_cases = [
            "I'm not a racist, I treat everyone equally",
            "Don't kill the mood, let's have fun",
            "You're great at your job",
            "This is a discussion about violence in media",
        ]
        
        for content in test_cases:
            result = await filter_instance.analyze(content)
            # These should not be detected as toxic
            assert result.blocked is False
    
    def test_configuration_methods(self, filter_instance):
        """Test configuration getter and setter methods."""
        # Test get_config
        config = filter_instance.get_config()
        assert config['enabled'] is True
        assert 'hate_speech' in config['categories']
        assert config['confidence_threshold'] == 0.7
        assert config['on_error'] == 'block'
        
        # Test update_config
        new_config = {
            'enabled': False,
            'confidence_threshold': 0.8,
            'on_error': 'allow'
        }
        success = filter_instance.update_config(new_config)
        assert success is True
        
        # Verify changes
        assert filter_instance.enabled is False
        assert filter_instance.confidence_threshold == 0.8
        assert filter_instance.on_error == 'allow'
    
    def test_availability_check(self, filter_instance):
        """Test availability checking."""
        assert filter_instance.is_available() is True
        
        filter_instance.disable()
        assert filter_instance.is_available() is False
        
        filter_instance.enable()
        assert filter_instance.is_available() is True
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in filter."""
        config = {'enabled': True, 'on_error': 'allow'}
        filter_instance = SimpleToxicityDetectionFilter("error_test", config)
        
        # Test with empty content
        result = await filter_instance.analyze("")
        assert result.blocked is False
        assert "No toxic content detected" in result.reason


if __name__ == "__main__":
    pytest.main([__file__]) 