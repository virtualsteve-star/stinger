# Phase 8: Post Alpha 1.0 Release - Testing Improvements

**Status:** 🚧 **PLANNING**  
**Start Date:** TBD (Post Alpha 1.0 Release)  
**Estimated Duration:** 2-3 weeks  
**Priority:** High (Critical for production readiness)

---

## 🎯 **Phase 8 Objective**

**Transform the testing strategy from development-focused to production-ready with clear separation of concerns, performance optimization, and comprehensive efficacy validation.**

Following the successful Alpha 1.0 release, implement the **three-tier testing strategy** and **pragmatic linting approach** to ensure robust, efficient, and comprehensive validation of the Stinger Guardrails Framework:

1. **CI Tests (Fast):** Run on every PR, <30s total
2. **Efficacy Tests (Correctness):** Run on main branch, comprehensive accuracy validation
3. **Performance Tests (Scalability):** Run before releases, load testing and scalability validation
4. **Pragmatic Linting:** Focus on real code quality issues, not style preferences

---

## 📋 **Key Deliverables**

### **8A: Three-Tier Test Suite Implementation (Week 1)**
- **CI Test Suite:** Fast tests for development workflow (<30s)
- **Efficacy Test Suite:** Comprehensive accuracy and correctness validation
- **Performance Test Suite:** Scalability, load testing, and performance benchmarks
- **Test Categorization:** Proper pytest markers for all three tiers

### **8B: Test Suite Reorganization (Week 2)**
- **Test Migration:** Move tests to appropriate tiers based on purpose and duration
- **CI/CD Integration:** Separate execution for each tier with appropriate triggers
- **Performance Optimization:** Ensure CI tests are truly fast, efficacy tests comprehensive
- **Load Testing Framework:** Implement scalable performance testing infrastructure

### **8C: Quality Gates & Monitoring (Week 3)**
- **Tier-Specific Quality Gates:** Different requirements for each test tier
- **Performance Monitoring:** Automated regression detection across all tiers
- **Test Metrics Dashboard:** Comprehensive tracking of all three test suites
- **Documentation:** Updated testing guides reflecting three-tier strategy

### **8D: Testing Documentation & Guides (Week 3)**
- **TESTING_GUIDE.md:** Comprehensive guide for developers
  - When to run each test tier
  - How to add new tests to appropriate tiers
  - Performance budgets and targets
  - Debugging slow tests
  - Test writing best practices
- **Test Architecture Documentation:** Visual diagrams of test structure
- **Performance Baseline Documentation:** Current benchmarks and targets
- **Troubleshooting Guide:** Common test issues and solutions

### **8E: Linting Strategy Implementation (Week 3)**
- **Pragmatic Linting Configuration:** Implement `.flake8` config to ignore style-only issues
- **Real Issue Focus:** Ensure CI catches actual bugs and code smells, not style preferences
- **Developer Workflow Optimization:** Remove pedantic style checks that block development
- **Quality Standards:** Maintain high code quality while being pragmatic about style

### **8F: Test Infrastructure & Tooling (Week 2-3)**
- **Test Fixture Management:**
  - Centralized fixture factory for common test objects
  - Cached fixtures for expensive operations (AI client setup)
  - Fixture teardown verification to prevent test pollution
  
- **Mock Infrastructure:**
  - Centralized mock factory for AI responses
  - Configurable response delays for performance testing
  - Mock failure injection for resilience testing
  
- **Test Data Management:**
  - Versioned test datasets in `tests/data/`
  - Automated test data generation scripts
  - PII-safe test data for public sharing
  
- **Test Reporting & Analytics:**
  - HTML test reports with trend analysis
  - Test coverage visualization by component
  - Flaky test detection and reporting
  - Performance regression alerting

### **8G: Test Automation & Monitoring (Week 3)**
- **Automated Test Scheduling:**
  - Scheduled efficacy tests every 6 hours
  - Weekly performance regression tests
  - Automated failure notifications
  
- **Test Health Dashboard:**
  - Real-time test execution status
  - Historical pass/fail rates by tier
  - Average execution times with trends
  - Flaky test tracking
  
- **Automated Test Maintenance:**
  - Script to identify and mark slow tests
  - Automatic test categorization based on runtime
  - Stale test detection (tests that always pass)

### **8H: Test Migration Execution Plan (Week 1-3)**
- **Week 1: Categorization**
  - Run all tests with timing analysis
  - Auto-categorize based on runtime
  - Manual review for edge cases
  
- **Week 2: Refactoring**
  - Extract common fixtures
  - Implement comprehensive mocking strategy
  - Optimize slow tests for appropriate tier
  
- **Week 3: Validation**
  - Verify all tests still pass
  - Confirm timing targets met
  - Update all documentation

### **8I: Slow Test Optimization (Week 2)**
- **Test Tier Redistribution:**
  - Move ALL AI-based tests to efficacy/performance tiers (they test real behavior)
  - Keep CI tier for non-AI components only (config, pipeline, regex guardrails)
  - Add `@pytest.mark.uses_ai` to clearly identify AI-dependent tests
  - No mocking of AI - that's the core behavior we're testing!
  
- **Test Data Optimization:**
  - Extract large test datasets to external files
  - Implement lazy loading for test data
  - Create minimal datasets for CI tests
  - Add data sampling strategies for large sets
  
- **Parallelization Strategy:**
  - Configure pytest-xdist for parallel execution
  - Group related tests to avoid fixture conflicts
  - Implement test isolation to enable safe parallelization
  - Add `--parallel` flag to test runner scripts

### **8J: Test Performance Monitoring (Week 3)**
- **Automated Performance Tracking:**
  - Add pytest-benchmark for performance regression detection
  - Create performance baselines for each test tier
  - Implement automated alerts for slowdown detection
  - Generate performance trend reports
  
