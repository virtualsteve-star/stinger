"""
AI-Based Toxicity Detection Filter

This module provides an AI-based toxicity detection filter using OpenAI
with centralized model configuration and fallback to simple regex detection.
"""

import json
import logging
from typing import Dict, Any, Optional
from ..core.guardrail_interface import GuardrailInterface, GuardrailType, GuardrailResult
from ..core.model_config import ModelFactory, ModelError
from ..core.conversation import Conversation
from ..core.api_key_manager import get_openai_key
from .simple_toxicity_detection_guardrail import SimpleToxicityDetectionGuardrail

logger = logging.getLogger(__name__)


class AIToxicityDetectionGuardrail(GuardrailInterface):
    """AI-based toxicity detection filter using centralized model configuration."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, GuardrailType.TOXICITY_DETECTION, config.get('enabled', True))
        
        # Use centralized API key manager instead of config
        self.api_key = get_openai_key()
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        self.on_error = config.get('on_error', 'allow')
        
        # Use centralized model factory
        self.model_factory = ModelFactory()
        self.model_provider = None
        
        if self.api_key:
            try:
                self.model_provider = self.model_factory.create_model_provider('toxicity_detection', self.api_key)
                logger.info(f"Initialized AI toxicity detection filter with centralized API key")
            except Exception as e:
                logger.error(f"Failed to create model provider for toxicity detection: {e}")
        else:
            logger.warning(f"No OpenAI API key available for AI toxicity detection filter")
        
        self.toxicity_prompt = """
You are a content moderation specialist. Analyze the following text for toxic content.

Toxic content includes:
- Hate speech and discrimination
- Harassment and bullying
- Threats and violence
- Sexual harassment
- Explicit or inappropriate content

Respond with a JSON object containing:
- "detected": boolean (true if toxic content detected)
- "toxicity_types": array of strings (types of toxicity found)
- "confidence": float (0.0 to 1.0)
- "details": string (brief explanation)

Text to analyze: {content}
"""
    
    async def analyze(self, content: str, conversation: Optional['Conversation'] = None) -> GuardrailResult:
        """Analyze content for toxicity using AI with centralized model configuration."""
        if not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="AI toxicity detection filter disabled",
                details={'method': 'ai', 'enabled': False},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        if not self.model_provider:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="AI toxicity detection unavailable - no API key",
                details={'error': 'no_api_key', 'method': 'ai', 'model': 'none'},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        try:
            # Use centralized model provider
            response_content = await self.model_provider.generate_response(
                self.toxicity_prompt.format(content=content)
            )
            
            if response_content:
                try:
                    data = json.loads(response_content.strip())
                    
                    detected = data.get("detected", False)
                    toxicity_types = data.get("toxicity_types", [])
                    confidence = data.get("confidence", 0.0)
                    
                    blocked = detected and confidence >= self.confidence_threshold
                    
                    return GuardrailResult(
                        blocked=blocked,
                        confidence=confidence,
                        reason=f"Toxic content detected (AI): {', '.join(toxicity_types)}" if detected else "No toxic content detected (AI)",
                        details={
                            'detected_toxicity': toxicity_types,
                            'confidence': confidence,
                            'method': 'ai',
                            'model': self.model_provider.get_model_name()
                        },
                        guardrail_name=self.name,
                        guardrail_type=self.guardrail_type
                    )
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON response from AI model: {e}")
                    return await self._fallback_result(content, "Invalid JSON response")
            else:
                return await self._fallback_result(content, "Empty response from AI model")
            
        except Exception as e:
            logger.error(f"AI toxicity detection error: {e}")
            return await self._fallback_result(content, str(e))
    
    async def _fallback_result(self, content: str, error: str = "AI analysis failed") -> GuardrailResult:
        """Fallback to simple regex detection when AI fails."""
        try:
            simple_filter = SimpleToxicityDetectionGuardrail(
                self.name, 
                {
                    'confidence_threshold': self.confidence_threshold,
                    'on_error': self.on_error
                }
            )
            result = await simple_filter.analyze(content)
            # Update the result to indicate it's a fallback
            result.details['fallback'] = True
            result.details['fallback_reason'] = error
            result.reason = f"AI failed ({error}), using regex fallback: {result.reason}"
            return result
        except Exception as fallback_error:
            logger.error(f"Fallback toxicity detection also failed: {fallback_error}")
            blocked = self.on_error == 'block'
            return GuardrailResult(
                blocked=blocked,
                confidence=0.0,
                reason=f"Toxicity detection failed: {error}, fallback failed: {fallback_error}",
                details={
                    'error': error,
                    'fallback_error': str(fallback_error),
                    'method': 'ai_fallback_failed'
                },
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
    
    def is_available(self) -> bool:
        """Check if this guardrail is available."""
        return self.enabled and self.model_provider is not None
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration of this guardrail."""
        return {
            'enabled': self.enabled,
            'api_key': '***' if self.api_key else None,
            'confidence_threshold': self.confidence_threshold,
            'on_error': self.on_error,
            'model': self.model_provider.get_model_name() if self.model_provider else None
        }
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update configuration of this guardrail."""
        try:
            if 'enabled' in config:
                self.enabled = config['enabled']
            if 'confidence_threshold' in config:
                self.confidence_threshold = config['confidence_threshold']
            if 'on_error' in config:
                self.on_error = config['on_error']
            return True
        except Exception as e:
            logger.error(f"Failed to update AI toxicity detection filter config: {e}")
            return False 