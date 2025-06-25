# Implementation Phasing Plan – LLM Guardrails Framework

| Phase | Objective | Key Deliverables | Exit Criteria |
|-------|-----------|------------------|---------------|
| **1** | **Scaffold + Test Bootstrap** | • `FilterPipeline` & `BaseFilter`  • YAML config loader with validation  • `test_runner.py`  • Smoke test corpus  • Basic error handling framework | *Smoke suite passes*  <br/>*Framework processes input → output unchanged*  <br/>*Config validation rejects invalid YAML* |
| **2** | **Rule‑Based Filters** | • URL/file‑type block  • Regex/keyword blacklist  • Language and length limits  • Expanded test suites  • Filter-level error handling (`block`/`allow`/`skip`) | *≥ 95 % block on malicious rule‑based corpus*  <br/>*≤ 2 % false positives on benign corpus*  <br/>*Error handling works for filter crashes* |
| **3** | **Comprehensive Integration Testing** | • Self-contained test scenarios  • Realistic conversation flows  • Customer service & medical bot scenarios  • Enhanced test infrastructure  • Human-readable documentation  • Master test runner | *2 realistic scenarios implemented*  <br/>*144 total tests across all suites*  <br/>*100% pass rate with expected results*  <br/>*Tests are human-readable and maintainable* |
| **4** | **Developer Experience & Configuration** | • Keyword list filter (multi-keyword support) with external file loading  • Enhanced error messages with debugging context  • YAML schema validation with helpful error messages  • Unified test command (`stinger test`)  • Getting started guide and configuration templates  • Configuration hot reload capability | *Configuration complexity reduced by 80%*  <br/>*Debug time reduced by 60% with better error messages*  <br/>*New developers can set up and run tests in <5 minutes*  <br/>*All existing configurations remain functional* |
| **4b** | **Hot Reload Completion** | • Automated file system event testing (integration/system)  • Comprehensive integration test coverage for hot reload scenarios  • Documentation and developer guidance for hot reload usage  • CLI/UX polish for hot reload status and control  • CI integration with test marking for flaky integration tests | *File system event tests pass reliably in dev/local environments*  <br/>*All major hot reload scenarios covered by integration tests*  <br/>*Documentation enables any developer to use and troubleshoot hot reload*  <br/>*CLI support is intuitive and robust*  <br/>*No regressions or breaking changes to existing features* |
| **4c** | **Hot Reload Rollback & Simplification** | • Complete removal of hot reload code and tests  • Simplified pipeline architecture (FilterPipeline only)  • Cleaned up CLI and configuration system  • Updated documentation and version history  • Tracking issue for future reference  • Restored focus on core filtering functionality | *All hot reload code removed (1,769 lines deleted)*  <br/>*Simplified architecture with no file system watching*  <br/>*Improved test reliability (no flaky integration tests)*  <br/>*All 13 tests pass with core functionality intact*  <br/>*Codebase focused on content filtering mission* |
| **5** | **OpenAI Content Moderation & Prompt Injection Detection** ✅ | • Universal guardrail interface  • OpenAI content moderation filter  • OpenAI prompt injection detection filter  • API key management system  • Simple error handling and graceful degradation | *Content moderation meets accuracy targets (95%+ precision, 90%+ recall)*  <br/>*Prompt injection detection meets accuracy targets (90%+ precision, 85%+ recall)*  <br/>*System continues operating when OpenAI APIs are down* |
| **5a** | **Additional Classifier Filters with Centralized Model Configuration** | • Centralized model configuration system (gpt-4.1-nano default)  • PII detection filters (regex-based + AI-based)  • Toxicity detection filters (regex-based + AI-based)  • Code generation filters (regex-based + AI-based)  • Enhanced regex pattern libraries  • Comprehensive test corpora for all filter types | *Centralized model configuration system implemented and tested*  <br/>*PII detection accuracy ≥ 95% (regex) / ≥ 98% (AI) on validation corpus*  <br/>*Toxicity detection accuracy ≥ 90% (regex) / ≥ 95% (AI) on validation corpus*  <br/>*Code generation detection accuracy ≥ 85% (regex) / ≥ 90% (AI) on validation corpus*  <br/>*All filters integrate with universal guardrail interface* |
| **5b** | **Configuration Reorganization** | • Co-locate configs with related source code following Python best practices  • Separate production, test, and example configurations  • Improve discoverability and maintainability  • Update all source code references and documentation  • Preserve functionality and backward compatibility | *All tests pass after reorganization*  <br/>*Configs are co-located with related source code*  <br/>*Clear separation between production, test, and example configs*  <br/>*No hardcoded paths to old config locations*  <br/>*Documentation is updated and accurate* |
| **6** | **Policy & Context Controls** | • Rate limiting per API key / user  • Topic allow/deny lists  • Role overrides  • Configuration hot reload  • Health monitoring dashboard | *End‑to‑end policy tests pass*  <br/>*Config changes applied without restart*  <br/>*Health status visible for all filters* |
| **7** | **Observability & CI** | • Structured logs to SIEM  • Prometheus metrics  • GitHub Actions running full suites on PRs  • Configuration testing framework  • Automatic rollback on validation failures  • **Performance logging for guardrail filters (execution times, latency, throughput)** | *CI green across all branches*  <br/>*Dashboards show live metrics and filter execution times*  <br/>*Config changes validated before deployment*  <br/>**Performance logs available for all guardrail filters** |
| **8** | **Hardening & Docs** | • Fail‑closed defaults  • Security reviews  • Developer guide & API docs  • Production deployment guide  • Incident response procedures | *Security review signed off*  <br/>*v1.0 tag published*  <br/>*Documentation complete for all personas* |

