# Testing Strategy for Stinger Guardrails

## Overview

Stinger Guardrails uses a **two-tier testing strategy** to balance development speed with comprehensive validation of AI guardrail effectiveness.

## Two-Tier Strategy

### Tier 1: Quick Sanity Tests (Regular Suite)
**Purpose**: Verify AI guardrails are working and responding correctly  
**Performance**: <30 seconds total for all AI sanity checks  
**Frequency**: Run on every PR, every development cycle  
**Location**: `tests/ai_sanity_tests.py`

#### What Tier 1 Tests Cover:
- ✅ Basic functionality verification
- ✅ Obvious detection cases (SSN, hate speech, etc.)
- ✅ Guardrail availability and initialization
- ✅ Configuration validation
- ✅ Response to benign content

#### Example Tier 1 Test:
```python
@pytest.mark.asyncio
async def test_ai_pii_sanity(self):
    """Verify AI PII detection responds to obvious PII"""
    result = await guardrail.analyze("My SSN is 123-45-6789")
    assert result.blocked is True, "AI PII should block obvious SSN"
    assert result.confidence > 0.5, "AI PII should have high confidence"
```

### Tier 2: Comprehensive Efficacy Suite
**Purpose**: Measure detection accuracy, false positive rates, and edge cases  
**Performance**: 5-10 minutes for thorough validation  
**Frequency**: Run in CI on main branch, before releases  
**Location**: `tests/efficacy/test_ai_efficacy_comprehensive.py`

#### What Tier 2 Tests Cover:
- 📊 **Accuracy Measurement**: Comprehensive test cases with expected outcomes
- 📈 **Performance Benchmarks**: Timing analysis and performance thresholds
- 🔍 **Edge Case Testing**: Unusual inputs, boundary conditions
- 📋 **False Positive/Negative Analysis**: Detailed error rate reporting
- 🎯 **Sophisticated Attack Detection**: Advanced prompt injection techniques

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

## Test Execution

### Using the Test Runner Script
```bash
# Quick sanity tests (development)
python3 run_test_suites.py sanity

# Comprehensive efficacy tests (CI/release)
python3 run_test_suites.py efficacy

# Fast tests only (excludes slow and efficacy)
python3 run_test_suites.py fast

# All tests including efficacy
python3 run_test_suites.py all
```

### Using pytest Directly
```bash
# Regular development (excludes slow and efficacy tests)
pytest -m "not slow and not efficacy"

# Fast tests only
pytest -m "not slow"

# Efficacy tests only
pytest -m "efficacy"

# All tests
pytest
```

## Test Categories and Markers

### Pytest Markers
- `@pytest.mark.efficacy`: Comprehensive efficacy testing
- `@pytest.mark.slow`: Tests that take significant time
- `@pytest.mark.integration`: Integration/system tests

### Test Organization
```
tests/
├── ai_sanity_tests.py              # Tier 1: Quick sanity checks
├── efficacy/                       # Tier 2: Comprehensive testing
│   ├── __init__.py
│   └── test_ai_efficacy_comprehensive.py
├── behavioral/                     # Behavioral test suite
├── integration/                    # Integration tests
└── ...                            # Other test categories
```

## CI/CD Integration

### Development Workflow
1. **PR Checks**: Run sanity tests + fast tests
2. **Main Branch**: Run all tests including efficacy
3. **Release Preparation**: Full efficacy test suite

### GitHub Actions Example
```yaml
# Fast tests on PR
- name: Run Fast Tests
  run: pytest -m "not slow and not efficacy"

# Efficacy tests on main
- name: Run Efficacy Tests
  run: pytest -m "efficacy"
  if: github.ref == 'refs/heads/main'
```

## Performance Benchmarks

### Target Performance Metrics
| Guardrail | Target Response Time | Accuracy Threshold |
|-----------|-------------------|-------------------|
| AI PII Detection | <3.0s | ≥80% |
| AI Toxicity | <2.0s | ≥75% |
| Prompt Injection | <5.0s | ≥80% |
| Content Moderation | <2.0s | ≥85% |

### Current Performance (from efficacy tests)
- **AI PII**: ~2.1s average, 85.7% accuracy ✅
- **AI Toxicity**: ~1.8s average, 78.6% accuracy ✅
- **Prompt Injection**: ~1.3s average, 56.25% accuracy ⚠️ (needs improvement)

## Quality Gates

### Sanity Test Requirements
- All AI guardrails must initialize successfully
- Obvious violations must be detected with high confidence
- Benign content should generally be allowed
- Response times under 5 seconds

### Efficacy Test Requirements
- **Accuracy**: ≥75% for most guardrails, ≥80% for critical ones
- **False Positives**: ≤20% for most guardrails, ≤15% for critical ones
- **False Negatives**: ≤15% for most guardrails, ≤10% for critical ones
- **Performance**: Within target response times

## Continuous Improvement

### Metrics Tracking
- Track accuracy trends over time
- Monitor false positive/negative rates
- Performance regression detection
- New attack vector identification

### Test Case Evolution
- Add new test cases based on real-world attacks
- Refine thresholds based on production data
- Expand edge case coverage
- Update performance benchmarks

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
- **Automated Test Case Generation**: Generate test cases from real-world data
- **Performance Regression Detection**: Automated alerts for performance degradation
- **A/B Testing Framework**: Compare different guardrail configurations
- **Real-time Monitoring**: Integration with production monitoring systems

### Research Areas
- **Adversarial Testing**: Automated generation of sophisticated attack vectors
- **Multi-modal Testing**: Testing with images, audio, and other content types
- **Context-aware Testing**: Testing with conversation history and context
- **Cross-cultural Testing**: Testing with different languages and cultural contexts 