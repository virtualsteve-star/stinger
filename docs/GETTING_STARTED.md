# Getting Started with Stinger

**LLM Guardrails Framework - Get up and running in under 10 minutes!**

## 🚀 Quick Start (5 minutes)

### 1. Installation

```bash
# Install the alpha release
pip install stinger-guardrails-alpha

# Verify installation
stinger --version

# Run the demo
stinger demo
```

#### Alternative: Install from Source
```bash
# Clone the repository  
git clone https://github.com/virtualsteve-star/stinger.git
cd Stinger

# Install dependencies
pip install -r requirements.txt

# Set up your API keys
python scripts/manage_api_keys.py add openai
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
stinger demo

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
- `medical`: Ensures medical information safety
- `basic`: Basic content moderation

## 🛠️ Basic Usage

### Using Presets

```python
from stinger import GuardrailPipeline

# Customer service preset (blocks PII, toxic content, etc.)
pipeline = GuardrailPipeline.from_preset('customer_service')

# Medical bot preset (stricter medical content filtering)
pipeline = GuardrailPipeline.from_preset('medical')

# Basic preset (basic content moderation)
pipeline = GuardrailPipeline.from_preset('basic')
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

## 🌟 Interactive Demos

### See Stinger in Action

Before diving into code, try our interactive demos to experience Stinger's capabilities:

#### Web Demo - Visual Guardrail Experience
```bash
# Quick start (single terminal)
cd demos/web_demo
pip install -r backend/requirements.txt  # First time only
(cd frontend && npm install)  # First time only

# Start both services
cd backend && python main.py &
sleep 2  # Give backend time to start
cd ../frontend && npm start

# Open http://localhost:3000 in your browser
```

Try these scenarios:
- Type a credit card number and watch PII detection activate
- Use offensive language to trigger toxicity guardrails
- Ask to generate code and see output filtering
- Switch between presets to see different security levels

#### Management Console - Real-Time Monitoring
```bash
# Quick start (single terminal)
cd management-console
pip install -r backend/requirements.txt  # First time only
(cd frontend && npm install)  # First time only

# Start both services
cd backend && python main.py &
sleep 2  # Give backend time to start
cd ../frontend && npm start

# Open http://localhost:3001 in your browser
```

Monitor:
- Real-time guardrail triggers
- System performance metrics
- Active conversations
- Security event history

## 🔑 API Key Setup

Some guardrails use AI for advanced detection. Here's how to set up API keys:

### Quick Setup (Environment Variable)
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# Or use the recommended secure method (macOS)
security add-generic-password -a "$USER" -s openai-api-key -w 'sk-...'
launchctl setenv OPENAI_API_KEY $(security find-generic-password -w -s openai-api-key)
```

### Which Guardrails Need API Keys?

**AI-Powered (Require API Key):**
- Content Moderation (`content_moderation`)
- Advanced Toxicity Detection
- Prompt Injection Detection (AI mode)

**Regex-Based (No API Key):**
- PII Detection (`simple_pii_detection`)
- Basic Toxicity (`simple_toxicity_detection`)
- Code Generation Detection
- Keyword Blocking

### Testing Your Setup
```bash
# Test with a simple (no API) guardrail
python examples/getting_started/02_simple_guardrail.py

# Test with an AI guardrail (requires API key)
python examples/getting_started/11_ai_powered_filters.py
```

## �� Health Monitoring

Monitor your system's health:

```bash
# Basic health check
stinger health

# Detailed health information
stinger health --detailed
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
pipeline = GuardrailPipeline.from_preset('medical')

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

# Check if rate limit is exceeded
exceeded = conv.check_rate_limit()
print(f"Rate limit exceeded: {exceeded}")
```

## 🧪 Testing Your Setup

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
pytest -m "efficacy" -v  # Run AI behavior tests

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
python scripts/manage_api_keys.py list

# Test your key
python scripts/manage_api_keys.py test openai

# Re-add if needed
python scripts/manage_api_keys.py add openai
```

**3. Configuration Errors**
```bash
# Check health status
stinger health

# Run with debug output
python demos/conversation_demo.py --debug
```

### Getting Help

- **Documentation**: Check the `docs/` directory
- **Examples**: Look at `examples/` and `demos/` directories
- **Tests**: Run tests to verify your setup
- **Health Monitor**: Use `stinger health` to diagnose issues

## 📈 Next Steps

Now that you're up and running:

1. **Explore Demos**: Run different demos to see Stinger in action
2. **Customize Configs**: Modify YAML configs for your specific needs
3. **Create Custom Filters**: See the Extensibility Guide
4. **Monitor Performance**: Use health monitoring for production insights
5. **Join the Community**: Contribute and share your use cases

## 📚 Getting Started Examples

We've created a comprehensive set of examples to help you learn Stinger step by step. Each example is self-contained and demonstrates specific features:

