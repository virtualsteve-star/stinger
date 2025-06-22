from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from ..utils.exceptions import FilterError

@dataclass
class FilterResult:
    action: str  # 'allow', 'block', 'warn', 'modify'
    confidence: float = 1.0
    reason: str = ""
    modified_content: Optional[str] = None

class BaseFilter(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.on_error = config.get('on_error', 'block')
    
    @abstractmethod
    async def run(self, content: str) -> FilterResult:
        """Run the filter on the given content."""
        pass
    
    def validate_config(self) -> bool:
        """Validate filter configuration."""
        return True
    
    async def run_safe(self, content: str) -> FilterResult:
        """Run filter with error handling."""
        try:
            return await self.run(content)
        except Exception as e:
            if self.on_error == 'block':
                return FilterResult(action='block', reason=f'Filter error: {str(e)}')
            elif self.on_error == 'allow':
                return FilterResult(action='allow', reason=f'Filter error, allowing: {str(e)}')
            else:  # skip
                return FilterResult(action='allow', reason=f'Filter skipped due to error: {str(e)}') 