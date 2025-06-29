# Stinger Examples

This directory contains executable examples that demonstrate how to use the Stinger LLM Guardrails Framework.

## 📁 Directory Structure

```
examples/
├── README.md                           # This file
├── simple_usage.py                     # Quick start example (existing)
├── getting_started/                    # Step-by-step learning series
│   ├── 01_basic_installation.py       # Basic installation and first guardrail
│   ├── 02_simple_filter.py            # Using different presets
│   ├── 03_global_rate_limiting.py     # Global rate limiting features
│   ├── 04_conversation_api.py         # Conversation API
│   ├── 05_conversation_rate_limiting.py # Per-conversation rate limiting
│   ├── 06_health_monitoring.py        # Health monitoring
│   ├── 07_cli_and_yaml_config.py      # CLI usage and YAML configuration
│   ├── 08_security_audit_trail.py     # Security audit trail and compliance logging
│   ├── 09_troubleshooting_and_testing.py # Troubleshooting and testing
│   └── configs/                        # Configuration files for examples
├── extensibility/                      # Custom filter development
│   ├── custom_filter_template.py      # Basic filter template
│   ├── custom_regex_filter.py         # Regex-based filter example
│   ├── custom_ai_filter.py            # AI-based filter example
│   └── configs/                        # Custom filter configs
└── api/                               # API usage patterns
    ├── basic_usage.py                 # Basic API usage
    ├── advanced_usage.py              # Advanced API patterns
    └── error_handling.py              # Error handling examples
```

## 🚀 Getting Started

### Prerequisites

1. **Install Stinger**: Follow the main Getting Started guide
2. **Set up API keys**: Run `python manage_api_keys.py add openai`
3. **Install dependencies**: `pip install -r requirements.txt`

### Running Examples

Each example is self-contained and can be run directly:

```bash
# Basic installation example
python examples/getting_started/01_basic_installation.py

# Simple filter example
python examples/getting_started/02_simple_filter.py

# Global rate limiting example
python examples/getting_started/03_global_rate_limiting.py

# Conversation API example
python examples/getting_started/04_conversation_api.py

# Per-conversation rate limiting example
python examples/getting_started/05_conversation_rate_limiting.py

# Health monitoring example
python examples/getting_started/06_health_monitoring.py

# CLI and YAML configuration example
python examples/getting_started/07_cli_and_yaml_config.py

# Security audit trail example
python examples/getting_started/08_security_audit_trail.py

# Troubleshooting and testing example
python examples/getting_started/09_troubleshooting_and_testing.py
```

### Learning Path

1. **Start with `01_basic_installation.py`** - Learn basic setup
2. **Continue with `02_simple_filter.py`** - Understand different presets
3. **Try `03_global_rate_limiting.py`** - Learn global rate limiting
4. **Explore `04_conversation_api.py`** - Learn conversation features
5. **Try `05_conversation_rate_limiting.py`** - Per-conversation rate limits
6. **Monitor with `06_health_monitoring.py`** - Monitor system health
7. **Configure with `07_cli_and_yaml_config.py`** - CLI and configuration
8. **Secure with `08_security_audit_trail.py`** - Security audit trail and compliance
9. **Troubleshoot with `09_troubleshooting_and_testing.py`** - Testing and debugging

## 📋 Example Features

### Getting Started Series
- **Minimal boilerplate** - Focus on essential concepts
- **Progressive complexity** - Build up step by step
- **Real test cases** - Practical examples
- **Clear output** - Shows exactly what happens

### Extensibility Examples
- **Custom filter templates** - Learn to create your own filters
- **Regex-based filters** - Pattern matching examples
- **AI-based filters** - OpenAI integration examples
- **Testing custom filters** - How to test your filters

### API Examples
- **Basic usage patterns** - Common API calls
- **Advanced patterns** - Complex scenarios
- **Error handling** - Graceful error management
- **Integration examples** - Real-world usage

## 🔧 Configuration Files

Each example may have corresponding configuration files in the `configs/` subdirectories:

- **YAML configurations** - Pipeline and filter settings
- **Test data** - Sample inputs and expected outputs
- **Custom settings** - Example-specific configurations

## 🧪 Testing Examples

All examples are designed to be testable:

```bash
# Run all examples
for example in examples/getting_started/*.py; do
    echo "Running $example..."
    python "$example"
    echo "---"
done
```

## 📚 Documentation

These examples correspond to sections in the main documentation:

- **Getting Started Guide**: `docs/GETTING_STARTED.md`
- **API Reference**: `docs/API_REFERENCE.md`
- **Extensibility Guide**: `docs/EXTENSIBILITY_GUIDE.md`

## 🎯 Design Principles

All examples follow these principles:

1. **Tight and focused** - Minimal boilerplate, clear purpose
2. **Self-contained** - Run independently without setup
3. **Real-world** - Practical use cases, not contrived examples
4. **Progressive** - Build complexity step by step
5. **Testable** - Can be automated and validated

## 🔄 Migration from simple_usage.py

The existing `simple_usage.py` file demonstrates excellent code quality and will be kept until the new examples adequately cover all its functionality. Once the new series provides the same learning value, `simple_usage.py` will be removed to avoid duplication.

## 🆘 Troubleshooting

If examples don't work:

1. **Check installation**: Ensure Stinger is properly installed
2. **Verify API keys**: Run `python manage_api_keys.py list`
3. **Check health**: Run `python -m stinger.cli health`
4. **Review logs**: Look for error messages in output

## 🤝 Contributing

When adding new examples:

1. **Follow the tight, focused approach** - Keep examples concise
2. **Include real test cases** - Use practical examples
3. **Add clear documentation** - Explain what the example demonstrates
4. **Test thoroughly** - Ensure examples work in clean environments
5. **Update this README** - Keep the documentation current 