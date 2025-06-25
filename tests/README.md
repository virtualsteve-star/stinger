# Test Suite Documentation

## 🎯 Overview

This directory contains comprehensive test suites for the LLM Guardrails Framework, organized by scenario to provide clear, maintainable, and realistic validation of the moderation system.

## 📁 Directory Structure

```
tests/
├── scenarios/                    # Integration test scenarios
│   ├── shared/                   # Shared test infrastructure
│   │   └── base_runner.py        # Base conversation simulator
│   ├── customer_service/         # Customer service bot tests
│   │   ├── README.md            # Scenario documentation
│   │   ├── test_data.jsonl      # Test conversations
│   │   ├── config.yaml          # Moderation rules
│   │   └── test_runner.py       # Test execution script
│   ├── medical_bot/             # Medical bot tests
│   │   ├── README.md            # Scenario documentation
│   │   ├── test_data.jsonl      # Test conversations
│   │   ├── config.yaml          # PII detection rules
│   │   └── test_runner.py       # Test execution script
│   └── run_all_tests.py         # Master test runner
├── test_corpus/                 # Legacy test data
│   ├── smoke_test.jsonl         # Basic functionality tests
│   ├── regex_test.jsonl         # Pattern matching tests
│   └── url_test.jsonl           # URL filtering tests
├── test_simple.py               # Basic unit tests
├── test_runner.py               # Legacy smoke test runner
├── test_phase2.py               # Comprehensive Phase 2 tests
├── test_integration.py          # Legacy integration tests
└── README.md                    # This documentation
```

## 🚀 Quick Start

### Run All Integration Tests
```bash
cd tests/scenarios
python3 run_all_tests.py
```

### Run Specific Scenario
```bash
cd tests/scenarios/customer_service
python3 test_runner.py
```

### List Available Scenarios
```bash
cd tests/scenarios
python3 run_all_tests.py --list
```

## 📋 Test Strategy

### **Dual Testing Approach**

The framework uses two complementary testing approaches:

#### 1. **Legacy Tests** (Technical Validation)
- **Purpose**: Validate individual filter functionality and edge cases
- **Location**: `tests/test_corpus/` + `tests/test_*.py`
- **Style**: Unit-style tests with isolated test cases
- **Coverage**: Technical validation of filter behavior

#### 2. **Integration Tests** (Real-World Validation)
- **Purpose**: Validate complete workflows in realistic scenarios
- **Location**: `tests/scenarios/`
- **Style**: Conversation-based tests with realistic flows
- **Coverage**: End-to-end validation of real-world use cases

### **Test Organization Benefits**

#### **Self-Contained Scenarios**
Each test scenario is completely self-contained with:
- **Test Data**: Realistic conversation examples
- **Configuration**: Scenario-specific moderation rules
- **Documentation**: Clear explanation of what's being tested
- **Runner**: Dedicated test execution script

#### **Shared Infrastructure**
- **Base Runner**: Common conversation simulation logic
- **Reusable Components**: Filter registry and utilities
- **Consistent Interface**: Standardized test execution

#### **Clear Documentation**
- **README per Scenario**: Explains purpose, data, and expected results
- **Configuration Comments**: Documents moderation rules
- **Usage Examples**: Shows how to run and modify tests

## 📊 Test Scenarios

### 🤖 Customer Service Bot
- **Purpose**: Validate toxic language detection in support conversations
- **Focus**: Blocking rude, abusive, or profane customer messages
- **Data**: 6 conversations, 38 messages total
- **Expected**: ~21% block rate for toxic content

### 🏥 Medical Bot
- **Purpose**: Validate PII detection in healthcare conversations
- **Focus**: Flagging personal information for review
- **Data**: 8 conversations, 48 messages total
- **Expected**: ~17% warn rate for PII content

## 🧪 Legacy Test Suites

### **Smoke Tests** (`test_runner.py`)
- **Purpose**: Basic functionality validation
- **Data**: `test_corpus/smoke_test.jsonl` (12 tests)
- **Coverage**: Core framework, basic filters, edge cases
- **Usage**: `python3 tests/test_runner.py`

### **Phase 2 Tests** (`test_phase2.py`)
- **Purpose**: Comprehensive rule-based filtering validation
- **Data**: Multiple test corpora (58 total tests)
- **Coverage**: Regex patterns, URL filtering, length validation
- **Usage**: `python3 tests/test_phase2.py`

