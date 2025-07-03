# Stinger Guardrails Overview

This document provides a comprehensive overview of all guardrails available in the Stinger Guardrails Framework, including their detection capabilities, implementation details, performance characteristics, and usage examples.

**Performance Note**: All performance numbers for simple (regex-based) guardrails are from actual measurements taken during testing. AI guardrail performance estimates are based on typical API response times and will vary based on network conditions and API load.

## Table of Contents

1. [Simple Guardrails](#simple-guardrails-regex-based)
2. [AI-Powered Guardrails](#ai-powered-guardrails)
3. [Specialized Guardrails](#specialized-guardrails)
4. [Utility Guardrails](#utility-guardrails)
5. [Performance Comparison](#performance-comparison)
6. [Developer Guide](#developer-guide)

---

## Simple Guardrails (Regex-Based)

These guardrails use pattern matching and are extremely fast, making them ideal for high-throughput scenarios or as fallbacks when AI services are unavailable.

### 1. Simple PII Detection Guardrail

**Purpose**: Detects Personally Identifiable Information using regex patterns

**Detection Capabilities**:
- Social Security Numbers (SSN): `123-45-6789` format
- Credit Card Numbers: 16-digit patterns with validation
- Email Addresses: Standard email format
- Phone Numbers: Various formats (US)
- IP Addresses: IPv4 format
- Driver's License Numbers: State-specific patterns
- Passport Numbers: International patterns
- Bank Account Numbers: 8-12 digit patterns

**How It Works**:
- Pre-compiled regex patterns for each PII type
- Confidence scoring based on pattern type:
  - High confidence (0.9): SSN, Credit Cards
  - Medium confidence (0.7): Email, Phone
  - Lower confidence (0.5): Bank accounts, IPs

**Performance**: 0.11ms average (measured)

**Example Usage**:
```python
config = {
    "name": "pii_filter",
    "type": "simple_pii_detection",
    "enabled": True,
    "on_error": "block",
    "config": {
        "patterns": ["ssn", "credit_card", "email"],
        "confidence_threshold": 0.8
    }
}
```

### 2. Simple Toxicity Detection Guardrail

**Purpose**: Detects toxic content using keyword patterns

**Detection Categories**:
- **Hate Speech**: Racist, bigoted, discriminatory language
- **Harassment**: Bullying, personal attacks ("I hate you", "you suck")
- **Threats**: Violence threats, death wishes
- **Sexual Harassment**: Explicit content, inappropriate requests
- **Violence**: Fighting, weapons, physical harm

**How It Works**:
- Regex patterns for each toxicity category
- Higher base confidence (0.6) for serious categories
- Case-insensitive matching by default

**Performance**: 0.12ms average (measured)

**Example Usage**:
```python
config = {
    "name": "toxicity_filter",
    "type": "simple_toxicity_detection",
    "enabled": True,
    "on_error": "block",
    "config": {
        "categories": ["hate_speech", "harassment", "threats"],
        "confidence_threshold": 0.7
    }
}
```

### 3. Simple Code Generation Guardrail

**Purpose**: Detects attempts to generate code or inject commands

**Detection Categories**:
- **Code Requests**: "Write a function", "Generate SQL query"
- **Code Blocks**: Markdown code blocks, inline code
- **Programming Keywords**: function, class, import, etc.
- **Code Injection**: eval, exec, system commands
- **File Operations**: File manipulation commands
- **System Commands**: Shell/terminal commands

**How It Works**:
- Multiple pattern categories with different base confidences
- Requires minimum keyword matches (configurable)
- Higher confidence for explicit code requests

**Performance**: 0.16ms average (measured)

**Example Usage**:
```python
config = {
    "name": "code_guard",
    "type": "simple_code_generation",
    "enabled": True,
    "on_error": "block",
    "config": {
        "categories": ["code_requests", "code_injection"],
        "confidence_threshold": 0.6,
        "min_keywords": 2
    }
}
```

### 4. Keyword Block Guardrail

**Purpose**: Blocks a single specific keyword

**How It Works**:
- Simple string containment check
- Optional case sensitivity

**Performance**: 0.11ms average (measured)

**Example Usage**:
```python
config = {
    "name": "block_confidential",
    "type": "keyword_block",
    "enabled": True,
    "on_error": "block",
    "config": {
        "keyword": "confidential",
        "case_sensitive": False
    }
}
```

### 5. Keyword List Guardrail

**Purpose**: Blocks multiple keywords from a list

**Features**:
- Inline keyword list or file-based
- Combines multiple sources
- Skip comments and empty lines in files

**Performance**: 0.11ms average (measured)

**Example Usage**:
```python
config = {
    "name": "profanity_filter",
    "type": "keyword_list",
    "enabled": True,
    "on_error": "block",
    "config": {
        "keywords": ["damn", "hell", "crap"],
        "keywords_file": "/path/to/bad_words.txt",
        "case_sensitive": False
    }
}
```

### 6. Regex Guardrail

**Purpose**: Flexible pattern matching with custom regex

**Security Features**:
- ReDoS (Regex Denial of Service) protection
- Pattern validation before compilation
- Safe execution with timeouts

**Performance**: 0.16ms average (measured)

**Example Usage**:
```python
config = {
    "name": "custom_filter",
    "type": "regex_filter",
    "enabled": True,
    "on_error": "block",
    "config": {
        "patterns": [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"password\s*[:=]\s*\S+"    # Password patterns
        ],
        "case_sensitive": False,
        "action": "block"
    }
}
```

---

## AI-Powered Guardrails

These guardrails use OpenAI's GPT models for intelligent content analysis. They provide more nuanced detection but with higher latency.

### 7. AI PII Detection Guardrail

**Purpose**: Advanced PII detection using AI understanding

**Advantages over Simple PII**:
- Detects obfuscated PII ("my ssn is one two three...")
- Understands context ("call me at five five five...")
- Handles variations and typos
- Multi-language support

**Performance**: ~200-500ms per check

**Model**: Uses gpt-4.1-nano (configurable)

**Example Usage**:
```python
config = {
    "name": "ai_pii",
    "type": "ai_pii_detection",
    "enabled": True,
    "on_error": "block",
    "config": {
        "confidence_threshold": 0.8,
        "fallback_to_simple": True  # Use simple detection if AI fails
    }
}
```

### 8. AI Toxicity Detection Guardrail

**Purpose**: Nuanced toxicity detection with context understanding

**Advantages over Simple Toxicity**:
- Understands implied toxicity
- Detects subtle harassment
- Context-aware (sarcasm, tone)
- Multi-language support

**Performance**: ~200-500ms per check

**Example Usage**:
```python
config = {
    "name": "ai_toxicity",
    "type": "ai_toxicity_detection",
    "enabled": True,
    "on_error": "block",
    "config": {
        "confidence_threshold": 0.7,
        "categories": ["hate", "harassment", "violence"]
    }
}
```

### 9. AI Code Generation Guardrail

**Purpose**: Sophisticated code generation detection

**Advantages over Simple Code**:
- Understands code intent
- Detects obfuscated code requests
- Recognizes pseudo-code
- Handles multiple programming languages

**Performance**: ~200-500ms per check

**Example Usage**:
```python
config = {
    "name": "ai_code",
    "type": "ai_code_generation",
    "enabled": True,
    "on_error": "warn",
    "config": {
        "confidence_threshold": 0.6
    }
}
```

### 10. Content Moderation Guardrail

**Purpose**: Uses OpenAI's specialized moderation API

**Categories**:
- Hate/threatening content
- Harassment/bullying
- Self-harm content
- Sexual content
- Violence/graphic content

**Performance**: ~100-300ms (optimized moderation endpoint)

**Example Usage**:
```python
config = {
    "name": "content_mod",
    "type": "content_moderation",
    "enabled": True,
    "on_error": "block",
    "config": {
        "block_categories": ["hate", "harassment", "sexual"],
        "warn_categories": ["violence"],
        "confidence_threshold": 0.7
    }
}
```

---

## Specialized Guardrails

### 11. Prompt Injection Guardrail

**Purpose**: Detects sophisticated prompt injection attempts

**Advanced Features**:
- **Conversation Awareness**: Analyzes multi-turn patterns
- **Trust Building Detection**: Identifies social engineering
- **Role Playing Detection**: Catches impersonation attempts
- **Context Manipulation**: Detects attempts to change context

**Configuration Options**:
- `risk_threshold`: 0-100 scale (default 70)
- `block_levels`: ["high", "critical"]
- `conversation_awareness`: Enable multi-turn analysis
- `context_strategy`: "recent", "suspicious", or "mixed"

**Performance**: ~300-700ms (with conversation analysis)

**Example Usage**:
```python
config = {
    "name": "injection_guard",
    "type": "prompt_injection",
    "enabled": True,
    "on_error": "block",
    "config": {
        "risk_threshold": 60,
        "block_levels": ["medium", "high", "critical"],
        "conversation_awareness": {
            "enabled": True,
            "context_strategy": "mixed",
            "max_context_turns": 5
        }
    }
}
```

### 12. URL Guardrail

**Purpose**: Filters URLs based on domain lists

**Features**:
- Domain blocking/allowing
- Subdomain matching
- Works with or without protocols
- Efficient URL extraction

**Performance**: 0.12ms average (measured)

**Example Usage**:
```python
config = {
    "name": "url_filter",
    "type": "url_filter",
    "enabled": True,
    "on_error": "block",
    "config": {
        "blocked_domains": ["evil.com", "malicious.org"],
        "allowed_domains": ["company.com", "trusted.org"]
    }
}
```

### 13. Topic Guardrail

**Purpose**: Content filtering based on topic lists

**Modes**:
- **Allow Mode**: Only permit specified topics
- **Deny Mode**: Block specified topics
- **Both Mode**: Apply both lists

**Performance**: 0.16ms average (measured)

**Example Usage**:
```python
config = {
    "name": "topic_filter",
    "type": "topic",
    "enabled": True,
    "on_error": "block",
    "config": {
        "mode": "both",
        "allow_topics": ["medical", "health", "treatment"],
        "deny_topics": ["politics", "religion"],
        "use_regex": True,
        "confidence_threshold": 0.5
    }
}
```

---

## Utility Guardrails

### 14. Length Guardrail

**Purpose**: Validates content length

**Use Cases**:
- Prevent empty inputs
- Limit message size
- Prevent resource exhaustion

**Performance**: 0.11ms average (measured)

**Example Usage**:
```python
config = {
    "name": "length_check",
    "type": "length_filter",
    "enabled": True,
    "on_error": "block",
    "config": {
        "min_length": 1,
        "max_length": 5000
    }
}
```

### 15. Pass Through Guardrail

**Purpose**: No-op filter for testing

**Use Cases**:
- Pipeline testing
- Placeholder in configurations
- Performance baseline

**Performance**: <0.1ms (measured)

**Example Usage**:
```python
config = {
    "name": "passthrough",
    "type": "pass_through",
    "enabled": True
}
```

---

## Performance Comparison

### Measured Performance (Simple Guardrails)

These measurements are from actual performance tests on standard hardware:

| Guardrail Type | Min Latency | Avg Latency | Max Latency | Use Case |
|----------------|-------------|-------------|-------------|-----------|
| Keyword Block | 0.10ms | 0.11ms | 0.11ms | Single keyword blocking |
| Length Filter | 0.10ms | 0.11ms | 0.14ms | Content size validation |
| Keyword List | 0.10ms | 0.11ms | 0.12ms | Multiple keyword blocking |
| Simple PII | 0.11ms | 0.11ms | 0.12ms | Fast PII detection |
| Simple Toxicity | 0.11ms | 0.12ms | 0.13ms | Fast toxicity detection |
| URL Filter | 0.11ms | 0.11ms | 0.14ms | Domain filtering |
| Simple Code | 0.14ms | 0.16ms | 0.23ms | Code detection |
| Regex Filter | 0.15ms | 0.16ms | 0.22ms | Custom patterns |

### Performance Scaling

From the behavioral performance tests:
- **PII Detection on various text sizes**:
  - Small text (<100 chars): ~0.14ms
  - Medium text (~1KB): ~0.17ms  
  - Large text (~13KB): ~0.63ms
  - Very large text (~50KB): <1s requirement met
- **Pipeline overhead**: ~0.21ms for 2 guardrails
- **Batch processing**: <50ms average per item across 100 items
- **Heavy pipeline**: 5 guardrails complete in <500ms
- **Concurrent performance**: <3x degradation under load

### AI Guardrail Performance (Estimated)

AI guardrails require API calls to OpenAI. Performance depends on:
- Network latency
- OpenAI API response time  
- Request complexity
- Retry logic on failures

| Guardrail Type | Estimated Latency | Notes |
|----------------|-------------------|-------|
| Content Moderation | 100-300ms | Uses optimized moderation endpoint |
| AI PII | 200-500ms | GPT model analysis |
| AI Toxicity | 200-500ms | GPT model analysis |
| AI Code | 200-500ms | GPT model analysis |
| Prompt Injection | 300-700ms | Most complex, includes conversation analysis |
| Pass Through | <0.1ms | No-op filter (negligible) |
| Topic Filter | ~0.11ms* | Similar to keyword matching |

*Topic filter not directly measured but expected similar to keyword-based filters

---

## Developer Guide

### Creating a Custom Guardrail

All guardrails inherit from `GuardrailInterface`:

```python
from typing import Optional, Dict, Any, List
from stinger.core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType
from stinger.core.conversation import Conversation

class MyCustomGuardrail(GuardrailInterface):
    def __init__(self, config: Dict[str, Any]):
        # Set guardrail name and type
        name = config.get("name", "my_custom_guardrail")
        super().__init__(name, GuardrailType.CUSTOM, config)
        
        # Handle nested config from pipeline
        nested_config = config.get("config", {})
        
        # Extract your configuration
        self.threshold = nested_config.get("threshold", config.get("threshold", 0.5))
        self.patterns = nested_config.get("patterns", config.get("patterns", []))
    
    async def analyze(
        self, 
        content: str, 
        conversation: Optional[Conversation] = None
    ) -> GuardrailResult:
        """Analyze content and return result"""
        
        # Your detection logic here
        detected = False
        confidence = 0.0
        
        # Check patterns
        for pattern in self.patterns:
            if pattern in content:
                detected = True
                confidence = 0.8
                break
        
        # Determine if should block
        blocked = detected and confidence >= self.threshold
        
        return GuardrailResult(
            blocked=blocked,
            confidence=confidence,
            reason="Custom detection triggered" if detected else "No issues found",
            details={
                "patterns_checked": len(self.patterns),
                "threshold": self.threshold
            },
            guardrail_name=self.name,
            guardrail_type=self.guardrail_type
        )
    
    def is_available(self) -> bool:
        """Check if guardrail is available"""
        return self.enabled
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return {
            "enabled": self.enabled,
            "threshold": self.threshold,
            "patterns": self.patterns
        }
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update configuration"""
        try:
            if "threshold" in config:
                self.threshold = config["threshold"]
            if "patterns" in config:
                self.patterns = config["patterns"]
            return True
        except Exception:
            return False
```

### Registering Your Guardrail

Add to the guardrail factory:

```python
# In guardrail_factory.py
def create_my_custom_guardrail(name: str, config: Dict[str, Any]) -> GuardrailInterface:
    """Create custom guardrail instance"""
    return MyCustomGuardrail(config)

# Register with factory
def initialize_factories(registry: GuardrailRegistry):
    # ... existing registrations ...
    registry.register_factory(GuardrailType.CUSTOM, create_my_custom_guardrail)
```

### Best Practices

1. **Configuration Handling**:
   - Always handle nested config structure
   - Provide sensible defaults
   - Validate configuration values

2. **Performance**:
   - Pre-compile regex patterns
   - Cache expensive computations
   - Consider async operations for I/O

3. **Error Handling**:
   - Respect `on_error` configuration
   - Log errors appropriately
   - Fail gracefully

4. **Testing**:
   - Write behavioral tests
   - Test edge cases
   - Verify performance characteristics

---

## Preset Configurations

Stinger includes preset configurations for common use cases:

- **Medical**: High PII protection, medical terminology allowed
- **Financial**: Strict PII/injection protection, financial terms monitoring
- **Educational**: Toxicity filtering, code generation allowed
- **Customer Service**: Balanced toxicity threshold, PII warnings

See `PresetConfigs` class for full preset definitions.

---

## Conclusion

The Stinger Guardrails Framework provides a comprehensive set of content filters ranging from simple pattern matching to sophisticated AI-powered detection. Choose guardrails based on your performance requirements and detection needs:

- Use **simple guardrails** for high-throughput, low-latency requirements
- Use **AI guardrails** when nuanced understanding is critical
- Combine both types for defense-in-depth protection
- Leverage **presets** for common use cases

For questions or contributions, please refer to the main project documentation.