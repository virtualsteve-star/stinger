# LLM Guardrails Framework – High‑Level Architecture

## 1 Component Diagram (Logical)

```
 +----------------------+        +--------------------------+
 |  Client / Agent      |        | Configuration Repository |
 +----------+-----------+        +-----------+--------------+
            |                                 ^
            v                                 |
 +----------+-----------+            +--------+---------+
 |  Input Guardrails    |<-----------+  Config Loader   |
 |  Pipeline            |            +---+--------------+
 +----------+-----------+                |
            |                            |
            v                            v
 +----------+-----------+        +-------+--------+
 | Underlying LLM / API |        | Logging /      |
 | (OpenAI, Anthropic)  |        | Observability  |
 +----------+-----------+        +-------+--------+
            |                            ^
            v                            |
 +----------+-----------+                |
 | Output Guardrails    |----------------+
 | Pipeline             |
 +----------+-----------+
            |
            v
 +----------+-----------+
 |   Final Response     |
 +----------------------+
```

*Both guardrail pipelines share the same **Filter Plugin** mechanism.*

## 2 Core Modules

| Module | Responsibility |
|--------|----------------|
| **Config Loader** | Parse YAML/JSON configs, validate schema, expose runtime settings. |
| **FilterPipeline** | Orchestrate filter execution, enforce order, aggregate results. |
| **BaseFilter** | Abstract class implementing `run(content) → FilterResult`. |
| **Rule‑Based Filters** | Regex, blacklist, language, length, URL/file‑type blocking. |
| **Classifier Filters** | Wrap external or local AI services (PII, toxicity, jailbreak). |
| **Result Handler** | Apply actions (`block`, `warn`, `modify`, etc.) and assemble response. |
| **Logging / Metrics** | Emit structured logs and Prometheus counters/timers. |

## 3 Error Handling & Degradation Strategy

### 3.1 Filter-Level Error Handling

| Error Type | Default Behavior | Configuration |
|------------|------------------|---------------|
| **Filter Crash** | Fail-closed (block request) | `on_error: block|allow|skip` |
| **Filter Timeout** | Fail-closed (block request) | `timeout_ms: 5000` |
| **Invalid Input** | Log warning, continue | `invalid_input: warn|block|skip` |
| **Resource Exhaustion** | Fail-closed (block request) | `resource_limit: block|allow` |

### 3.2 External API Failure Handling

| Service | Circuit Breaker | Fallback Strategy | Retry Logic |
|---------|----------------|-------------------|-------------|
| **OpenAI Moderation** | 5 failures → 30s open | Skip filter, log warning | 3 attempts, exponential backoff |
| **Perspective API** | 3 failures → 60s open | Use cached results if available | 2 attempts, 1s delay |
| **Google Safe Browsing** | 10 failures → 5min open | Allow request, log alert | 1 attempt, no retry |
| **Local Models** | N/A (local) | Use rule-based fallback | N/A |

### 3.3 Pipeline Degradation Modes

| Mode | Trigger | Behavior | Recovery |
|------|---------|----------|----------|
| **Graceful Degradation** | External API unavailable | Skip failed filters, continue with available | Automatic when APIs return |
| **Fail-Safe Mode** | Critical filter failure | Block all requests, log emergency | Manual intervention required |
| **Bypass Mode** | Emergency override | Allow all requests, log everything | Manual intervention required |

### 3.4 Error Recovery & Monitoring

- **Health Checks**: Each filter reports health status every 30s
- **Alert Thresholds**: Alert when >10% of requests hit circuit breakers
- **Auto-Recovery**: Circuit breakers automatically close after timeout
- **Manual Override**: Emergency bypass switches for critical situations

## 4 Configuration Management & Validation

### 4.1 Configuration Schema

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

### 4.2 Configuration Validation

| Validation Level | Checks | Action |
|------------------|--------|--------|
| **Syntax** | YAML/JSON format | Reject invalid configs |
| **Schema** | Required fields, data types | Reject malformed configs |
| **Semantic** | Filter dependencies, resource limits | Warn on suspicious configs |
| **Runtime** | Filter availability, API connectivity | Log warnings, continue |

### 4.3 Configuration Deployment

- **Version Control**: All configs stored in Git with change history
- **Rollback Capability**: Automatic rollback on validation failures
- **Hot Reload**: Config changes applied without service restart
- **Environment Isolation**: Separate configs for dev/staging/prod

### 4.4 Configuration Testing

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

## 5 Testing Sub‑system

| Component | Detail |
|-----------|--------|
| **Test Runner** | CLI/SDK to execute suites, collect results, produce JSON + Markdown reports. |
| **Test Corpus** | Labeled JSONL files stored under `/tests/**`. |
| **Suite Config** | YAML: list of corpora, filters, expected pass criteria. |
| **Autonomous Repair Hooks** | Scripts (`patch_config.py`) to let coding agents adjust YAML and rerun. |
| **CI Integration** | GitHub Actions job: run suites on PR, fail build on regression. |

## 6 Runtime Deployment Views

### 6.1 Local Development
* Developer installs package, runs `guardrails apply` on sample inputs.  
* Agents can run `python test_runner.py tests/full_suite.yaml`.

### 6.2 Staging / Production
* Deployed as a sidecar micro‑service or library inside the API server.  
* Uses async calls to external moderation endpoints with timeouts.  
* Logs shipped to central SIEM (Elastic, Splunk, etc.).  
* Metrics scraped by Prometheus and visualised in Grafana.

## 7 Data Stores

* **Config repo** – Version‑controlled YAML/JSON.  
* **Test datasets** – JSONL, versioned alongside code.  
* **Audit logs** – Structured, time‑series; retention policy 90 days.  
* **Metrics store** – Prometheus TSDB.

## 8 Extensibility Points

1. **Filter Plugins** – Drop‑in Python modules under `filters/`.  
2. **Classifier Adapters** – Abstract provider interface (`provider=openai|google|custom`).  
3. **Action Hooks** – Custom logic on `block` or `warn` (e.g., revive request, notify Slack).  

## 9 Security Considerations

* All secrets in environment variables or secret manager.  
* Default behaviour is **fail‑closed** for critical filters.  
* No raw prompts logged; redact PII in logs.

