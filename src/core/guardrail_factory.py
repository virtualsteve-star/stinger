"""
Guardrail Factory

This module provides factory functions for creating guardrail instances
and registers them with the guardrail registry.
"""

import logging
from typing import Dict, Any, Optional
from .guardrail_interface import GuardrailInterface, GuardrailType, GuardrailRegistry, GuardrailFactory

# Import legacy filter adapters
from ..filters.legacy_adapters import (
    KeywordBlockAdapter,
    RegexFilterAdapter,
    LengthFilterAdapter,
    URLFilterAdapter,
    PassThroughFilterAdapter
)

# Import new Phase 5 filters
try:
    from ..filters.content_moderation_filter import ContentModerationFilter
    from ..filters.prompt_injection_filter import PromptInjectionFilter
    PHASE5_AVAILABLE = True
except ImportError:
    PHASE5_AVAILABLE = False
    ContentModerationFilter = None
    PromptInjectionFilter = None

logger = logging.getLogger(__name__)


def create_keyword_block_filter(name: str, config: Dict[str, Any]) -> Optional[GuardrailInterface]:
    """Create a keyword block filter."""
    try:
        return KeywordBlockAdapter(name, config)
    except Exception as e:
        logger.error(f"Failed to create keyword block filter '{name}': {e}")
        return None


def create_regex_filter(name: str, config: Dict[str, Any]) -> Optional[GuardrailInterface]:
    """Create a regex filter."""
    try:
        return RegexFilterAdapter(name, config)
    except Exception as e:
        logger.error(f"Failed to create regex filter '{name}': {e}")
        return None


def create_length_filter(name: str, config: Dict[str, Any]) -> Optional[GuardrailInterface]:
    """Create a length filter."""
    try:
        return LengthFilterAdapter(name, config)
    except Exception as e:
        logger.error(f"Failed to create length filter '{name}': {e}")
        return None


def create_url_filter(name: str, config: Dict[str, Any]) -> Optional[GuardrailInterface]:
    """Create a URL filter."""
    try:
        return URLFilterAdapter(name, config)
    except Exception as e:
        logger.error(f"Failed to create URL filter '{name}': {e}")
        return None


def create_pass_through_filter(name: str, config: Dict[str, Any]) -> Optional[GuardrailInterface]:
    """Create a pass-through filter."""
    try:
        return PassThroughFilterAdapter(name, config)
    except Exception as e:
        logger.error(f"Failed to create pass-through filter '{name}': {e}")
        return None


def create_content_moderation_filter(name: str, config: Dict[str, Any]) -> Optional[GuardrailInterface]:
    """Create a content moderation filter."""
    if not PHASE5_AVAILABLE or ContentModerationFilter is None:
        logger.warning("Content moderation filter not available (Phase 5 not installed)")
        return None
    
    try:
        return ContentModerationFilter(name, config)
    except Exception as e:
        logger.error(f"Failed to create content moderation filter '{name}': {e}")
        return None


def create_prompt_injection_filter(name: str, config: Dict[str, Any]) -> Optional[GuardrailInterface]:
    """Create a prompt injection detection filter."""
    if not PHASE5_AVAILABLE or PromptInjectionFilter is None:
        logger.warning("Prompt injection filter not available (Phase 5 not installed)")
        return None
    
    try:
        return PromptInjectionFilter(name, config)
    except Exception as e:
        logger.error(f"Failed to create prompt injection filter '{name}': {e}")
        return None


def register_all_factories(registry: GuardrailRegistry) -> None:
    """Register all guardrail factories with the registry."""
    # Register existing filters
    registry.register_factory(GuardrailType.KEYWORD_BLOCK, create_keyword_block_filter)
    registry.register_factory(GuardrailType.REGEX_FILTER, create_regex_filter)
    registry.register_factory(GuardrailType.LENGTH_FILTER, create_length_filter)
    registry.register_factory(GuardrailType.URL_FILTER, create_url_filter)
    registry.register_factory(GuardrailType.PASS_THROUGH, create_pass_through_filter)
    
    # Register Phase 5 filters if available
    if PHASE5_AVAILABLE:
        registry.register_factory(GuardrailType.CONTENT_MODERATION, create_content_moderation_filter)
        registry.register_factory(GuardrailType.PROMPT_INJECTION, create_prompt_injection_filter)
        logger.info("Registered Phase 5 guardrail factories")
    else:
        logger.info("Phase 5 guardrails not available - skipping registration")


def create_guardrail_from_config(config: Dict[str, Any], registry: GuardrailRegistry) -> Optional[GuardrailInterface]:
    """Create a guardrail from configuration using the registry."""
    factory = GuardrailFactory(registry)
    return factory.create_from_config(config)


def create_guardrails_from_configs(configs: list, registry: GuardrailRegistry) -> list:
    """Create multiple guardrails from configuration list."""
    factory = GuardrailFactory(registry)
    return factory.create_multiple_from_configs(configs) 