- **Test Execution Analytics:**
  - Track test execution times in CI/CD
  - Generate test duration heat maps
  - Identify consistently slow tests
  - Create monthly performance reports
  
- **Continuous Optimization:**
  - Weekly review of slowest tests
  - Quarterly test suite performance audit
  - Automated suggestions for test optimization
  - Performance budgets for each test tier

---

## 🚨 **Critical Issues to Address**

### **1. Three-Tier Test Categorization**
Based on current test analysis, tests should be organized into three tiers:

#### **CI Tests (Fast - <30s total)**
- **Purpose:** Basic functionality, quick sanity checks
- **Frequency:** Every PR, every development cycle
- **Location:** `tests/ci/` or marked with `@pytest.mark.ci`
- **Examples:** Basic guardrail initialization, simple pattern matching, configuration loading

#### **Efficacy Tests (Correctness - 5-10 minutes)**
- **Purpose:** Comprehensive accuracy validation, edge cases, sophisticated attacks
- **Frequency:** Main branch, before releases
- **Location:** `tests/efficacy/` or marked with `@pytest.mark.efficacy`
- **Examples:** 
  - `test_prompt_injection_accuracy` (23.29s)
  - `test_pii_detection_accuracy` (17.37s)
  - `test_sophisticated_injections` (22.99s)
  - `test_bypass_techniques` (22.46s)

#### **Performance Tests (Scalability - 10-30 minutes)**
- **Purpose:** Load testing, scalability validation, performance benchmarks
- **Frequency:** Before major releases, performance regression detection
- **Location:** `tests/performance/` or marked with `@pytest.mark.performance`
- **Examples:**
  - `test_ai_guardrail_performance_benchmarks` (17.09s)
  - Load testing with concurrent requests
  - Memory usage analysis
  - Response time distribution analysis

### **2. Test Suite Organization**
- **Current Issue:** Mixed test types causing slow development cycles
- **Solution:** Clear separation between CI, efficacy, and performance test tiers
- **Impact:** Development workflow optimization and CI/CD efficiency

### **3. Scalability Testing Gap**
- **Current Issue:** No dedicated scalability and load testing infrastructure
- **Solution:** Implement dedicated performance test suite with load testing capabilities
- **Impact:** Ensure production readiness for high-traffic scenarios

### **4. CI Linting Failures**
- **Current Issue:** CI failures due to pedantic style checks blocking development
- **Solution:** Implement pragmatic linting strategy with per-file ignores and focus on real issues
- **Impact:** Improved developer workflow, reduced CI noise, focus on actual code quality, CI will now pass

### **5. Test Execution Time Issues (GitHub Issue #56)**
- **Current Issue:** Test suite takes 3+ minutes with some tests taking 30+ seconds
- **Solution:** Implement comprehensive mocking, parallel execution, and test tiering
- **Impact:** CI tests complete in <30s, development velocity improved 10x

---

## 🏗️ **Implementation Plan**

### **8.0: Address GitHub Issue #56 - Slow Test Performance**

#### **Immediate Actions (Before Week 1)**
```python
# Top 4 slow tests identified:
# 1. test_encoding_based_bypasses: 32.08s
# 2. test_injection_evasion_techniques: 26.85s  
# 3. test_sophisticated_injections: 24.43s
# 4. test_ai_guardrail_performance_benchmarks: 20.34s

# Quick wins:
# - Move these to efficacy/performance tiers
# - Add @pytest.mark.slow decorators
# - Implement mock responses for CI tier
# - Enable parallel execution
```

#### **Root Cause Solutions**
1. **AI API Calls**: Move AI tests to efficacy tier (no mocking - we need real behavior)
2. **Complex Test Data**: Use minimal datasets for CI
3. **Sequential Execution**: Enable pytest-xdist
4. **No Test Categorization**: Implement 3-tier strategy

### **8A.1: CI Test Suite Implementation**

#### **8A.1.1: Ultra-Fast Smoke Tests**
```python
# tests/ci/test_smoke.py
import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.ci
class TestSmoke:
    """Ultra-fast smoke tests for CI - <5s total"""
    
    def test_imports(self):
        """Verify all modules import successfully"""
        import stinger
        from stinger.core.pipeline import GuardrailPipeline
        from stinger.core.guardrail_interface import GuardrailRegistry
        from stinger.guardrails.simple_pii_detection_guardrail import SimplePIIDetectionGuardrail
        
    def test_basic_pipeline_creation(self):
        """Pipeline can be created with minimal config"""
        config = {"guardrails": {"input": [], "output": []}}
        # No mocking needed - empty pipeline doesn't use AI
        pipeline = GuardrailPipeline.from_dict(config)
        assert pipeline is not None
        
    def test_guardrail_registry(self):
        """All guardrails are registered"""
        from stinger.core.guardrail_interface import GuardrailRegistry
        guardrails = GuardrailRegistry.list_guardrails()
        assert len(guardrails) >= 10
        assert 'simple_pii_detection' in [g['type'] for g in guardrails]

# tests/ci/test_config_validation.py
@pytest.mark.ci
class TestConfigValidation:
    """Fast config validation tests"""
    
    @pytest.mark.parametrize("preset", [
        "customer_service",
        "medical_bot",
        "education"
    ])
    def test_preset_configs_valid(self, preset):
        """All preset configs are valid"""
        from stinger.core.preset_configs import PresetConfigs
        # Just validate config structure, don't initialize AI guardrails
        config = PresetConfigs.get_config(preset)
        assert config is not None
        assert 'guardrails' in config
        assert 'input' in config['guardrails']
        assert 'output' in config['guardrails']
    
    def test_config_schema_validation(self):
        """Config schema validation works"""
        from stinger.core.config import ConfigLoader
        valid_config = {
            "guardrails": {
                "input": [{"type": "simple_pii_detection", "enabled": True}],
                "output": []
            }
        }
        # Should not raise
        ConfigLoader._validate_config(valid_config)

# tests/ci/test_simple_guardrails.py
@pytest.mark.ci 
class TestSimpleGuardrails:
    """Fast tests for non-AI guardrails"""
    
    def test_simple_pii_detection(self):
        """Simple regex-based PII detection (NOT AI)"""
        from stinger.guardrails.simple_pii_detection_guardrail import SimplePIIDetectionGuardrail
        config = {"confidence_threshold": 0.7}
        guardrail = SimplePIIDetectionGuardrail("test", config)
        
        # This uses regex patterns, not AI
        result = asyncio.run(guardrail.analyze("SSN: 123-45-6789"))
        assert result.blocked
        
        result = asyncio.run(guardrail.analyze("Hello world"))
        assert not result.blocked
    
    def test_simple_toxicity(self):
        """Simple pattern-based toxicity (NOT AI)"""
        from stinger.guardrails.simple_toxicity_detection_guardrail import SimpleToxicityDetectionGuardrail
        config = {"confidence_threshold": 0.7}
        guardrail = SimpleToxicityDetectionGuardrail("test", config)
        
        # Uses keyword patterns, not AI
        result = asyncio.run(guardrail.analyze("I hate you"))
        assert result.blocked
```

