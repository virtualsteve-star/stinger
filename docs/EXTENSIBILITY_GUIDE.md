# Extensibility Guide

**How to Create Custom Filters and Guardrails for Stinger**

This guide will teach you how to extend Stinger with your own custom filters, guardrails, and monitoring capabilities.

> **Note:** As of Phase 7B, all custom guardrails should implement `GuardrailInterface` directly. The `BaseGuardrail` class has been removed from the public API. For AI-powered guardrails, you can extend `BaseAIGuardrail` which provides common AI functionality.

## 🏗️ Architecture Overview

Stinger is built around a modular architecture with these key components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Conversation  │    │   Guardrail     │    │   Health        │
│   Management    │    │   Pipeline      │    │   Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Filter        │
                    │   Interface     │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PII Filter    │    │  Toxicity       │    │  Custom Filter  │
│                 │    │  Filter         │    │  (Your Code)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Creating Your First Custom Filter

### Step 1: Understand the Interface

All guardrails must implement the `GuardrailInterface` directly:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class GuardrailResult:
    blocked: bool
    confidence: float
    reason: str
    details: Dict[str, Any]

class GuardrailInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the guardrail."""
        pass
    
    @property
    @abstractmethod
    def guardrail_type(self) -> GuardrailType:
        """Type of guardrail."""
        pass
    
    @abstractmethod
    async def analyze(self, content: str, conversation: Optional[Any] = None) -> GuardrailResult:
        """Analyze content and return result."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if guardrail is available."""
        pass
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Get guardrail configuration."""
        pass
```

### Step 2: Create Your Guardrail

Here's a simple example - a profanity filter:

```python
# src/stinger/guardrails/custom_profanity_guardrail.py

import re
from typing import Dict, Any, List, Optional
from stinger import GuardrailInterface, GuardrailResult, GuardrailType
from ..core.config_validator import ConfigValidator, ValidationRule

class CustomProfanityGuardrail(GuardrailInterface):
    """
    Custom profanity guardrail that blocks content containing profane words.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._name = config.get('name', 'custom_profanity')
        self.enabled = config.get('enabled', True)
        
        # Validate configuration
        self._validate_config(config)
        
        # Load profanity list from config
        self.profanity_words = config.get('profanity_words', [])
        self.case_sensitive = config.get('case_sensitive', False)
        self.block_threshold = config.get('block_threshold', 1)
        
        # Compile regex patterns for efficiency
        self._compile_patterns()
    
    def get_validation_rules(self) -> List[ValidationRule]:
        """Define validation rules for this guardrail."""
        return [
            ValidationRule("profanity_words", list, required=True),
            ValidationRule("case_sensitive", bool, default=False),
            ValidationRule("block_threshold", int, default=1, min_value=1)
        ]
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration using rules."""
        validator = ConfigValidator(self.get_validation_rules())
        validator.validate(config)
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def guardrail_type(self) -> GuardrailType:
        return GuardrailType.CUSTOM
    
    def _compile_patterns(self):
        """Compile regex patterns for profanity detection."""
        if self.case_sensitive:
            patterns = [re.escape(word) for word in self.profanity_words]
        else:
            patterns = [re.escape(word) for word in self.profanity_words]
        
        self.profanity_pattern = re.compile('|'.join(patterns), 
                                          flags=0 if self.case_sensitive else re.IGNORECASE)
    
    async def analyze(self, content: str, conversation: Optional[Any] = None) -> GuardrailResult:
        """
        Analyze content for profanity.
        
        Args:
            content: Content to analyze
            conversation: Optional conversation context
            
        Returns:
            GuardrailResult with analysis
        """
        if not content or not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Filter disabled or empty content",
                details={'profanity_count': 0}
            )
        
        # Find profanity matches
        matches = self.profanity_pattern.findall(content)
        profanity_count = len(matches)
        
        # Determine if content should be blocked
        blocked = profanity_count >= self.block_threshold
        confidence = min(1.0, profanity_count / max(self.block_threshold, 1))
        
        # Create reason message
        if blocked:
            reason = f"Content contains {profanity_count} profane words (threshold: {self.block_threshold})"
        else:
            reason = f"Content contains {profanity_count} profane words (below threshold)"
        
        return GuardrailResult(
            blocked=blocked,
            confidence=confidence,
            reason=reason,
            details={
                'profanity_count': profanity_count,
                'profanity_words': list(set(matches)),
                'threshold': self.block_threshold
            }
        )
    
    def is_available(self) -> bool:
        """Check if filter is available."""
        return len(self.profanity_words) > 0
    
    def get_config(self) -> Dict[str, Any]:
        """Get filter configuration."""
        return {
            'name': self.name,
            'type': 'custom_profanity_filter',
            'enabled': self.enabled,
            'profanity_words_count': len(self.profanity_words),
            'case_sensitive': self.case_sensitive,
            'block_threshold': self.block_threshold
        }
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update filter configuration."""
        try:
            if 'profanity_words' in config:
                self.profanity_words = config['profanity_words']
                self._compile_patterns()
            
            if 'case_sensitive' in config:
                self.case_sensitive = config['case_sensitive']
                self._compile_patterns()
            
            if 'block_threshold' in config:
                self.block_threshold = config['block_threshold']
            
            return True
        except Exception as e:
            logger.error(f"Failed to update profanity filter config: {e}")
            return False
