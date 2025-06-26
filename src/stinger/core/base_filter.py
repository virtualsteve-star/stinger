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
    filter_name: Optional[str] = None
    filter_type: Optional[str] = None

class BaseFilter(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.on_error = config.get('on_error', 'block')
        self.name = config.get('name', self.__class__.__name__)
        self.type = config.get('type', self.__class__.__name__)
    
    @abstractmethod
    async def run(self, content: str) -> FilterResult:
        """Run the filter on the given content."""
        pass
    
    def validate_config(self) -> bool:
        """Validate filter configuration."""
        return True
    
    async def run_safe(self, content: str) -> FilterResult:
        """Run filter with error handling and enhanced error context."""
        try:
            result = await self.run(content)
            result.filter_name = self.name
            result.filter_type = self.type
            return result
        except Exception as e:
            error_result = FilterResult(
                action='block' if self.on_error == 'block' else 'allow',
                reason=f"Filter error in '{self.name}' ({self.type}): {str(e)}",
                filter_name=self.name,
                filter_type=self.type
            )
            return error_result 