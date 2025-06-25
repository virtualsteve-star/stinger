# Phase 5 Test Plan: OpenAI Content Moderation & Prompt Injection Detection

## Overview
This test plan covers the implementation of OpenAI content moderation and prompt injection detection filters. The plan ensures comprehensive testing of both filters, including API integration, error handling, and accuracy validation.

## Test Categories

### 1. Pluggable Interface Tests
- **Interface Contracts**: Test that all guardrails implement required interface
- **Result Standardization**: Test standardized result format across implementations
- **Registry Functionality**: Test guardrail registry and factory patterns
- **Implementation Swapping**: Test switching between different implementations
- **Type Safety**: Test type-specific base classes and inheritance

### 2. API Key Management Tests
- **Key Loading**: Test secure loading from environment variables
- **Key Validation**: Test key format and connectivity validation
- **Key Rotation**: Test key rotation workflows
- **Security Features**: Test encrypted storage and key masking
- **Health Monitoring**: Test key health checking and monitoring

### 3. OpenAI Adapter Tests
- **OpenAI API Integration**: Test OpenAI Moderation and GPT API integration
- **Result Structure Validation**: Validate moderation and injection result data structures
- **Error Handling**: Test API failures and error handling patterns
- **Health Checks**: Test service availability detection

### 4. Content Moderation Filter Tests
- **Content Moderation Accuracy**: Test content moderation using OpenAI API
- **Category Detection**: Test detection of different content categories
- **Threshold Configuration**: Test confidence threshold handling
- **Fallback Mechanisms**: Test fallback when API is unavailable
- **Error Handling**: Test error handling in content moderation filter

### 4. Prompt Injection Detection Filter Tests
- **Prompt Injection Detection**: Test prompt injection detection using OpenAI API
- **Risk Level Classification**: Test low/medium/high/critical risk level classification
- **Indicator Detection**: Test detection of specific injection indicators
- **Threshold Configuration**: Test risk threshold handling
- **Fallback Mechanisms**: Test fallback when API is unavailable
- **Error Handling**: Test error handling in prompt injection filter

### 5. Integration Tests
- **End-to-End Pipeline**: Test complete pipeline with both filters
- **Graceful Degradation**: Test system operation when OpenAI APIs are down
- **Performance Tests**: Test execution time and throughput
- **Combined Filter Operation**: Test both filters working together

### 6. Accuracy Validation Tests
- **Content Moderation Accuracy**: Test against known content moderation corpus
- **Prompt Injection Risk Assessment**: Test risk level classification accuracy
- **Prompt Injection Indicator Detection**: Test detection of specific injection indicators

## Test Data Requirements

### API Key Management Test Data
- **Valid API Keys**: Test keys for validation testing
- **Invalid API Keys**: Test keys for error handling
- **Environment Variables**: Test environment variable configurations
- **Encryption Keys**: Test encryption/decryption scenarios

### OpenAI API Test Data
- **OpenAI Moderation Test Data**: Mock responses for different content types
- **OpenAI GPT Test Data**: Mock responses for prompt injection detection
- **API Failure Scenarios**: Test data for various API failure modes

### Accuracy Validation Test Data
- **Content Moderation Corpus**: Known content examples with expected classifications
- **Prompt Injection Corpus**: Known prompt injection attempts with expected risk levels and indicators

### Performance Test Data
- **Large Content Samples**: Various content sizes for performance testing
- **Mixed Content Types**: Different content types for comprehensive testing

## Test Execution Strategy

### Phase 1: Unit Tests
- **API Key Management Tests**: Test key loading, validation, and security features
- **OpenAI Adapter Tests**: Test adapter interface and API integration
- **Filter Tests**: Test individual filter implementations
- **Error Handling Tests**: Test simple error handling patterns

### Phase 2: Integration Tests
- **End-to-End Pipeline Tests**: Test complete pipeline with OpenAI APIs
- **Graceful Degradation Tests**: Test system operation when APIs are down
- **Performance Tests**: Test execution time and throughput

### Phase 3: Accuracy Validation Tests
- **Content Moderation Accuracy**: Test against known content moderation corpus
- **Prompt Injection Accuracy**: Test against known prompt injection corpus

## Success Criteria

### Test Coverage
- [ ] >90% code coverage for new adapter and filter code
- [ ] API key management system fully tested and validated
- [ ] All OpenAI API integrations tested and validated
- [ ] All filter implementations tested with comprehensive scenarios
- [ ] Error handling tested for all failure scenarios
- [ ] Graceful degradation tested when APIs are unavailable

### Accuracy Validation
- [ ] Content moderation accuracy ≥ 95% on validation corpus
- [ ] Prompt injection risk level classification accuracy ≥ 90% on validation corpus
- [ ] Prompt injection indicator detection accuracy ≥ 85% on validation corpus

### Reliability Validation
- [ ] System continues operating when OpenAI APIs are down
- [ ] Graceful degradation to local filters when APIs fail
- [ ] Error recovery works correctly after API restoration

## Risk Mitigation
- **API Rate Limits**: Test rate limiting and retry logic
- **API Costs**: Monitor usage during testing
- **API Availability**: Test fallback mechanisms thoroughly
- **Model Changes**: Use stable API endpoints for testing 