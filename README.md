# Stinger - LLM Guardrails Framework

A configurable guardrails layer that filters inputs to and outputs from Large Language Models (LLMs). The framework blocks or transforms unwanted content while allowing safe traffic with minimal latency.

## Current Status

**Version 0.0.3 Complete**: Comprehensive integration testing with realistic conversation scenarios for customer service and medical bots, featuring toxic language detection and PII protection.

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation
```bash
# Clone the repository
git clone https://github.com/virtualsteve-star/stinger.git
cd stinger

# Install dependencies
pip install -r requirements.txt
```

### Running Tests
```bash
# Run all integration test scenarios
cd tests/scenarios
python3 run_all_tests.py

# Run specific scenario
cd tests/scenarios/customer_service
python3 test_runner.py

# Run with conversation transcript
python3 test_runner.py --transcript
```

## Unified CLI Usage

The new unified CLI (`stinger.py`) allows you to run all or specific test scenarios with a single command, with options for debug, quiet, transcript, and custom config/test data files.

### Examples

```bash
# Run all scenarios
python3 stinger.py --all

# Run a specific scenario
python3 stinger.py --scenario customer_service
python3 stinger.py --scenario medical_bot

# Run with debug output (shows filter-by-filter processing)
python3 stinger.py --scenario customer_service --debug

# Run with summary only (no conversation details)
python3 stinger.py --scenario customer_service --quiet

# Show conversation transcript with inline moderation tags
python3 stinger.py --scenario customer_service --transcript

# List available scenarios and their descriptions
python3 stinger.py --list

# Run with a custom config or test data file
python3 stinger.py --scenario customer_service --config configs/customer_service.yaml --test-data tests/scenarios/customer_service/test_data.jsonl
```

### Environment Variable Overrides

When running a scenario, you can override the default config or test data by setting the following environment variables:
- `STINGER_CONFIG`: Path to a custom YAML config file
- `STINGER_TEST_DATA`: Path to a custom test data file (JSONL)

These are set automatically by the CLI when you use the `--config` or `--test-data` flags.

## Project Structure

```
stinger/
├── src/                    # Source code
│   ├── core/              # Core framework classes
│   │   ├── base_filter.py # Abstract filter base class
│   │   ├── pipeline.py    # Filter pipeline orchestration
│   │   └── config.py      # Configuration loader
│   ├── filters/           # Filter implementations
│   │   ├── pass_through.py # Pass-through filter
│   │   ├── keyword_block.py # Keyword blocking filter
│   │   ├── regex_filter.py # Regex pattern matching
│   │   ├── length_filter.py # Length validation
│   │   └── url_filter.py  # URL domain blocking
│   └── utils/             # Utilities
│       └── exceptions.py  # Custom exceptions
├── tests/                 # Test framework
│   ├── scenarios/         # Integration test scenarios
│   │   ├── shared/        # Shared test infrastructure
│   │   │   └── base_runner.py # Base conversation simulator
│   │   ├── customer_service/ # Customer service bot tests
│   │   │   ├── README.md  # Scenario documentation
│   │   │   ├── test_data.jsonl # Test conversations
│   │   │   ├── config.yaml # Moderation rules
│   │   │   └── test_runner.py # Test execution script
│   │   ├── medical_bot/   # Medical bot tests
│   │   │   ├── README.md  # Scenario documentation
│   │   │   ├── test_data.jsonl # Test conversations
│   │   │   ├── config.yaml # PII detection rules
│   │   │   └── test_runner.py # Test execution script
│   │   └── run_all_tests.py # Master test runner
│   ├── test_simple.py     # Basic unit tests
│   └── test_runner.py     # Legacy test runner
├── configs/               # Configuration files
│   ├── minimal.yaml       # Minimal test configuration
│   ├── comprehensive.yaml # Full feature configuration
│   ├── customer_service.yaml # Customer service moderation
│   └── medical_bot.yaml   # Medical PII detection
├── specs/                 # Project specifications
└── plans/                 # Implementation plans
```

## Configuration

The framework uses YAML configuration files to define filter pipelines:

### Customer Service Configuration
```yaml
version: "1.0"
pipeline:
  input:
    - name: "length_check"
      type: "length_filter"
      enabled: true
      min_length: 0
      max_length: 1000
      on_error: "allow"
    
    - name: "toxic_keywords"
      type: "keyword_block"
      enabled: true
      keywords: ["idiot", "stupid", "useless", "garbage", "worst", "hate"]
      on_error: "block"
    
    - name: "profanity"
      type: "regex_filter"
      enabled: true
      patterns: ["\\b(shit|hell|damn|fuck|bitch|ass)\\b"]
      action: "block"
      on_error: "block"
```