### **8A.2: Efficacy Suite Implementation**

#### **8A.2.1: Expand Efficacy Test Coverage**
```python
# tests/efficacy/test_ai_efficacy_comprehensive.py
# Add comprehensive test categories:

# Test categorization for AI vs non-AI tests
# NO MOCKING - AI behavior is what we're testing!

class TestAIPIIEfficacy:
    """Comprehensive PII detection accuracy testing"""
    - test_pii_detection_accuracy (existing)
    - test_pii_false_positive_analysis (new)
    - test_pii_edge_cases (new)
    - test_pii_performance_benchmarks (new)

class TestAIToxicityEfficacy:
    """Comprehensive toxicity detection accuracy testing"""
    - test_toxicity_detection_accuracy (new)
    - test_toxicity_category_analysis (new)
    - test_toxicity_cultural_context (new)
    - test_toxicity_performance_benchmarks (new)

class TestPromptInjectionEfficacy:
    """Comprehensive prompt injection detection testing"""
    - test_prompt_injection_accuracy (existing)
    - test_sophisticated_injection_techniques (new)
    - test_conversation_aware_injection (new)
    - test_injection_bypass_techniques (new)

class TestAIPerformanceBenchmarks:
    """Performance benchmarking and regression detection"""
    - test_ai_guardrail_performance_benchmarks (existing)
    - test_concurrent_request_performance (new)
    - test_memory_usage_analysis (new)
    - test_response_time_distribution (new)
```

#### **8A.1.2: Performance Benchmark Implementation**
```python
# tests/efficacy/test_performance_benchmarks.py
class TestPerformanceBenchmarks:
    """Automated performance regression detection"""
    
    def test_ai_guardrail_response_times(self):
        """Test that AI guardrails meet performance targets"""
        targets = {
            'ai_pii_detection': 3.0,
            'ai_toxicity': 2.0,
            'prompt_injection': 5.0,
            'content_moderation': 2.0
        }
        
        for guardrail_type, target_time in targets.items():
            avg_time = self.measure_average_response_time(guardrail_type)
            assert avg_time <= target_time, f"{guardrail_type} exceeds {target_time}s target"
    
    def test_memory_usage_analysis(self):
        """Test memory usage stays within acceptable limits"""
        # Implementation for memory monitoring
    
    def test_concurrent_request_handling(self):
        """Test performance under concurrent load"""
        # Implementation for load testing
```

#### **8A.1.3: Accuracy Measurement Framework**
```python
# tests/efficacy/test_accuracy_measurement.py
class TestAccuracyMeasurement:
    """Comprehensive accuracy measurement and reporting"""
    
    def test_false_positive_analysis(self):
        """Detailed false positive rate analysis"""
        # Implementation for FP analysis
    
    def test_false_negative_analysis(self):
        """Detailed false negative rate analysis"""
        # Implementation for FN analysis
    
    def test_confidence_calibration(self):
        """Test confidence score calibration"""
        # Implementation for confidence analysis
```

### **8A.2: Test Suite Reorganization**

#### **8A.2.1: Test Directory Structure**
```
tests/
├── ci/                      # <30s total
│   ├── test_smoke.py       # Basic functionality
│   ├── test_config_validation.py
│   ├── test_simple_guardrails.py
│   └── test_imports.py
│
├── efficacy/               # 5-10 minutes
│   ├── accuracy/          # Accuracy measurements
│   │   ├── test_pii_accuracy.py
│   │   ├── test_toxicity_accuracy.py
│   │   └── test_injection_accuracy.py
│   ├── edge_cases/        # Edge case testing
│   │   ├── test_unicode_handling.py
│   │   ├── test_large_inputs.py
│   │   └── test_multilingual.py
│   └── attacks/           # Security testing
│       ├── test_bypass_attempts.py
│       ├── test_injection_variants.py
│       └── test_evasion_techniques.py
│
├── performance/            # 10-30 minutes
│   ├── load/              # Load testing
│   │   ├── test_concurrent_users.py
│   │   ├── test_sustained_load.py
│   │   └── test_spike_testing.py
│   ├── memory/            # Memory analysis
│   │   ├── test_memory_leaks.py
│   │   ├── test_large_payloads.py
│   │   └── test_long_running.py
│   └── benchmarks/        # Performance benchmarks
│       ├── test_latency_targets.py
│       ├── test_throughput.py
│       └── test_resource_usage.py
│
├── integration/           # Cross-component tests
├── shared/               # Shared utilities
│   ├── fixtures.py
│   ├── mocks.py
│   └── test_data.py
└── data/                # Test data files
    ├── pii_samples.json
    ├── injection_attacks.txt
    └── performance_payloads/
```

