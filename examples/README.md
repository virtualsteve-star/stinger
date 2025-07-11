# Stinger Examples

This directory contains examples demonstrating various features of the Stinger Guardrails Framework.

## Getting Started Examples

The `getting_started/` directory contains progressive examples following the Getting Started guide:

1. **00_verify_installation.py** - Verify your Stinger installation
2. **01_basic_installation.py** - Your first guardrail check
3. **02_simple_guardrail.py** - Using different presets
4. **03_global_rate_limiting.py** - Rate limiting across conversations
5. **04_conversation_api.py** - Conversation-aware filtering
6. **05_conversation_rate_limiting.py** - Per-conversation rate limits
7. **06_health_monitoring.py** - System health and monitoring
8. **07_cli_and_yaml_config.py** - CLI usage and YAML configuration
9. **08_security_audit_trail.py** - Security audit logging
10. **09_troubleshooting_and_testing.py** - Debugging and testing
11. **11_ai_powered_filters.py** - AI-based guardrails
12. **12_rest_api_usage.py** - 🆕 Using Stinger via REST API

## Running Examples

### Prerequisites

1. **Install Stinger**:
   ```bash
   pip install stinger-guardrails-alpha
   ```

2. **Set up environment** (for AI features):
   ```bash
   export OPENAI_API_KEY='your-key-here'
   # Or run: stinger setup
   ```

3. **Verify installation**:
   ```bash
   stinger demo
   ```

### Running an Example

Each example is self-contained and can be run directly:

```bash
python examples/getting_started/01_basic_installation.py
```

**Note**: The REST API example (12) requires starting the API server first:
```bash
# Install API dependencies
pip install stinger-guardrails-alpha[api]

# Terminal 1: Start server
stinger-api

# Terminal 2: Run example
python examples/getting_started/12_rest_api_usage.py
```

## Example Structure

All examples follow a standard structure for consistency:

```python
#!/usr/bin/env python3
"""
Example description and purpose.
"""

import sys
import os

def check_prerequisites() -> bool:
    """Check if prerequisites are met."""
    # Check Python version
    # Check Stinger installation
    # Check optional requirements
    return True

def run_example():
    """Main example logic."""
    # Import Stinger components
    # Demonstrate features
    # Handle errors gracefully
    pass

def main():
    """Entry point with error handling."""
    if not check_prerequisites():
        return 1
    
    try:
        run_example()
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Error Handling

All examples include:
- ✅ **Prerequisite checking** - Verify environment before running
- ✅ **Clear error messages** - Understand what went wrong
- ✅ **Troubleshooting tips** - How to fix common issues
- ✅ **Graceful failures** - Examples fail cleanly with helpful output

## Common Issues

### "Stinger is not installed"
```bash
pip install stinger-guardrails-alpha
```

### "OPENAI_API_KEY not found"
Some examples require AI features. Set your API key:
```bash
export OPENAI_API_KEY='your-key-here'
```
Or use local-only guardrails.

### "Python version too old"
Stinger requires Python 3.8+. Update your Python version.

## Example Categories

### Basic Usage
- Installation verification
- Simple filtering
- Preset usage

### Advanced Features
- Rate limiting
- Conversation tracking
- Custom pipelines

### Operations
- Health monitoring
- Audit trails
- Configuration management

### Integration
- CLI usage
- YAML configuration
- REST API usage
- Language-agnostic integration

## Creating New Examples

Use `example_template.py` as a starting point:

```bash
cp examples/example_template.py examples/my_example.py
```

Follow these guidelines:
1. Include prerequisite checking
2. Use clear, descriptive output
3. Handle errors gracefully
4. Add troubleshooting tips
5. Document the purpose clearly

## Demo Scripts

The `demos/` directory contains more complex demonstration scripts:
- Full application examples
- Integration scenarios
- Performance testing
- Multi-guardrail pipelines

## Contributing

When contributing examples:
1. Follow the standard structure
2. Test with fresh installation
3. Include clear documentation
4. Handle missing dependencies
5. Provide helpful error messages

---

For more information, see the [Stinger Documentation](https://github.com/virtualsteve-star/stinger).