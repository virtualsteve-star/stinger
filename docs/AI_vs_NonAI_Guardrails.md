# AI vs Non-AI Guardrails: Architectural Principles

## Core Principle: Non-AI Guardrails are NOT Fallbacks

Non-AI guardrails (e.g., `simple_pii_detection`, `simple_toxicity_detection`) are **standalone alternatives**, not automatic fallbacks for failed AI detection. They serve distinct use cases and should be chosen deliberately based on your requirements.

## When to Use Each Type

### AI-Based Guardrails
**Use when you need:**
- Advanced semantic understanding
- Context-aware detection
- High accuracy for complex patterns
- Nuanced classification

**Trade-offs:**
- Requires API key and internet connectivity
- Higher latency (API calls)
- Cost per request
- Potential for API failures

### Non-AI (Regex/Rule-Based) Guardrails  
**Use when you need:**
- Fast, deterministic detection
- Offline/air-gapped operation
- Resource-constrained environments
- Low-latency requirements
- Cost-sensitive deployments

**Trade-offs:**
- Lower accuracy for complex patterns
- May produce more false positives
- Limited semantic understanding

## Error Handling Philosophy

When AI guardrails fail (no API key, network issues, etc.), the behavior is controlled by the `on_error` configuration:

```yaml
on_error: block   # Fail hard - block content for safety (recommended for high-security)
on_error: warn    # Allow content but with prominent warning
on_error: allow   # Allow content with minimal logging
```

**Important:** There is NO automatic fallback to non-AI detection. This is intentional:
- Maintains clear expectations about detection quality
- Prevents silent degradation of security
- Forces explicit architectural decisions

## Defense in Depth Strategy

For maximum security, consider running BOTH AI and non-AI guardrails:

```yaml
guardrails:
  # Layer 1: Fast regex detection
  - name: simple_code_check
    type: simple_code_generation
    confidence_threshold: 0.7
    
  # Layer 2: AI semantic analysis  
  - name: ai_code_check
    type: ai_code_generation
    confidence_threshold: 0.6
    on_error: block
```

This provides:
- Fast initial filtering (regex)
- Deep semantic analysis (AI)
- Continued protection if AI fails

## Migration Path

If transitioning from AI to non-AI (or vice versa):

1. **Run both in parallel** during transition
2. **Compare detection rates** to understand differences
3. **Adjust thresholds** as needed
4. **Make explicit switch** when ready

## Configuration Examples

### High-Security Environment
```yaml
# AI with hard failure on errors
- name: ai_pii_detector
  type: ai_pii_detection
  on_error: block  # Never allow if AI unavailable
```

### Resource-Constrained Environment
```yaml
# Use only non-AI detection
- name: simple_pii_detector
  type: simple_pii_detection
  confidence_threshold: 0.8
```

### Balanced Approach
```yaml
# AI with graceful degradation
- name: ai_toxicity_detector
  type: ai_toxicity_detection
  on_error: warn  # Alert operators but don't block
  
# Also run non-AI as backup layer
- name: simple_toxicity_detector
  type: simple_toxicity_detection
  confidence_threshold: 0.7
```

## Key Takeaways

1. **Choose explicitly** between AI and non-AI based on requirements
2. **No silent fallbacks** - failures are visible and handled per configuration
3. **Defense in depth** - consider using both types together
4. **Clear error handling** - `on_error` controls failure behavior
5. **Architectural decision** - not an implementation detail

This design ensures security posture is explicit, visible, and maintainable.