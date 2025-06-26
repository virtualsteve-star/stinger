from typing import Optional
from ..core.base_filter import BaseFilter, FilterResult

class LengthFilter(BaseFilter):
    def __init__(self, config: dict):
        super().__init__(config)
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
    
    async def run(self, content: str) -> FilterResult:
        if content is None:
            content = ""
        
        content_length = len(content)
        
        # Check minimum length
        if content_length < self.min_length:
            reason = f"content too short: {content_length} chars (min: {self.min_length})"
            return FilterResult(
                action=self.action,
                reason=reason,
                confidence=1.0
            )
        
        # Check maximum length
        if self.max_length is not None and content_length > self.max_length:
            reason = f"content too long: {content_length} chars (max: {self.max_length})"
            return FilterResult(
                action=self.action,
                reason=reason,
                confidence=1.0
            )
        
        return FilterResult(
            action='allow',
            reason=f'length acceptable: {content_length} chars',
            confidence=1.0
        )
    
    def validate_config(self) -> bool:
        """Validate length filter configuration."""
        if not isinstance(self.min_length, (int, float)):
            return False
        
        if self.max_length is not None and not isinstance(self.max_length, (int, float)):
            return False
        
        if self.action not in ['block', 'allow', 'warn']:
            return False
        
        return True 