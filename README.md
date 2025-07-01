# 🚀 Stinger - AI Guardrails Framework

A powerful, easy-to-use Python framework for safeguarding LLM applications with comprehensive content filtering and moderation capabilities.

> **Note:** PyPI installation (`pip install stinger`) is coming soon! For now, install from source (see below).

## ✨ Features

- **🛡️ Comprehensive Guardrails**: Toxicity detection, PII protection, code generation prevention, and more
- **🔒 Security Audit Trail**: Complete logging of all security decisions for compliance and forensics
- **🎯 Simple API**: Get started in 3 lines of code
- **⚡ High Performance**: Async-ready with synchronous convenience wrapper
- **🔧 Configurable**: YAML-based configuration with runtime updates
- **🧪 Production Ready**: Comprehensive testing and error handling
- **📚 Well Documented**: Complete API reference and examples

## 🚀 Quick Start

### Installation (from source)

```bash
pip install .
```

### Basic Usage

```python
from stinger import GuardrailPipeline

# Create a pipeline from configuration
pipeline = GuardrailPipeline("config.yaml")

# Check input content
result = pipeline.check_input("Hello, world!")
if result['blocked']:
    print(f"Input blocked: {result['reasons']}")

# Check output content
result = pipeline.check_output("Here's your response...")
if result['blocked']:
    print(f"Output blocked: {result['reasons']}")
```

## 🖥️ Command Line Interface (CLI)

After installing Stinger, you can use the CLI:

```sh
stinger demo
stinger check-prompt "My SSN is 123-45-6789."
stinger check-response "Here is your password: hunter2"
```

## 🛡️ Available Guardrails

### Input Guardrails
- **Toxicity Detection**: Identify hate speech, harassment, threats
- **PII Detection**: Protect credit cards, SSNs, emails, phone numbers
- **Prompt Injection**: Prevent malicious prompt manipulation
- **Keyword Blocking**: Block specific words or phrases
- **Length Filtering**: Control input/output length

### Output Guardrails
- **Code Generation**: Prevent unauthorized code generation
- **Content Moderation**: AI-powered content screening
- **URL Filtering**: Block malicious or unwanted URLs
- **Toxicity Detection**: Screen generated responses

## 🔒 Security Audit Trail

Stinger provides comprehensive security audit logging for compliance and forensic analysis:

### Zero-Config Audit Trail
```python
from stinger import audit

# Enable with smart defaults (just works!)
audit.enable()

# Or specify destination
audit.enable("./logs/security.log")

# With PII redaction for compliance
audit.enable("./logs/audit.log", redact_pii=True)
```

### Complete Security Tracking
- **User Prompts**: All user inputs logged with attribution
- **LLM Responses**: All AI responses tracked with context
- **Guardrail Decisions**: Every security decision with full reasoning
- **Conversation Flow**: Complete conversation reconstruction
- **User Attribution**: IP, session, user ID tracking for forensics

### Compliance Ready
- **GDPR Compliance**: PII redaction while preserving audit value
- **HIPAA Ready**: Healthcare data protection capabilities
- **Enterprise Audit**: Complete audit trail for security reviews
- **Forensic Analysis**: Reconstruct security incidents completely
- **Async Performance**: Zero-impact logging with background processing

### Audit Trail Features
- **Smart Environment Detection**: Auto-configures for dev/prod/docker
- **Async Buffering**: Background processing with <10ms latency impact
- **Query Tools**: Easy audit trail searching and analysis
- **Export Capabilities**: CSV/JSON export for compliance reporting
- **Cannot be disabled in production**: Ensures audit trail integrity

## 📋 Configuration

Stinger uses YAML configuration files:

```yaml
version: "1.0"

pipeline:
  input:
    - name: toxicity_check
      type: simple_toxicity_detection
      enabled: true
      confidence_threshold: 0.7
      categories: [hate_speech, harassment, threats]
    
    - name: pii_check
      type: simple_pii_detection
      enabled: true
      confidence_threshold: 0.8
      categories: [credit_card, ssn, email]
  
  output:
    - name: code_generation_check
      type: simple_code_generation
      enabled: true
      confidence_threshold: 0.6
      categories: [programming_keywords, code_blocks]
```

## 🎯 API Reference

### GuardrailPipeline

The main class for using Stinger guardrails.

```python
# Initialize
pipeline = GuardrailPipeline("config.yaml")

# Check content
result = pipeline.check_input(content)
result = pipeline.check_output(content)

# Get status
status = pipeline.get_guardrail_status()

# Dynamic configuration
pipeline.enable_guardrail("toxicity_check")
pipeline.disable_guardrail("pii_check")
pipeline.update_guardrail_config("toxicity_check", {"confidence_threshold": 0.9})
```

