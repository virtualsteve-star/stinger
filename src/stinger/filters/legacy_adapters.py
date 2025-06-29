"""
Legacy Filter Adapters

This module provides adapter classes that wrap existing BaseFilter implementations
to work with the new GuardrailInterface system.
"""

import logging
from typing import Dict, Any
from ..core.guardrail_interface import GuardrailInterface, GuardrailType, GuardrailResult
from ..core.base_filter import BaseFilter, FilterResult

logger = logging.getLogger(__name__)


class LegacyFilterAdapter(GuardrailInterface):
    """Adapter that wraps legacy BaseFilter implementations."""
    
    def __init__(self, name: str, guardrail_type: GuardrailType, legacy_filter: BaseFilter):
        """Initialize the adapter with a legacy filter."""
        super().__init__(name, guardrail_type, legacy_filter.enabled)
        self.legacy_filter = legacy_filter
    
    async def analyze(self, content: str) -> GuardrailResult:
        """Run the legacy filter and convert the result."""
        try:
            legacy_result = await self.legacy_filter.run_safe(content)
            
            # Convert legacy FilterResult to GuardrailResult
            blocked = legacy_result.action == 'block'
            confidence = legacy_result.confidence
            
            return GuardrailResult(
                blocked=blocked,
                confidence=confidence,
                reason=legacy_result.reason,
                details={
                    'action': legacy_result.action,
                    'modified_content': legacy_result.modified_content,
                    'filter_name': legacy_result.filter_name,
                    'filter_type': legacy_result.filter_type
                },
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
            
        except Exception as e:
            logger.error(f"Legacy filter analysis failed for {self.name}: {e}")
            return GuardrailResult(
                blocked=self.legacy_filter.on_error == 'block',
                confidence=0.0,
                reason=f"Legacy filter error: {str(e)}",
                details={'error': str(e)},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
    
    def is_available(self) -> bool:
        """Check if the legacy filter is available."""
        return self.legacy_filter.enabled
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration of this filter."""
        return {
            'name': self.name,
            'type': self.guardrail_type.value,
            'enabled': self.is_enabled(),
            'legacy_config': self.legacy_filter.config,
            'available': self.is_available()
        }
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update configuration of this filter."""
        try:
            # Update legacy filter config
            if 'legacy_config' in config:
                self.legacy_filter.config.update(config['legacy_config'])
            
            # Update enabled status
            if 'enabled' in config:
                if config['enabled']:
                    self.enable()
                    self.legacy_filter.enabled = True
                else:
                    self.disable()
                    self.legacy_filter.enabled = False
            
            logger.info(f"Updated configuration for {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration for {self.name}: {e}")
            return False


# Specific adapter classes for each filter type
class KeywordBlockAdapter(LegacyFilterAdapter):
    """Adapter for KeywordBlockFilter."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        from .keyword_block import KeywordBlockFilter
        legacy_filter = KeywordBlockFilter(config)
        super().__init__(name, GuardrailType.KEYWORD_BLOCK, legacy_filter)


class RegexFilterAdapter(LegacyFilterAdapter):
    """Adapter for RegexFilter."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        from .regex_filter import RegexFilter
        legacy_filter = RegexFilter(config)
        super().__init__(name, GuardrailType.REGEX_FILTER, legacy_filter)


class LengthFilterAdapter(LegacyFilterAdapter):
    """Adapter for LengthFilter."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        from .length_filter import LengthFilter
        # Extract the nested config if it exists, otherwise use the config as-is
        filter_config = config.get('config', config).copy()
        # Also copy top-level settings that LengthFilter needs
        if 'action' not in filter_config and 'on_error' in config:
            filter_config['action'] = config['on_error']
        legacy_filter = LengthFilter(filter_config)
        super().__init__(name, GuardrailType.LENGTH_FILTER, legacy_filter)


class URLFilterAdapter(LegacyFilterAdapter):
    """Adapter for URLFilter."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        from .url_filter import URLFilter
        legacy_filter = URLFilter(config)
        super().__init__(name, GuardrailType.URL_FILTER, legacy_filter)


class PassThroughFilterAdapter(LegacyFilterAdapter):
    """Adapter for PassThroughFilter."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        from .pass_through import PassThroughFilter
        legacy_filter = PassThroughFilter(config)
        super().__init__(name, GuardrailType.PASS_THROUGH, legacy_filter) 