```

### Step 3: Create Configuration

Create a YAML configuration file:

```yaml
# src/stinger/guardrails/configs/custom_profanity.yaml
name: "custom_profanity_guardrail"
enabled: true
profanity_words:
  - "bad_word_1"
  - "bad_word_2"
  - "bad_word_3"
case_sensitive: false
block_threshold: 1
```

### Step 4: Register Your Guardrail

Add your guardrail to the factory:

```python
# src/stinger/core/guardrail_factory.py

def create_custom_profanity_guardrail(name: str, config: Dict[str, Any]) -> GuardrailInterface:
    """Create a custom profanity guardrail."""
    from ..guardrails.custom_profanity_guardrail import CustomProfanityGuardrail
    return CustomProfanityGuardrail(config)

# In register_all_factories function:
registry.register_factory(GuardrailType.CUSTOM_PROFANITY, create_custom_profanity_guardrail)
```

### Step 5: Use Your Guardrail

```python
# Use in a pipeline
from stinger import GuardrailPipeline

# Create pipeline with your custom filter
pipeline = GuardrailPipeline("path/to/config.yaml")

# Test your filter
result = await pipeline.check_input("This contains bad_word_1")
print(f"Blocked: {result['blocked']}")
```

## 🧪 Testing Your Custom Filter

### Unit Tests

```python
# tests/test_custom_profanity_filter.py

import pytest
from stinger.guardrails.custom_profanity_filter import CustomProfanityFilter

class TestCustomProfanityFilter:
    
    def test_profanity_detection(self):
        """Test basic profanity detection."""
        config = {
            'name': 'test_profanity',
            'profanity_words': ['bad', 'evil'],
            'block_threshold': 1
        }
        
        guardrail = CustomProfanityGuardrail(config)
        
        # Test with profanity
        result = await guardrail_instance.analyze("This is bad content")
        assert result.blocked == True
        assert result.confidence > 0.5
        
        # Test without profanity
        result = await guardrail_instance.analyze("This is good content")
        assert result.blocked == False
        assert result.confidence == 0.0
    
    def test_threshold_behavior(self):
        """Test block threshold behavior."""
        config = {
            'name': 'test_profanity',
            'profanity_words': ['bad'],
            'block_threshold': 2
        }
        
        guardrail = CustomProfanityGuardrail(config)
        
        # One profanity word (below threshold)
        result = await guardrail_instance.analyze("This is bad")
        assert result.blocked == False
        
        # Two profanity words (at threshold)
        result = await guardrail_instance.analyze("This is bad and bad")
        assert result.blocked == True
```

### Integration Tests

```python
# tests/test_integration_filters.py

def test_custom_profanity_in_pipeline():
    """Test custom profanity filter in pipeline."""
    config = {
        'input_guardrails': [
            {
                'type': 'custom_profanity',
                'name': 'test_profanity',
                'enabled': True,
                'profanity_words': ['bad'],
                'block_threshold': 1
            }
        ]
    }
    
    pipeline = GuardrailPipeline(config)
    result = pipeline.check_input("This is bad content")
    
    assert result['blocked'] == True
    assert 'test_profanity' in result['reasons'][0]
```

## 🔄 Advanced Filter Patterns

### 1. AI-Powered Guardrails

For AI-powered guardrails, extend `BaseAIGuardrail` which provides common AI functionality:

```python
from stinger.guardrails.base_ai_guardrail import BaseAIGuardrail
from stinger import GuardrailResult, GuardrailType
import json

