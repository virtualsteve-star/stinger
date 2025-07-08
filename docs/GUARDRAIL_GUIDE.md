# Stinger Guardrail Guide

This document provides comprehensive documentation for all guardrails available in the Stinger security framework, including their detection capabilities, implementation details, performance characteristics, and usage examples.

**Performance Note**: All performance numbers for simple (regex-based) guardrails are from actual measurements taken during testing. AI guardrail performance estimates are based on typical API response times and will vary based on network conditions and API load.

## Table of Contents

1. [Overview](#overview)
2. [Quick Reference Table](#quick-reference-table)
3. [Simple Guardrails (Regex-Based)](#simple-guardrails-regex-based)
4. [AI-Powered Guardrails](#ai-powered-guardrails)
5. [Specialized Guardrails](#specialized-guardrails)
6. [Utility Guardrails](#utility-guardrails)
7. [Performance Comparison](#performance-comparison)
8. [Configuration Guidelines](#configuration-guidelines)
9. [Integration Examples](#integration-examples)
10. [Developer Guide](#developer-guide)

---

## Overview

Stinger provides a comprehensive set of guardrails to protect AI applications from various security and safety threats. These guardrails are categorized into two main types:

- **Local/Rule-based Filters**: Fast, deterministic filters that don't require external API calls
- **AI-powered Filters**: Advanced filters that use external AI services for contextual analysis

## Quick Reference Table

| Guardrail Type | Display Name | AI/Local | Purpose | Detects/Filters | Usage |
|---|---|---|---|---|---|
| **keyword_block** | Keyword Block | Local | Simple keyword blocking | Single keyword matches | Input/Output |
| **keyword_list** | Keyword List | Local | Multiple keyword blocking | Keywords from lists or files | Input/Output |
| **regex_filter** | Regular Expression Filter | Local | Pattern-based filtering | Complex text patterns | Input/Output |
| **length_filter** | Length Filter | Local | Content length validation | Min/max character limits | Input/Output |
| **url_filter** | URL Filter | Local | URL blocking/allowing | URLs and domains | Input/Output |
| **pass_through** | Pass Through | Local | Testing/bypassing | Nothing (allows all) | Input/Output |
| **content_moderation** | Content Moderation | AI | Comprehensive content safety | Hate, harassment, violence, sexual content | Input/Output |
| **prompt_injection** | Prompt Injection Detection | AI | Injection attack prevention | Prompt injection attempts | Input |
| **simple_pii_detection** | Simple PII Detection | Local | Basic PII identification | SSN, credit cards, emails, phones | Input/Output |
| **ai_pii_detection** | AI PII Detection | AI | Advanced PII identification | Contextual PII detection | Input/Output |
| **simple_toxicity_detection** | Simple Toxicity Detection | Local | Basic toxicity filtering | Toxic language keywords | Input/Output |
| **ai_toxicity_detection** | AI Toxicity Detection | AI | Advanced toxicity detection | Contextual toxicity analysis | Input/Output |
| **simple_code_generation** | Simple Code Generation Detection | Local | Basic code detection | Code patterns and keywords | Input/Output |
| **ai_code_generation** | AI Code Generation Detection | AI | Advanced code detection | Contextual code analysis | Input/Output |

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

**Configuration**:
```yaml
- name: basic_pii_check
  type: simple_pii_detection
  enabled: true
  on_error: allow
  config:
    risk_threshold: 70
    block_levels: ["high", "critical"]
    warn_levels: ["medium"]
    patterns:
      - ssn
      - credit_card
      - email
      - phone
```

**Features**:
- Fast regex-based detection
- Common PII patterns
- No external dependencies
- Reliable baseline protection

**Use Cases**:
- Basic PII protection
- Fast screening
- Fallback detection

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

**Configuration**:
```yaml
- name: basic_toxicity_check
  type: simple_toxicity_detection
  enabled: true
  on_error: allow
  config:
    risk_threshold: 70
    keywords_file: "toxic_keywords.txt"
    action: block
```

**Features**:
- Keyword-based detection
- Fast processing
- Customizable word lists
- Language-specific support

**Use Cases**:
- Basic content filtering
- Quick toxicity screening
- Performance-critical applications

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

**Configuration**:
```yaml
- name: basic_code_check
  type: simple_code_generation
  enabled: true
  on_error: allow
  config:
    risk_threshold: 70
    patterns:
      - programming_keywords
      - code_structures
      - file_operations
```

**Features**:
- Pattern-based detection
- Programming language recognition
- Fast processing
- Customizable patterns

**Use Cases**:
- Basic code filtering
- Educational platforms
- Content guidelines enforcement

### 4. Keyword Block Guardrail

**Purpose**: Blocks content containing a specific keyword.

**Configuration**:
```yaml
- name: sensitive_keyword_block
  type: keyword_block
  enabled: true
  on_error: allow
  config:
    keyword: "confidential"
```

**Features**:
- Case-insensitive matching
- Fast substring search
- Simple configuration
- Immediate blocking on match

**Performance**: 0.11ms average (measured)

**Use Cases**:
- Block specific terms or phrases
- Content filtering for specific words
- Quick keyword-based protection

### 5. Keyword List Guardrail

**Purpose**: Blocks content containing any keyword from a predefined list.

**Configuration**:
```yaml
- name: forbidden_words
  type: keyword_list
  enabled: true
  on_error: allow
  config:
    keywords: ["secret", "password", "confidential"]
    keyword_file: "path/to/keywords.txt"  # Optional
    case_sensitive: false
```

**Features**:
- Multiple keyword matching
- File-based keyword loading
- Case sensitivity options
- Comments support in files

**Performance**: 0.11ms average (measured)

**Use Cases**:
- Block multiple sensitive terms
- Industry-specific filtering
- Maintain keyword lists externally

### 6. Regex Guardrail

**Purpose**: Blocks content matching regular expression patterns.

**Configuration**:
```yaml
- name: pattern_filter
  type: regex_filter
  enabled: true
  on_error: allow
  config:
    patterns:
      - "\\d{3}-\\d{2}-\\d{4}"  # SSN pattern
      - "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"  # Email
    case_sensitive: true
    flags: 0  # Regex flags (e.g., re.MULTILINE)
    action: block
```

**Features**:
- Full regex pattern support
- Multiple pattern matching
- Regex flags support
- Pattern compilation optimization
- ReDoS (Regex Denial of Service) protection
- Pattern validation before compilation
- Safe execution with timeouts

**Performance**: 0.16ms average (measured)

**Use Cases**:
- Complex pattern detection
- Structured data identification
- Advanced text matching

### 7. Length Guardrail

**Purpose**: Validates content length within specified limits.

**Configuration**:
```yaml
- name: content_length_check
  type: length_filter
  enabled: true
  on_error: allow
  config:
    min_length: 10
    max_length: 1000
    action: block
```

**Features**:
- Minimum and maximum length validation
- Character count based
- Boundary condition handling
- Performance optimized

**Performance**: 0.11ms average (measured)

**Use Cases**:
- Input validation
- Content size control
- Prevent extremely long inputs

### 8. URL Guardrail

**Purpose**: Blocks or allows specific URLs and domains.

**Configuration**:
```yaml
- name: domain_filter
  type: url_filter
  enabled: true
  on_error: allow
  config:
    blocked_domains: ["malicious.com", "spam.org"]
    allowed_domains: ["trusted.com", "safe.org"]  # Optional whitelist
    action: block
```

**Features**:
- Domain-based filtering
- URL extraction from text
- Whitelist and blacklist support
- Port-aware domain matching

**Performance**: 0.12ms average (measured)

**Use Cases**:
- Block malicious domains
- Whitelist trusted sites
- URL-based content filtering

### 9. Pass Through Guardrail

**Purpose**: Testing filter that allows all content to pass through.

**Configuration**:
```yaml
- name: testing_filter
  type: pass_through
  enabled: true
  on_error: allow
```

**Features**:
- Always allows content
- No processing overhead
- Useful for testing pipelines

**Performance**: <0.1ms (measured)

**Use Cases**:
- Pipeline testing
- Debugging configurations
- Placeholder filter

---

## AI-Powered Guardrails

These guardrails use OpenAI's GPT models for intelligent content analysis. They provide more nuanced detection but with higher latency.

### 10. AI PII Detection Guardrail

**Purpose**: Advanced PII detection using AI understanding

**Advantages over Simple PII**:
- Detects obfuscated PII ("my ssn is one two three...")
- Understands context ("call me at five five five...")
- Handles variations and typos
- Multi-language support

**Performance**: ~1.5s per check (measured)

**Model**: Uses gpt-4.1-nano (configurable)

**Configuration**:
```yaml
- name: advanced_pii_check
  type: ai_pii_detection
  enabled: true
  on_error: warn  # block/warn/allow - controls behavior when AI unavailable
  config:
    risk_threshold: 70
    block_levels: ["high", "critical"]
    warn_levels: ["medium"]
```

**Features**:
- Contextual PII analysis
- AI-powered detection
- High accuracy detection
- Clear failure handling (no silent degradation)

**Use Cases**:
- Comprehensive PII protection
- Context-sensitive detection
- High-security environments

### 11. AI Toxicity Detection Guardrail

**Purpose**: Nuanced toxicity detection with context understanding

**Advantages over Simple Toxicity**:
- Understands implied toxicity
- Detects subtle harassment
- Context-aware (sarcasm, tone)
- Multi-language support

**Performance**: ~0.9s per check (measured)

**Configuration**:
```yaml
- name: advanced_toxicity_check
  type: ai_toxicity_detection
  enabled: true
  on_error: allow
  config:
    risk_threshold: 70
    block_levels: ["high", "critical"]
    warn_levels: ["medium"]
    categories:
      - harassment
      - hate_speech
      - threats
```

**Features**:
- Contextual analysis
- Nuanced detection
- Multiple toxicity categories
- AI-powered accuracy

**Use Cases**:
- Sophisticated content moderation
- Context-aware filtering
- Platform safety

### 12. AI Code Generation Guardrail

**Purpose**: Sophisticated code generation detection

**Advantages over Simple Code**:
- Understands code intent
- Detects obfuscated code requests
- Recognizes pseudo-code
- Handles multiple programming languages

**Performance**: ~0.9s per check (measured)

**Configuration**:
```yaml
- name: advanced_code_check
  type: ai_code_generation
  enabled: true
  on_error: allow
  config:
    risk_threshold: 70
    block_levels: ["high", "critical"]
    warn_levels: ["medium"]
    intent_analysis: true
```

**Features**:
- Intent-based analysis
- Context understanding
- Multi-language support
- AI-powered accuracy

**Use Cases**:
- Comprehensive code filtering
- Intent detection
- Policy enforcement

### 13. Content Moderation Guardrail

**Purpose**: Uses OpenAI's specialized moderation API

**Categories**:
- Hate/threatening content
- Harassment/bullying
- Self-harm content
- Sexual content
- Violence/graphic content

**Performance**: ~0.8s (measured)

**Configuration**:
```yaml
- name: content_safety
  type: content_moderation
  enabled: true
  on_error: allow
  config:
    risk_threshold: 70
    block_levels: ["high", "critical"]
    warn_levels: ["medium"]
    categories:
      - hate
      - harassment
      - violence
      - sexual
      - self-harm
```

**Features**:
- OpenAI moderation API integration
- Multiple content categories
- Confidence thresholds
- Configurable error handling (block/warn/allow)

**Use Cases**:
- General content safety
- Social media platforms
- User-generated content filtering

---

## Specialized Guardrails

### 14. Prompt Injection Guardrail

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

**Performance**: 
- **Regular mode**: ~2.1s (measured)
- **Conversation-aware**: ~2.3s (measured, +10% overhead)
- **With suspicious context**: ~1.8s (measured, faster due to early detection)

**Configuration**:
```yaml
- name: injection_protection
  type: prompt_injection
  enabled: true
  on_error: allow
  config:
    risk_threshold: 70
    block_levels: ["high", "critical"]
    warn_levels: ["medium"]
    conversation_awareness:
      enabled: true
      context_strategy: "mixed"
      max_context_turns: 5
      suspicious_indicators:
        - "ignore"
        - "forget"
        - "bypass"
```

**Features**:
- Multi-turn conversation analysis
- Context-aware detection
- Suspicious pattern recognition
- Advanced AI-based analysis

**Use Cases**:
- Protect AI assistants
- Prevent system prompt manipulation
- Security-critical applications

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

### AI Guardrail Performance (Measured)

AI guardrails require API calls to OpenAI. Performance depends on:
- Network latency
- OpenAI API response time  
- Request complexity
- Retry logic on failures

**Actual measurements** from performance testing:

| Guardrail Type | Measured Latency | Notes |
|----------------|------------------|-------|
| Content Moderation | 818ms | Uses optimized moderation endpoint |
| AI Toxicity | 885ms | GPT model analysis |
| AI Code Generation | 913ms | GPT model analysis |
| AI PII | 1,546ms | GPT model analysis (most complex) |
| Prompt Injection (Regular) | 2,110ms | Basic prompt injection detection |
| Prompt Injection (Conversation) | 2,319ms | +10% overhead for conversation analysis |
| Prompt Injection (Suspicious) | 1,765ms | Faster when suspicious context detected |
| Pass Through | <0.1ms | No-op filter (negligible) |

**Performance Notes:**
- **Content Moderation** is fastest among AI guardrails (~800ms)
- **AI PII** takes longer due to comprehensive pattern analysis (~1.5s)
- **Prompt Injection** varies by mode:
  - Regular mode: ~2.1s (basic detection)
  - Conversation-aware: ~2.3s (+10% overhead for context analysis)
  - With suspicious context: ~1.8s (faster due to early detection)
- All AI guardrails are significantly slower than regex-based alternatives
- Performance may vary based on network conditions and API load

### Performance Considerations

**Fast Filters** (< 1ms):
- pass_through
- keyword_block  
- length_filter

**Medium Filters** (1-10ms):
- keyword_list
- regex_filter
- url_filter
- simple_pii_detection
- simple_toxicity_detection
- simple_code_generation

**Slower Filters** (100-1000ms):
- content_moderation
- prompt_injection
- ai_pii_detection
- ai_toxicity_detection
- ai_code_generation

---

## Configuration Guidelines

### Common Configuration Options

All guardrails support these common configuration options:

```yaml
- name: guardrail_name
  type: guardrail_type
  enabled: true  # Enable/disable the guardrail
  on_error: allow  # Action on error: allow, block, warn
  config:
    # Guardrail-specific configuration
```

### Action Types

- **allow**: Permit the content to pass through
- **block**: Prevent the content from passing through
- **warn**: Allow content but generate a warning

### Error Handling

- **allow**: Continue processing if the guardrail encounters an error
- **block**: Block content if the guardrail encounters an error (safest)
- **warn**: Allow content with a warning if the guardrail encounters an error
- **skip**: Skip the guardrail if it encounters an error

### Best Practices

1. **Layer Multiple Filters**: Use both simple and AI filters for comprehensive protection
2. **Configure Thresholds**: Adjust risk thresholds based on your security requirements
3. **Monitor Performance**: Balance security and performance based on your needs
4. **Test Configurations**: Validate guardrail configurations in staging environments
5. **Regular Updates**: Keep keyword lists and patterns updated
6. **Fallback Strategy**: Configure error handling appropriate for your use case

---

## Integration Examples

### Basic Pipeline Configuration

```yaml
version: "1.0"
pipeline:
  input:
    - name: length_check
      type: length_filter
      enabled: true
      on_error: allow
      config:
        min_length: 1
        max_length: 1000
    
    - name: pii_detection
      type: simple_pii_detection
      enabled: true
      on_error: allow
      config:
        risk_threshold: 70

  output:
    - name: content_safety
      type: content_moderation
      enabled: true
      on_error: allow
      config:
        risk_threshold: 70
        block_levels: ["high", "critical"]
```

### Security-focused Pipeline

```yaml
version: "1.0"
pipeline:
  input:
    - name: injection_protection
      type: prompt_injection
      enabled: true
      on_error: block
      config:
        risk_threshold: 60
        conversation_awareness:
          enabled: true
    
    - name: sensitive_patterns
      type: regex_filter
      enabled: true
      on_error: block
      config:
        patterns:
          - "(?i)\\b(password|secret|api[_-]?key)\\b"
          - "\\d{3}-\\d{2}-\\d{4}"
        case_sensitive: false

  output:
    - name: comprehensive_pii
      type: ai_pii_detection
      enabled: true
      on_error: warn  # Consider using both AI and non-AI for defense-in-depth
      config:
        risk_threshold: 70
```

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

## Testing and Validation

Each guardrail type includes comprehensive test suites covering:

- Basic functionality
- Edge cases and boundary conditions
- Configuration validation
- Performance characteristics
- Concurrent operation
- Error handling

See the `/tests` directory for complete test implementations.

---

## Support and Documentation

For additional support:
- Check the `/examples` directory for usage examples
- Review test files for implementation details
- Consult the API reference for programmatic usage
- See the configuration guide for advanced settings

---

## Conclusion

The Stinger Guardrails Framework provides a comprehensive set of content filters ranging from simple pattern matching to sophisticated AI-powered detection. Choose guardrails based on your performance requirements and detection needs:

- Use **simple guardrails** for high-throughput, low-latency requirements
- Use **AI guardrails** when nuanced understanding is critical
- Combine both types for defense-in-depth protection
- Leverage **presets** for common use cases

For questions or contributions, please refer to the main project documentation. 