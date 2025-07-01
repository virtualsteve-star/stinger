from typing import Optional
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType
from ..core.conversation import Conversation

# Need to recreate FilterResult for backward compatibility
from dataclasses import dataclass

class KeywordBlockGuardrail(GuardrailInterface):
    def __init__(self, config: dict):
        """Initialize keyword block filter."""
        name = config.get('name', 'keyword_block')
        enabled = config.get('enabled', True)
        super().__init__(name, GuardrailType.KEYWORD_BLOCK, enabled)
        
        # Keep config for backward compatibility
        self.config = config.copy()
        self.keyword = config.get('keyword', '').lower()
    

    async def analyze(self, content: str, conversation: Optional['Conversation'] = None) -> GuardrailResult:
        """Analyze content for blocked keywords."""
        if not self.keyword:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason='No keyword configured',
                details={},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level='low'
            )
        
        if not content:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason='No content to analyze',
                details={},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level='low'
            )
        
        if self.keyword in content.lower():
            return GuardrailResult(
                blocked=True,
                confidence=1.0,
                reason=f'Blocked keyword found: {self.keyword}',
                details={'keyword': self.keyword},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level='high'
            )
        
        return GuardrailResult(
            blocked=False,
            confidence=0.0,
            reason='No keyword match found',
            details={'keyword': self.keyword},
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
            'keyword': self.keyword
        }
    
    def update_config(self, config: dict) -> bool:
        """Update configuration."""
        try:
            if 'keyword' in config:
                self.keyword = config['keyword'].lower()
            if 'enabled' in config:
                self.enabled = config['enabled']
            return True
        except Exception:
            return False 