### **01_basic_installation.py** - Basic Installation
```bash
python examples/getting_started/01_basic_installation.py
```
- Verify Stinger installation
- Test basic imports and functionality
- Confirm API key setup

### **02_simple_filter.py** - Simple Filter Presets
```bash
python examples/getting_started/02_simple_filter.py
```
- Use pre-configured filter presets
- Test customer service and medical bot presets
- Understand blocking vs warning behavior

### **03_global_rate_limiting.py** - Global Rate Limiting
```bash
python examples/getting_started/03_global_rate_limiting.py
```
- Global rate limiting for API keys
- Monitor rate limit status across users
- Understand rate limit windows and tracking

### **04_conversation_api.py** - Conversation API
```bash
python examples/getting_started/04_conversation_api.py
```
- Use the Conversation API for multi-turn interactions
- Automatic guardrail application
- Conversation context and history management

Example usage:
```python
from stinger import Conversation

conv = Conversation.human_ai("user123", "assistant")
conv.add_exchange("Hello", "Hi there! How can I help you today?")
conv.add_exchange("How are you?", "I'm doing well, thanks for asking!")

# Check if rate limit is exceeded
exceeded = conv.check_rate_limit()
print(f"Rate limit exceeded: {exceeded}")

# Get conversation history
for turn in conv.get_history():
    print(f"Prompt: {turn.prompt} | Response: {turn.response}")
```

### **05_conversation_rate_limiting.py** - Conversation Rate Limiting
```bash
python examples/getting_started/05_conversation_rate_limiting.py
```
- Rate limiting within conversations
- Monitor conversation-specific rate limits
- Understand conversation turn limits

### **06_health_monitoring.py** - Health Monitoring
```bash
python examples/getting_started/06_health_monitoring.py
```
- Monitor system health and performance
- Check guardrail status and configuration
- View detailed health metrics

Example usage:
```python
from stinger.core.health_monitor import HealthMonitor

monitor = HealthMonitor()
health = monitor.get_system_health()
print(f"Overall status: {health.overall_status}")
print(f"Pipeline status: {health.pipeline_healthy}")
print(f"API keys status: {health.api_keys_configured}")
print(f"Rate limiter status: {health.rate_limiter_healthy}")
```

### **07_cli_and_yaml_config.py** - CLI and YAML Configuration
```bash
python examples/getting_started/07_cli_and_yaml_config.py
```
- Use the command-line interface
- Create and load custom YAML configurations
- Understand configuration structure

Example YAML config:
```yaml
version: '1.0'
pipeline:
  input:
    - name: toxicity_check
      type: simple_toxicity_detection
      enabled: true
      on_error: block
      config:
        categories: [hate_speech, harassment]
        confidence_threshold: 0.8
    - name: pii_check
      type: simple_pii_detection
      enabled: true
      on_error: warn
    - name: length_check
      type: length_filter
      enabled: true
      on_error: warn
      config:
        max_length: 1000
        min_length: 1
  output:
    - name: content_moderation
      type: content_moderation
      enabled: true
      on_error: block
```

Load and use the config in Python:
```python
from stinger import GuardrailPipeline

pipeline = GuardrailPipeline('configs/custom_example.yaml')
result = pipeline.check_input('Test content')
print(result)
```

### **08_security_audit_trail.py** - Security Audit Trail
```bash
python examples/getting_started/08_security_audit_trail.py
```
- Enable security audit logging with zero configuration
- Track all security decisions for compliance
- Use smart environment detection for automatic setup
- Implement PII redaction and forensic analysis

Example usage:
```python
from stinger.core import audit

audit.enable()  # Zero-config, just works!

# Enable with file destination and PII redaction
audit.enable('audit.log', redact_pii=True)
```

### **09_troubleshooting_and_testing.py** - Troubleshooting and Testing
```bash
python examples/getting_started/09_troubleshooting_and_testing.py
```
- Debug common issues
- Test your setup comprehensively
- Validate configuration and API keys

### Running All Examples
```bash
# Run all examples in sequence
for example in examples/getting_started/*.py; do
    echo "Running $example..."
    python "$example"
    echo "---"
done
```

Each example is designed to be run independently and includes clear output showing what's happening. They follow the same structure as this Getting Started guide and provide hands-on experience with Stinger's features.

## 🎯 Quick Reference

### CLI Commands
```bash
stinger demo                    # Run demo
stinger health                  # Health check
stinger check-prompt "text"     # Check prompt
stinger check-response "text"   # Check response
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
version: "1.0"
pipeline:
  input:
    - name: pii_check
      type: simple_pii_detection
      enabled: true
      on_error: block
    - name: toxicity_check
      type: simple_toxicity_detection
      enabled: true
      on_error: warn
  output:
    - name: content_check
      type: content_moderation
      enabled: true
      on_error: block
```

---

**🎉 You're all set! Stinger is protecting your LLM applications.**