> **Note:** Phases 1–3 are designed for quick iteration (~2–3 sprints). Phase 4 focuses on developer experience improvements that will accelerate development of later phases. Later phases can proceed in parallel once Phase 4 stability is proven.

## Error Handling & Configuration Management Integration

### Phase 1 Additions
- **Config Validation**: YAML schema validation with clear error messages
- **Basic Error Handling**: Filter-level error handling with configurable actions
- **Test Framework**: Configuration testing alongside filter testing

### Phase 2 Additions  
- **Error Recovery**: Filter crash handling and recovery mechanisms
- **Config Safety**: Configuration change validation before deployment

### Phase 3 Additions
- **Test Organization**: Self-contained scenarios with comprehensive documentation
- **Realistic Validation**: Conversation-based testing with human-readable results
- **Flexible Execution**: Multiple test modes and master test runner
- **Backward Compatibility**: All legacy tests preserved and functional

### Phase 4 Additions
- **Developer Experience**: Keyword list filters, enhanced error messages, unified test commands
- **Configuration Simplification**: Multi-keyword support, schema validation, configuration templates
- **Onboarding**: Getting started guide, quick setup, configuration hot reload
- **Debugging**: Detailed error context, filter-level logging, debug mode
- **Hot Reload**: Configuration changes without service restart, validation and rollback
- **Integration Testing**: File system event testing, comprehensive hot reload scenarios
- **Documentation**: Complete hot reload usage guide, troubleshooting, and CI integration

### Phase 4c Additions
- **Hot Reload Rollback**: Complete removal of hot reload functionality due to complexity and reliability issues
- **Architecture Simplification**: Removed file system watching, threading, and observer lifecycle management
- **Test Reliability**: Eliminated flaky integration tests and file system dependencies
- **Codebase Focus**: Restored focus on core content filtering functionality
- **Documentation**: Updated all documentation to reflect simplified architecture
- **Tracking**: Created issue #6 to document rollback rationale for future reference

### Phase 5 Additions
- **Universal Guardrail Interface**: Standardized interface for all guardrails
- **OpenAI Integration**: Content moderation and prompt injection detection using OpenAI APIs
- **API Key Management**: Secure key handling with environment variables and encryption
- **Simple Error Handling**: Basic try/catch patterns with graceful degradation
- **Guardrail Registry**: Dynamic loading and factory patterns for guardrail implementations

### Phase 5a Additions
- **Centralized Model Configuration**: Unified model configuration system with gpt-4.1-nano as default
- **Model Abstraction Factory**: Abstract ModelProvider interface and OpenAIModelProvider implementation
- **PII Detection**: Regex-based detection of sensitive personal information + AI-based detection using centralized model config
- **Toxicity Detection**: Regex-based detection of toxic language patterns + AI-based detection using centralized model config
- **Code Generation Filter**: Regex-based detection of code patterns + AI-based detection using centralized model config
- **Enhanced Pattern Libraries**: Comprehensive regex patterns for simple filter implementations
- **AI-Powered Detection**: OpenAI-based detection for higher accuracy and context understanding
- **Specialized Test Corpora**: Validation data for both regex and AI-based filter implementations
- **Fallback Mechanisms**: Automatic fallback from AI to simple filters when AI is unavailable

### Phase 5b Additions
- **Configuration Reorganization**: Co-locate configs with related source code following Python best practices
- **Separation of Concerns**: Clear distinction between production, test, and example configurations
- **Improved Discoverability**: Configs are easy to find and map to their related source code
- **Enhanced Maintainability**: Easier to maintain and refactor configurations
- **Backward Compatibility**: All existing functionality preserved during reorganization
- **Documentation Updates**: Updated all references and documentation to reflect new structure

### Phase 6 Additions
- **Hot Reload**: Configuration changes without service restart
- **Rollback Capability**: Automatic rollback on configuration validation failures
- **Environment Management**: Separate configs for dev/staging/prod

- Compound filters now use additive certainty scoring (not weights).
- All rules use 'certainty' (0-100) instead of 'weight'.

