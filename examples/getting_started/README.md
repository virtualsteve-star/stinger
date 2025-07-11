# Getting Started Examples

Progressive examples to learn Stinger guardrails step by step.

## Examples

1. **00_verify_installation.py** - Verify your Stinger installation
2. **01_basic_installation.py** - Basic setup and first guardrail
3. **02_simple_guardrail.py** - Simple guardrail usage
4. **03_global_rate_limiting.py** - Rate limiting features
5. **04_conversation_api.py** - Conversation tracking
6. **05_conversation_rate_limiting.py** - Per-conversation limits
7. **06_health_monitoring.py** - System health checks
8. **07_cli_and_yaml_config.py** - CLI tools and configuration
9. **08_security_audit_trail.py** - Security and audit logging
10. **09_troubleshooting_and_testing.py** - Debugging and testing
11. **11_ai_powered_filters.py** - AI-based guardrails
12. **12_rest_api_usage.py** - 🆕 **Using Stinger via REST API**

## Running the Examples

Most examples use Stinger directly as a Python library:

```bash
python 01_basic_installation.py
```

### For the REST API Example (12)

The REST API example requires starting a server first:

```bash
# Install API dependencies
pip install stinger-guardrails-alpha[api]

# Terminal 1: Start the API server
stinger-api

# Terminal 2: Run the example
python 12_rest_api_usage.py
```

## Prerequisites

- Python 3.8+
- For AI examples: `export OPENAI_API_KEY="your-key"`
- For API example: `pip install stinger-guardrails-alpha[api]`

## configs/

This directory contains example YAML configuration files used by some examples.