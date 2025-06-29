# Phase 5a Test Plan – OpenAI Integration & Content Moderation

**Status: ✅ COMPLETED**  
**Start Date**: 2025-06-25  
**Completion Date**: 2025-06-25  

## 🎯 Phase 5a Test Objective

## Overview
This test plan covers the implementation of three additional classifier filter categories, each with both simple (regex/blocklist) and AI-based implementations: PII detection, toxicity detection, and code generation detection. The plan ensures comprehensive testing of all filter implementations, including pattern matching accuracy, AI integration, and configuration options.

## Test Categories

### 1. PII Detection Filter Tests

#### Simple PII Detection Tests
- **Pattern Matching Accuracy**: Test detection of various PII formats using regex
- **SSN Detection**: Test Social Security Number patterns (XXX-XX-XXXX)
- **Credit Card Detection**: Test credit card number patterns (various formats)
- **Email Detection**: Test email address patterns
- **Phone Number Detection**: Test phone number patterns (various formats)
- **IP Address Detection**: Test IP address patterns
- **Configuration Options**: Test enabling/disabling specific PII types
- **Confidence Thresholds**: Test different confidence threshold settings
- **False Positive Testing**: Test with similar but non-PII content

#### AI-Based PII Detection Tests
- **OpenAI Integration**: Test AI-based PII detection using OpenAI API
- **Context Understanding**: Test AI's ability to understand context and edge cases
- **Accuracy Comparison**: Compare AI accuracy vs simple regex accuracy
- **Fallback Mechanisms**: Test fallback to simple detection when AI fails
- **API Error Handling**: Test handling of OpenAI API errors
- **Confidence Scoring**: Test AI confidence scoring accuracy

### 2. Toxicity Detection Filter Tests

#### Simple Toxicity Detection Tests
- **Hate Speech Detection**: Test detection of hate speech patterns using regex
- **Harassment Detection**: Test detection of harassment patterns
- **Threat Detection**: Test detection of threat patterns
- **Sexual Harassment Detection**: Test detection of sexual harassment patterns
- **Category Configuration**: Test enabling/disabling specific toxicity categories
- **Confidence Scoring**: Test confidence calculation based on match count
- **Pattern Strength**: Test different pattern strengths and combinations
- **False Positive Testing**: Test with similar but non-toxic content

#### AI-Based Toxicity Detection Tests
- **OpenAI Integration**: Test AI-based toxicity detection using OpenAI API
- **Context Understanding**: Test AI's ability to understand context and nuance
- **Accuracy Comparison**: Compare AI accuracy vs simple regex accuracy
- **Fallback Mechanisms**: Test fallback to simple detection when AI fails
- **API Error Handling**: Test handling of OpenAI API errors
- **Confidence Scoring**: Test AI confidence scoring accuracy

### 3. Code Generation Filter Tests

#### Simple Code Generation Tests
- **Code Block Detection**: Test detection of markdown and HTML code blocks
- **Programming Keywords**: Test detection of programming language keywords
- **Code Injection Detection**: Test detection of code injection attempts
- **File Operation Detection**: Test detection of file system operations
- **Category Configuration**: Test enabling/disabling specific code categories
- **Keyword Thresholds**: Test minimum keyword count requirements
- **Confidence Calculation**: Test confidence based on category and match count
- **False Positive Testing**: Test with similar but non-code content

#### AI-Based Code Generation Tests
- **OpenAI Integration**: Test AI-based code generation detection using OpenAI API
- **Context Understanding**: Test AI's ability to understand code context
- **Accuracy Comparison**: Compare AI accuracy vs simple regex accuracy
- **Fallback Mechanisms**: Test fallback to simple detection when AI fails
- **API Error Handling**: Test handling of OpenAI API errors
- **Confidence Scoring**: Test AI confidence scoring accuracy

### 4. Integration Tests
- **Universal Interface Compliance**: Test all filters implement GuardrailInterface
- **Factory Registration**: Test filter registration with GuardrailFactory
- **Pipeline Integration**: Test filters working together in pipeline
- **Configuration Loading**: Test YAML configuration loading for all filters
- **Error Handling**: Test error handling across all filter types
- **Performance Comparison**: Test performance differences between simple and AI implementations

### 5. Accuracy Validation Tests
- **Simple Filter Accuracy**: Test accuracy of regex-based implementations
- **AI Filter Accuracy**: Test accuracy of AI-based implementations
- **Cross-Implementation Comparison**: Compare accuracy between simple and AI implementations
- **Cross-Filter Validation**: Test filters don't interfere with each other

## Test Data Requirements

### PII Detection Test Data
- **Valid PII Examples**:
  - SSN: "123-45-6789", "123456789"
  - Credit Cards: "1234-5678-9012-3456", "1234567890123456"
  - Emails: "test@example.com", "user.name+tag@domain.co.uk"
  - Phone Numbers: "(555) 123-4567", "+1-555-123-4567", "555.123.4567"
  - IP Addresses: "192.168.1.1", "10.0.0.1", "172.16.0.1"

- **Invalid PII Examples**:
  - Similar patterns that aren't PII
  - Edge cases and boundary conditions
  - International formats

- **Context-Dependent PII Examples**:
  - PII mentioned in educational contexts
  - PII in fictional scenarios
  - PII in code examples

### Toxicity Detection Test Data
- **Hate Speech Examples**:
  - Explicit hate speech terms
  - Coded language and dog whistles
  - Context-dependent hate speech

- **Harassment Examples**:
  - Direct harassment patterns
  - Indirect harassment patterns
  - Cyberbullying examples

