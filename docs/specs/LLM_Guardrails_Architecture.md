# LLM Guardrails Framework – High‑Level Architecture

## 1 Component Diagram (Logical)

```
 +----------------------+        +--------------------------+
 |  Client / Agent      |        | Configuration Repository |
 +----------+-----------+        +-----------+--------------+
            |                                 ^
            v                                 |
 +----------+-----------+            +--------+---------+
 |  Conversation        |            |  Config Loader   |
 |  Management          |            +---+--------------+
 +----------+-----------+                |
            |                            |
            v                            v
 +----------+-----------+        +-------+--------+
 |  Input Guardrails    |<--------+  Config Loader   |
 |  Pipeline            |        +---+--------------+
 +----------+-----------+            |
            |                        |
            v                        v
 +----------+-----------+    +-------+--------+
 | Underlying LLM / API |    | Audit Logging  |
 | (OpenAI, Anthropic)  |    | & Compliance   |
 +----------+-----------+    +-------+--------+
            |                        ^
            v                        |
 +----------+-----------+            |
 | Output Guardrails    |------------+
 | Pipeline             |
 +----------+-----------+
            |
            v
 +----------+-----------+
 |   Final Response     |
 +----------------------+
```

*Both guardrail pipelines share the same **Filter Plugin** mechanism and **Audit Logging** system.*

## 2 Core Modules

| Module | Responsibility |
|--------|----------------|
| **Config Loader** | Parse YAML/JSON configs, validate schema, expose runtime settings. |
| **FilterPipeline** | Orchestrate filter execution, enforce order, aggregate results. |
| **Conversation Management** | Handle multi-turn conversations, context tracking, rate limiting. |
| **BaseGuardrail** | Abstract class implementing `run(content) → FilterResult`. |
| **Rule‑Based Filters** | Regex, blacklist, language, length, URL/file‑type blocking. |
| **Keyword List Filter** | Load keywords from files or inline configs with case sensitivity options. |
| **Compound Scoring Filter** | Multi-rule weighted scoring with configurable thresholds. |
| **Classifier Filters** | Wrap external or local AI services (PII, toxicity, jailbreak). |
| **Result Handler** | Apply actions (`block`, `warn`, `modify`, etc.) and assemble response. |
| **Audit Logging** | Structured logging for compliance and security audit trails. |
| **Unified CLI** | Single entry point for running scenarios, tests, and debugging. |

## 3 Filter Types & Scoring System

### 3.1 Filter Categories

| Category | Examples | Scoring Method |
|----------|----------|----------------|
| **Simple Filters** | regex_filter, keyword_block, length_filter | Binary (pass/fail) |
| **List-Based Filters** | keyword_list_filter | Binary with external file support |
| **Compound Filters** | compound_filter, prompt_injection_filter | Weighted scoring (0-100) |
| **AI-Based Filters** | ai_scorer (future) | Confidence scoring (0-100) |

### 3.2 Compound Scoring Architecture

```
Compound Filter
├── Rule Engine
│   ├── Regex Rules (weighted patterns)
│   ├── Keyword Rules (weighted lists)
│   ├── Combination Rules (AND/OR logic)
│   └── Contextual Rules (context-dependent scoring)
├── Scoring Engine
│   ├── Weight Calculation
│   ├── Threshold Management
│   └── Fuzzy Decision Logic
└── Result Aggregation
    ├── Matched Rules Tracking
    ├── Score Explanation
    └── Action Determination
```

### 3.3 Scoring Thresholds

```yaml
thresholds:
  allow: 0-20     # Low risk - allow with logging
  warn: 21-60     # Medium risk - warn user
  block: 61-100   # High risk - block content
```

## 4 Conversation Management & Audit Logging

### 4.1 Conversation Infrastructure

The framework provides comprehensive conversation management with:

- **Conversation Types**: Factory methods for human_ai, bot_to_bot, agent_to_agent, human_to_human
- **Turn Management**: Structured turns with prompt/response/speaker/listener
- **Context Tracking**: Automatic conversation history passing to all guardrails
- **Rate Limiting**: Per-conversation rate limiting with minute/hour limits
- **Serialization**: Full conversation serialization (to_dict/from_dict) for persistence

### 4.2 Audit Logging System

The audit logging system provides:

