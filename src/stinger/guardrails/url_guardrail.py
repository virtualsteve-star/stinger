import re
from urllib.parse import urlparse
from typing import List, Optional
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType
from ..core.config_validator import ValidationRule, URL_GUARDRAIL_RULES
from ..core.conversation import Conversation

class URLGuardrail(GuardrailInterface):
    def __init__(self, config: dict):
        """Initialize URL filter."""
        name = config.get('name', 'url_filter')
        super().__init__(name, GuardrailType.URL_FILTER, config)
        
        self.blocked_domains = config.get('blocked_domains', [])
        self.allowed_domains = config.get('allowed_domains', [])
        self.action = config.get('action', 'block')
        
        # Improved URL regex pattern that handles ports
        self.url_pattern = re.compile(
            r'https?://[^\s<>"{}|\\^`\[\]]+',
            re.IGNORECASE
        )
    
    def get_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for URL guardrail."""
        return URL_GUARDRAIL_RULES
    

    async def analyze(self, content: str, conversation: Optional['Conversation'] = None) -> GuardrailResult:
        """Analyze content for blocked URLs."""
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
        
        # Extract URLs from content
        urls = self.url_pattern.findall(content)
        if not urls:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason='No URLs found',
                details={'urls_found': 0},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level='low'
            )
        
        blocked_urls = []
        allowed_urls = []
        
        for url in urls:
            try:
                parsed = urlparse(url)
                # Extract domain without port for comparison
                domain = parsed.netloc.split(':')[0].lower()
                
                # Check blocked domains first
                if domain in self.blocked_domains:
                    blocked_urls.append(url)
                    continue
                
                # Check allowed domains (if specified)
                if self.allowed_domains:
                    if domain in self.allowed_domains:
                        allowed_urls.append(url)
                    else:
                        blocked_urls.append(url)
                else:
                    # No allowed domains specified, so all non-blocked are allowed
                    allowed_urls.append(url)
                    
            except Exception as e:
                # Invalid URL, treat as blocked
                blocked_urls.append(url)
        
        if blocked_urls:
            reason = f"Blocked URLs found: {', '.join(blocked_urls[:3])}"
            if len(blocked_urls) > 3:
                reason += f" and {len(blocked_urls) - 3} more"
            
            return GuardrailResult(
                blocked=True,
                confidence=1.0,
                reason=reason,
                details={
                    'blocked_urls': blocked_urls,
                    'allowed_urls': allowed_urls,
                    'total_urls': len(urls)
                },
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level='high' if blocked_urls else 'low'
            )
        
        return GuardrailResult(
            blocked=False,
            confidence=1.0,
            reason=f'All URLs allowed: {len(allowed_urls)} found',
            details={
                'blocked_urls': [],
                'allowed_urls': allowed_urls,
                'total_urls': len(urls)
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
            'blocked_domains': self.blocked_domains,
            'allowed_domains': self.allowed_domains,
            'action': self.action
        }
    
    def update_config(self, config: dict) -> bool:
        """Update configuration."""
        try:
            if 'blocked_domains' in config:
                self.blocked_domains = config['blocked_domains']
            if 'allowed_domains' in config:
                self.allowed_domains = config['allowed_domains']
            if 'action' in config:
                self.action = config['action']
            if 'enabled' in config:
                self.enabled = config['enabled']
            return True
        except Exception:
            return False
    
    def validate_config(self) -> bool:
        """Validate URL filter configuration."""
        if not isinstance(self.blocked_domains, list):
            return False
        
        if not isinstance(self.allowed_domains, list):
            return False
        
        if self.action not in ['block', 'allow', 'warn']:
            return False
        
        return True 