### **Unit Tests** (`test_simple.py`)
- **Purpose**: Basic unit test validation
- **Coverage**: Core classes and utilities
- **Usage**: `python3 tests/test_simple.py`

## 🔧 Test Data Format

### **Legacy Format** (JSONL)
```json
{
  "input": "Message content",
  "expected": "allow|warn|block",
  "description": "What this tests"
}
```

### **Integration Format** (JSONL)
```json
{
  "input": "Message content",
  "expected": "allow|warn|block",
  "description": "What this tests",
  "conversation_id": "CONV001",
  "turn": 1,
  "speaker": "user|bot"
}
```

## 🚀 Running Tests

### **Integration Tests**

#### Individual Scenario
```bash
cd tests/scenarios/customer_service
python3 test_runner.py                    # Full output
python3 test_runner.py --quiet            # Summary only
python3 test_runner.py --transcript       # Conversation view
```

#### All Scenarios
```bash
cd tests/scenarios
python3 run_all_tests.py                  # Run all scenarios
python3 run_all_tests.py --quiet          # Summary only
python3 run_all_tests.py --scenario customer_service  # Specific scenario
```

### **Legacy Tests**
```bash
cd tests
python3 test_simple.py                    # Basic unit tests
python3 test_runner.py                    # Legacy smoke tests
python3 test_phase2.py                    # Comprehensive Phase 2 tests
```

## 📈 Test Results

### **Overall Coverage**
- **144 Total Tests**: Across all test suites
- **100% Pass Rate**: All tests passing with expected results
- **Multiple Validation Approaches**: Unit, integration, and scenario testing

### **Integration Test Results**
- **Customer Service**: 38 messages, 21.1% blocked (toxic content)
- **Medical Bot**: 48 messages, 14.0% warned (PII content)

### **Legacy Test Results**
- **Smoke Tests**: 12/12 passed (100%)
- **Regex Tests**: 20/20 passed (100%)
- **URL Tests**: 26/26 passed (100%)

## 🔍 Test Validation

### **What We Validate**
1. **Accuracy**: Correct moderation actions for test cases
2. **Coverage**: Realistic conversation scenarios
3. **Performance**: Efficient processing of messages
4. **Configurability**: Easy adjustment of moderation rules

### **Success Criteria**
- **Zero False Positives**: No legitimate content incorrectly flagged
- **Zero False Negatives**: No problematic content missed
- **Appropriate Actions**: Correct warn/block decisions
- **Context Preservation**: Normal interactions remain allowed

## 🛠️ Adding New Tests

### **Adding New Scenarios**
1. Create scenario directory in `tests/scenarios/`
2. Add required files:
   - `test_data.jsonl` - Conversation test cases
   - `config.yaml` - Moderation configuration
   - `test_runner.py` - Test execution script
   - `README.md` - Scenario documentation
3. Follow the integration test format for test data

### **Adding Legacy Tests**
1. Add test cases to appropriate JSONL file in `tests/test_corpus/`
2. Follow the legacy test format
3. Update relevant test runner if needed

### **Adding Unit Tests**
1. Add test functions to `tests/test_simple.py`
2. Follow standard Python unittest patterns
3. Test individual components and edge cases

## 📚 Related Documentation

- **Framework**: `../src/` - Core framework implementation
- **Configs**: `tests/configs/` - Test-specific configurations
- **Specs**: `../specs/` - Project specifications
- **Plans**: `../plans/` - Implementation plans

## 🎯 Testing Philosophy

### **Human-Readable Tests**
- Tests should be understandable by humans, not just machines
- Clear documentation of what each test validates
- Realistic scenarios that reflect actual use cases

### **Comprehensive Coverage**
- Multiple testing approaches for different validation needs
- Both technical correctness and real-world applicability
- Edge case coverage alongside happy path validation

### **Maintainable Organization**
- Self-contained test scenarios for easy maintenance
- Shared infrastructure to reduce code duplication
- Clear separation between different types of tests

### **Backward Compatibility**
- Legacy tests preserved and functional
- No breaking changes to existing test infrastructure
- Gradual migration path for test organization

---

**Last Updated**: December 2024  
**Test Coverage**: 144 tests across all suites  
**Scenarios**: 2 integration scenarios + legacy test suites  
**Maintainer**: Product Team 