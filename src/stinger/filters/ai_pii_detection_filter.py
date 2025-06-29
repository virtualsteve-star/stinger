"""
AI-Based PII Detection Filter

This module provides an AI-based PII detection filter using OpenAI
with centralized model configuration and fallback to simple regex detection.
"""

import json
import logging
from typing import Dict, Any
from ..core.guardrail_interface import GuardrailInterface, GuardrailType, GuardrailResult
from ..core.model_config import ModelFactory, ModelError
from ..core.api_key_manager import get_openai_key
from .simple_pii_detection_filter import SimplePIIDetectionFilter

logger = logging.getLogger(__name__)


class AIPIIDetectionFilter(GuardrailInterface):
    """AI-based PII detection filter using centralized model configuration."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, GuardrailType.PII_DETECTION, config.get('enabled', True))
        
        # Use centralized API key manager instead of config
        self.api_key = get_openai_key()
        self.confidence_threshold = config.get('confidence_threshold', 0.8)
        self.on_error = config.get('on_error', 'allow')
        
        # Use centralized model factory
        self.model_factory = ModelFactory()
        self.model_provider = None
        
        if self.api_key:
            try:
                self.model_provider = self.model_factory.create_model_provider('pii_detection', self.api_key)
                logger.info(f"Initialized AI PII detection filter with centralized API key")
            except Exception as e:
                logger.error(f"Failed to create model provider for PII detection: {e}")
        else:
            logger.warning(f"No OpenAI API key available for AI PII detection filter")
        
        self.pii_prompt = """
You are a data privacy specialist. Analyze the following text and identify any Personally Identifiable Information (PII).

PII includes:
- Social Security Numbers (SSN)
- Credit card numbers
- Email addresses
- Phone numbers
- IP addresses
- Driver's license numbers
- Passport numbers
- Bank account numbers

Respond with a JSON object containing:
- "detected": boolean (true if PII detected)
- "pii_types": array of strings (types of PII found)
- "confidence": float (0.0 to 1.0)
- "details": string (brief explanation)

Text to analyze: {content}
"""
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Analyze content for PII using AI with centralized model configuration."""
        if not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="AI PII detection filter disabled",
                details={'method': 'ai', 'enabled': False},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        if not self.model_provider:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="AI PII detection unavailable - no API key",
                details={'error': 'no_api_key', 'method': 'ai', 'model': 'none'},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        try:
            # Use centralized model provider
            response_content = await self.model_provider.generate_response(
                self.pii_prompt.format(content=content)
            )
            
            if response_content:
                try:
                    data = json.loads(response_content.strip())
                    
                    detected = data.get("detected", False)
                    pii_types = data.get("pii_types", [])
                    confidence = data.get("confidence", 0.0)
                    
                    blocked = detected and confidence >= self.confidence_threshold
                    
                    return GuardrailResult(
                        blocked=blocked,
                        confidence=confidence,
                        reason=f"PII detected (AI): {', '.join(pii_types)}" if detected else "No PII detected (AI)",
                        details={
                            'detected_pii': pii_types,
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
            logger.error(f"AI PII detection error: {e}")
            return await self._fallback_result(content, str(e))
    
    async def _fallback_result(self, content: str, error: str = "AI analysis failed") -> GuardrailResult:
        """Fallback to simple regex detection when AI fails."""
        try:
            simple_filter = SimplePIIDetectionFilter(
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
            logger.error(f"Fallback PII detection also failed: {fallback_error}")
            blocked = self.on_error == 'block'
            return GuardrailResult(
                blocked=blocked,
                confidence=0.0,
                reason=f"PII detection failed: {error}, fallback failed: {fallback_error}",
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
            logger.error(f"Failed to update AI PII detection filter config: {e}")
            return False 