#### **8A.2.2: Move Slow Tests to Appropriate Tiers**
```bash
# Move these files from behavioral/ to efficacy/attacks/:
mv tests/behavioral/test_bypass_attempts.py tests/efficacy/attacks/
mv tests/behavioral/test_injection_behavior.py tests/efficacy/attacks/

# Move performance tests to performance/:
mv tests/behavioral/test_performance_behavior.py tests/performance/benchmarks/

# Update imports and test organization
```

#### **8A.2.2: Implement Proper Test Markers**
```python
# Update test files with proper markers:

# Fast tests (development)
@pytest.mark.fast
def test_basic_functionality():
    """Quick sanity check - should run in <1s"""
    pass

# Efficacy tests (comprehensive)
@pytest.mark.efficacy
def test_comprehensive_accuracy():
    """Comprehensive accuracy testing - may take 15-30s"""
    pass

# Slow tests (performance)
@pytest.mark.slow
def test_performance_benchmarks():
    """Performance testing - may take 30s+"""
    pass
```

#### **8A.2.3: Update pytest.ini Configuration**
```ini
[pytest]
markers =
    ci: marks tests as fast CI tests (<30s total)
    efficacy: marks tests as comprehensive efficacy testing (5-10 minutes)
    performance: marks tests as performance/scalability testing (10-30 minutes)
    integration: marks tests as integration/system tests

# Test execution options:
# - Development: pytest -m "ci" (fast tests only)
# - CI Pipeline: pytest -m "ci" (fast tests only)
# - Efficacy Testing: pytest -m "efficacy" (comprehensive accuracy)
# - Performance Testing: pytest -m "performance" (scalability/load)
# - All Tests: pytest (includes all tiers)
```

### **8A.3: CI/CD Integration**

#### **8A.3.1: GitHub Actions Workflow Updates**
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  ci-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run CI Tests
        run: |
          pip install -r requirements.txt
          pytest -m "ci" --durations=10

  efficacy-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v3
      - name: Run Efficacy Tests
        run: |
          pip install -r requirements.txt
          pytest -m "efficacy" --durations=10
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

  performance-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3
      - name: Run Performance Tests
        run: |
          pip install -r requirements.txt
          pytest -m "performance" --durations=10
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

#### **8A.3.2: Test Runner Script Updates**
```python
# scripts/run_test_suites.py
#!/usr/bin/env python3
"""
Test Suite Runner for Stinger Guardrails

Implements the three-tier testing strategy from TESTING_STRATEGY.md
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

def run_ci_tests():
    """Run Tier 1: Fast CI tests (<30s)"""
    print("🚀 Running CI Tests (Tier 1: Fast Tests)")
    start = time.time()
    result = subprocess.run([
        "pytest", "-m", "ci", "--durations=10", "-v"
    ])
    elapsed = time.time() - start
    print(f"⏱️  CI tests completed in {elapsed:.1f}s")
    return result.returncode == 0

def run_efficacy_tests():
    """Run Tier 2: Comprehensive efficacy tests (5-10 minutes)"""
    print("🧪 Running Efficacy Tests (Tier 2: Correctness Testing)")
    result = subprocess.run([
        "pytest", "-m", "efficacy", "--durations=10", "-v"
    ])
    return result.returncode == 0

def run_performance_tests():
    """Run Tier 3: Performance and scalability tests (10-30 minutes)"""
    print("📊 Running Performance Tests (Tier 3: Scalability Testing)")
    result = subprocess.run([
        "pytest", "-m", "performance", "--durations=10", "-v"
    ])
    return result.returncode == 0

def run_failed_only():
    """Run only previously failed tests"""
    print("🔄 Running Previously Failed Tests")
    result = subprocess.run([
        "pytest", "--lf", "-v"
    ])
    return result.returncode == 0

def run_changed_only():
    """Run tests for changed files only"""
    print("📝 Running Tests for Changed Files")
    # Get changed files
    git_diff = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True, text=True
    )
    changed_files = git_diff.stdout.strip().split('\n')
    
    # Find related test files
    test_files = []
    for file in changed_files:
        if file.startswith('src/'):
            test_file = file.replace('src/', 'tests/').replace('.py', '_test.py')
            if Path(test_file).exists():
                test_files.append(test_file)
    
    if test_files:
        result = subprocess.run(["pytest"] + test_files + ["-v"])
        return result.returncode == 0
    else:
        print("No test files found for changed files")
        return True

def run_all_tests():
    """Run all tests across all tiers"""
    print("🎯 Running All Tests (All Tiers)")
    result = subprocess.run([
        "pytest", "--durations=10", "-v"
    ])
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Stinger Test Suite Runner")
    parser.add_argument("suite", choices=["ci", "efficacy", "performance", "all", "failed", "changed"], 
                       help="Test suite to run")
    parser.add_argument("--profile", action="store_true", help="Profile test execution")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    
    args = parser.parse_args()
    
    # Add coverage if requested
    if args.coverage:
        subprocess.run(["coverage", "erase"])
    
    if args.suite == "ci":
        success = run_ci_tests()
    elif args.suite == "efficacy":
        success = run_efficacy_tests()
    elif args.suite == "performance":
        success = run_performance_tests()
    elif args.suite == "all":
        success = run_all_tests()
    elif args.suite == "failed":
        success = run_failed_only()
    elif args.suite == "changed":
        success = run_changed_only()
    
    if args.coverage:
        subprocess.run(["coverage", "report", "-m"])
        subprocess.run(["coverage", "html"])
        print("📊 Coverage report generated in htmlcov/")
    
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

#### **8A.3.3: Developer Test Helper Script**
```bash
# scripts/test-helper.sh
#!/bin/bash
# Interactive test helper for developers

