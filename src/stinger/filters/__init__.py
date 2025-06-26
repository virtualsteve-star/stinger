"""
Filter registry for Stinger LLM Guardrails.
Maps filter type names to their corresponding filter classes.
"""

from .pass_through import PassThroughFilter
from .keyword_block import KeywordBlockFilter
from .keyword_list import KeywordListFilter
from .regex_filter import RegexFilter
from .length_filter import LengthFilter
from .url_filter import URLFilter

# Registry mapping filter type names to filter classes
FILTER_REGISTRY = {
    'pass_through': PassThroughFilter,
    'keyword_block': KeywordBlockFilter,
    'keyword_list': KeywordListFilter,
    'regex_filter': RegexFilter,
    'length_filter': LengthFilter,
    'url_filter': URLFilter,
}

# Export all filter classes for direct import
__all__ = [
    'FILTER_REGISTRY',
    'PassThroughFilter',
    'KeywordBlockFilter', 
    'KeywordListFilter',
    'RegexFilter',
    'LengthFilter',
    'URLFilter',
]