### Medical Bot Configuration
```yaml
version: "1.0"
pipeline:
  input:
    - name: "length_check"
      type: "length_filter"
      enabled: true
      min_length: 0
      max_length: 1000
      on_error: "allow"
    
    - name: "pii_detection"
      type: "regex_filter"
      enabled: true
      patterns:
        - "\\b\\d{3}-\\d{2}-\\d{4}\\b"  # SSN
        - "\\b\\d{4}-\\d{4}-\\d{4}-\\d{4}\\b"  # Credit card
        - "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"  # Email
        - "\\b[A-Z][a-z]+\\s+[A-Z][a-z]+\\b"  # Full names
      action: "warn"
      on_error: "allow"
```

## Compound Filters: Additive Certainty Scoring

Stinger's compound filters now use an additive certainty system:
- Each rule contributes a certainty value (0-100).
- The total certainty is the sum of matched rules (capped at 100).
- Thresholds (allow/warn/block) are based on the total certainty.
- This system is deterministic, intuitive, and flexible.

### Example YAML

```yaml
rules:
  - name: ssn_pattern
    type: regex
    pattern: "\\d{3}-\\d{2}-\\d{4}"
    certainty: 40
    description: "Social Security Number"
    case_sensitive: false
  # ... more rules ...
thresholds:
  allow: [0, 20]
  warn: [21, 60]
  block: [61, 100]
```

### Migration Note
If you previously used 'weight' for rules, replace it with 'certainty' (1-100). The system is now additive, not normalized.

## Current Features

### Core Framework
- **Filter Pipeline**: Sequential processing of content through multiple filters
- **Configuration System**: YAML-based configuration with validation
- **Error Handling**: Graceful error handling with configurable actions
- **Test Framework**: Automated testing with JSONL test corpora

### Available Filters
- **Pass-Through Filter**: Allows all content (for testing)
- **Keyword Block Filter**: Blocks content containing specified keywords
- **Regex Filter**: Detects patterns like credit card numbers, emails, and PII
- **Length Filter**: Validates content length against min/max thresholds
- **URL Filter**: Blocks content containing URLs from specified domains

### Test Scenarios

#### 🤖 Customer Service Bot
- **Purpose**: Validate toxic language detection in support conversations
- **Focus**: Blocking rude, abusive, or profane customer messages
- **Data**: 6 conversations, 38 messages total
- **Results**: 21.1% block rate for toxic content

#### 🏥 Medical Bot
- **Purpose**: Validate PII detection in healthcare conversations
- **Focus**: Flagging personal information for review
- **Data**: 8 conversations, 48 messages total
- **Results**: 14.0% warn rate for PII content

## Test Results

### **Overall Coverage**
- **144 Total Tests**: Across all test suites (integration + legacy)
- **2 Integration Scenarios**: Customer service and medical bot
- **86 Total Messages**: Realistic conversation testing
- **100% Pass Rate**: All scenarios passing with expected results

### **Customer Service Results**
- **Total Messages**: 38
- **Allowed**: 30 (78.9%)
- **Blocked**: 8 (21.1%)
- **Success**: Toxic language properly detected

### **Medical Bot Results**
- **Total Messages**: 48
- **Allowed**: 43 (86.0%)
- **Warned**: 7 (14.0%)
- **Success**: PII properly flagged

## Development

### Adding a New Test Scenario

1. Create a new scenario directory in `tests/scenarios/`
2. Add required files:
   - `test_data.jsonl` - Conversation test cases
   - `config.yaml` - Moderation configuration
   - `test_runner.py` - Test execution script
   - `README.md` - Scenario documentation
3. Test data format:
   ```json
   {
     "input": "Message content",
     "expected": "allow|warn|block",
     "description": "What this tests",
     "conversation_id": "CONV001",
     "turn": 1,
     "speaker": "user|bot"
   }
   ```

### Running Tests

```bash
# Run all scenarios
cd tests/scenarios
python3 run_all_tests.py

# Run specific scenario
cd tests/scenarios/customer_service
python3 test_runner.py

# See conversation transcript
python3 test_runner.py --transcript

# List available scenarios
python3 run_all_tests.py --list
```

### Adding a New Filter

1. Create a new filter class in `src/filters/`
2. Inherit from `BaseFilter`
3. Implement the `run()` method
4. Add to the filter registry in `tests/shared/base_runner.py`
5. Add test cases to relevant scenarios

## Next Steps

- Phase 4: External API integration (OpenAI Moderation, etc.)
- Phase 5: Advanced features (rate limiting, context controls)

## Contributing

This is an early-stage project. Contributions are welcome!

## License

MIT License - see [LICENSE](LICENSE) file for details. 