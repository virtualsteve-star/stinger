# Testing Strategy for Stinger Guardrails

## Overview

Stinger Guardrails uses a **three-tier testing strategy** to balance development speed with comprehensive validation of AI guardrail effectiveness and scalability.

## Three-Tier Strategy

### Tier 1: CI Tests (Fast Development)
**Purpose**: Verify basic functionality and quick sanity checks  
**Performance**: <30 seconds total for all CI tests  
**Frequency**: Run on every PR, every development cycle  
**Location**: `tests/ci/` or marked with `@pytest.mark.ci`

#### What Tier 1 Tests Cover:
- ✅ Basic functionality verification
- ✅ Obvious detection cases (SSN, hate speech, etc.)
- ✅ Guardrail availability and initialization
- ✅ Configuration validation
- ✅ Response to benign content
- ✅ Simple pattern matching validation

#### Example Tier 1 Test:
```python
@pytest.mark.ci
@pytest.mark.asyncio
async def test_ai_pii_sanity(self):
    """Verify AI PII detection responds to obvious PII"""
    result = await guardrail.analyze("My SSN is 123-45-6789")
    assert result.blocked is True, "AI PII should block obvious SSN"
    assert result.confidence > 0.5, "AI PII should have high confidence"
```

### Tier 2: Efficacy Tests (Correctness Validation)
**Purpose**: Measure detection accuracy, false positive rates, and edge cases  
**Performance**: 5-10 minutes for thorough validation  
**Frequency**: Run on main branch, before releases  
**Location**: `tests/efficacy/` or marked with `@pytest.mark.efficacy`

#### What Tier 2 Tests Cover:
- 📊 **Accuracy Measurement**: Comprehensive test cases with expected outcomes
- 📈 **Performance Benchmarks**: Timing analysis and performance thresholds
- 🔍 **Edge Case Testing**: Unusual inputs, boundary conditions
- 📋 **False Positive/Negative Analysis**: Detailed error rate reporting
- 🎯 **Sophisticated Attack Detection**: Advanced prompt injection techniques
- 🧪 **Comprehensive Validation**: Deep testing of guardrail effectiveness

#### Example Tier 2 Test Results:
```
PII Detection Accuracy: 85.7%
False Positives: 2/14 (14.3%)
False Negatives: 0/14 (0.0%)

Toxicity Detection Accuracy: 78.6%
False Positives: 3/14 (21.4%)
False Negatives: 0/14 (0.0%)

Prompt Injection Detection Accuracy: 56.25%
False Positives: 0/16 (0.0%)
False Negatives: 7/16 (43.75%)
```

### Tier 3: Performance Tests (Scalability & Load)
**Purpose**: Validate scalability, load handling, and performance under stress  
**Performance**: 10-30 minutes for comprehensive scalability validation  
**Frequency**: Run before major releases, performance regression detection  
**Location**: `tests/performance/` or marked with `@pytest.mark.performance`

#### What Tier 3 Tests Cover:
- 🚀 **Load Testing**: Concurrent request handling and throughput analysis
- 📊 **Scalability Validation**: Performance under increasing load
- 💾 **Memory Usage Analysis**: Memory consumption patterns and leaks
- ⏱️ **Response Time Distribution**: P95, P99 latency analysis
- 🔄 **Stress Testing**: System behavior under extreme conditions
- 📈 **Performance Regression Detection**: Automated performance monitoring

## Test Execution

### Using the Test Runner Script
```bash
# Quick CI tests (development)
python3 run_test_suites.py ci

# Comprehensive efficacy tests (correctness validation)
python3 run_test_suites.py efficacy

# Performance and scalability tests
python3 run_test_suites.py performance

# All tests across all tiers
python3 run_test_suites.py all
```

### Using pytest Directly
```bash
# CI tests only (fast development)
pytest -m "ci"

# Efficacy tests only (comprehensive validation)
pytest -m "efficacy"

# Performance tests only (scalability/load)
pytest -m "performance"

# All tests across all tiers
pytest
```

## Test Categories and Markers

### Pytest Markers
- `@pytest.mark.ci`: Fast CI tests for development workflow
- `@pytest.mark.efficacy`: Comprehensive efficacy testing
- `@pytest.mark.performance`: Performance and scalability testing
- `@pytest.mark.integration`: Integration/system tests

### Test Organization
```
tests/
├── ci/                            # Tier 1: Fast CI tests
│   ├── __init__.py
│   └── test_ci_sanity.py
├── efficacy/                      # Tier 2: Comprehensive testing
│   ├── __init__.py
│   └── test_ai_efficacy_comprehensive.py
├── performance/                   # Tier 3: Scalability & load testing
│   ├── __init__.py
│   ├── test_load_handling.py
│   └── test_scalability.py
├── behavioral/                    # Behavioral test suite
├── integration/                   # Integration tests
└── ...                           # Other test categories
```

