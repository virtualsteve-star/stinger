# Stinger API Reference

## Overview

Stinger provides a simple, powerful API for safeguarding LLM applications with comprehensive content filtering and moderation capabilities.

## Quick Start

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

## Core Classes

### GuardrailPipeline

The main class for using Stinger guardrails. Provides a simple, synchronous interface for content screening.

#### Constructor

```python
GuardrailPipeline(config_path: Optional[Union[str, Path]] = None) -> None
```

**Parameters:**
- `config_path`: Path to YAML configuration file. If None, uses default config.

**Raises:**
- `FileNotFoundError`: If config file doesn't exist
- `ValueError`: If config file is invalid  
- `RuntimeError`: If pipeline initialization fails

**Example:**
```python
# Use custom config
pipeline = GuardrailPipeline("my_config.yaml")

# Use default config
pipeline = GuardrailPipeline()
```

#### Methods

##### check_input()

```python
check_input(content: str) -> PipelineResult
```

Check input content through all input guardrails.

**Parameters:**
- `content`: The input content to check

**Returns:**
- `PipelineResult`: Dictionary with 'blocked', 'warnings', 'reasons', and 'details' keys

**Raises:**
- `ValueError`: If content is None or empty
- `RuntimeError`: If pipeline execution fails

**Example:**
```python
result = pipeline.check_input("User input here")
if result['blocked']:
    print(f"Input blocked: {result['reasons']}")
elif result['warnings']:
    print(f"Warnings: {result['warnings']}")
```

##### check_output()

```python
check_output(content: str) -> PipelineResult
```

Check output content through all output guardrails.

**Parameters:**
- `content`: The output content to check

**Returns:**
- `PipelineResult`: Dictionary with 'blocked', 'warnings', 'reasons', and 'details' keys

**Raises:**
- `ValueError`: If content is None or empty
- `RuntimeError`: If pipeline execution fails

**Example:**
```python
result = pipeline.check_output("LLM response here")
if result['blocked']:
    print(f"Output blocked: {result['reasons']}")
```

##### get_guardrail_status()

```python
get_guardrail_status() -> PipelineStatus
```

Get status of all guardrails in the pipeline.

**Returns:**
- `PipelineStatus`: Dictionary with guardrail status information

**Example:**
```python
status = pipeline.get_guardrail_status()
print(f"Enabled guardrails: {status['total_enabled']}")
print(f"Input guardrails: {len(status['input_guardrails'])}")
print(f"Output guardrails: {len(status['output_guardrails'])}")
```

##### enable_guardrail()

```python
enable_guardrail(name: str) -> bool
```

Enable a specific guardrail by name.

**Parameters:**
- `name`: Name of the guardrail to enable

**Returns:**
- `bool`: True if guardrail was found and enabled, False otherwise

**Example:**
```python
success = pipeline.enable_guardrail("toxicity_check")
if success:
    print("Toxicity check enabled")
```

##### disable_guardrail()

```python
disable_guardrail(name: str) -> bool
```

Disable a specific guardrail by name.

**Parameters:**
- `name`: Name of the guardrail to disable

**Returns:**
- `bool`: True if guardrail was found and disabled, False otherwise

**Example:**
```python
success = pipeline.disable_guardrail("pii_check")
if success:
    print("PII check disabled")
```

##### get_guardrail_config()

```python
get_guardrail_config(name: str) -> Optional[Dict[str, Any]]
```

Get configuration of a specific guardrail.

**Parameters:**
- `name`: Name of the guardrail

**Returns:**
- `Optional[Dict[str, Any]]`: Guardrail configuration or None if not found

**Example:**
```python
config = pipeline.get_guardrail_config("toxicity_check")
if config:
    print(f"Confidence threshold: {config.get('confidence_threshold')}")
```

##### update_guardrail_config()

```python
update_guardrail_config(name: str, config: Dict[str, Any]) -> bool
```

Update configuration of a specific guardrail.

**Parameters:**
- `name`: Name of the guardrail
- `config`: New configuration dictionary

**Returns:**
- `bool`: True if guardrail was found and updated, False otherwise

**Example:**
```python
new_config = {'confidence_threshold': 0.8}
success = pipeline.update_guardrail_config("toxicity_check", new_config)
if success:
    print("Configuration updated")
```

## Data Types

### PipelineResult

Type definition for guardrail check results.

```python
class PipelineResult(TypedDict):
    blocked: bool          # Whether content was blocked
    warnings: List[str]    # List of warning messages
    reasons: List[str]     # List of blocking reasons
    details: Dict[str, Any] # Detailed results from each guardrail
    pipeline_type: str     # Type of pipeline ("input" or "output")
```

**Example:**
```python
result = pipeline.check_input("Test content")
print(f"Blocked: {result['blocked']}")
print(f"Reasons: {result['reasons']}")
print(f"Warnings: {result['warnings']}")
```

### PipelineStatus

Type definition for pipeline status information.

```python
class PipelineStatus(TypedDict):
    input_guardrails: List[Dict[str, Any]]  # Input guardrail status
    output_guardrails: List[Dict[str, Any]] # Output guardrail status
    total_enabled: int                       # Total enabled guardrails
    total_disabled: int                      # Total disabled guardrails
```

## Convenience Functions

### create_pipeline()

```python
create_pipeline(config_path: Optional[Union[str, Path]] = None) -> GuardrailPipeline
```

Create a guardrail pipeline with the given configuration. This is a convenience function for quick pipeline creation.

**Parameters:**
- `config_path`: Path to YAML configuration file

**Returns:**
- `GuardrailPipeline`: Configured GuardrailPipeline instance

**Example:**
```python
from stinger import create_pipeline

pipeline = create_pipeline("my_config.yaml")
result = pipeline.check_input("Hello, world!")
```

## Configuration

Stinger uses YAML configuration files to define guardrail pipelines. Here's an example:

```yaml
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

## Error Handling

Stinger provides comprehensive error handling:

```python
try:
    pipeline = GuardrailPipeline("config.yaml")
    result = pipeline.check_input("Test content")
except FileNotFoundError:
    print("Configuration file not found")
except ValueError as e:
    print(f"Invalid configuration: {e}")
except RuntimeError as e:
    print(f"Pipeline error: {e}")
```

## Logging

Stinger uses Python's standard logging module. Configure logging to see detailed information:

```python
import logging
logging.basicConfig(level=logging.INFO)

pipeline = GuardrailPipeline("config.yaml")
# Will log initialization and guardrail status
```

## Best Practices

1. **Always check results**: Always check the `blocked` field in results
2. **Handle warnings**: Monitor `warnings` for potential issues
3. **Use appropriate thresholds**: Adjust confidence thresholds based on your use case
4. **Test thoroughly**: Test with various content types before production
5. **Monitor performance**: Use logging to monitor guardrail performance

## Examples

### Basic Usage

```python
from stinger import GuardrailPipeline

# Initialize pipeline
pipeline = GuardrailPipeline("config.yaml")

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

### Advanced Usage

```python
from stinger import GuardrailPipeline

# Initialize with custom config
pipeline = GuardrailPipeline("my_config.yaml")

# Get pipeline status
status = pipeline.get_guardrail_status()
print(f"Pipeline has {status['total_enabled']} enabled guardrails")

# Dynamically enable/disable guardrails
pipeline.disable_guardrail("pii_check")
pipeline.enable_guardrail("toxicity_check")

# Update guardrail configuration
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