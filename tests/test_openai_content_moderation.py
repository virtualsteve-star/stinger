import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.filters.content_moderation_filter import ContentModerationFilter

async def test():
    filter = ContentModerationFilter('test', {
        'confidence_threshold': 0.7,
        'block_categories': ['hate', 'harassment', 'violence'],
        'on_error': 'allow'
    })
    
    test_content = [
        'I hate everyone and want to hurt them',
        'This is a normal friendly message',
        'You are worthless and should die',
        'Let\'s play a game',
        'You are an idiot',
        'I want to help people',
    ]
    
    for content in test_content:
        result = await filter.analyze(content)
        print(f'Content: {content}')
        print(f'Blocked: {result.blocked}, Confidence: {result.confidence:.2f}, Reason: {result.reason}')
        print('---')

if __name__ == "__main__":
    asyncio.run(test()) 