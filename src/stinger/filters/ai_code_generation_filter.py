"""
AI-Based Code Generation Filter

This module provides an AI-based code generation detection filter using OpenAI
with centralized model configuration and fallback to simple regex detection.
"""

import json
import logging
from typing import Dict, Any, Optional
from ..core.guardrail_interface import GuardrailInterface, GuardrailType, GuardrailResult
from ..core.model_config import ModelFactory, ModelError
from ..core.conversation import Conversation
from ..core.api_key_manager import get_openai_key
from .simple_code_generation_filter import SimpleCodeGenerationFilter

logger = logging.getLogger(__name__)


class AICodeGenerationFilter(GuardrailInterface):
    """AI-based code generation detection filter using centralized model configuration."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, GuardrailType.CODE_GENERATION, config.get('enabled', True))
        
        # Use centralized API key manager instead of config
        self.api_key = get_openai_key()
        self.confidence_threshold = config.get('confidence_threshold', 0.6)
        self.on_error = config.get('on_error', 'warn')
        
        # Use centralized model factory
        self.model_factory = ModelFactory()
        self.model_provider = None
        
        if self.api_key:
            try:
                self.model_provider = self.model_factory.create_model_provider('code_generation', self.api_key)
                logger.info(f"Initialized AI code generation filter with centralized API key")
            except Exception as e:
                logger.error(f"Failed to create model provider for code generation: {e}")
        else:
            logger.warning(f"No OpenAI API key available for AI code generation filter")
        
        self.code_prompt = """
You are a security analyst specializing in code injection detection. Analyze the following text and determine if it contains code generation or injection attempts.

Code generation/injection includes:
- Programming code blocks
- Code snippets and functions
- System commands and scripts
- Database queries
- File operations
- Code execution attempts

Respond with a JSON object containing:
- "detected": boolean (true if code generation detected)
- "code_types": array of strings (types of code found)
- "confidence": float (0.0 to 1.0)
- "details": string (brief explanation)

Text to analyze: {content}
"""
    
    async def analyze(self, content: str, conversation: Optional['Conversation'] = None) -> GuardrailResult:
        """Analyze content for code generation using AI with centralized model configuration."""
        if not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="AI code generation filter disabled",
                details={'method': 'ai', 'enabled': False},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        if not self.model_provider:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="AI code generation detection unavailable - no API key",
                details={'error': 'no_api_key', 'method': 'ai', 'model': 'none'},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        try:
            # Use centralized model provider
            response_content = await self.model_provider.generate_response(
                self.code_prompt.format(content=content)
            )
            
            if response_content:
                try:
                    data = json.loads(response_content.strip())
                    
                    detected = data.get("detected", False)
                    code_types = data.get("code_types", [])
                    confidence = data.get("confidence", 0.0)
                    
                    blocked = detected and confidence >= self.confidence_threshold
                    
                    return GuardrailResult(
                        blocked=blocked,
                        confidence=confidence,
                        reason=f"Code generation detected (AI): {', '.join(code_types)}" if detected else "No code generation detected (AI)",
                        details={
                            'detected_code': code_types,
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
            logger.error(f"AI code generation detection error: {e}")
            return await self._fallback_result(content, str(e))
    
    async def _fallback_result(self, content: str, error: str = "AI analysis failed") -> GuardrailResult:
        """Fallback to simple regex detection when AI fails."""
        try:
            simple_filter = SimpleCodeGenerationFilter(
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
            logger.error(f"Fallback code generation detection also failed: {fallback_error}")
            blocked = self.on_error == 'block'
            return GuardrailResult(
                blocked=blocked,
                confidence=0.0,
                reason=f"Code generation detection failed: {error}, fallback failed: {fallback_error}",
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
            logger.error(f"Failed to update AI code generation filter config: {e}")
            return False 