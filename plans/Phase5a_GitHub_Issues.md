# Phase 5a GitHub Issues

## Issue #7: Implement PII Detection Filters (Simple + AI)

**Title**: Implement PII Detection Filters for Phase 5a

**Description**:
Implement both simple (regex-based) and AI-based PII (Personally Identifiable Information) detection filters that can identify sensitive personal information in content.

**Requirements**:
- **Simple PII Detection**: Regex-based detection of SSN, credit cards, emails, phone numbers, IP addresses
- **AI-Based PII Detection**: OpenAI-based detection with higher accuracy and context understanding
- Configurable confidence thresholds for both implementations
- Integration with universal guardrail interface
- Fallback mechanism from AI to simple detection when API is unavailable

**Technical Details**:
- Implement `SimplePIIDetectionFilter` class with regex patterns
- Implement `AIPIIDetectionFilter` class using OpenAI API
- Add `PII_DETECTION` to `GuardrailType` enum
- Create comprehensive test suite for both implementations
- Add configuration examples for both filter types

**Acceptance Criteria**:
- [ ] Simple PII detection filter implemented and tested (accuracy ≥ 95%)
- [ ] AI-based PII detection filter implemented and tested (accuracy ≥ 98%)
- [ ] Fallback mechanism works when AI is unavailable
- [ ] Integration with universal guardrail interface
- [ ] Configuration examples provided for both implementations
- [ ] Comprehensive test coverage (>90%)

**Files to Create/Modify**:
- `src/filters/simple_pii_detection_filter.py`
- `src/filters/ai_pii_detection_filter.py`
- `src/core/guardrail_interface.py` (add PII_DETECTION type)
- `tests/test_simple_pii_detection_filter.py`
- `tests/test_ai_pii_detection_filter.py`
- `configs/keyword_lists/pii_patterns.txt`
- `configs/phase5a_simple_pii.yaml`
- `configs/phase5a_ai_pii.yaml`

**Labels**: `phase-5a`, `enhancement`, `pii-detection`

---

## Issue #8: Implement Toxicity Detection Filters (Simple + AI)

**Title**: Implement Toxicity Detection Filters for Phase 5a

**Description**:
Implement both simple (regex-based) and AI-based toxicity detection filters that can identify toxic language and content patterns in text.

**Requirements**:
- **Simple Toxicity Detection**: Regex-based detection of hate speech, harassment, threats, sexual harassment
- **AI-Based Toxicity Detection**: OpenAI-based detection with higher accuracy and context understanding
- Configurable confidence thresholds for both implementations
- Integration with universal guardrail interface
- Fallback mechanism from AI to simple detection when API is unavailable

**Technical Details**:
- Implement `SimpleToxicityDetectionFilter` class with regex patterns
- Implement `AIToxicityDetectionFilter` class using OpenAI API
- Add `TOXICITY_DETECTION` to `GuardrailType` enum
- Create comprehensive test suite for both implementations
- Add configuration examples for both filter types

**Acceptance Criteria**:
- [ ] Simple toxicity detection filter implemented and tested (accuracy ≥ 90%)
- [ ] AI-based toxicity detection filter implemented and tested (accuracy ≥ 95%)
- [ ] Fallback mechanism works when AI is unavailable
- [ ] Integration with universal guardrail interface
- [ ] Configuration examples provided for both implementations
- [ ] Comprehensive test coverage (>90%)

**Files to Create/Modify**:
- `src/filters/simple_toxicity_detection_filter.py`
- `src/filters/ai_toxicity_detection_filter.py`
- `src/core/guardrail_interface.py` (add TOXICITY_DETECTION type)
- `tests/test_simple_toxicity_detection_filter.py`
- `tests/test_ai_toxicity_detection_filter.py`
- `configs/keyword_lists/toxicity_patterns.txt`
- `configs/phase5a_simple_toxicity.yaml`
- `configs/phase5a_ai_toxicity.yaml`

**Labels**: `phase-5a`, `enhancement`, `toxicity-detection`

---

## Issue #9: Implement Code Generation Filters (Simple + AI)

**Title**: Implement Code Generation Filters for Phase 5a

**Description**:
Implement both simple (regex-based) and AI-based code generation detection filters that can identify code injection and generation attempts in content.

**Requirements**:
- **Simple Code Generation Detection**: Regex-based detection of code blocks, programming keywords, code injection, file operations
- **AI-Based Code Generation Detection**: OpenAI-based detection with higher accuracy and context understanding
- Configurable confidence thresholds and keyword minimums for simple implementation
- Integration with universal guardrail interface
- Fallback mechanism from AI to simple detection when API is unavailable

**Technical Details**:
- Implement `SimpleCodeGenerationFilter` class with regex patterns
- Implement `AICodeGenerationFilter` class using OpenAI API
- Add `CODE_GENERATION` to `GuardrailType` enum
- Create comprehensive test suite for both implementations
- Add configuration examples for both filter types