## CI/CD Integration

### Development Workflow
1. **PR Checks**: Run CI tests only (<30s)
2. **Main Branch**: Run CI + efficacy tests
3. **Release Preparation**: Run all three tiers (CI + efficacy + performance)

### GitHub Actions Example
```yaml
# CI tests on PR
- name: Run CI Tests
  run: pytest -m "ci"

# Efficacy tests on main
- name: Run Efficacy Tests
  run: pytest -m "efficacy"
  if: github.ref == 'refs/heads/main'

# Performance tests before releases
- name: Run Performance Tests
  run: pytest -m "performance"
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

## Performance Benchmarks

### Target Performance Metrics
| Guardrail | Target Response Time | Accuracy Threshold | Scalability Target |
|-----------|-------------------|-------------------|-------------------|
| AI PII Detection | <3.0s | ≥80% | 100 req/sec |
| AI Toxicity | <2.0s | ≥75% | 150 req/sec |
| Prompt Injection | <5.0s | ≥80% | 50 req/sec |
| Content Moderation | <2.0s | ≥85% | 200 req/sec |

### Current Performance (from efficacy tests)
- **AI PII**: ~2.1s average, 85.7% accuracy ✅
- **AI Toxicity**: ~1.8s average, 78.6% accuracy ✅
- **Prompt Injection**: ~1.3s average, 56.25% accuracy ⚠️ (needs improvement)

### Scalability Targets (Tier 3 Performance Tests)
- **Concurrent Requests**: Handle 50+ concurrent users
- **Memory Usage**: <500MB under normal load
- **Response Time P95**: <5s under load
- **Throughput**: 100+ requests per second

## Quality Gates

### CI Test Requirements (Tier 1)
- All AI guardrails must initialize successfully
- Obvious violations must be detected with high confidence
- Benign content should generally be allowed
- Response times under 5 seconds
- Test suite completes in <30 seconds

### Efficacy Test Requirements (Tier 2)
- **Accuracy**: ≥75% for most guardrails, ≥80% for critical ones
- **False Positives**: ≤20% for most guardrails, ≤15% for critical ones
- **False Negatives**: ≤15% for most guardrails, ≤10% for critical ones
- **Performance**: Within target response times
- **Comprehensive Coverage**: Edge cases and sophisticated attacks

### Performance Test Requirements (Tier 3)
- **Scalability**: Handle target concurrent load without degradation
- **Memory Usage**: Stay within memory limits under load
- **Response Time**: P95 latency within acceptable thresholds
- **Throughput**: Meet minimum requests per second targets
- **Stability**: No crashes or resource leaks under stress

## Continuous Improvement

### Metrics Tracking
- Track accuracy trends over time across all tiers
- Monitor false positive/negative rates (Tier 2)
- Performance regression detection (Tier 3)
- Scalability metrics and load handling (Tier 3)
- New attack vector identification (Tier 2)

### Test Case Evolution
- Add new test cases based on real-world attacks (Tier 2)
- Refine thresholds based on production data (Tier 2)
- Expand edge case coverage (Tier 2)
- Update performance benchmarks (Tier 3)
- Enhance load testing scenarios (Tier 3)

## Troubleshooting

### Common Issues
1. **API Key Issues**: Ensure OpenAI API key is set
2. **Rate Limiting**: Tests may fail if API limits are exceeded
3. **Network Issues**: AI guardrails require internet connectivity
4. **Timeout Issues**: Increase timeout for slow tests

### Debugging Tips
- Run individual test files: `pytest tests/ai_sanity_tests.py -v`
- Use `-s` flag to see print statements: `pytest -s tests/efficacy/`
- Check API key configuration: `python3 -c "import os; print('OPENAI_API_KEY' in os.environ)"`

## Future Enhancements

### Planned Improvements
- **Automated Test Case Generation**: Generate test cases from real-world data (Tier 2)
- **Performance Regression Detection**: Automated alerts for performance degradation (Tier 3)
- **Load Testing Automation**: Automated scalability validation (Tier 3)
- **A/B Testing Framework**: Compare different guardrail configurations (Tier 2)
- **Real-time Monitoring**: Integration with production monitoring systems (Tier 3)

### Research Areas
- **Adversarial Testing**: Automated generation of sophisticated attack vectors (Tier 2)
- **Multi-modal Testing**: Testing with images, audio, and other content types (Tier 2)
- **Context-aware Testing**: Testing with conversation history and context (Tier 2)
- **Cross-cultural Testing**: Testing with different languages and cultural contexts (Tier 2)
- **Distributed Load Testing**: Multi-node scalability validation (Tier 3)
- **Memory Profiling**: Advanced memory usage analysis (Tier 3) 