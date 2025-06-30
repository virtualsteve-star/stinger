import re
from typing import List, Optional
from ..core.base_filter import BaseFilter, FilterResult
from ..core.regex_security import RegexSecurityValidator, SecurityError

class RegexFilter(BaseFilter):
    def __init__(self, config: dict):
        super().__init__(config)
        self.patterns = config.get('patterns', [])
        self.action = config.get('action', 'block')  # 'block', 'allow', 'warn'
        self.flags = config.get('flags', 0)
        self.case_sensitive = config.get('case_sensitive', True)
        
        # Initialize security validator
        self.security_validator = RegexSecurityValidator()
        
        # Compile patterns with security validation
        self.compiled_patterns = []
        for pattern in self.patterns:
            try:
                # Validate pattern for security before compiling
                is_safe, reason = self.security_validator.validate_pattern(pattern)
                if not is_safe:
                    raise SecurityError(f"Unsafe regex pattern '{pattern}': {reason}")
                
                flags = 0 if self.case_sensitive else re.IGNORECASE
                flags |= self.flags
                
                # Use safe compilation
                compiled = self.security_validator.safe_compile(pattern, flags)
                self.compiled_patterns.append(compiled)
                
            except (re.error, SecurityError) as e:
                raise ValueError(f"Invalid or unsafe regex pattern '{pattern}': {str(e)}")
    
    async def run(self, content: str) -> FilterResult:
        if not content or not self.compiled_patterns:
            return FilterResult(action='allow', reason='no content or patterns')
        
        matches = []
        for i, pattern in enumerate(self.compiled_patterns):
            try:
                # Use safe search with timeout protection
                match = self.security_validator.safe_search(pattern, content)
                if match:
                    matches.append(self.patterns[i])
            except SecurityError as e:
                # Log security error but continue processing other patterns
                import logging
                logging.warning(f"Regex security error for pattern '{self.patterns[i]}': {e}")
                continue
        
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