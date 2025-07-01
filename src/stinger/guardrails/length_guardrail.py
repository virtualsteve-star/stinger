from typing import Optional
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType
from ..core.conversation import Conversation

# Need to recreate FilterResult for backward compatibility
from dataclasses import dataclass

class LengthGuardrail(GuardrailInterface):
    def __init__(self, config: dict):
        """Initialize length filter."""
        name = config.get('name', 'length_filter')
        enabled = config.get('enabled', True)
        super().__init__(name, GuardrailType.LENGTH_FILTER, enabled)
        
        # Keep config for backward compatibility
        self.config = config.copy()
        self.min_length = config.get('min_length', 0)
        self.max_length = config.get('max_length', None)
        self.action = config.get('action', 'block')
        
        # Validate configuration
        if self.min_length < 0:
            raise ValueError("min_length must be non-negative")
        if self.max_length is not None and self.max_length < 0:
            raise ValueError("max_length must be non-negative")
        if (self.max_length is not None and 
            self.min_length > self.max_length):
            raise ValueError("min_length cannot be greater than max_length")
    

    async def analyze(self, content: str, conversation: Optional['Conversation'] = None) -> GuardrailResult:
        """Analyze content length."""
        if content is None:
            content = ""
        
        content_length = len(content)
        
        # Check minimum length
        if content_length < self.min_length:
            return GuardrailResult(
                blocked=True,
                confidence=1.0,
                reason=f"Content too short: {content_length} chars (min: {self.min_length})",
                details={
                    'content_length': content_length,
                    'min_length': self.min_length,
                    'max_length': self.max_length,
                    'violation': 'too_short'
                },
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level='medium'
            )
        
        # Check maximum length
        if self.max_length is not None and content_length > self.max_length:
            return GuardrailResult(
                blocked=True,
                confidence=1.0,
                reason=f"Content too long: {content_length} chars (max: {self.max_length})",
                details={
                    'content_length': content_length,
                    'min_length': self.min_length,
                    'max_length': self.max_length,
                    'violation': 'too_long'
                },
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level='medium'
            )
        
        return GuardrailResult(
            blocked=False,
            confidence=1.0,
            reason=f'Length acceptable: {content_length} chars',
            details={
                'content_length': content_length,
                'min_length': self.min_length,
                'max_length': self.max_length,
                'violation': None
            },
            guardrail_name=self.name,
            guardrail_type=self.guardrail_type,
            risk_level='low'
        )

    def is_available(self) -> bool:
        """Check if filter is available."""
        return True
    
    def get_config(self) -> dict:
        """Get current configuration."""
        return {
            'name': self.name,
            'type': self.guardrail_type.value,
            'enabled': self.enabled,
            'min_length': self.min_length,
            'max_length': self.max_length,
            'action': self.action
        }
    
    def update_config(self, config: dict) -> bool:
        """Update configuration."""
        try:
            if 'min_length' in config:
                min_length = config['min_length']
                if min_length < 0:
                    return False
                self.min_length = min_length
            
            if 'max_length' in config:
                max_length = config['max_length']
                if max_length is not None and max_length < 0:
                    return False
                self.max_length = max_length
            
            if 'action' in config:
                self.action = config['action']
            
            if 'enabled' in config:
                self.enabled = config['enabled']
            
            # Validate that min <= max
            if (self.max_length is not None and 
                self.min_length > self.max_length):
                return False
            
            return True
        except Exception:
            return False
    
    def validate_config(self) -> bool:
        """Validate length filter configuration."""
        if not isinstance(self.min_length, (int, float)):
            return False
        
        if self.max_length is not None and not isinstance(self.max_length, (int, float)):
            return False
        
        if self.action not in ['block', 'allow', 'warn']:
            return False
        
        return True 