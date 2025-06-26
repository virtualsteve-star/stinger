from ..core.base_filter import BaseFilter, FilterResult

class KeywordBlockFilter(BaseFilter):
    async def run(self, content: str) -> FilterResult:
        keyword = self.config.get('keyword', '').lower()
        if not keyword:
            return FilterResult(action='allow', reason='no keyword set')
        if content and keyword in content.lower():
            return FilterResult(action='block', reason=f'blocked keyword: {keyword}')
        return FilterResult(action='allow', reason='no match') 