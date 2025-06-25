import re
from typing import List, Optional
from ..core.base_filter import BaseFilter, FilterResult

class RegexFilter(BaseFilter):
    def __init__(self, config: dict):
        super().__init__(config)
        self.patterns = config.get('patterns', [])
        self.action = config.get('action', 'block')  # 'block', 'allow', 'warn'
        self.flags = config.get('flags', 0)
        self.case_sensitive = config.get('case_sensitive', True)
        
        # Compile patterns for performance
        self.compiled_patterns = []
        for pattern in self.patterns:
            try:
                flags = 0 if self.case_sensitive else re.IGNORECASE
                flags |= self.flags
                self.compiled_patterns.append(re.compile(pattern, flags))
            except re.error as e:
                raise ValueError(f"Invalid regex pattern '{pattern}': {str(e)}")
    
    async def run(self, content: str) -> FilterResult:
        if not content or not self.compiled_patterns:
            return FilterResult(action='allow', reason='no content or patterns')
        
        matches = []
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(content):
                matches.append(self.patterns[i])
        
        if matches:
            reason = f"matched patterns: {', '.join(matches)}"
            return FilterResult(
                action=self.action,
                reason=reason,
                confidence=1.0
            )
        
        return FilterResult(action='allow', reason='no pattern matches')
    
    def validate_config(self) -> bool:
        """Validate regex filter configuration."""
        if not isinstance(self.patterns, list):
            return False
        
        if self.action not in ['block', 'allow', 'warn']:
            return False
        
        # Validate regex patterns
        for pattern in self.patterns:
            try:
                re.compile(pattern)
            except re.error:
                return False
        
        return True 