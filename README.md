# 🚀 Stinger - AI Guardrails Framework

A powerful, easy-to-use Python framework for safeguarding LLM applications with comprehensive content filtering and moderation capabilities.

## ✨ Features

- **🛡️ Comprehensive Guardrails**: Toxicity detection, PII protection, code generation prevention, and more
- **🎯 Simple API**: Get started in 3 lines of code
- **⚡ High Performance**: Async-ready with synchronous convenience wrapper
- **🔧 Configurable**: YAML-based configuration with runtime updates
- **🧪 Production Ready**: Comprehensive testing and error handling
- **📚 Well Documented**: Complete API reference and examples

## 🚀 Quick Start

### Installation

```bash
pip install stinger
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

### Simple Example

```python
from stinger import GuardrailPipeline

# Initialize pipeline
pipeline = GuardrailPipeline()

# Process user input
user_input = "Hello, how can you help me?"
input_result = pipeline.check_input(user_input)

if input_result['blocked']:
    print("Input blocked by guardrails")
    return

# Generate LLM response
llm_response = generate_response(user_input)

# Check LLM response
output_result = pipeline.check_output(llm_response)

if output_result['blocked']:
    print("Response blocked by guardrails")
    return

print("Response approved:", llm_response)
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
from stinger import GuardrailPipeline

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

## 📚 Documentation

- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [Configuration Guide](docs/CONFIGURATION.md) - Configuration file format
- [Examples](examples/) - Code examples and demos
- [Testing](tests/) - Test suite and scenarios

## 🔧 Development

### Installation from Source

```bash
git clone https://github.com/your-org/stinger.git
cd stinger
pip install -e .
```

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
stinger/
├── core/           # Core components and high-level API
├── filters/        # Guardrail implementations
├── data/           # Keyword lists and data files
├── scenarios/      # Pre-configured scenarios
├── demos/          # Demo applications
├── examples/       # Code examples
├── tests/          # Test suite
└── docs/           # Documentation
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](docs/)
- 🐛 [Issues](https://github.com/your-org/stinger/issues)
- 💬 [Discussions](https://github.com/your-org/stinger/discussions)

---

**Made with ❤️ for safer AI applications** 