echo "🧪 Stinger Test Helper"
echo "===================="
echo ""
echo "Quick Actions:"
echo "1. Run CI tests (<30s)"
echo "2. Run specific guardrail tests"
echo "3. Profile slow test"
echo "4. Generate test report"
echo "5. Check test coverage"
echo "6. Run failed tests only"
echo "7. Run tests for changed files"
echo "8. Debug flaky test"
echo ""
echo -n "Select action (1-8): "
read action

case $action in
    1)
        echo "Running CI tests..."
        python3 scripts/run_test_suites.py ci
        ;;
    2)
        echo -n "Enter guardrail name (e.g., pii, toxicity): "
        read guardrail
        pytest -k $guardrail -v
        ;;
    3)
        echo -n "Enter test name to profile: "
        read test_name
        pytest -v -s --durations=10 -k "$test_name" --profile
        ;;
    4)
        pytest --html=report.html --self-contained-html
        echo "Report generated: report.html"
        ;;
    5)
        pytest --cov=src/stinger --cov-report=html
        echo "Coverage report: htmlcov/index.html"
        ;;
    6)
        python3 scripts/run_test_suites.py failed
        ;;
    7)
        python3 scripts/run_test_suites.py changed
        ;;
    8)
        echo -n "Enter flaky test name: "
        read test_name
        pytest -v -x --flaky-test-reporter -k "$test_name"
        ;;
    *)
        echo "Invalid selection"
        exit 1
        ;;
esac
```

### **8K: Developer Test Helper Scripts**

#### **8K.1: Quick Test Runners**
```bash
# scripts/test-fast.sh - Run only CI tests (<30s)
#!/bin/bash
echo "Running fast CI tests..."
pytest -m "ci" -n auto --durations=10

# scripts/test-efficacy.sh - Run accuracy tests
#!/bin/bash
echo "Running efficacy tests (may take 5-10 minutes)..."
pytest -m "efficacy" --durations=20

# scripts/test-all.sh - Run complete test suite
#!/bin/bash
echo "Running all tests (may take 30+ minutes)..."
pytest --durations=50
```

#### **8K.2: Test Time Analysis Tool**
```python
# scripts/analyze_test_times.py
"""Analyze and report on test execution times"""
import json
import subprocess
from pathlib import Path

def analyze_pytest_durations():
    """Parse pytest durations and generate report"""
    result = subprocess.run(
        ["pytest", "--durations=0", "--json-report"],
        capture_output=True
    )
    
    # Load test results
    with open(".report.json") as f:
        report = json.load(f)
    
    # Analyze slow tests
    slow_tests = []
    for test in report["tests"]:
        if test["duration"] > 1.0:  # Tests longer than 1s
            slow_tests.append({
                "name": test["nodeid"],
                "duration": test["duration"],
                "outcome": test["outcome"]
            })
    
    # Generate recommendations
    print("\n=== Slow Test Analysis ===")
    print(f"Found {len(slow_tests)} slow tests (>1s)\n")
    
    for test in sorted(slow_tests, key=lambda x: x["duration"], reverse=True)[:10]:
        print(f"{test['duration']:.2f}s - {test['name']}")
        
        # Suggest tier assignment
        if test['duration'] > 10:
            print("  → Move to performance tier")
        elif test['duration'] > 2:
            print("  → Move to efficacy tier")
        else:
            print("  → Optimize or mock external calls")

if __name__ == "__main__":
    analyze_pytest_durations()
```

#### **8K.3: Test Categorization Helper**
```python
# scripts/categorize_tests.py
"""Help categorize tests into appropriate tiers"""
import ast
import subprocess
from pathlib import Path

def uses_ai_calls(test_file):
    """Check if a test file uses AI guardrails"""
    content = Path(test_file).read_text()
    tree = ast.parse(content)
    
    ai_imports = [
        'AIBasedPIIDetectionGuardrail',
        'AIBasedToxicityGuardrail', 
        'PromptInjectionGuardrail',
        'ContentModerationGuardrail'
    ]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if any(ai in alias.name for ai in ai_imports):
                    return True
    return False

def categorize_all_tests():
    """Categorize all tests based on content"""
    test_files = Path("tests").rglob("test_*.py")
    
    categories = {
        "ci": [],      # Fast, non-AI tests
        "efficacy": [], # AI behavior tests
        "performance": [] # Load/scale tests
    }
    
    for test_file in test_files:
        if "performance" in str(test_file) or "benchmark" in str(test_file):
            categories["performance"].append(test_file)
        elif uses_ai_calls(test_file):
            categories["efficacy"].append(test_file)
        else:
            # Measure execution time
            result = subprocess.run(
                ["pytest", str(test_file), "--durations=0", "-q"],
                capture_output=True
            )
            # If fast and no AI, put in CI
            categories["ci"].append(test_file)
    
    # Generate report
    print("=== Test Categorization Report ===")
    for tier, files in categories.items():
        print(f"\n{tier.upper()} Tier ({len(files)} files):")
        for f in sorted(files)[:5]:
            print(f"  - {f}")
        if len(files) > 5:
            print(f"  ... and {len(files)-5} more")

if __name__ == "__main__":
    categorize_all_tests()
```

#### **8K.4: Test Optimization Validator**
```python
# scripts/validate_test_optimization.py
"""Validate that test optimizations are working"""
import time
import subprocess

