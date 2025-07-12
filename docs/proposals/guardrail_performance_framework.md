# Guardrail Performance Framework Proposal

## Executive Summary

We need a simple way to classify guardrails by speed so Stinger can make intelligent decisions about when and how to run them. This will dramatically improve user experience without compromising security.

## The Problem

Currently, Stinger treats all guardrails equally, but their performance varies by 1000x:
- **Regex pattern matching**: 2-5 milliseconds
- **AI-powered analysis**: 2,000-5,000 milliseconds (2-5 seconds)

This causes:
- ❌ Slow guardrails blocking conversations
- ❌ Fast guardrails running in inefficient order
- ❌ No way to show accurate progress to users
- ❌ Plugin team receiving 20 API calls per message

## Proposed Solution

### Simple Performance Classification

Every guardrail declares its speed category:

| Category | Response Time | Examples | User Experience |
|----------|--------------|----------|-----------------|
| **Instant** | < 10ms | Credit card regex, keyword blocking | Invisible to users |
| **Fast** | 10-100ms | Complex patterns, local rules | Barely noticeable |
| **Moderate** | 100ms-1s | Database lookups, simple ML | Brief pause |
| **Slow** | 1-5 seconds | AI analysis, external APIs | Noticeable wait |

### What This Enables

#### 1. Smart Execution Order
```
Before: Random order, might wait 3 seconds before finding a simple violation
After:  Instant checks first - fail fast on obvious issues
```

#### 2. Streaming Optimization
```
Before: Check every word with slow AI (impossible)
After:  Instant guards → every word
        Fast guards → every sentence  
        Slow guards → complete message only
```

#### 3. Accurate Progress Indicators
```
Before: Generic "Checking..." spinner
After:  "✓ PII Check (2ms)"
        "⏳ AI Analysis (est. 2s)"
```

#### 4. Automatic Optimization Suggestions
```
"The 'ai_sentiment' guardrail is averaging 3.2s (SLOW).
 Consider running it in monitor mode to improve response time."
```

## Implementation Details

### What Developers Provide

Each guardrail implements one simple method:
```python
def get_performance_class(self):
    return PerformanceClass.INSTANT  # or FAST, MODERATE, SLOW
```

### What We Track Automatically

- Actual execution time (to verify classifications)
- Success/failure rates by performance class
- Optimization opportunities

### Validation Through Performance Testing

Our existing performance test suite becomes the source of truth:

```python
# Performance tests automatically validate classifications
def test_credit_card_guardrail_performance():
    guardrail = CreditCardGuardrail()
    
    # Test declares expected performance
    assert guardrail.get_performance_class() == PerformanceClass.INSTANT
    
    # Test measures actual performance
    actual_time = measure_performance(guardrail, sample_content)
    assert actual_time < 10  # ms - matches INSTANT classification
    
    # Automated alerts if performance degrades
    if actual_time > 10:
        alert("CreditCardGuardrail no longer meets INSTANT criteria")
```

This gives us:
- **Continuous validation** that classifications are accurate
- **Regression detection** when guardrails get slower
- **Data-driven classification** based on real measurements
- **Automated documentation** of actual performance

### Configuration Options

Users can override behavior based on performance:
```yaml
guardrails:
  - name: credit_card_check
    type: regex_pii
    # No config needed - automatically INSTANT
    
  - name: ai_content_moderation  
    type: openai_moderation
    # Automatically SLOW, but user can choose:
    mode: monitor  # Run async, don't block conversation
```

## Benefits

### For End Users
- **50% faster response times** (by optimizing execution order)
- **Real-time feedback** on what's being checked
- **No more timeouts** on slow guardrails

### For Plugin Developers  
- **85% fewer API calls** (check at appropriate intervals)
- **Predictable performance** characteristics
- **Automatic optimization** suggestions

### For Operations Teams
- **Clear performance metrics** by guardrail
- **Capacity planning** based on guardrail mix
- **Cost optimization** (reduce unnecessary AI calls)

## Performance Test Suite Integration

### Automated Classification Validation

The performance test suite runs nightly to ensure classifications remain accurate:

