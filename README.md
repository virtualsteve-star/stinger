# Stinger - LLM Guardrails Framework

A configurable guardrails layer that filters inputs to and outputs from Large Language Models (LLMs). The framework blocks or transforms unwanted content while allowing safe traffic with minimal latency.

## Current Status

**Phase 2 Complete**: Comprehensive rule-based filtering with regex patterns, length validation, URL blocking, and enhanced testing framework.

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
# Run all Phase 2 test suites
python3 tests/test_phase2.py

# Run individual test suites
python3 tests/test_runner.py  # Smoke tests only
```

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
│   ├── test_corpus/       # Test data
│   │   ├── smoke_test.jsonl
│   │   ├── regex_test.jsonl
│   │   └── url_test.jsonl
│   ├── test_runner.py     # Basic test runner
│   └── test_phase2.py     # Comprehensive test suite
├── configs/               # Configuration files
│   ├── minimal.yaml       # Minimal test configuration
│   └── comprehensive.yaml # Full feature configuration
├── specs/                 # Project specifications
└── plans/                 # Implementation plans
```

## Configuration

The framework uses YAML configuration files to define filter pipelines:

### Minimal Configuration
```yaml
version: "1.0"
pipeline:
  input:
    - name: "pass_through"
      type: "pass_through"
      enabled: true
      on_error: "allow"
    - name: "keyword_block"
      type: "keyword_block"
      enabled: true
      on_error: "allow"
      keywords: ["blockme"]
```

### Comprehensive Configuration
```yaml
version: "1.0"
pipeline:
  input:
    - name: "length_check"
      type: "length_filter"
      enabled: true
      min_length: 0
      max_length: 10000
      on_error: "block"
    
    - name: "url_check"
      type: "url_filter"
      enabled: true
      blocked_domains: ["malicious.com", "spam.net", "evil.org"]
      on_error: "block"
    
    - name: "keyword_block"
      type: "keyword_block"
      enabled: true
      keywords: ["blockme", "spam", "malware"]
      on_error: "block"
    
    - name: "regex_check"
      type: "regex_filter"
      enabled: true
      patterns: 
        - "\\b\\d{4}-\\d{4}-\\d{4}-\\d{4}\\b"  # Credit card
        - "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"  # Email
      action: "warn"
      on_error: "block"
```

## Current Features

### Core Framework
- **Filter Pipeline**: Sequential processing of content through multiple filters
- **Configuration System**: YAML-based configuration with validation
- **Error Handling**: Graceful error handling with configurable actions
- **Test Framework**: Automated testing with JSONL test corpora

### Available Filters
- **Pass-Through Filter**: Allows all content (for testing)
- **Keyword Block Filter**: Blocks content containing specified keywords
- **Regex Filter**: Detects patterns like credit card numbers and email addresses
- **Length Filter**: Validates content length against min/max thresholds
- **URL Filter**: Blocks content containing URLs from specified domains

### Test Coverage
- **58 test cases** across 3 test suites
- **100% pass rate** for all implemented features
- Comprehensive edge case coverage
- Real-world scenario testing

## Development

### Adding a New Filter

1. Create a new filter class in `src/filters/`
2. Inherit from `BaseFilter`
3. Implement the `run()` method
4. Add to the filter registry in test files
5. Add test cases to the corpus

### Running Tests

```bash
# Run all Phase 2 tests
python3 tests/test_phase2.py

# Run smoke tests only
python3 tests/test_runner.py
```

## Next Steps

- Phase 3: External API integration (OpenAI Moderation, etc.)
- Phase 4: Advanced features (rate limiting, context controls)

## Contributing

This is an early-stage project. Contributions are welcome!

## License

MIT License - see [LICENSE](LICENSE) file for details. 