def measure_test_suite_time(marker):
    """Measure execution time for a test suite"""
    start = time.time()
    result = subprocess.run(
        ["pytest", "-m", marker, "-q"],
        capture_output=True
    )
    elapsed = time.time() - start
    return elapsed, result.returncode

def validate_optimization():
    """Validate test suite meets performance targets"""
    targets = {
        "ci": 30,      # 30 seconds
        "efficacy": 600,  # 10 minutes
        "performance": 1800  # 30 minutes
    }
    
    print("=== Test Suite Performance Validation ===")
    
    for suite, target in targets.items():
        print(f"\nValidating {suite} suite...")
        elapsed, returncode = measure_test_suite_time(suite)
        
        if returncode != 0:
            print(f"  ❌ {suite} tests failed!")
        elif elapsed > target:
            print(f"  ❌ {suite} took {elapsed:.1f}s (target: {target}s)")
        else:
            print(f"  ✅ {suite} passed in {elapsed:.1f}s")

if __name__ == "__main__":
    validate_optimization()
```

### **8A.4: Quality Gates Implementation**

#### **8A.4.1: Three-Tier Quality Gates**
```python
# tests/quality_gates/test_tier_quality_gates.py
class TestTierQualityGates:
    """Quality gates for each test tier"""
    
    def test_ci_test_performance(self):
        """CI tests must complete in <30 seconds"""
        start_time = time.time()
        result = subprocess.run(["pytest", "-m", "ci", "-q"])
        elapsed = time.time() - start_time
        
        assert elapsed < 30, f"CI tests took {elapsed:.1f}s, must be <30s"
        assert result.returncode == 0, "CI tests must pass"
    
    def test_efficacy_test_performance(self):
        """Efficacy tests must complete in <10 minutes"""
        start_time = time.time()
        result = subprocess.run(["pytest", "-m", "efficacy", "-q"])
        elapsed = time.time() - start_time
        
        assert elapsed < 600, f"Efficacy tests took {elapsed:.1f}s, must be <600s"
        assert result.returncode == 0, "Efficacy tests must pass"
    
    def test_performance_test_performance(self):
        """Performance tests must complete in <30 minutes"""
        start_time = time.time()
        result = subprocess.run(["pytest", "-m", "performance", "-q"])
        elapsed = time.time() - start_time
        
        assert elapsed < 1800, f"Performance tests took {elapsed:.1f}s, must be <1800s"
        assert result.returncode == 0, "Performance tests must pass"
    
    def test_accuracy_thresholds(self):
        """Verify accuracy meets production thresholds"""
        # Implementation for accuracy validation
```

#### **8D.1: Testing Documentation Implementation**

##### **8D.1.1: TESTING_GUIDE.md Structure**
```markdown
# Stinger Testing Guide

## Overview
This guide covers the three-tier testing strategy for the Stinger Guardrails Framework.

## Test Tiers

### Tier 1: CI Tests (Fast - <30s)
- **When to run:** Every commit, before pushing
- **Command:** `pytest -m ci`
- **Purpose:** Quick sanity checks, basic functionality
- **Examples:** Configuration loading, simple pattern matching

### Tier 2: Efficacy Tests (Correctness - 5-10min)
- **When to run:** Before merging PRs, on main branch
- **Command:** `pytest -m efficacy`
- **Purpose:** Comprehensive accuracy validation
- **Examples:** AI accuracy tests, sophisticated attack scenarios

### Tier 3: Performance Tests (Scalability - 10-30min)
- **When to run:** Before releases, performance investigations
- **Command:** `pytest -m performance`
- **Purpose:** Load testing, scalability validation
- **Examples:** Concurrent user simulations, memory stability

## Adding New Tests

### 1. Determine the appropriate tier:
- Is it a quick sanity check? → CI tier
- Is it testing accuracy/correctness? → Efficacy tier
- Is it testing performance/scale? → Performance tier

### 2. Add appropriate markers:
```python
@pytest.mark.ci
def test_quick_functionality():
    pass

@pytest.mark.efficacy
def test_accuracy_validation():
    pass

@pytest.mark.performance
def test_load_handling():
    pass
```

### 3. Place in correct directory:
- `tests/ci/` - Fast tests
- `tests/efficacy/` - Accuracy tests
- `tests/performance/` - Performance tests

## Performance Budgets

### CI Tests
- Individual test: <1s
- Total suite: <30s

### Efficacy Tests
- Individual test: <30s
- Total suite: <10 minutes

### Performance Tests
- Individual test: <5 minutes
- Total suite: <30 minutes

## Debugging Slow Tests

1. Run with durations: `pytest --durations=10`
2. Profile specific tests: `pytest -v -s tests/slow_test.py::test_name`
3. Check for:
   - Unnecessary API calls (mock them in CI tests)
   - Large test data sets (use smaller samples for CI)
   - Missing test fixtures (cache expensive setups)

## Best Practices

### CI Tests
- Mock external dependencies
- Use small, focused test data
- Test one thing at a time
- Avoid file I/O when possible

### Efficacy Tests
- Use realistic test data
- Cover edge cases thoroughly
- Test against known attack patterns
- Validate accuracy metrics

### Performance Tests
- Simulate realistic load patterns
- Test resource limits
- Monitor memory usage
- Measure latency percentiles

## Common Issues

### Test Timeouts
- Check for infinite loops
- Verify API mocking is working
- Reduce test data size

### Flaky Tests
- Add retries for network calls
- Use deterministic test data
- Avoid time-dependent assertions