```
PERFORMANCE TEST REPORT - 2025-07-12
====================================
✅ regex_pii_guardrail: INSTANT (avg: 3.2ms, max: 8.1ms)
✅ keyword_blocker: FAST (avg: 45ms, max: 92ms)
⚠️ local_ml_classifier: MODERATE (avg: 890ms, max: 1,205ms)
   WARNING: Approaching SLOW threshold
❌ ai_sentiment: SLOW (avg: 5,421ms, max: 12,003ms)
   ERROR: Exceeded SLOW threshold - should be VERY_SLOW
```

### Dynamic Optimization

Based on performance test data, the system can:
1. **Auto-adjust classifications** when performance changes
2. **Suggest optimizations** for degrading guardrails
3. **Generate reports** for capacity planning

### Performance Contracts

Each guardrail's tests serve as a performance contract:
```python
@performance_contract(
    p50=5,    # 50th percentile < 5ms
    p95=10,   # 95th percentile < 10ms
    p99=15    # 99th percentile < 15ms
)
class CreditCardGuardrail(BaseGuardrail):
    performance_class = PerformanceClass.INSTANT
```

## Migration Path

### Phase 1: Classification + Testing (Week 1)
- Add performance classification to existing guardrails
- Create performance tests for each guardrail
- Establish baseline measurements

### Phase 2: Optimization (Week 2)
- Enable execution order optimization
- Show performance in logs/metrics
- Alert on classification violations

### Phase 3: Advanced Features (Week 3+)
- Streaming checkpoint optimization
- Monitor mode suggestions
- Performance dashboards with test data

## Success Metrics

1. **User Experience**
   - Median response time reduced by 50%
   - 95th percentile under 1 second

2. **System Efficiency**
   - 85% reduction in streaming API calls
   - 30% reduction in infrastructure costs

3. **Developer Experience**
   - Zero additional complexity for basic usage
   - Automatic performance insights

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Incorrect classification | Track actual vs declared performance |
| Added complexity | Make it optional - sensible defaults |
| Breaking changes | Backward compatible - enhance, don't replace |

## Recommendation

Approve this framework as foundational infrastructure for Phase 14. It's simple enough to implement quickly but powerful enough to enable significant optimizations.

## Next Steps

1. Review and approve performance categories
2. Implement base framework (3 days)
3. Classify existing guardrails (2 days)
4. Enable optimizations (1 week)

---

## Leveraging Existing Infrastructure

### Current Performance Test Suite

We already have performance tests in `tests/performance/` that measure:
- Individual guardrail execution time
- Pipeline overhead
- Concurrent request handling
- Memory usage patterns

### Enhanced with Classifications

The performance framework enhances these tests:

```python
# Before: Just measuring time
def test_guardrail_performance():
    time = measure_guardrail(guardrail, content)
    assert time < 1000  # Arbitrary threshold

# After: Validating against declared performance
def test_guardrail_performance():
    time = measure_guardrail(guardrail, content)
    expected_class = guardrail.get_performance_class()
    
    if expected_class == PerformanceClass.INSTANT:
        assert time < 10, f"INSTANT guardrail took {time}ms"
    elif expected_class == PerformanceClass.FAST:
        assert time < 100, f"FAST guardrail took {time}ms"
    # ... etc
```

### Continuous Monitoring

The performance tests can now:
1. **Generate classification reports** showing which guardrails are in each category
2. **Track performance trends** to catch gradual degradation
3. **Validate optimization decisions** (e.g., "Did reordering actually help?")
4. **Provide data for auto-tuning** streaming checkpoints

## Appendix: Technical Details

### Performance Class Definition
```python
class PerformanceClass(Enum):
    INSTANT = "instant"      # < 10ms
    FAST = "fast"            # 10-100ms  
    MODERATE = "moderate"    # 100ms-1s
    SLOW = "slow"            # 1-5s
```

### Additional Metadata (Optional)
- `is_deterministic`: Same input always takes same time?
- `supports_streaming`: Can check partial content?
- `supports_caching`: Can cache results?

### Example Implementation
```python
class CreditCardGuardrail(BaseGuardrail):
    def get_performance_class(self):
        return PerformanceClass.INSTANT
        
    def analyze(self, content):
        # 2-5ms regex check
        return self._check_credit_cards(content)
```