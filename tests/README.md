# Stinger Test Suite

This directory contains comprehensive tests for the Stinger guardrail system, organized by purpose and testing tier.

## 📁 Test Directory Structure (Phase 9A Reorganization)

```
tests/
├── behavioral/          # Behavioral tests for guardrails
├── ci/                 # Fast CI tests (<30s) - @pytest.mark.ci
├── efficacy/           # AI behavior tests (5-10min) - @pytest.mark.efficacy  
├── human/              # Human verification tests for manual QA
├── integration/        # Integration and system tests
├── performance/        # Performance tests - @pytest.mark.performance
├── validation/         # Input validation and error handling
├── configs/            # Test configuration files
├── scenarios/          # End-to-end scenario tests
├── test_corpus/        # Test data files
└── test_*.py           # Unit tests for individual guardrails (in root)
```

## 🚀 Quick Start

### Run Tests by Tier

```bash
# Fast CI tests (<30s)
pytest -m "ci"

# Efficacy tests with real AI (requires OPENAI_API_KEY)
pytest -m "efficacy"

# Performance tests
pytest -m "performance"

# All tests (required before pushing to main!)
pytest

# Human verification tests
cd tests/human && python human_verification_test.py
```

### Run Tests by Category

```bash
# Unit tests (in root)
pytest tests/test_*_guardrail.py

# Integration tests
pytest tests/integration/

# Behavioral tests
pytest tests/behavioral/

# Validation tests
pytest tests/validation/
```

## 🎯 Test Organization Philosophy

### Three-Tier Testing Strategy

1. **CI Tests** (`ci/`) - Fast feedback for development
   - Marked with `@pytest.mark.ci`
   - Run on every commit
   - <30 seconds total runtime
   - No external dependencies

2. **Efficacy Tests** (`efficacy/`) - AI behavior validation  
   - Marked with `@pytest.mark.efficacy`
   - Require OPENAI_API_KEY
   - Test real AI responses (no mocking!)
   - 5-10 minutes runtime

3. **Performance Tests** (`performance/`) - Scalability validation
   - Marked with `@pytest.mark.performance`
   - Test throughput and latency
   - 10-30 minutes runtime

### Test Categories

- **Unit Tests** (root directory) - Individual guardrail functionality
- **Integration Tests** (`integration/`) - Multi-component interactions
- **Behavioral Tests** (`behavioral/`) - Real-world usage patterns
- **Validation Tests** (`validation/`) - Input/error handling
- **Human Tests** (`human/`) - Manual verification with reports

## 📊 Human Verification Testing (Phase 9B)

### Overview
Comprehensive human-in-the-loop testing that provides visual reports for manual QA.

### Location
- Script: `tests/human/human_verification_test.py`
- Config: `tests/human/config.yaml`
- Results: `tests/human/results/`

### Features
- Tests all 9 guardrail types
- Compares AI vs local implementations
- Shows configuration transparency
- Provides performance metrics
- Generates pretty-printed reports

### Usage
```bash
cd tests/human

# Run with default config
python human_verification_test.py

# Custom configuration
python human_verification_test.py --config custom.yaml

# Export reports
python human_verification_test.py --output report.txt --json report.json
```

### Sample Output
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                           HUMAN VERIFICATION REPORT                          ║
║                              Phase 9 Testing                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 SUMMARY
═══════════════════════════════════════════════════════════════════════════════════
Total Tests: 24 (9 guardrails × 2 tests each, including AI and local versions)
✅ Matched Expectations: 22
❌ Failed Expectations: 2
Success Rate: 91.7%
```

## 🧪 Integration Test Scenarios

### Customer Service Bot (`scenarios/customer_service/`)
- Tests toxic language detection
- 38 messages across 6 conversations
- ~21% expected block rate

### Medical Bot (`scenarios/medical_bot/`)
- Tests PII detection in healthcare
- 48 messages across 8 conversations
- ~17% expected warn rate

### Running Test Suites
```bash
# Fast CI tests
pytest -m "ci" -v

# AI behavior tests (requires OPENAI_API_KEY)
pytest -m "efficacy" -v

# Performance tests
pytest -m "performance" -v

# All tests
python run_test_suites.py all
```

## 📝 Adding New Tests

### 1. Determine Test Category
- Fast, no AI → `ci/`
- Uses AI → `efficacy/`
- Tests performance → `performance/`
- Tests integration → `integration/`
- Unit test → root directory

### 2. Add Appropriate Markers
```python
import pytest

@pytest.mark.ci  # For CI tests
def test_fast_operation():
    pass

@pytest.mark.efficacy  # For AI tests
def test_ai_behavior():
    pass
```

### 3. Follow Naming Conventions
- Unit tests: `test_<guardrail_name>_guardrail.py`
- Integration: `test_<feature>_integration.py`
- Validation: `test_<aspect>_validation.py`

## 🔧 Test Configuration

### pytest.ini Markers
- `ci` - Fast CI tests
- `efficacy` - AI behavior tests
- `performance` - Performance tests
- `integration` - Integration tests
- `uses_ai` - Tests requiring OpenAI API key

### Environment Variables
- `OPENAI_API_KEY` - Required for efficacy tests
- `STINGER_ENV` - Set to "test" during testing

## 📈 Test Coverage

### Current Status
- **Total Tests**: 500+ across all categories
- **CI Tests**: ~51 tests, <45 seconds
- **Efficacy Tests**: ~50 tests, 5-10 minutes
- **Unit Tests**: 10 guardrail implementations
- **Human Verification**: 24 test cases

### Coverage Goals
- Unit test coverage: >90%
- Integration coverage: All major workflows
- Behavioral coverage: Real-world scenarios
- Human verification: All guardrails

## 🚨 Important Notes

### No Mocking of AI Behavior
**Core Testing Philosophy**: We test real AI responses, not mocks!
- Stinger is an AI product - we must test actual AI behavior
- Mocking AI responses defeats the entire purpose
- Use local development with OPENAI_API_KEY set
- CI may skip AI tests, but local must run them all

### Test Organization Rules
1. Tests must be in appropriate directories based on markers
2. Unit tests remain in root for easy access
3. All directories must have `__init__.py`
4. Update imports if moving test files

### Pre-Push Checklist
1. Run ALL tests locally: `pytest`
2. Ensure OPENAI_API_KEY is set
3. Run human verification tests
4. Check CI markers are appropriate

## 📚 Related Documentation

- [Testing Strategy](../docs/TESTING_STRATEGY.md)
- [Phase 8 Plan](../docs/plans/Phase8_Post_Alpha_Testing_Improvements.md)
- [Phase 9 Plan](../docs/plans/Phase9_Human_in_the_Loop_Testing_Plan.md)
- [CI/CD Workflow](../.github/workflows/ci.yml)

---

**Last Updated**: January 2025
**Test Organization**: Phase 9A Complete
**Maintainer**: Stinger Team