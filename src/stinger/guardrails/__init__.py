"""
Filter registry for Stinger LLM Guardrails.
Maps filter type names to their corresponding filter classes.
"""

from .pass_through import PassThroughGuardrail
from .keyword_block import KeywordBlockGuardrail
from .keyword_list import KeywordListGuardrail
from .regex_guardrail import RegexGuardrail
from .length_guardrail import LengthGuardrail
from .url_guardrail import URLGuardrail
from .topic_guardrail import TopicGuardrail

# Registry mapping filter type names to filter classes
GUARDRAIL_REGISTRY = {
    'pass_through': PassThroughGuardrail,
    'keyword_block': KeywordBlockGuardrail,
    'keyword_list': KeywordListGuardrail,
    'regex_filter': RegexGuardrail,
    'length_filter': LengthGuardrail,
    'url_filter': URLGuardrail,
    'topic_filter': TopicGuardrail,
}

# Export all filter classes for direct import
__all__ = [
    'GUARDRAIL_REGISTRY',
    'PassThroughGuardrail',
    'KeywordBlockGuardrail', 
    'KeywordListGuardrail',
    'RegexGuardrail',
    'LengthGuardrail',
    'URLGuardrail',
    'TopicGuardrail',
]