### Import Errors
- Ensure PYTHONPATH includes src/
- Check for circular imports
- Verify all dependencies installed
```

#### **8E.1.1: Pragmatic Linting Configuration**
```ini
# .flake8
[flake8]
max-line-length = 100
extend-ignore = 
    E203,  # Whitespace before ':' (Black compatibility)
    W503,  # Line break before binary operator (Black compatibility)
    E712,  # True/False comparisons (style preference)
    F541,  # f-strings without placeholders (minor)
    E402,  # Import order in tests (needed for sys.path)
    W293,  # Whitespace on blank lines (trivial)
    E501   # Long lines (many valid reasons)

# Focus on real issues:
# F401: Unused imports in src/ (real code smell) - MUST FIX
# F841: Unused variables in src/ (real code smell) - MUST FIX
# E722: Bare except (security risk) - MUST FIX
# F811: Redefinitions (actual bugs) - MUST FIX

# Per-file ignores:
# - Tests can have unused variables (F841)
# - Complex functions marked as legitimately complex (C901)
```

#### **8A.4.2: Accuracy Quality Gates**
```python
# Quality gate requirements based on TESTING_STRATEGY.md:

ACCURACY_THRESHOLDS = {
    'ai_pii_detection': {
        'accuracy': 0.80,
        'false_positives': 0.15,
        'false_negatives': 0.10,
        'response_time': 3.0
    },
    'ai_toxicity': {
        'accuracy': 0.75,
        'false_positives': 0.20,
        'false_negatives': 0.15,
        'response_time': 2.0
    },
    'prompt_injection': {
        'accuracy': 0.80,
        'false_positives': 0.15,
        'false_negatives': 0.10,
        'response_time': 5.0
    }
}
```

#### **8A.4.3: Test Quality KPIs**
```python
# tests/quality_gates/test_quality_metrics.py
class TestQualityMetrics:
    """Monitor and enforce test quality KPIs"""
    
    def test_coverage_targets(self):
        """Verify test coverage meets targets"""
        import coverage
        cov = coverage.Coverage()
        cov.load()
        
        # Check core module coverage
        core_coverage = cov.report(include="src/stinger/core/*", show_missing=False)
        assert core_coverage >= 90, f"Core coverage {core_coverage}% < 90%"
        
        # Check guardrail coverage
        guardrail_coverage = cov.report(include="src/stinger/guardrails/*", show_missing=False)
        assert guardrail_coverage >= 85, f"Guardrail coverage {guardrail_coverage}% < 85%"
    
    def test_performance_targets(self):
        """Verify test performance meets targets"""
        # CI suite target
        ci_time = self._measure_suite_time("ci")
        assert ci_time < 30, f"CI suite took {ci_time}s, must be <30s"
        
        # Individual test targets
        slow_tests = self._find_slow_tests("ci", max_time=1.0)
        assert len(slow_tests) == 0, f"Found {len(slow_tests)} slow CI tests"
    
    def test_reliability_metrics(self):
        """Track test reliability metrics"""
        # Flaky test detection
        flaky_rate = self._calculate_flaky_rate()
        assert flaky_rate < 0.02, f"Flaky test rate {flaky_rate:.1%} > 2%"
        
        # False positive rate
        false_positive_rate = self._calculate_false_positive_rate()
        assert false_positive_rate < 0.05, f"False positive rate {false_positive_rate:.1%} > 5%"
```

### **8A.5: Automated Test Scheduling**
```yaml
# .github/workflows/scheduled-tests.yml
name: Scheduled Test Suites

on:
  schedule:
    # Efficacy tests every 6 hours
    - cron: '0 */6 * * *'
    # Performance tests weekly on Sunday
    - cron: '0 0 * * 0'
  workflow_dispatch:  # Allow manual trigger

jobs:
  efficacy-tests:
    if: github.event.schedule == '0 */6 * * *' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-html
      - name: Run Efficacy Tests
        run: |
          pytest -m efficacy --html=efficacy-report.html --self-contained-html
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: efficacy-report
          path: efficacy-report.html
      - name: Notify on Failure
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Scheduled Efficacy Tests Failed',
              body: 'The scheduled efficacy test suite failed. Check the [workflow run](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}).'
            })

  performance-tests:
    if: github.event.schedule == '0 0 * * 0' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-benchmark
      - name: Run Performance Tests
        run: |
          pytest -m performance --benchmark-json=benchmark.json
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      - name: Store Benchmark Result
        uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: 'pytest'
          output-file-path: benchmark.json
          github-token: ${{ secrets.GITHUB_TOKEN }}
          auto-push: true
```

### **8A.6: Pre-commit Test Hooks**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: fast-tests
        name: Run Fast CI Tests
        entry: pytest -m ci -x --tb=short -q
        language: system
        pass_filenames: false
        stages: [commit]
        
      - id: test-quality
        name: Check Test Quality
        entry: python scripts/check_test_quality.py
        language: system
        files: ^tests/.*\.py$
        
      - id: no-slow-tests-in-ci
        name: Prevent Slow Tests in CI
        entry: python scripts/validate_test_markers.py
        language: system
        files: ^tests/ci/.*\.py$
```

---

## 📊 **Success Criteria**

### **8A: Three-Tier Test Suite Implementation**
- [ ] CI test suite implemented with <30s execution time
- [ ] Efficacy test suite with comprehensive accuracy validation
- [ ] Performance test suite with scalability and load testing
- [ ] Proper pytest markers implemented across all test files

### **8B: Test Suite Reorganization**
- [ ] Tests categorized into appropriate tiers based on purpose and duration
- [ ] CI/CD workflows updated with separate execution for each tier
- [ ] Load testing framework implemented for performance tier
- [ ] Test migration completed with proper organization

### **8C: Quality Gates & Monitoring**
- [ ] Tier-specific quality gates implemented and passing
- [ ] Performance regression detection across all tiers
- [ ] Scalability monitoring and alerting configured
- [ ] Comprehensive test metrics dashboard implemented

