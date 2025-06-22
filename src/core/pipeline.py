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
        highest_action = 'allow'
        highest_reason = 'All filters passed'
        
        for filter_obj in self.filters:
            try:
                result = await filter_obj.run_safe(content)
                filter_results.append(result)
                print(f"[Pipeline] {filter_obj.__class__.__name__}: {result.action} ({result.reason})")
                
                # If filter blocks, stop processing
                if result.action == 'block':
                    return PipelineResult(
                        action='block',
                        reason=f"{filter_obj.__class__.__name__}: {result.reason}",
                        filter_results=filter_results,
                        content=content
                    )
                
                # Update content if modified
                if result.modified_content is not None:
                    content = result.modified_content
                    
                if result.action == 'warn' and highest_action != 'warn':
                    highest_action = 'warn'
                    highest_reason = f"{filter_obj.__class__.__name__}: {result.reason}"
                
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
            action=highest_action,
            reason=highest_reason,
            filter_results=filter_results,
            content=content
        ) 