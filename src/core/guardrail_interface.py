"""
Universal Guardrail Interface System

This module provides the core interface for all guardrails to ensure pluggability
and consistent behavior across different implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class GuardrailType(Enum):
    """Types of guardrails available in the system."""
    CONTENT_MODERATION = "content_moderation"
    PROMPT_INJECTION = "prompt_injection"
    KEYWORD_BLOCK = "keyword_block"
    REGEX_FILTER = "regex_filter"
    LENGTH_FILTER = "length_filter"
    URL_FILTER = "url_filter"
    PASS_THROUGH = "pass_through"


@dataclass
class GuardrailResult:
    """Standardized result format for all guardrails."""
    blocked: bool
    confidence: float  # 0.0 to 1.0
    reason: str
    details: Dict[str, Any]
    guardrail_name: str
    guardrail_type: GuardrailType
    risk_level: Optional[str] = None  # "low", "medium", "high", "critical"
    indicators: Optional[List[str]] = None  # Array of evidence strings


class GuardrailInterface(ABC):
    """Universal interface for all guardrails to ensure pluggability."""
    
    def __init__(self, name: str, guardrail_type: GuardrailType, enabled: bool = True):
        """Initialize guardrail with name, type, and enabled status."""
        self.name = name
        self.guardrail_type = guardrail_type
        self.enabled = enabled
    
    @abstractmethod
    async def analyze(self, content: str) -> GuardrailResult:
        """Analyze content and return standardized result."""
        pass
    
    def get_name(self) -> str:
        """Return the name/identifier of this guardrail."""
        return self.name
    
    def get_type(self) -> GuardrailType:
        """Return the type of this guardrail."""
        return self.guardrail_type
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this guardrail is available/healthy."""
        pass
    
    def is_enabled(self) -> bool:
        """Check if this guardrail is enabled."""
        return self.enabled
    
    def enable(self) -> None:
        """Enable this guardrail."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable this guardrail."""
        self.enabled = False
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration of this guardrail."""
        pass
    
    @abstractmethod
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update configuration of this guardrail."""
        pass


class GuardrailRegistry:
    """Registry for managing guardrail implementations."""
    
    def __init__(self):
        """Initialize the guardrail registry."""
        self._guardrails: Dict[str, GuardrailInterface] = {}
        self._factories: Dict[GuardrailType, Callable[[str, Dict[str, Any]], Optional[GuardrailInterface]]] = {}
    
    def register_guardrail(self, guardrail: GuardrailInterface) -> None:
        """Register a guardrail instance."""
        self._guardrails[guardrail.get_name()] = guardrail
    
    def unregister_guardrail(self, name: str) -> bool:
        """Unregister a guardrail by name."""
        if name in self._guardrails:
            del self._guardrails[name]
            return True
        return False
    
    def get_guardrail(self, name: str) -> Optional[GuardrailInterface]:
        """Get a guardrail by name."""
        return self._guardrails.get(name)
    
    def get_all_guardrails(self) -> Dict[str, GuardrailInterface]:
        """Get all registered guardrails."""
        return self._guardrails.copy()
    
    def get_guardrails_by_type(self, guardrail_type: GuardrailType) -> List[GuardrailInterface]:
        """Get all guardrails of a specific type."""
        return [
            guardrail for guardrail in self._guardrails.values()
            if guardrail.get_type() == guardrail_type
        ]
    
    def register_factory(self, guardrail_type: GuardrailType, factory_func: Callable[[str, Dict[str, Any]], Optional[GuardrailInterface]]) -> None:
        """Register a factory function for creating guardrails of a specific type."""
        self._factories[guardrail_type] = factory_func
    
    def create_guardrail(self, guardrail_type: GuardrailType, name: str, config: Dict[str, Any]) -> Optional[GuardrailInterface]:
        """Create a new guardrail instance using the registered factory."""
        if guardrail_type in self._factories:
            return self._factories[guardrail_type](name, config)
        return None
    
    def clear(self) -> None:
        """Clear all registered guardrails and factories."""
        self._guardrails.clear()
        self._factories.clear()


class GuardrailFactory:
    """Factory for creating guardrail instances."""
    
    def __init__(self, registry: GuardrailRegistry):
        """Initialize the factory with a registry."""
        self.registry = registry
    
    def create_from_config(self, config: Dict[str, Any]) -> Optional[GuardrailInterface]:
        """Create a guardrail from configuration dictionary."""
        name = config.get('name')
        guardrail_type_str = config.get('type')
        
        if not name or not guardrail_type_str:
            return None
        
        try:
            guardrail_type = GuardrailType(guardrail_type_str)
        except ValueError:
            return None
        
        return self.registry.create_guardrail(guardrail_type, name, config)
    
    def create_multiple_from_configs(self, configs: List[Dict[str, Any]]) -> List[GuardrailInterface]:
        """Create multiple guardrails from configuration list."""
        guardrails = []
        for config in configs:
            guardrail = self.create_from_config(config)
            if guardrail:
                guardrails.append(guardrail)
        return guardrails 