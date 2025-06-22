from typing import List
from dataclasses import dataclass
from .base_filter import BaseFilter, FilterResult
from ..utils.exceptions import PipelineError

@dataclass
class PipelineResult:
    action: str
    reason: str
    filter_results: List[FilterResult]
    content: str

class FilterPipeline:
    def __init__(self, filters: List[BaseFilter]):
        self.filters = [f for f in filters if f.enabled]
    
    async def process(self, content: str) -> PipelineResult:
        """Process content through all filters."""
        if not content:
            content = ""
        
        filter_results = []
        
        for filter_obj in self.filters:
            try:
                result = await filter_obj.run_safe(content)
                filter_results.append(result)
                
                # If filter blocks, stop processing
                if result.action == 'block':
                    return PipelineResult(
                        action='block',
                        reason=result.reason,
                        filter_results=filter_results,
                        content=content
                    )
                
                # Update content if modified
                if result.modified_content is not None:
                    content = result.modified_content
                    
            except Exception as e:
                # If filter fails and is configured to block on error
                if filter_obj.on_error == 'block':
                    return PipelineResult(
                        action='block',
                        reason=f'Pipeline error: {str(e)}',
                        filter_results=filter_results,
                        content=content
                    )
        
        # If we get here, all filters passed
        return PipelineResult(
            action='allow',
            reason='All filters passed',
            filter_results=filter_results,
            content=content
        ) 