- **Structured Logging**: Complete record of all guardrail decisions with full context
- **Async Performance**: Buffered logging with <10ms additional latency
- **PII Redaction**: Automatic redaction of sensitive information using configurable patterns
- **Export Utility**: Simple log export tool for compliance reporting
- **Reliability**: Graceful failure handling - system continues operating during logging failures
- **Developer Usability**: Simple configuration and human-readable log format

### 4.3 Conversation-Aware Filters

Filters can leverage conversation context for enhanced detection:

- **Multi-turn Pattern Detection**: Trust-building, gradual escalation, context manipulation
- **Context Preparation**: Recent, suspicious, mixed strategies for context preparation
- **Long Conversation Management**: Token limits and truncation for long conversations
- **Enhanced AI Analysis**: AI analysis prompts with conversation history

## 5 Error Handling & Degradation Strategy

### 5.1 Filter-Level Error Handling

| Error Type | Default Behavior | Configuration |
|------------|------------------|---------------|
| **Filter Crash** | Fail-closed (block request) | `on_error: block|allow|skip` |
| **Filter Timeout** | Fail-closed (block request) | `timeout_ms: 5000` |
| **Invalid Input** | Log warning, continue | `invalid_input: warn|block|skip` |
| **Resource Exhaustion** | Fail-closed (block request) | `resource_limit: block|allow` |
| **Schema Validation** | Fail-closed (block request) | `schema_validation: strict|warn|off` |

### 5.2 External API Failure Handling

| Service | Circuit Breaker | Fallback Strategy | Retry Logic |
|---------|----------------|-------------------|-------------|
| **OpenAI Moderation** | 5 failures → 30s open | Skip filter, log warning | 3 attempts, exponential backoff |
| **Perspective API** | 3 failures → 60s open | Use cached results if available | 2 attempts, 1s delay |
| **Google Safe Browsing** | 10 failures → 5min open | Allow request, log alert | 1 attempt, no retry |
| **Local Models** | N/A (local) | Use rule-based fallback | N/A |

### 5.3 Pipeline Degradation Modes

| Mode | Trigger | Behavior | Recovery |
|------|---------|----------|----------|
| **Graceful Degradation** | External API unavailable | Skip failed filters, continue with available | Automatic when APIs return |
| **Fail-Safe Mode** | Critical filter failure | Block all requests, log emergency | Manual intervention required |
| **Bypass Mode** | Emergency override | Allow all requests, log everything | Manual intervention required |

### 5.4 Error Recovery & Monitoring

- **Health Checks**: Each filter reports health status every 30s
- **Alert Thresholds**: Alert when >10% of requests hit circuit breakers
- **Auto-Recovery**: Circuit breakers automatically close after timeout
- **Manual Override**: Emergency bypass switches for critical situations

## 6 Configuration Management & Validation

### 6.1 Configuration Schema

```yaml
# Schema version and validation
version: "1.0"
schema_validation: strict  # strict|warn|off

# Environment-specific overrides
environments:
  development:
    log_level: DEBUG
    fail_closed: false
  staging:
    log_level: INFO
    fail_closed: true
  production:
    log_level: WARN
    fail_closed: true

# Pipeline configuration
pipelines:
  input:
    - name: "language_check"
      type: "rule_based"
      enabled: true
      on_error: "block"
      timeout_ms: 1000
    - name: "keyword_list"
      type: "keyword_list"
      enabled: true
      keywords: ["blocked_word1", "blocked_word2"]
      keyword_files: ["configs/keyword_lists/toxic_language.txt"]
      case_sensitive: false
      on_error: "block"
    - name: "pii_detection"
      type: "compound_filter"
      enabled: true
      thresholds:
        allow: 0-20
        warn: 21-60
        block: 61-100
      rules:
        - name: ssn_pattern
          type: regex
          pattern: "\\b\\d{3}-\\d{2}-\\d{4}\\b"
          certainty: 80
        - name: phone_pattern
          type: regex
          pattern: "\\b\\d{3}-\\d{3}-\\d{4}\\b"
          certainty: 50
      on_error: "block"
    - name: "toxicity_filter"
      type: "classifier"
      provider: "openai"
      enabled: true
      on_error: "skip"
      timeout_ms: 5000
      circuit_breaker:
        failure_threshold: 5
        recovery_timeout: 30
```

