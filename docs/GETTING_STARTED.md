# Getting Started with Stinger

**LLM Guardrails Framework - Get up and running in under 10 minutes!**

## 🚀 Quick Start (5 minutes)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/Stinger.git
cd Stinger

# Install dependencies
pip install -r requirements.txt

# Set up your API keys
python manage_api_keys.py add openai
```

### 2. Your First Guardrail Check

```python
from stinger import GuardrailPipeline

# Create a pipeline with customer service preset
pipeline = GuardrailPipeline.from_preset('customer_service')

# Check a user prompt
result = pipeline.check_input("My credit card is 1234-5678-9012-3456")
print(f"Blocked: {result['blocked']}")
print(f"Reasons: {result['reasons']}")
```

### 3. Run a Demo

```bash
# Run the CLI demo
python -m stinger.cli demo

# Or run a comprehensive demo
python demos/conversation_demo.py
```

**🎉 Congratulations! You've successfully set up Stinger and run your first guardrail check.**

## 📚 What is Stinger?

Stinger is a comprehensive LLM guardrails framework that helps you:

- **Protect against prompt injection attacks**
- **Detect and block PII (Personal Identifiable Information)**
- **Filter toxic content and harassment**
- **Prevent code generation in inappropriate contexts**
- **Enforce rate limiting and usage policies**
- **Monitor system health and performance**

## 🔧 Core Concepts

### Guardrails
Guardrails are filters that check content before it reaches your LLM or after it's generated. They can:
- **Block** content that violates policies
- **Warn** about potentially problematic content
- **Log** all activity for monitoring

### Pipeline
A pipeline is a sequence of guardrails that process content in order. Stinger supports:
- **Input pipelines**: Check user prompts before sending to LLM
- **Output pipelines**: Check LLM responses before sending to users

### Presets
Pre-configured pipeline setups for common use cases:
- `customer_service`: Protects customer support interactions
- `medical_bot`: Ensures medical information safety
- `general`: Basic content moderation

## 🛠️ Basic Usage

### Using Presets

```python
from stinger import GuardrailPipeline

# Customer service preset (blocks PII, toxic content, etc.)
pipeline = GuardrailPipeline.from_preset('customer_service')

# Medical bot preset (stricter medical content filtering)
pipeline = GuardrailPipeline.from_preset('medical_bot')

# General preset (basic content moderation)
pipeline = GuardrailPipeline.from_preset('general')
```

### Checking Content

```python
# Check user input
input_result = pipeline.check_input("User message here")

# Check LLM response
output_result = pipeline.check_output("LLM response here")

# Check both in a conversation context
from stinger import Conversation

conv = Conversation.human_ai("user123", "assistant")
conv.add_exchange("Hello, how can I help?", "I'm here to assist you!")

# The conversation automatically applies guardrails
```

### Understanding Results

```python
result = pipeline.check_input("Some content")

if result['blocked']:
    print("❌ Content blocked!")
    print(f"Reasons: {result['reasons']}")
else:
    print("✅ Content approved")
    if result['warnings']:
        print(f"Warnings: {result['warnings']}")
```

## 🔑 API Key Setup

Stinger supports multiple AI providers. Set up your keys:

```bash
# Add OpenAI API key
python manage_api_keys.py add openai

# Test your key
python manage_api_keys.py test openai

# List configured services
python manage_api_keys.py list
```

## 🏥 Health Monitoring

Monitor your system's health:

```bash
# Basic health check
python -m stinger.cli health

# Detailed health information
python -m stinger.cli health --detailed
```

## 📖 Common Use Cases

### 1. Customer Service Bot

```python
from stinger import GuardrailPipeline

pipeline = GuardrailPipeline.from_preset('customer_service')

# This will be blocked (contains PII)
result = pipeline.check_input("My SSN is 123-45-6789")
assert result['blocked'] == True

# This will pass
result = pipeline.check_input("I need help with my order")
assert result['blocked'] == False
```

### 2. Medical Information Bot

```python
pipeline = GuardrailPipeline.from_preset('medical_bot')

# This will be blocked (medical advice)
result = pipeline.check_input("I have chest pain, what should I do?")
assert result['blocked'] == True

# This will pass (general health info)
result = pipeline.check_input("What are the benefits of exercise?")
assert result['blocked'] == False
```

### 3. Rate Limiting

```python
from stinger import Conversation

# Create conversation with rate limiting
conv = Conversation.human_ai("user123", "assistant")

# Add exchanges (automatically rate limited)
conv.add_exchange("Hello", "Hi there!")
conv.add_exchange("How are you?", "I'm doing well, thanks!")

# Check rate limit status
status = conv.get_rate_limit_status()
print(f"Remaining requests: {status['remaining']}")
```

## 🧪 Testing Your Setup

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific scenario tests
python tests/scenarios/run_all_tests.py --scenario customer_service

# Run integration tests
python tests/test_integration.py
```

## 🚨 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Make sure you're in the right directory
cd Stinger
export PYTHONPATH=src:$PYTHONPATH
```

**2. API Key Issues**
```bash
# Check if your key is set up
python manage_api_keys.py list

# Test your key
python manage_api_keys.py test openai

# Re-add if needed
python manage_api_keys.py add openai
```

**3. Configuration Errors**
```bash
# Check health status
python -m stinger.cli health

# Run with debug output
python demos/conversation_demo.py --debug
```

### Getting Help

- **Documentation**: Check the `docs/` directory
- **Examples**: Look at `examples/` and `demos/` directories
- **Tests**: Run tests to verify your setup
- **Health Monitor**: Use `python -m stinger.cli health` to diagnose issues

## 📈 Next Steps

Now that you're up and running:

1. **Explore Demos**: Run different demos to see Stinger in action
2. **Customize Configs**: Modify YAML configs for your specific needs
3. **Create Custom Filters**: See the Extensibility Guide
4. **Monitor Performance**: Use health monitoring for production insights
5. **Join the Community**: Contribute and share your use cases

## 🎯 Quick Reference

### CLI Commands
```bash
python -m stinger.cli demo                    # Run demo
python -m stinger.cli health                  # Health check
python -m stinger.cli check-prompt "text"     # Check prompt
python -m stinger.cli check-response "text"   # Check response
```

### Python API
```python
from stinger import GuardrailPipeline, Conversation

# Create pipeline
pipeline = GuardrailPipeline.from_preset('customer_service')

# Check content
result = pipeline.check_input("content")

# Create conversation
conv = Conversation.human_ai("user", "assistant")
conv.add_exchange("prompt", "response")
```

### Configuration
```yaml
# config.yaml
input_guardrails:
  - type: pii_detection
    enabled: true
  - type: toxicity_detection
    enabled: true

output_guardrails:
  - type: content_moderation
    enabled: true
```

---

**🎉 You're all set! Stinger is protecting your LLM applications.** 