class AIContentGuardrail(BaseAIGuardrail):
    """Guardrail using AI to analyze content."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.threshold = config.get('threshold', 0.7)
    
    def _get_detection_type(self) -> str:
        """Return the type of detection this guardrail performs."""
        return "content_analysis"
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI analysis."""
        return """You are a content moderation expert. Analyze content for inappropriate material 
        including but not limited to: hate speech, violence, adult content, or harmful instructions."""
    
    def _get_analysis_prompt(self, content: str) -> str:
        """Get the analysis prompt for the given content."""
        return f"""Analyze this content for inappropriate material:
        
        "{content}"
        
        Return a JSON response with:
        - is_inappropriate: boolean
        - confidence: float (0-1)
        - reason: string explaining your decision
        - categories: list of detected issue categories
        """
    
    def _parse_ai_response(self, response_text: str) -> GuardrailResult:
        """Parse the AI response into a GuardrailResult."""
        try:
            result_data = json.loads(response_text)
            
            blocked = result_data.get('is_inappropriate', False)
            confidence = float(result_data.get('confidence', 0.0))
            
            # Apply threshold
            if confidence < self.threshold:
                blocked = False
            
            return GuardrailResult(
                blocked=blocked,
                confidence=confidence,
                reason=result_data.get('reason', 'No reason provided'),
                details={
                    'categories': result_data.get('categories', []),
                    'threshold': self.threshold,
                    'raw_confidence': confidence
                },
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        except Exception as e:
            # If parsing fails, use the fallback handler
            return self._handle_ai_failure(content, f"Failed to parse AI response: {str(e)}")
```

### 2. Regex-Based Guardrails

```python
from stinger import GuardrailInterface, GuardrailResult, GuardrailType
from stinger.core.config_validator import ConfigValidator, ValidationRule
from stinger.core.regex_security import RegexSecurityValidator
import re

class CustomRegexGuardrail(GuardrailInterface):
    """Guardrail using regex patterns with security validation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._name = config.get('name', 'custom_regex')
        self.enabled = config.get('enabled', True)
        
        # Validate configuration
        self._validate_config(config)
        
        self.patterns = config.get('patterns', [])
        self.case_sensitive = config.get('case_sensitive', False)
        
        # Security validator for regex patterns
        self.security_validator = RegexSecurityValidator()
        
        # Compile patterns with security validation
        self.compiled_patterns = []
        flags = 0 if self.case_sensitive else re.IGNORECASE
        
        for pattern in self.patterns:
            # Validate pattern for security
            self.security_validator.validate_pattern(pattern)
            self.compiled_patterns.append(re.compile(pattern, flags))
    
    def get_validation_rules(self) -> List[ValidationRule]:
        """Define validation rules for this guardrail."""
        return [
            ValidationRule("patterns", list, required=True),
            ValidationRule("case_sensitive", bool, default=False)
        ]
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration using rules."""
        validator = ConfigValidator(self.get_validation_rules())
        validator.validate(config)
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def guardrail_type(self) -> GuardrailType:
        return GuardrailType.REGEX_FILTER
    
    async def analyze(self, content: str, conversation: Optional[Any] = None) -> GuardrailResult:
        """Check content against regex patterns."""
        if not self.enabled or not content:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Guardrail disabled or empty content",
                details={},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        matches = []
        
        for i, pattern in enumerate(self.compiled_patterns):
            # Use security validator to check execution time
            if self.security_validator.is_pattern_safe_for_content(self.patterns[i], content):
                pattern_matches = pattern.findall(content)
                if pattern_matches:
                    matches.extend(pattern_matches)
        
        blocked = len(matches) > 0
        confidence = min(1.0, len(matches) / 10.0)  # Normalize to 0-1
        
        return GuardrailResult(
            blocked=blocked,
            confidence=confidence,
            reason=f"Found {len(matches)} regex matches" if blocked else "No regex matches",
            details={'matches': matches[:10], 'patterns_checked': len(self.patterns)},  # Limit matches in response
            guardrail_name=self.name,
            guardrail_type=self.guardrail_type
        )
    
    def is_available(self) -> bool:
        """Check if guardrail is available."""
        return len(self.patterns) > 0
    
    def get_config(self) -> Dict[str, Any]:
        """Get guardrail configuration."""
        return {
            'name': self.name,
            'type': str(self.guardrail_type.value),
            'enabled': self.enabled,
            'patterns_count': len(self.patterns),
            'case_sensitive': self.case_sensitive
        }
```

### 3. Rate-Limited Guardrails

```python
from stinger import GuardrailInterface, GuardrailResult, GuardrailType
from stinger.core.rate_limiter import get_global_rate_limiter
from stinger.core.config_validator import ConfigValidator, ValidationRule

class RateLimitedGuardrail(GuardrailInterface):
    """Guardrail with built-in rate limiting."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._name = config.get('name', 'rate_limited')
        self.enabled = config.get('enabled', True)
        
        # Validate configuration
        self._validate_config(config)
        
        self.rate_limiter = get_global_rate_limiter()
        self.rate_limit_key = config.get('rate_limit_key', 'default')
        self.max_requests_per_minute = config.get('max_requests_per_minute', 60)
        
        # Your custom logic configuration
        self.custom_threshold = config.get('custom_threshold', 0.5)
    
    def get_validation_rules(self) -> List[ValidationRule]:
        """Define validation rules for this guardrail."""
        return [
            ValidationRule("rate_limit_key", str, default='default'),
            ValidationRule("max_requests_per_minute", int, default=60, min_value=1),
            ValidationRule("custom_threshold", float, default=0.5, min_value=0.0, max_value=1.0)
        ]
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration using rules."""
        validator = ConfigValidator(self.get_validation_rules())
        validator.validate(config)
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def guardrail_type(self) -> GuardrailType:
        return GuardrailType.CUSTOM
    
    async def analyze(self, content: str, conversation: Optional[Any] = None) -> GuardrailResult:
        """Analyze with rate limiting."""
        if not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Guardrail disabled",
                details={},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        # Check rate limit
        rate_result = self.rate_limiter.check_rate_limit(
            self.rate_limit_key,
            {'requests_per_minute': self.max_requests_per_minute}
        )
        
        if rate_result['exceeded']:
            return GuardrailResult(
                blocked=True,
                confidence=1.0,
                reason=f"Rate limit exceeded: {rate_result['reason']}",
                details={'rate_limit': rate_result},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        # Record request
        self.rate_limiter.record_request(self.rate_limit_key)
        
        # Perform your custom analysis here
        # This is where you'd implement your specific logic
        analysis_score = len(content) / 1000.0  # Example: score based on content length
        blocked = analysis_score > self.custom_threshold
        
        return GuardrailResult(
            blocked=blocked,
            confidence=min(1.0, analysis_score),
            reason="Content exceeds threshold" if blocked else "Content within limits",
            details={
                'rate_limit_remaining': rate_result['remaining'],
                'analysis_score': analysis_score,
                'threshold': self.custom_threshold
            },
            guardrail_name=self.name,
            guardrail_type=self.guardrail_type
        )
    
    def is_available(self) -> bool:
        """Check if guardrail is available."""
        return self.rate_limiter is not None
    
    def get_config(self) -> Dict[str, Any]:
        """Get guardrail configuration."""
        return {
            'name': self.name,
            'type': 'rate_limited',
            'enabled': self.enabled,
            'rate_limit_key': self.rate_limit_key,
            'max_requests_per_minute': self.max_requests_per_minute,
            'custom_threshold': self.custom_threshold
        }
```

## 📊 Health Monitoring for Custom Guardrails

### Adding Health Status

```python
import time
from typing import Dict, Any

class MonitoredGuardrail(GuardrailInterface):
    """Custom guardrail with health monitoring capabilities."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._name = config.get('name', 'monitored')
        self.enabled = config.get('enabled', True)
        
        # Validate configuration
        self._validate_config(config)
        
        # Initialize metrics
        self.total_checks = 0
        self.blocked_count = 0
        self.avg_response_time = 0.0
        self.last_error = None
        self.error_count = 0
    
    def get_validation_rules(self) -> List[ValidationRule]:
        """Define validation rules for this guardrail."""
        return [
            ValidationRule("monitoring_enabled", bool, default=True)
        ]
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration using rules."""
        validator = ConfigValidator(self.get_validation_rules())
        validator.validate(config)
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def guardrail_type(self) -> GuardrailType:
        return GuardrailType.CUSTOM
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get guardrail health status."""
        return {
            'name': self.name,
            'type': str(self.guardrail_type.value),
            'enabled': self.enabled,
            'available': self.is_available(),
            'last_check': time.time(),
            'custom_metrics': {
                'total_checks': self.total_checks,
                'blocked_count': self.blocked_count,
                'avg_response_time_ms': self.avg_response_time,
                'error_count': self.error_count,
                'last_error': self.last_error
            }
        }
    
    def record_metrics(self, response_time_ms: float, blocked: bool, error: Optional[str] = None):
        """Record performance metrics."""
        self.total_checks += 1
        if blocked:
            self.blocked_count += 1
        if error:
            self.error_count += 1
            self.last_error = error
        
        # Update average response time
        if self.total_checks == 1:
            self.avg_response_time = response_time_ms
        else:
            self.avg_response_time = (
                (self.avg_response_time * (self.total_checks - 1) + response_time_ms) 
                / self.total_checks
            )
```

### Health Check Integration

```python
    async def analyze(self, content: str, conversation: Optional[Any] = None) -> GuardrailResult:
        """Analyze content with metric tracking."""
        start_time = time.time()
        
        try:
            # Your custom analysis logic here
            # Example: simple keyword check
            blocked = "prohibited" in content.lower()
            confidence = 1.0 if blocked else 0.0
            
            result = GuardrailResult(
                blocked=blocked,
                confidence=confidence,
                reason="Prohibited content detected" if blocked else "Content allowed",
                details={'processing_time_ms': (time.time() - start_time) * 1000},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
            
            # Record metrics
            response_time = (time.time() - start_time) * 1000
            self.record_metrics(response_time, result.blocked)
            
            return result
            
        except Exception as e:
            # Record error
            response_time = (time.time() - start_time) * 1000
            self.record_metrics(response_time, False, str(e))
            
            # Return safe default on error
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason=f"Error during analysis: {str(e)}",
                details={'error': str(e)},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
    
    def is_available(self) -> bool:
        """Check if guardrail is available."""
        return self.enabled and self.error_count < 10  # Disable after too many errors
    
    def get_config(self) -> Dict[str, Any]:
        """Get guardrail configuration."""
        return {
            'name': self.name,
            'type': str(self.guardrail_type.value),
            'enabled': self.enabled,
            'monitoring_enabled': self.config.get('monitoring_enabled', True)
        }
```

## 🔧 Configuration Management

### Dynamic Configuration Updates

Since guardrails validate configuration at initialization, dynamic updates require creating a new instance. Here's a pattern for managing configuration updates:

```python
from stinger import GuardrailInterface, GuardrailResult, GuardrailType
from stinger.core.config_validator import ConfigValidator, ValidationRule
import logging

logger = logging.getLogger(__name__)

class ConfigurableGuardrail(GuardrailInterface):
    """Guardrail with configuration update support."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.copy()  # Keep a copy of the full config
        self._name = config.get('name', 'configurable')
        self.enabled = config.get('enabled', True)
        
        # Validate configuration
        self._validate_config(config)
        
        # Apply configuration
        self.threshold = config.get('threshold', 0.5)
        self.strict_mode = config.get('strict_mode', False)
        self.keywords = config.get('keywords', [])
    
    def get_validation_rules(self) -> List[ValidationRule]:
        """Define validation rules for this guardrail."""
        return [
            ValidationRule("threshold", float, default=0.5, min_value=0.0, max_value=1.0),
            ValidationRule("strict_mode", bool, default=False),
            ValidationRule("keywords", list, default=[])
        ]
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration using rules."""
        validator = ConfigValidator(self.get_validation_rules())
        validator.validate(config)
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def guardrail_type(self) -> GuardrailType:
        return GuardrailType.CUSTOM
    
    def create_with_updated_config(self, updates: Dict[str, Any]) -> 'ConfigurableGuardrail':
        """Create a new instance with updated configuration."""
        # Merge updates with existing config
        new_config = self.config.copy()
        new_config.update(updates)
        
        # Log the change
        logger.info(f"Creating new instance of {self.name} with updated config")
        
        # Return new instance with updated config
        return ConfigurableGuardrail(new_config)
    
    async def analyze(self, content: str, conversation: Optional[Any] = None) -> GuardrailResult:
        """Analyze content based on configuration."""
        if not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Guardrail disabled",
                details={},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        # Example analysis based on keywords
        found_keywords = [kw for kw in self.keywords if kw.lower() in content.lower()]
        confidence = len(found_keywords) / max(len(self.keywords), 1)
        
        blocked = confidence >= self.threshold
        if self.strict_mode and found_keywords:
            blocked = True
        
        return GuardrailResult(
            blocked=blocked,
            confidence=confidence,
            reason=f"Found keywords: {found_keywords}" if found_keywords else "No keywords found",
            details={
                'found_keywords': found_keywords,
                'threshold': self.threshold,
                'strict_mode': self.strict_mode
            },
            guardrail_name=self.name,
            guardrail_type=self.guardrail_type
        )
    
    def is_available(self) -> bool:
        """Check if guardrail is available."""
        return True
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()
```

### Configuration Validation

Using the built-in validation framework:

```python
import yaml
from typing import Dict, Any
from stinger.core.config_validator import ConfigValidator, ValidationRule
from stinger.core.guardrail_interface import GuardrailType

def validate_guardrail_config(config_path: str) -> bool:
    """Validate guardrail configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Define validation rules
        rules = [
            ValidationRule("name", str, required=True),
            ValidationRule("type", str, required=True, 
                         choices=[gt.value for gt in GuardrailType]),
            ValidationRule("enabled", bool, default=True),
        ]
        
        # Add type-specific rules
        if config.get('type') == 'custom_profanity':
            rules.extend([
                ValidationRule("profanity_words", list, required=True),
                ValidationRule("block_threshold", int, default=1, min_value=1)
            ])
        elif config.get('type') == 'regex_filter':
            rules.extend([
                ValidationRule("patterns", list, required=True),
                ValidationRule("case_sensitive", bool, default=False)
            ])
        
        # Validate using ConfigValidator
        validator = ConfigValidator(rules)
        validator.validate(config)
        
        print("✅ Configuration is valid")
        return True
        
    except ValueError as e:
        print(f"❌ Configuration validation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        return False
```

## 🚀 Best Practices

### 1. Performance Optimization

```python
import hashlib
from collections import OrderedDict
from typing import Dict, Any, Optional

class OptimizedGuardrail(GuardrailInterface):
    """Guardrail with performance optimizations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._name = config.get('name', 'optimized')
        self.enabled = config.get('enabled', True)
        
        # Validate configuration
        self._validate_config(config)
        
        # Pre-compile patterns for efficiency
        self.patterns = config.get('patterns', [])
        self._compile_patterns()
        
        # Use LRU cache for expensive operations
        self._cache_size = config.get('cache_size', 1000)
        self._cache = OrderedDict()
    
    def get_validation_rules(self) -> List[ValidationRule]:
        """Define validation rules for this guardrail."""
        return [
            ValidationRule("patterns", list, default=[]),
            ValidationRule("cache_size", int, default=1000, min_value=0)
        ]
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration using rules."""
        validator = ConfigValidator(self.get_validation_rules())
        validator.validate(config)
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def guardrail_type(self) -> GuardrailType:
        return GuardrailType.CUSTOM
    
    def _compile_patterns(self):
        """Pre-compile regex patterns."""
        self.compiled_patterns = []
        for pattern in self.patterns:
            try:
                compiled = re.compile(pattern)
                self.compiled_patterns.append(compiled)
            except re.error as e:
                logger.warning(f"Invalid pattern '{pattern}': {e}")
    
    def _get_cache_key(self, content: str) -> str:
        """Generate cache key for content."""
        return hashlib.md5(content.encode()).hexdigest()
    
    def _cache_get(self, key: str) -> Optional[GuardrailResult]:
        """Get from cache with LRU behavior."""
        if key in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return self._cache[key]
        return None
    
    def _cache_put(self, key: str, result: GuardrailResult):
        """Put in cache with LRU eviction."""
        self._cache[key] = result
        self._cache.move_to_end(key)
        
        # Evict oldest if cache is full
        if len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)
    
    async def analyze(self, content: str, conversation: Optional[Any] = None) -> GuardrailResult:
        """Analyze with caching and optimization."""
        if not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Guardrail disabled",
                details={},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        # Check cache first
        cache_key = self._get_cache_key(content)
        cached_result = self._cache_get(cache_key)
        if cached_result:
            return cached_result
        
        # Perform analysis with compiled patterns
        matches = []
        for pattern in self.compiled_patterns:
            if pattern.search(content):
                matches.append(pattern.pattern)
        
        blocked = len(matches) > 0
        confidence = min(1.0, len(matches) / max(len(self.patterns), 1))
        
        result = GuardrailResult(
            blocked=blocked,
            confidence=confidence,
            reason=f"Matched {len(matches)} patterns" if matches else "No pattern matches",
            details={'matched_patterns': matches},
            guardrail_name=self.name,
            guardrail_type=self.guardrail_type
        )
        
        # Cache result
        if self._cache_size > 0:
            self._cache_put(cache_key, result)
        
        return result
    
    def is_available(self) -> bool:
        """Check if guardrail is available."""
        return len(self.compiled_patterns) > 0
    
    def get_config(self) -> Dict[str, Any]:
        """Get guardrail configuration."""
        return {
            'name': self.name,
            'type': str(self.guardrail_type.value),
            'enabled': self.enabled,
            'patterns_count': len(self.patterns),
            'cache_size': self._cache_size,
            'cache_entries': len(self._cache)
        }
```

### 2. Error Handling

```python
from stinger.core.error_handling import ProductionErrorHandler
import logging

logger = logging.getLogger(__name__)

class RobustGuardrail(GuardrailInterface):
    """Guardrail with comprehensive error handling."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._name = config.get('name', 'robust')
        self.enabled = config.get('enabled', True)
        self.error_handler = ProductionErrorHandler()
        
        # Validate configuration
        self._validate_config(config)
        
        # Your configuration
        self.max_retries = config.get('max_retries', 3)
        self.fail_open = config.get('fail_open', True)  # Safe default on error
    
    def get_validation_rules(self) -> List[ValidationRule]:
        """Define validation rules for this guardrail."""
        return [
            ValidationRule("max_retries", int, default=3, min_value=0, max_value=10),
            ValidationRule("fail_open", bool, default=True)
        ]
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration using rules."""
        validator = ConfigValidator(self.get_validation_rules())
        validator.validate(config)
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def guardrail_type(self) -> GuardrailType:
        return GuardrailType.CUSTOM
    
    async def analyze(self, content: str, conversation: Optional[Any] = None) -> GuardrailResult:
        """Robust analysis with error handling."""
        # Input validation
        if not isinstance(content, str):
            logger.warning(f"Invalid input type for {self.name}: {type(content)}")
            return self._create_error_result("Invalid input type", {"input_type": str(type(content))})
        
        if not content:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Empty content",
                details={},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        # Retry logic for transient failures
        last_error = None
        for attempt in range(self.max_retries):
            try:
                # Your analysis logic here
                result = await self._perform_analysis(content)
                
                # Validate result
                if not isinstance(result, GuardrailResult):
                    raise ValueError("Analysis must return GuardrailResult")
                
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"{self.name} attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
        
        # All retries failed
        error_msg = self.error_handler.safe_error_message(str(last_error))
        logger.error(f"{self.name} failed after {self.max_retries} attempts: {error_msg}")
        
        # Return safe default based on fail_open policy
        return GuardrailResult(
            blocked=not self.fail_open,  # Block if fail_closed
            confidence=0.0,
            reason=f"Analysis failed: {error_msg}",
            details={
                'error_id': error_msg.split()[-1] if 'Error ID:' in error_msg else None,
                'fail_open': self.fail_open,
                'attempts': self.max_retries
            },
            guardrail_name=self.name,
            guardrail_type=self.guardrail_type
        )
    
    async def _perform_analysis(self, content: str) -> GuardrailResult:
        """Perform actual analysis - override in subclass."""
        # Example implementation
        blocked = "malicious" in content.lower()
        
        return GuardrailResult(
            blocked=blocked,
            confidence=1.0 if blocked else 0.0,
            reason="Malicious content detected" if blocked else "Content is safe",
            details={},
            guardrail_name=self.name,
            guardrail_type=self.guardrail_type
        )
    
    def _create_error_result(self, reason: str, details: Dict[str, Any]) -> GuardrailResult:
        """Create standardized error result."""
        return GuardrailResult(
            blocked=not self.fail_open,
            confidence=0.0,
            reason=reason,
            details=details,
            guardrail_name=self.name,
            guardrail_type=self.guardrail_type
        )
    
    def is_available(self) -> bool:
        """Check if guardrail is available."""
        return self.enabled
    
    def get_config(self) -> Dict[str, Any]:
        """Get guardrail configuration."""
        return {
            'name': self.name,
            'type': str(self.guardrail_type.value),
            'enabled': self.enabled,
            'max_retries': self.max_retries,
            'fail_open': self.fail_open
        }
```

### 3. Logging and Monitoring

```python
import logging
from datetime import datetime

class MonitoredFilter(BaseGuardrail, GuardrailInterface):
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(f"filter.{self.name}")
        self.metrics = {
            'total_requests': 0,
            'blocked_requests': 0,
            'errors': 0,
            'avg_response_time': 0.0
        }
    
    async def analyze(self, content: str) -> GuardrailResult:
        start_time = datetime.now()
        
        try:
            self.metrics['total_requests'] += 1
            
            result = await self._perform_analysis(content)
            
            if result.blocked:
                self.metrics['blocked_requests'] += 1
                self.logger.info(f"Blocked content: {result.reason}")
            
            # Update metrics
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_response_time(response_time)
            
            return result
            
        except Exception as e:
            self.metrics['errors'] += 1
            self.logger.error(f"Analysis error: {e}")
            raise
    
    def _update_response_time(self, response_time_ms: float):
        """Update average response time."""
        total = self.metrics['total_requests']
        current_avg = self.metrics['avg_response_time']
        self.metrics['avg_response_time'] = (
            (current_avg * (total - 1) + response_time_ms) / total
        )
```

## 📚 Example Implementations

### Complete Example: Sentiment Guardrail

```python
# src/stinger/guardrails/sentiment_guardrail.py

import re
from typing import Dict, Any, List, Optional
from stinger import GuardrailInterface, GuardrailResult, GuardrailType
from stinger.core.config_validator import ConfigValidator, ValidationRule

class SentimentGuardrail(GuardrailInterface):
    """
    Guardrail content based on sentiment analysis.
    Blocks overly negative or hostile content.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._name = config.get('name', 'sentiment')
        self.enabled = config.get('enabled', True)
        
        # Validate configuration
        self._validate_config(config)
        
        # Sentiment thresholds
        self.negative_threshold = config.get('negative_threshold', -0.5)
        self.hostile_threshold = config.get('hostile_threshold', -0.8)
        
        # Negative word patterns
        self.negative_words = config.get('negative_words', [])
        self.hostile_words = config.get('hostile_words', [])
        
        # Compile patterns
        self._compile_patterns()
    
    def get_validation_rules(self) -> List[ValidationRule]:
        """Define validation rules for this guardrail."""
        return [
            ValidationRule("negative_threshold", float, default=-0.5, min_value=-1.0, max_value=0.0),
            ValidationRule("hostile_threshold", float, default=-0.8, min_value=-1.0, max_value=0.0),
            ValidationRule("negative_words", list, default=[]),
            ValidationRule("hostile_words", list, default=[])
        ]
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration using rules."""
        validator = ConfigValidator(self.get_validation_rules())
        validator.validate(config)
        
        # Additional validation
        if self.hostile_threshold > self.negative_threshold:
            raise ValueError("hostile_threshold must be less than negative_threshold")
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def guardrail_type(self) -> GuardrailType:
        return GuardrailType.CUSTOM
    
    def _compile_patterns(self):
        """Compile regex patterns for sentiment detection."""
        self.negative_pattern = re.compile(
            '|'.join(re.escape(word) for word in self.negative_words),
            re.IGNORECASE
        )
        self.hostile_pattern = re.compile(
            '|'.join(re.escape(word) for word in self.hostile_words),
            re.IGNORECASE
        )
    
    async def analyze(self, content: str, conversation: Optional[Any] = None) -> GuardrailResult:
        """Analyze content sentiment."""
        if not content or not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Guardrail disabled or empty content",
                details={'sentiment_score': 0.0},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type
            )
        
        # Calculate sentiment score
        sentiment_score = self._calculate_sentiment(content)
        
        # Determine if content should be blocked
        blocked = sentiment_score <= self.hostile_threshold
        confidence = abs(sentiment_score)
        
        # Create reason
        if sentiment_score <= self.hostile_threshold:
            reason = f"Hostile content detected (score: {sentiment_score:.2f})"
        elif sentiment_score <= self.negative_threshold:
            reason = f"Negative content detected (score: {sentiment_score:.2f})"
        else:
            reason = f"Content sentiment acceptable (score: {sentiment_score:.2f})"
        
        return GuardrailResult(
            blocked=blocked,
            confidence=confidence,
            reason=reason,
            details={
                'sentiment_score': sentiment_score,
                'negative_threshold': self.negative_threshold,
                'hostile_threshold': self.hostile_threshold
            },
            guardrail_name=self.name,
            guardrail_type=self.guardrail_type
        )
    
    def _calculate_sentiment(self, content: str) -> float:
        """Calculate sentiment score (-1 to 1)."""
        # Count negative and hostile words
        negative_count = len(self.negative_pattern.findall(content))
        hostile_count = len(self.hostile_pattern.findall(content))
        
        # Calculate score (negative = negative sentiment)
        total_words = len(content.split())
        if total_words == 0:
            return 0.0
        
        # Weight hostile words more heavily
        sentiment_score = -(negative_count + 2 * hostile_count) / total_words
        
        # Clamp to -1 to 1
        return max(-1.0, min(1.0, sentiment_score))
    
    def is_available(self) -> bool:
        """Check if guardrail is available."""
        return len(self.negative_words) > 0 or len(self.hostile_words) > 0
    
    def get_config(self) -> Dict[str, Any]:
        """Get guardrail configuration."""
        return {
            'name': self.name,
            'type': str(self.guardrail_type.value),
            'enabled': self.enabled,
            'negative_threshold': self.negative_threshold,
            'hostile_threshold': self.hostile_threshold,
            'negative_words_count': len(self.negative_words),
            'hostile_words_count': len(self.hostile_words)
        }
```

## 🎯 Next Steps

Now that you understand how to create custom guardrails:

1. **Start Simple**: Begin with basic regex or keyword filters
2. **Add Testing**: Write comprehensive tests for your filters
3. **Optimize**: Add caching and performance improvements
4. **Monitor**: Integrate with health monitoring
5. **Share**: Contribute your filters to the community

## 📖 Additional Resources

- **Guardrail Interface**: `src/stinger/core/guardrail_interface.py`
- **Base AI Guardrail**: `src/stinger/guardrails/base_ai_guardrail.py` (for AI-powered guardrails)
- **Existing Guardrails**: `src/stinger/guardrails/` directory
- **Test Examples**: `tests/` directory
- **Configuration Examples**: `src/stinger/guardrails/configs/`
- **Config Validator**: `src/stinger/core/config_validator.py`

---

**🚀 Happy coding! Your custom filters will help make LLM applications safer and more reliable.** 