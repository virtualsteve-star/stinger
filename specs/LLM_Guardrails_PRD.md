# LLM Guardrails Framework – Product Requirements Document (PRD)

**Project Name:** LLM Guardrails Framework  
**Owner:** Steve Wilson  
**Document Version:** 0.2  
**Date:** June 22, 2025

---

## 1 Purpose

Provide a configurable guardrails layer that filters *inputs to* and *outputs from* any Large Language Model (LLM).  
The framework must block or transform unwanted content (e.g., PII, prompt‑injection attempts, toxic language) while allowing safe traffic with minimal latency.

---

## 2 Target Users & Personas

| Persona | Primary Goals | Pain Points Addressed |
|---------|---------------|-----------------------|
| **Application Developer** | Embed LLM features quickly, enforce basic safety and compliance rules. | Lacks time to write bespoke filters; needs turnkey guardrails. |
| **AI Coding Agent** (e.g. Claude Code, Cursor) | Run tests, diagnose failures, auto‑patch configs. | Needs machine‑readable test output and clear failure modes. |
| **Security Lead / SOC Engineer** | Guarantee policy enforcement, auditing, and incident response. | Must trust that filters catch abuses and generate logs. |
| **Compliance Officer** | Demonstrate adherence to privacy and content regulations (GDPR, COPPA, etc.). | Requires evidence of controls and test results. |
| **DevOps Engineer** | Deploy and manage guardrails with minimal downtime and maximum reliability. | Needs hot reload, validation, and graceful degradation. |

---

## 3 User Stories

1. **Developer**: "I configure a YAML file to block non‑English inputs and URL links, then run `python3 stinger.py --scenario customer_service --debug` and see violations flagged."  
2. **Security Lead**: "I view a daily report showing 98 % of toxic prompts were blocked; no legitimate requests were dropped."  
3. **AI Agent**: "I execute the test suite, detect a false negative in the jailbreak filter, update the threshold, rerun, and all tests pass."  
4. **Operations Engineer**: "When the OpenAI moderation API is down, the system automatically falls back to rule-based filters and continues operating."  
5. **DevOps Engineer**: "I can deploy configuration changes with validation and automatic rollback if the new config causes issues."
6. **Developer**: "I can modify keyword lists in external files and see changes applied immediately with hot reload."
7. **Security Engineer**: "I can create compound filters that detect sophisticated attack patterns using weighted scoring."
8. **Compliance Officer**: "I can validate that PII detection uses multiple weighted rules to reduce false positives."

---

## 4 Functional Requirements

| ID | Requirement |
|----|-------------|
| FR‑1 | Support chained input and output filter pipelines. |
| FR‑2 | Provide built‑in rule‑based filters: regex blacklist, language check, length limit, URL/file‑type block. |
| FR‑3 | Provide pluggable classifier filters (OpenAI Moderation, Perspective API, Google Prompt Armor, Anthropic, local models). |
| FR‑4 | YAML/JSON configuration with per‑filter parameters and action (`allow`, `block`, `warn`, `modify`, `log_only`). |
| FR‑5 | Test framework that loads labeled examples, runs filters, and produces JSON results with pass/fail and metrics. |
| FR‑6 | Structured logging of filter decisions and latency. |
| FR‑7 | Fail‑closed or configurable soft‑fail behaviour on filter errors/timeouts. |
| FR‑8 | CLI and Python SDK for integration into apps and CI pipelines. |
| FR‑9 | **Error Handling**: Configurable error handling per filter (`block`, `allow`, `skip` on error). |
| FR‑10 | **Circuit Breakers**: Automatic circuit breaker pattern for external API calls with configurable thresholds. |
| FR‑11 | **Graceful Degradation**: System continues operating with available filters when external services fail. |
| FR‑12 | **Configuration Validation**: Multi-level validation (syntax, schema, semantic, runtime) with clear error messages. |
| FR‑13 | **Hot Reload**: Configuration changes applied without service restart. |
| FR‑14 | **Configuration Testing**: Pre-deployment validation of configuration changes against test corpora. |
| FR‑15 | **Health Monitoring**: Real-time health status reporting for all filters and external dependencies. |
| FR‑16 | **Unified CLI**: Single entry point (`stinger.py`) for running all scenarios, tests, and debugging. |
| FR‑17 | **Keyword List Filters**: Support for external keyword files with fallback to inline keywords. |
| FR‑18 | **Schema Validation**: JSON schema validation for all configuration files with detailed error reporting. |
| FR‑19 | **Compound Scoring Filters**: Multi-rule weighted scoring system with configurable thresholds (0-100). |
| FR‑20 | **Debug Mode**: Detailed filter-by-filter processing output for troubleshooting. |
| FR‑21 | **Environment Variable Overrides**: Support for custom config and test data via environment variables. |

---

## 5 Non‑Functional Requirements

