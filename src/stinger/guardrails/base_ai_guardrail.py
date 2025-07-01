"""
Base AI Filter

This module provides a base class for AI-powered filters with fallback support.
It consolidates common logic for API key handling, model setup, fallback mechanisms,
and configuration management across all AI filter implementations.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Type
from abc import abstractmethod

from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType
from ..core.api_key_manager import APIKeyManager
from ..core.conversation import Conversation
from ..adapters.openai_adapter import ModelFactory

logger = logging.getLogger(__name__)


class BaseAIGuardrail(GuardrailInterface):
    """
    Base class for AI-powered filters with fallback support.
    
    This class provides common functionality for all AI filters including:
    - API key initialization and management
    - Model provider setup
    - Fallback logic to simple filters
    - Configuration handling
    - Error handling
    """
    
    def __init__(self, 
                 name: str, 
                 guardrail_type: GuardrailType,
                 config: Dict[str, Any],
                 prompt_template: str,
                 simple_filter_class: Type[GuardrailInterface],
                 detected_field_name: str = "detected",
                 types_field_name: str = "types"):
        """
        Initialize the base AI filter.
        
        Args:
            name: Filter name
            guardrail_type: Type of guardrail
            config: Configuration dictionary
            prompt_template: Template for AI prompt
            simple_filter_class: Fallback simple filter class
            detected_field_name: JSON field name for detection result
            types_field_name: JSON field name for detected types
        """
        enabled = config.get('enabled', True)
        super().__init__(name, guardrail_type, enabled)
        
        self.prompt_template = prompt_template
        self.simple_filter_class = simple_filter_class
        self.detected_field_name = detected_field_name
        self.types_field_name = types_field_name
        
        # Get API key from centralized manager
        api_key_manager = APIKeyManager()
        self.api_key = api_key_manager.get_api_key()
        
        # Configuration
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        self.on_error = config.get('on_error', 'allow')
        
        # Create model provider
        self.model_provider = None
        if self.api_key:
            try:
                factory = ModelFactory()
                self.model_provider = factory.get_model_provider('openai', api_key=self.api_key)
                logger.info(f"Initialized {self.__class__.__name__} '{self.name}' with OpenAI model")
            except Exception as e:
                logger.warning(f"Failed to initialize AI model for {self.__class__.__name__}: {e}")
                self.model_provider = None
        else:
            logger.warning(f"{self.__class__.__name__} initialized without API key - will use fallback")
    
    async def analyze(self, content: str, conversation: Optional['Conversation'] = None) -> GuardrailResult:
        """
        Analyze content using AI model with fallback support.
        
        Args:
            content: Content to analyze
            conversation: Optional conversation context
            
        Returns:
            GuardrailResult with analysis results
        """
        if not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason=f"{self.guardrail_type.value} filter disabled",
                details={'enabled': False},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        if not content:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Empty content",
                details={'empty_content': True},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        # Try AI analysis if available
        if self.model_provider and self.api_key:
            try:
                # Generate AI response
                response = await self.model_provider.generate_response(
                    prompt=self.prompt_template.format(user_input=content)
                )
                
                # Parse JSON response
                try:
                    result_data = json.loads(response)
                    detected = result_data.get(self.detected_field_name, False)
                    confidence = result_data.get('confidence', 0.0)
                    detected_types = result_data.get(self.types_field_name, [])
                    
                    # Determine if we should block
                    should_block = detected and confidence >= self.confidence_threshold
                    
                    reason = self._format_reason(detected, detected_types, confidence)
                    
                    return GuardrailResult(
                        blocked=should_block,
                        confidence=confidence,
                        reason=reason,
                        details={
                            self.detected_field_name: detected,
                            self.types_field_name: detected_types,
                            'ai_model': 'gpt-4.1-nano'
                        },
                        guardrail_name=self.name,
                        guardrail_type=self.guardrail_type,
                        risk_level='high' if should_block else 'low'
                    )
                    
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON response from AI model: {response}")
                    return await self._fallback_result(content, "Invalid AI response format")
                except KeyError as e:
                    logger.error(f"Missing required field in AI response: {e}")
                    return await self._fallback_result(content, f"Missing field: {e}")
                    
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                return await self._fallback_result(content, str(e))
        else:
            # No API key or model provider, use fallback
            return await self._fallback_result(content, "No API key available")
    
    async def _fallback_result(self, content: str, error: str) -> GuardrailResult:
        """
        Generate result using fallback simple filter.
        
        Args:
            content: Content to analyze
            error: Error message that triggered fallback
            
        Returns:
            GuardrailResult from fallback filter
        """
        logger.info(f"Using fallback simple filter due to: {error}")
        
        try:
            # Create and use simple filter
            simple_filter = self.simple_filter_class(self.name, {'enabled': True})
            result = await simple_filter.analyze(content)
            
            # Update result to indicate fallback was used
            result.details['fallback'] = True
            result.details['fallback_reason'] = error
            
            return result
            
        except Exception as e:
            logger.error(f"Fallback filter also failed: {e}")
            
            # Determine action based on on_error setting
            if self.on_error == 'block':
                return GuardrailResult(
                    blocked=True,
                    confidence=1.0,
                    reason="Analysis failed - blocking by default",
                    details={'error': str(e), 'fallback_failed': True},
                    guardrail_name=self.name,
                    guardrail_type=self.guardrail_type,
                    risk_level='high'
                )
            else:
                return GuardrailResult(
                    blocked=False,
                    confidence=0.0,
                    reason="Analysis failed - allowing by default",
                    details={'error': str(e), 'fallback_failed': True},
                    guardrail_name=self.name,
                    guardrail_type=self.guardrail_type,
                    risk_level='low'
                )
    
    @abstractmethod
    def _format_reason(self, detected: bool, detected_types: List[str], confidence: float) -> str:
        """
        Format the reason message based on detection results.
        
        This method must be implemented by subclasses to provide
        filter-specific reason formatting.
        
        Args:
            detected: Whether content was detected
            detected_types: Types of content detected
            confidence: Confidence score
            
        Returns:
            Formatted reason string
        """
        pass
    
    def is_available(self) -> bool:
        """Check if the filter is available."""
        return True
    
    def get_config(self) -> Dict[str, Any]:
        """Get filter configuration."""
        return {
            'name': self.name,
            'type': self.guardrail_type.value,
            'enabled': self.enabled,
            'confidence_threshold': self.confidence_threshold,
            'on_error': self.on_error,
            'has_api_key': bool(self.api_key),
            'has_model_provider': bool(self.model_provider)
        }
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update filter configuration."""
        try:
            if 'enabled' in config:
                self.enabled = config['enabled']
            if 'confidence_threshold' in config:
                self.confidence_threshold = config['confidence_threshold']
            if 'on_error' in config:
                self.on_error = config['on_error']
            return True
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False