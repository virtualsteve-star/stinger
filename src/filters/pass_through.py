from ..core.base_filter import BaseFilter, FilterResult

class PassThroughFilter(BaseFilter):
    async def run(self, content: str) -> FilterResult:
        return FilterResult(action='allow', reason='pass_through') 