### **8D: Testing Documentation & Guides**
- [ ] TESTING_GUIDE.md created with comprehensive developer guidance
- [ ] Test architecture documentation with visual diagrams
- [ ] Performance baseline documentation established
- [ ] Troubleshooting guide for common test issues
- [ ] Best practices documented for each test tier

### **8E: Linting Strategy Implementation**
- [ ] `.flake8` configuration implemented with pragmatic rules
- [ ] Style-only issues ignored (E203, W503, E712, F541, E402, W293, E501)
- [ ] Real code quality issues enforced (F401, F841 in src/, E722, F811)
- [ ] Per-file ignores configured for tests and complex functions
- [ ] CI pipeline updated to focus on actual bugs vs style preferences

### **8F: Test Infrastructure & Tooling**
- [ ] Centralized test fixture management implemented
- [ ] Mock infrastructure for AI responses created
- [ ] Test data management system established
- [ ] HTML test reports with trend analysis configured
- [ ] Flaky test detection and reporting implemented

### **8G: Test Automation & Monitoring**
- [ ] Automated test scheduling configured (6-hour efficacy, weekly performance)
- [ ] Test health dashboard implemented
- [ ] Automated test categorization scripts created
- [ ] GitHub Actions workflows for scheduled tests deployed
- [ ] Failure notifications configured

### **8H: Test Migration Execution**
- [ ] All tests categorized by runtime and purpose
- [ ] Common fixtures extracted and optimized
- [ ] Slow tests moved to appropriate tiers
- [ ] All tests passing in new structure
- [ ] Documentation updated to reflect new organization

### **8I: Slow Test Optimization**
- [ ] AI tests moved to efficacy/performance tiers
- [ ] CI tests limited to non-AI components
- [ ] Parallel execution configured
- [ ] CI tests complete in <30s

### **8J: Test Performance Monitoring**
- [ ] Performance tracking implemented
- [ ] Test analytics dashboard created
- [ ] Continuous optimization process established
- [ ] Performance budgets enforced

---

## 🚀 **Usage Examples**

### **Development Workflow**
```bash
# Quick development testing (<30s)
python3 scripts/run_test_suites.py ci

# Comprehensive correctness testing (5-10 minutes)
python3 scripts/run_test_suites.py efficacy

# Performance and scalability testing (10-30 minutes)
python3 scripts/run_test_suites.py performance

# All tests across all tiers
python3 scripts/run_test_suites.py all
```

### **CI/CD Integration**
```bash
# CI tests on every PR
pytest -m "ci" --durations=10

# Efficacy tests on main branch
pytest -m "efficacy" --durations=10

# Performance tests before releases
pytest -m "performance" --durations=10
```

---

## 📚 **References**

- **Testing Strategy:** `docs/TESTING_STRATEGY.md`
- **Current Test Analysis:** Based on `pytest --durations=10` output
- **Quality Requirements:** Performance and accuracy thresholds from testing strategy
- **CI/CD Best Practices:** GitHub Actions workflow optimization

---

## 🔄 **Future Enhancements**

### **Phase 8.1: Advanced Testing Features**
- **Automated Test Case Generation:** Generate test cases from real-world data
- **A/B Testing Framework:** Compare different guardrail configurations
- **Real-time Monitoring:** Integration with production monitoring systems
- **Cross-cultural Testing:** Testing with different languages and cultural contexts

### **Phase 8.2: Performance Optimization**
- **Test Parallelization:** Parallel execution of independent tests
- **Test Caching:** Cache test results for faster re-runs
- **Incremental Testing:** Only run tests affected by changes
- **Performance Profiling:** Detailed performance analysis tools

### **8K: Developer Test Helper Scripts**
- [ ] Quick test runner scripts created
- [ ] Test time analysis tool implemented
- [ ] Mock data generator available
- [ ] Developer documentation updated

### **Test Tier Philosophy**

**Key Principle: NO MOCKING OF AI BEHAVIOR**

The core value of Stinger is testing real AI guardrail behavior. Mocking AI responses defeats the entire purpose. Instead:

1. **CI Tier**: Test everything EXCEPT AI behavior
   - Configuration, pipeline construction, simple regex patterns
   - These are genuinely fast because they don't call AI
   - May run in GitHub Actions without API keys

2. **Efficacy Tier**: Test ALL AI behavior here
   - Accept that these tests take 20-30s each
   - This is where we validate that guardrails actually work
   - No mocks - we need real AI responses
   - MUST run locally before any push to main

3. **Performance Tier**: Test scale and load
   - How does the system perform under load?
   - What are the latency distributions?
   - Memory usage patterns
   - MUST run locally before any push to main

**Release Rule**: This is an AI product! No code goes to main without passing ALL tests locally with real API keys. GitHub CI may skip AI tests for security, but developers MUST run them locally.

### **Phase 8.3: Advanced Test Types**
- **Security Regression Tests:** Dedicated security-focused test suite
  - Penetration testing scenarios
  - Security vulnerability scanning
  - Attack pattern validation
  - Security regression detection
- **Integration Tests:** Cross-guardrail interaction testing
  - Pipeline integration scenarios
  - Multi-guardrail coordination
  - Edge case handling across components
  - End-to-end workflow validation
- **Chaos Engineering Tests:** Resilience under failure conditions
  - Random failure injection
  - Network partition simulation
  - Resource exhaustion scenarios
  - Recovery and self-healing validation
- **Compliance Tests:** Regulatory and standards compliance
  - GDPR compliance validation
  - Industry-specific requirements
  - Data retention policy tests
  - Audit trail completeness

---

**Last Updated:** 2025-01-02  
**Next Review:** TBD (Post Alpha 1.0 Release) 