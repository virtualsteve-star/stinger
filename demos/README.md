# Stinger Demos

## Purpose

The `/demos` folder contains **interactive demonstrations** and **feature showcases** for exploring Stinger's capabilities. These are designed for developers who want to see complex features in action and understand advanced use cases.

## How Demos Differ from Examples

| Aspect | Demos | Examples |
|--------|-------|----------|
| **Purpose** | Interactive exploration | Structured learning |
| **Complexity** | Complex, multi-scenario | Simple, focused |
| **Audience** | Developers exploring features | New users learning |
| **Style** | Feature showcases | Step-by-step tutorials |
| **Output** | Detailed, verbose | Clear, concise |

## Available Demos

### **Core Features**
- **`conversation_demo.py`** - Comprehensive conversation management with rate limiting, history tracking, and pipeline integration
- **`global_rate_limiting_demo.py`** - Advanced rate limiting scenarios including custom limits and monitoring
- **`topic_filter_demo.py`** - Topic-based content filtering with allow/deny lists

### **Advanced Features**
- **`conversation_aware_prompt_injection_demo.py`** - Prompt injection detection with conversation context
- **`demo_presets.py`** - Pre-configured pipeline presets for different use cases

### **Scenario-Based**
- **`tech_support/`** - Complete customer service scenario with configuration files and utilities

## Running Demos

```bash
# Run a specific demo
python demos/conversation_demo.py

# Run tech support scenario
cd demos/tech_support
python demo.py

# Run with custom configuration
python demos/global_rate_limiting_demo.py --config custom_config.yaml
```

## Demo Output

Demos provide detailed, interactive output showing:
- **Feature behavior** in real-time
- **Configuration options** and their effects
- **Error handling** and edge cases
- **Performance characteristics**
- **Integration patterns**

## When to Use Demos

- **Exploring new features** before implementing
- **Understanding complex scenarios** and edge cases
- **Testing different configurations** and parameters
- **Demonstrating capabilities** to stakeholders
- **Debugging and troubleshooting** advanced use cases

## Related Resources

- **Examples**: See `/examples/getting_started/` for structured learning
- **Documentation**: Check `/docs/` for comprehensive guides
- **Tests**: Review `/tests/` for detailed test scenarios 