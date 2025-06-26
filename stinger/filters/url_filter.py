import re
from urllib.parse import urlparse
from typing import List, Optional
from ..core.base_filter import BaseFilter, FilterResult

class URLFilter(BaseFilter):
    def __init__(self, config: dict):
        super().__init__(config)
        self.blocked_domains = config.get('blocked_domains', [])
        self.allowed_domains = config.get('allowed_domains', [])
        self.action = config.get('action', 'block')
        
        # Improved URL regex pattern that handles ports
        self.url_pattern = re.compile(
            r'https?://[^\s<>"{}|\\^`\[\]]+',
            re.IGNORECASE
        )
    
    async def run(self, content: str) -> FilterResult:
        if not content:
            return FilterResult(action='allow', reason='no content')
        
        # Extract URLs from content
        urls = self.url_pattern.findall(content)
        if not urls:
            return FilterResult(action='allow', reason='no URLs found')
        
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
            reason = f"blocked URLs: {', '.join(blocked_urls[:3])}"  # Limit to first 3
            if len(blocked_urls) > 3:
                reason += f" and {len(blocked_urls) - 3} more"
            
            return FilterResult(
                action=self.action,
                reason=reason,
                confidence=1.0
            )
        
        return FilterResult(
            action='allow',
            reason=f'all URLs allowed: {len(allowed_urls)} found',
            confidence=1.0
        )
    
    def validate_config(self) -> bool:
        """Validate URL filter configuration."""
        if not isinstance(self.blocked_domains, list):
            return False
        
        if not isinstance(self.allowed_domains, list):
            return False
        
        if self.action not in ['block', 'allow', 'warn']:
            return False
        
        return True 