**Acceptance Criteria**:
- [ ] Simple code generation filter implemented and tested (accuracy ≥ 85%)
- [ ] AI-based code generation filter implemented and tested (accuracy ≥ 90%)
- [ ] Fallback mechanism works when AI is unavailable
- [ ] Integration with universal guardrail interface
- [ ] Configuration examples provided for both implementations
- [ ] Comprehensive test coverage (>90%)

**Files to Create/Modify**:
- `src/filters/simple_code_generation_filter.py`
- `src/filters/ai_code_generation_filter.py`
- `src/core/guardrail_interface.py` (add CODE_GENERATION type)
- `tests/test_simple_code_generation_filter.py`
- `tests/test_ai_code_generation_filter.py`
- `configs/keyword_lists/code_patterns.txt`
- `configs/phase5a_simple_code_generation.yaml`
- `configs/phase5a_ai_code_generation.yaml`

**Labels**: `phase-5a`, `enhancement`, `code-detection`

---

## Issue #10: Update Guardrail Interface for Phase 5a

**Title**: Update Guardrail Interface to Support Phase 5a Filter Types

**Description**:
Update the universal guardrail interface to support the new filter types introduced in Phase 5a.

**Requirements**:
- Add new filter types to `GuardrailType` enum
- Update factory registration for new filter types
- Add new filter types to test suite
- Ensure backward compatibility

**Technical Details**:
- Add `PII_DETECTION`, `TOXICITY_DETECTION`, `CODE_GENERATION` to enum
- Update factory registration in `GuardrailFactory`
- Add new filter types to test suite
- Update documentation

**Acceptance Criteria**:
- [ ] New filter types added to `GuardrailType` enum
- [ ] Factory registration updated for new filter types
- [ ] Test suite updated to include new filter types
- [ ] Backward compatibility maintained
- [ ] Documentation updated

**Files to Modify**:
- `src/core/guardrail_interface.py`
- `src/core/guardrail_factory.py`
- `tests/test_phase5.py` (add new filter type tests)

**Labels**: `phase-5a`, `enhancement`, `interface-update`

---

## Issue #11: Create Phase 5a Integration Tests

**Title**: Create Comprehensive Integration Tests for Phase 5a Filters

**Description**:
Create comprehensive integration tests to ensure all Phase 5a filters (both simple and AI-based) work together correctly in the pipeline.

**Requirements**:
- Test all filters working together in pipeline
- Test configuration loading for all new filters
- Test error handling across all filter types
- Test fallback mechanisms from AI to simple filters
- Test performance differences between simple and AI implementations
- Create comprehensive test corpora

**Technical Details**:
- Create integration test suite
- Create test corpora for each filter type
- Test pipeline integration
- Test configuration loading
- Test error handling and fallback mechanisms

**Acceptance Criteria**:
- [ ] Integration test suite created
- [ ] All filters work correctly in pipeline
- [ ] Configuration loading tested for all filters
- [ ] Error handling tested across all filters
- [ ] Fallback mechanisms tested when AI is unavailable
- [ ] Performance comparison tests implemented
- [ ] Test corpora created for validation

**Files to Create**:
- `tests/test_phase5a_integration.py`
- `tests/test_phase5a_performance.py`
- `tests/test_corpus/pii_test_corpus.jsonl`
- `tests/test_corpus/toxicity_test_corpus.jsonl`
- `tests/test_corpus/code_generation_test_corpus.jsonl`
- `configs/phase5a_comprehensive.yaml`

**Labels**: `phase-5a`, `testing`, `integration`

---

## Issue #12: Create Phase 5a Configuration Examples

**Title**: Create Configuration Examples for Phase 5a Filters

**Description**:
Create comprehensive configuration examples and documentation for all Phase 5a filters (both simple and AI-based implementations).

**Requirements**:
- Create YAML configuration examples for each filter implementation
- Create comprehensive configuration example combining all filters
- Update documentation with new filter usage
- Create demo scripts for new filters
- Document performance characteristics of each implementation

**Technical Details**:
- Create individual configuration files for each filter implementation
- Create comprehensive configuration example
- Update README and documentation
- Create demo scripts
- Document performance trade-offs

**Acceptance Criteria**:
- [ ] Configuration examples created for all filter implementations
- [ ] Comprehensive configuration example created
- [ ] Documentation updated with new filter usage
- [ ] Demo scripts created for new filters
- [ ] Performance characteristics documented

**Files to Create**:
- `configs/phase5a_simple_pii.yaml`
- `configs/phase5a_ai_pii.yaml`
- `configs/phase5a_simple_toxicity.yaml`
- `configs/phase5a_ai_toxicity.yaml`
- `configs/phase5a_simple_code_generation.yaml`
- `configs/phase5a_ai_code_generation.yaml`
- `configs/phase5a_comprehensive.yaml`
- `demo_phase5a.py`
- Update README.md with Phase 5a information

**Labels**: `phase-5a`, `documentation`, `configuration` 