| Category | Target |
|----------|--------|
| **Performance** | ≤ 200 ms added latency for a 5‑filter stack. |
| **Scalability** | Handle 100 req/s with linear scaling. |
| **Reliability** | 99.9 % uptime; filters must degrade gracefully. |
| **Security** | All external API keys stored securely; no sensitive data logged in plaintext. |
| **Observability** | Export Prometheus metrics and structured logs. |
| **Maintainability** | Filters and configs isolated; coding agents can update without human help. |
| **Error Resilience** | System continues operating when ≤50% of external APIs are unavailable. |
| **Configuration Safety** | Zero-downtime configuration deployments with automatic rollback on validation failures. |
| **Recovery Time** | Circuit breakers recover automatically within 5 minutes of external service restoration. |
| **Developer Experience** | Hot reload config changes within 1 second; debug output available for all filters. |
| **Configuration Validation** | Schema validation completes within 100ms; detailed error messages for all validation failures. |

---

## 6 Success Metrics

* ≥ 95 % true‑positive rate on malicious test corpora.  
* ≤ 2 % false‑positive rate on benign corpora.  
* 100 % of test suites pass on every CI run.  
* Latency delta ≤ 200 ms @ P95 with full filter stack.
* **Error Handling**: ≤ 1% of requests fail due to filter errors (excluding intentional blocks).
* **Configuration Safety**: 100% of configuration changes pass pre-deployment validation.
* **Developer Experience**: ≤ 5 minutes to run first scenario with debug output.
* **Hot Reload**: ≤ 1 second to detect and apply configuration changes.
* **Compound Filter Accuracy**: ≥ 90% accuracy on weighted scoring decisions.

---

## 7 Filter Types & Capabilities

### 7.1 Simple Filters
- **regex_filter**: Pattern matching with configurable actions
- **keyword_block**: Single keyword blocking
- **length_filter**: Content length validation
- **url_filter**: URL domain blocking

### 7.2 Advanced Filters
- **keyword_list_filter**: Multiple keywords with external file support
- **compound_filter**: Multi-rule weighted scoring (0-100)
- **prompt_injection_filter**: Specialized for prompt injection detection
- **pii_detection_filter**: Specialized for personal information detection

### 7.3 Scoring System
- **Binary Scoring**: Simple filters (pass/fail)
- **Weighted Scoring**: Compound filters (0-100 with configurable thresholds)
- **Fuzzy Logic**: Support for partial certainty and graduated responses
- **Contextual Scoring**: Same pattern scored differently based on context

---

## 8 Out‑of‑Scope (v1)

* No GUI for policy management.  
* No per‑customer tenancy or billing.  
* No model‑specific optimisation (framework is model‑agnostic).
* No AI-based scoring (planned for future versions).

---

## 9 Dependencies & Assumptions

* Access to Google Safe Browsing, Perspective, and OpenAI moderation endpoints.  
* JSONL test data can be shared internally (no licensing blockers).  
* Agents (Cursor, Claude Code) can read/write repository files.
* File system access for keyword list files and hot reload functionality.

---

## 10 Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| External moderation API latency | Add async calls, caching, and fallback thresholds. |
| False positives blocking valid traffic | Maintain balanced benign corpora and regression tests. |
| API quota exhaustion | Implement rate limiting and exponential backoff with circuit‑breaker. |
| Filter mis‑configuration | Provide schema validation and default safe configs. |
| **External API failures** | **Circuit breakers, graceful degradation, and health monitoring.** |
| **Configuration errors** | **Multi-level validation, testing framework, and automatic rollback.** |
| **System overload** | **Resource limits, request queuing, and priority-based filtering.** |
| **Complex filter logic** | **Comprehensive testing, debug output, and gradual rollout.** |
| **Hot reload race conditions** | **Thread-safe configuration loading and atomic updates.** |

---

## 11 Glossary

* **Filter** – A unit that inspects content and returns an action.  
* **Classifier** – An AI model (local or SaaS) that labels content (toxicity, PII, etc.).  
* **Pipeline** – Ordered list of filters executed on input or output.
* **Circuit Breaker** – Pattern to prevent cascading failures by temporarily disabling failing external services.
* **Graceful Degradation** – System continues operating with reduced functionality when some components fail.
* **Compound Filter** – Multi-rule filter using weighted scoring to determine actions.
* **Hot Reload** – Ability to apply configuration changes without restarting the service.
* **Schema Validation** – Validation of configuration files against predefined schemas.
* **Weighted Scoring** – Scoring system where different rules contribute different weights to the final decision.

## Compound Filter Additive Certainty System

- Each rule in a compound filter has a certainty value (0-100).
- When content matches a rule, its certainty is added to the total certainty (capped at 100).
- Thresholds (allow/warn/block) are based on the total certainty.
- This replaces the previous weighted/normalized scoring system.

### Migration Note
If you previously used 'weight' for rules, replace it with 'certainty' (1-100). The system is now additive, not normalized.
