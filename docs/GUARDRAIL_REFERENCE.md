# Stinger Guardrail Reference

This document provides comprehensive documentation for all 14 guardrail types available in the Stinger security framework.

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

## Local/Rule-based Filters

### keyword_block

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

**Use Cases**:
- Block specific terms or phrases
- Content filtering for specific words
- Quick keyword-based protection

### keyword_list

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

**Use Cases**:
- Block multiple sensitive terms
- Industry-specific filtering
- Maintain keyword lists externally

### regex_filter

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

**Use Cases**:
- Complex pattern detection
- Structured data identification
- Advanced text matching

### length_filter

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

**Use Cases**:
- Input validation
- Content size control
- Prevent extremely long inputs

### url_filter

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

**Use Cases**:
- Block malicious domains
- Whitelist trusted sites
- URL-based content filtering

### pass_through

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

**Use Cases**:
- Pipeline testing
- Debugging configurations
- Placeholder filter

## AI-powered Filters

### content_moderation

**Purpose**: Comprehensive content safety using OpenAI's moderation API.

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
- Automatic fallback handling

**Use Cases**:
- General content safety
- Social media platforms
- User-generated content filtering

### prompt_injection

**Purpose**: Detects and prevents prompt injection attacks.

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

### simple_pii_detection

**Purpose**: Detects common PII patterns using regex.

**Configuration**:
```yaml
- name: basic_pii_check
  type: simple_pii_detection
  enabled: true
  on_error: allow
  config:
    risk_threshold: 70
    block_levels: ["high", "critical"]
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

### ai_pii_detection

**Purpose**: Advanced PII detection using AI analysis.

**Configuration**:
```yaml
- name: advanced_pii_check
  type: ai_pii_detection
  enabled: true
  on_error: allow
  config:
    risk_threshold: 70
    block_levels: ["high", "critical"]
    warn_levels: ["medium"]
    fallback_to_simple: true
```

**Features**:
- Contextual PII analysis
- AI-powered detection
- Fallback to simple detection
- High accuracy detection

**Use Cases**:
- Comprehensive PII protection
- Context-sensitive detection
- High-security environments

### simple_toxicity_detection

**Purpose**: Basic toxicity detection using keyword patterns.

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

### ai_toxicity_detection

**Purpose**: Advanced toxicity detection using AI analysis.

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

### simple_code_generation

**Purpose**: Detects code patterns using regex and keywords.

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

### ai_code_generation

**Purpose**: Advanced code detection using AI analysis.

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

### Best Practices

1. **Layer Multiple Filters**: Use both simple and AI filters for comprehensive protection
2. **Configure Thresholds**: Adjust risk thresholds based on your security requirements
3. **Monitor Performance**: Balance security and performance based on your needs
4. **Test Configurations**: Validate guardrail configurations in staging environments
5. **Regular Updates**: Keep keyword lists and patterns updated
6. **Fallback Strategy**: Configure error handling appropriate for your use case

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
      on_error: warn
      config:
        risk_threshold: 70
        fallback_to_simple: true
```

## Testing and Validation

Each guardrail type includes comprehensive test suites covering:

- Basic functionality
- Edge cases and boundary conditions
- Configuration validation
- Performance characteristics
- Concurrent operation
- Error handling

See the `/tests` directory for complete test implementations.

## Support and Documentation

For additional support:
- Check the `/examples` directory for usage examples
- Review test files for implementation details
- Consult the API reference for programmatic usage
- See the configuration guide for advanced settings