- **Threat Examples**:
  - Direct threats
  - Implied threats
  - Conditional threats

- **Sexual Harassment Examples**:
  - Explicit sexual harassment
  - Implied sexual harassment
  - Workplace harassment patterns

- **Context-Dependent Examples**:
  - Educational content about toxicity
  - Fictional scenarios
  - Academic discussions

### Code Generation Test Data
- **Code Block Examples**:
  - Markdown code blocks
  - HTML code tags
  - Inline code snippets

- **Programming Keywords**:
  - Common programming language keywords
  - Function and class definitions
  - Control flow statements

- **Code Injection Examples**:
  - eval() and exec() calls
  - System commands
  - Database queries

- **File Operation Examples**:
  - File read/write operations
  - Directory operations
  - Permission changes

- **Context-Dependent Examples**:
  - Educational code examples
  - Documentation with code
  - Technical discussions

## Test Execution Strategy

### Phase 1: Simple Filter Unit Tests
- **Pattern Matching Tests**: Test individual regex patterns
- **Filter Logic Tests**: Test filter analysis logic
- **Configuration Tests**: Test configuration loading and validation
- **Error Handling Tests**: Test error scenarios

### Phase 2: AI Filter Unit Tests
- **OpenAI Integration Tests**: Test API integration
- **Prompt Engineering Tests**: Test prompt effectiveness
- **Response Parsing Tests**: Test JSON response parsing
- **Fallback Mechanism Tests**: Test fallback to simple filters

### Phase 3: Integration Tests
- **Interface Compliance**: Test universal interface implementation
- **Factory Integration**: Test filter creation and registration
- **Pipeline Integration**: Test filters in pipeline context
- **Performance Comparison**: Test performance differences

### Phase 4: Accuracy Validation Tests
- **Corpus Testing**: Test against comprehensive test corpora
- **Accuracy Measurement**: Measure precision, recall, and F1 scores
- **Cross-Implementation Comparison**: Compare simple vs AI accuracy
- **False Positive Analysis**: Analyze false positive rates

## Success Criteria

### Test Coverage
- [ ] >90% code coverage for all filter implementations
- [ ] All pattern matching scenarios tested (simple filters)
- [ ] All AI integration scenarios tested (AI filters)
- [ ] All configuration options tested
- [ ] All error handling scenarios tested
- [ ] Integration with universal interface tested

### Accuracy Validation
- [ ] Simple PII detection accuracy ≥ 95% on validation corpus
- [ ] AI-based PII detection accuracy ≥ 98% on validation corpus
- [ ] Simple toxicity detection accuracy ≥ 90% on validation corpus
- [ ] AI-based toxicity detection accuracy ≥ 95% on validation corpus
- [ ] Simple code generation detection accuracy ≥ 85% on validation corpus
- [ ] AI-based code generation detection accuracy ≥ 90% on validation corpus
- [ ] False positive rate < 5% for all filter implementations

### Integration Validation
- [ ] All filters integrate with universal guardrail interface
- [ ] All filters work correctly in pipeline context
- [ ] Configuration loading works for all filter types
- [ ] Error handling works consistently across all filters
- [ ] Fallback mechanisms work correctly when AI is unavailable

### Performance Validation
- [ ] Simple filter execution time < 10ms per message
- [ ] AI filter execution time < 500ms per message
- [ ] Memory usage < 50MB for typical workloads
- [ ] Throughput > 100 messages per second (simple filters)
- [ ] Throughput > 10 messages per second (AI filters)

## Test Implementation

### Test File Structure
```
tests/
├── test_simple_pii_detection_filter.py
├── test_ai_pii_detection_filter.py
├── test_simple_toxicity_detection_filter.py
├── test_ai_toxicity_detection_filter.py
├── test_simple_code_generation_filter.py
├── test_ai_code_generation_filter.py
├── test_phase5a_integration.py
└── test_corpus/
    ├── pii_test_corpus.jsonl
    ├── toxicity_test_corpus.jsonl
    └── code_generation_test_corpus.jsonl
```

### Test Data Files
```
configs/keyword_lists/
├── pii_patterns.txt
├── toxicity_patterns.txt
└── code_patterns.txt
```

### Configuration Test Files
```
configs/
├── phase5a_simple_pii.yaml
├── phase5a_ai_pii.yaml
├── phase5a_simple_toxicity.yaml
├── phase5a_ai_toxicity.yaml
├── phase5a_simple_code_generation.yaml
├── phase5a_ai_code_generation.yaml
└── phase5a_comprehensive.yaml
```

## Risk Mitigation
- **Pattern Accuracy**: Comprehensive testing of regex patterns
- **AI Reliability**: Test fallback mechanisms when AI is unavailable
- **False Positives**: Extensive false positive testing for both implementations
- **Performance**: Monitor execution times and optimize patterns
- **Configuration**: Validate all configuration options
- **Integration**: Test filters work together without conflicts

## Test Execution Commands
```bash
# Run all Phase 5a tests
python3 -m pytest tests/test_phase5a_*.py -v

# Run simple filter tests
python3 -m pytest tests/test_simple_*_filter.py -v

# Run AI filter tests
python3 -m pytest tests/test_ai_*_filter.py -v

# Run integration tests
python3 -m pytest tests/test_phase5a_integration.py -v

# Run with coverage
python3 -m pytest tests/test_phase5a_*.py --cov=src/filters --cov-report=html

# Run performance comparison tests
python3 -m pytest tests/test_phase5a_performance.py -v
``` 