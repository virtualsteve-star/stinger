"""
Prompt Injection Detection Filter

This filter uses OpenAI's GPT models to detect prompt injection attempts.
"""

import logging
from typing import Dict, Any, Optional
from ..core.guardrail_interface import GuardrailInterface, GuardrailType, GuardrailResult
from ..core.api_key_manager import APIKeyManager
from ..adapters.openai_adapter import OpenAIAdapter, InjectionResult

logger = logging.getLogger(__name__)


class PromptInjectionFilter(GuardrailInterface):
    """Prompt injection detection filter using OpenAI API."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize the prompt injection detection filter."""
        super().__init__(name, GuardrailType.PROMPT_INJECTION, config.get('enabled', True))
        
        # Configuration
        self.risk_threshold = config.get('risk_threshold', 70)  # 0-100
        self.block_levels = config.get('block_levels', ['high', 'critical'])
        self.warn_levels = config.get('warn_levels', ['medium'])
        self.on_error = config.get('on_error', 'allow')  # 'allow', 'block', 'warn'
        
        # API setup
        self.api_key_manager = APIKeyManager()
        self.openai_adapter: Optional[OpenAIAdapter] = None
        self._initialize_adapter()
    
    def _initialize_adapter(self) -> None:
        """Initialize the OpenAI adapter."""
        try:
            api_key = self.api_key_manager.get_openai_key()
            if api_key:
                self.openai_adapter = OpenAIAdapter(api_key)
                logger.info(f"Initialized OpenAI adapter for {self.name}")
            else:
                logger.warning(f"No OpenAI API key found for {self.name}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI adapter for {self.name}: {e}")
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Analyze content for prompt injection attempts."""
        if not self.is_enabled():
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Filter disabled",
                details={},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        if not self.is_available():
            return self._handle_unavailable()
        
        try:
            # Use OpenAI prompt injection detection
            if self.openai_adapter is None:
                return self._handle_error(Exception("OpenAI adapter not initialized"))
            
            injection_result = await self.openai_adapter.detect_prompt_injection(content)
            
            # Determine action based on risk level and threshold
            should_block = (
                injection_result.detected and 
                (injection_result.risk_percent >= self.risk_threshold or 
                 injection_result.level in self.block_levels)
            )
            
            should_warn = (
                injection_result.detected and 
                not should_block and
                injection_result.level in self.warn_levels
            )
            
            # Create result
            reason = self._build_reason(injection_result, should_block, should_warn)
            
            return GuardrailResult(
                blocked=should_block,
                confidence=injection_result.confidence,
                reason=reason,
                risk_level=injection_result.level,
                indicators=injection_result.indicators,
                details={
                    'injection_result': {
                        'detected': injection_result.detected,
                        'risk_percent': injection_result.risk_percent,
                        'level': injection_result.level,
                        'indicators': injection_result.indicators,
                        'comment': injection_result.comment
                    },
                    'risk_threshold': self.risk_threshold,
                    'block_levels': self.block_levels,
                    'warn_levels': self.warn_levels
                },
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
            
        except Exception as e:
            logger.error(f"Prompt injection analysis failed for {self.name}: {e}")
            return self._handle_error(e)
    
    def _build_reason(self, injection_result: InjectionResult, should_block: bool, should_warn: bool) -> str:
        """Build a human-readable reason for the injection detection decision."""
        if should_block:
            return f"Prompt injection detected: {injection_result.level} risk ({injection_result.risk_percent}%) - {injection_result.comment}"
        elif should_warn:
            return f"Potential prompt injection: {injection_result.level} risk ({injection_result.risk_percent}%) - {injection_result.comment}"
        elif injection_result.detected:
            return f"Low-risk prompt injection detected: {injection_result.level} risk ({injection_result.risk_percent}%) - {injection_result.comment}"
        else:
            return "No prompt injection detected"
    
    def _handle_unavailable(self) -> GuardrailResult:
        """Handle case when OpenAI API is unavailable."""
        if self.on_error == 'block':
            return GuardrailResult(
                blocked=True,
                confidence=0.0,
                reason="Prompt injection detection unavailable - blocking for safety",
                details={'error': 'API unavailable'},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        elif self.on_error == 'warn':
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Prompt injection detection unavailable - allowing with warning",
                details={'error': 'API unavailable'},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        else:  # 'allow'
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Prompt injection detection unavailable - allowing",
                details={'error': 'API unavailable'},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
    
    def _handle_error(self, error: Exception) -> GuardrailResult:
        """Handle errors during analysis."""
        if self.on_error == 'block':
            return GuardrailResult(
                blocked=True,
                confidence=0.0,
                reason=f"Prompt injection detection error - blocking for safety: {str(error)}",
                details={'error': str(error)},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        elif self.on_error == 'warn':
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason=f"Prompt injection detection error - allowing with warning: {str(error)}",
                details={'error': str(error)},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        else:  # 'allow'
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason=f"Prompt injection detection error - allowing: {str(error)}",
                details={'error': str(error)},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
    
    def is_available(self) -> bool:
        """Check if the prompt injection detection filter is available."""
        return (
            self.openai_adapter is not None and 
            self.api_key_manager.get_openai_key() is not None
        )
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration of this filter."""
        return {
            'name': self.name,
            'type': self.guardrail_type.value,
            'enabled': self.is_enabled(),
            'risk_threshold': self.risk_threshold,
            'block_levels': self.block_levels,
            'warn_levels': self.warn_levels,
            'on_error': self.on_error,
            'available': self.is_available()
        }
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update configuration of this filter."""
        try:
            if 'risk_threshold' in config:
                self.risk_threshold = config['risk_threshold']
            
            if 'block_levels' in config:
                self.block_levels = config['block_levels']
            
            if 'warn_levels' in config:
                self.warn_levels = config['warn_levels']
            
            if 'on_error' in config:
                self.on_error = config['on_error']
            
            if 'enabled' in config:
                if config['enabled']:
                    self.enable()
                else:
                    self.disable()
            
            logger.info(f"Updated configuration for {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration for {self.name}: {e}")
            return False 