### Result Format

```python
{
    'blocked': bool,           # Whether content was blocked
    'warnings': List[str],     # List of warning messages
    'reasons': List[str],      # List of blocking reasons
    'details': Dict[str, Any], # Detailed results from each guardrail
    'pipeline_type': str       # Type of pipeline ("input" or "output")
}
```

### Audit Trail API

```python
from stinger import audit

# Enable audit trail
audit.enable("./logs/audit.log")

# Query audit trail
records = audit.query(
    conversation_id="conv_123",
    user_id="user_456",
    last_hour=True
)

# Export for compliance
audit.export_csv("./logs/audit.log", "compliance_report.csv")

# Get performance stats
stats = audit.get_stats()
print(f"Queued: {stats['queued']}, Written: {stats['written']}")
```

## 📖 Examples

### Basic Usage
```python
from stinger import GuardrailPipeline

pipeline = GuardrailPipeline("config.yaml")

# Simple content checking
result = pipeline.check_input("User input here")
if result['blocked']:
    print(f"Blocked: {result['reasons']}")
elif result['warnings']:
    print(f"Warnings: {result['warnings']}")
else:
    print("Content approved")
```

### Advanced Usage
```python
from stinger import GuardrailPipeline, audit

# Enable security audit trail
audit.enable("./logs/audit.log", redact_pii=True)

# Initialize with custom config
pipeline = GuardrailPipeline("my_config.yaml")

# Get pipeline status
status = pipeline.get_guardrail_status()
print(f"Pipeline has {status['total_enabled']} enabled guardrails")

# Dynamically configure guardrails
pipeline.disable_guardrail("pii_check")
pipeline.enable_guardrail("toxicity_check")

# Update configuration
pipeline.update_guardrail_config("toxicity_check", {
    'confidence_threshold': 0.9
})

# Process content with detailed results
result = pipeline.check_input("Test content")
print(f"Blocked: {result['blocked']}")
print(f"Reasons: {result['reasons']}")
print(f"Warnings: {result['warnings']}")
print(f"Details: {result['details']}")

# All security decisions automatically logged to audit trail
```

## 🧪 Testing

Run the demo to see Stinger in action:

```bash
# Run the tech support demo
cd demos/tech_support
python3 demo.py

# Run the simple example
python3 examples/simple_usage.py
```

## 📚 Learning Resources

### Examples (`/examples`)
**Start here** - Minimal, focused code examples that mirror the Getting Started guide:
- `01_basic_installation.py` - Installation and basic setup
- `02_simple_filter.py` - Simple guardrail usage
- `03_global_rate_limiting.py` - Rate limiting configuration
- `04_conversation_api.py` - Conversation-based filtering
- `05_conversation_rate_limiting.py` - Conversation rate limiting
- `06_health_monitoring.py` - Health monitoring and status
- `07_cli_and_yaml_config.py` - CLI and YAML configuration
- `08_security_audit_trail.py` - Security audit trail setup and usage
- `09_troubleshooting_and_testing.py` - Testing and debugging

**Run examples:**
```bash
cd examples/getting_started
python 01_basic_installation.py
```

### Demos (`/demos`)
Advanced demonstrations showcasing specific features and scenarios:
- `conversation_aware_prompt_injection_demo.py` - Advanced prompt injection detection
- `global_rate_limiting_demo.py` - Rate limiting demonstrations
- `topic_filter_demo.py` - Topic-based filtering
- `tech_support/` - Complete tech support scenario with audit trail

**Run demos:**
```bash
cd demos
python conversation_aware_prompt_injection_demo.py
```

### Learning Path
1. **Start with examples** - Run through the numbered examples in order
2. **Explore demos** - Try the advanced demonstrations
3. **Check the tech support scenario** - See a complete real-world implementation
4. **Review API docs** - Deep dive into the complete API reference

## 🔧 Development

> **Note:** Stinger uses a modern `src/` layout. All package code is under `src/stinger/`.

### Installation from Source

```bash
git clone https://github.com/virtualsteve-star/stinger.git
cd stinger
pip install -e .
```

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
src/
  └── stinger/
      ├── core/           # Core components and high-level API
      ├── filters/        # Guardrail implementations
      ├── data/           # Keyword lists and data files
      ├── scenarios/      # Pre-configured scenarios
      ├── utils/          # Utilities and exceptions
      ├── adapters/       # Model adapters
      ├── cli.py          # CLI entry point
      └── ...
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](docs/)
- 🐛 [Issues](https://github.com/virtualsteve-star/stinger/issues)

---

**Made with ❤️ for safer AI applications** 