### 6.2 Configuration Validation

| Validation Level | Checks | Action |
|------------------|--------|--------|
| **Syntax** | YAML/JSON format | Reject invalid configs |
| **Schema** | Required fields, data types | Reject malformed configs |
| **Semantic** | Filter dependencies, resource limits | Warn on suspicious configs |
| **Runtime** | Filter availability, API connectivity | Log warnings, continue |

### 6.3 Configuration Deployment

- **Version Control**: All configs stored in Git with change history
- **Rollback Capability**: Automatic rollback on validation failures
- **Environment Isolation**: Separate configs for dev/staging/prod

### 6.4 Configuration Testing

```yaml
# Test configuration changes before deployment
config_tests:
  - name: "validate_filter_chain"
    type: "dependency_check"
    description: "Ensure filter dependencies are met"
  
  - name: "test_performance_impact"
    type: "load_test"
    description: "Verify config doesn't exceed latency targets"
    
  - name: "regression_test"
    type: "corpus_test"
    description: "Ensure no new false positives/negatives"
```

## 7 Testing Sub‑system

| Component | Detail |
|-----------|--------|
| **Unified Test Runner** | CLI (`stinger.py`) to execute scenarios, collect results, produce reports. |
| **Test Corpus** | Labeled JSONL files stored under `/tests/**`. |
| **Suite Config** | YAML: list of corpora, filters, expected pass criteria. |
| **Scenario Runners** | Individual test runners for specific use cases (customer service, medical bot). |
| **Autonomous Repair Hooks** | Scripts (`patch_config.py`) to let coding agents adjust YAML and rerun. |
| **CI Integration** | GitHub Actions job: run suites on PR, fail build on regression. |

## 8 Developer Experience Features

### 8.1 Unified CLI Interface

```bash
# Run all scenarios
python3 stinger.py --all

# Run specific scenario with debug
python3 stinger.py --scenario customer_service --debug

# Custom config and test data
python3 stinger.py --scenario customer_service --config custom.yaml --test-data custom.jsonl
```

### 8.2 Debug & Observability

- **Filter-by-filter processing** with `--debug` flag
- **Detailed error messages** with filter names and types
- **Schema validation errors** with clear field-level feedback

### 8.3 Configuration Management

- **External keyword files** for easier maintenance
- **Schema validation** with comprehensive error reporting
- **Environment variable overrides** for flexible deployment

## 9 Runtime Deployment Views

### 9.1 Local Development
* Developer installs package, runs `python3 stinger.py --scenario customer_service --debug`.  
* Agents can run `python3 stinger.py --all` for comprehensive testing.

### 9.2 Staging / Production
* Deployed as a sidecar micro‑service or library inside the API server.  
* Uses async calls to external moderation endpoints with timeouts.  
* Logs shipped to central SIEM (Elastic, Splunk, etc.).  
* Metrics scraped by Prometheus and visualised in Grafana.

## 10 Data Stores

* **Config repo** – Version‑controlled YAML/JSON.  
* **Keyword files** – Text files for keyword lists, versioned alongside code.
* **Test datasets** – JSONL, versioned alongside code.  
* **Audit logs** – Structured, time‑series; retention policy 90 days.  
* **Metrics store** – Prometheus TSDB.

## 11 Extensibility Points

1. **Filter Plugins** – Drop‑in Python modules under `filters/`.  
2. **Compound Filter Rules** – Extensible rule types (regex, keyword, combination, AI).
3. **Classifier Adapters** – Abstract provider interface (`provider=openai|google|custom`).  
4. **Action Hooks** – Custom logic on `block` or `warn` (e.g., revive request, notify Slack).  

## 12 Security Considerations

* All secrets in environment variables or secret manager.  
* Default behaviour is **fail‑closed** for critical filters.  
* No raw prompts logged; redact PII in logs.
* Schema validation prevents malicious config injection.

## Compound Filter Additive Certainty System

- Each rule in a compound filter has a certainty value (0-100).
- When content matches a rule, its certainty is added to the total certainty (capped at 100).
- Thresholds (allow/warn/block) are based on the total certainty.
- This replaces the previous weighted/normalized scoring system.

### Migration Note
If you previously used 'weight' for rules, replace it with 'certainty' (1-100). The system is now additive, not normalized.

