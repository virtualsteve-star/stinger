# Stinger - LLM Guardrails Framework

A configurable guardrails layer that filters inputs to and outputs from Large Language Models (LLMs). The framework blocks or transforms unwanted content while allowing safe traffic with minimal latency.

## Current Status

**Phase 1 Complete**: Basic scaffolding with pass-through and keyword blocking filters, configuration system, and test framework.

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
# Run the smoke test suite
python3 tests/test_runner.py
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
│   │   └── keyword_block.py # Keyword blocking filter
│   └── utils/             # Utilities
│       └── exceptions.py  # Custom exceptions
├── tests/                 # Test framework
│   ├── test_corpus/       # Test data
│   │   └── smoke_test.jsonl
│   └── test_runner.py     # Test runner
├── configs/               # Configuration files
│   └── minimal.yaml       # Minimal test configuration
├── specs/                 # Project specifications
└── plans/                 # Implementation plans
```

## Configuration

The framework uses YAML configuration files to define filter pipelines:

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
      keyword: "blockme"
```

## Current Features

- **Filter Pipeline**: Sequential processing of content through multiple filters
- **Pass-Through Filter**: Allows all content (for testing)
- **Keyword Block Filter**: Blocks content containing specified keywords
- **Configuration System**: YAML-based configuration with validation
- **Error Handling**: Graceful error handling with configurable actions
- **Test Framework**: Automated testing with JSONL test corpora

## Development

### Adding a New Filter

1. Create a new filter class in `src/filters/`
2. Inherit from `BaseFilter`
3. Implement the `run()` method
4. Add to the filter registry in `tests/test_runner.py`
5. Add test cases to the corpus

### Running Tests

```bash
# Run smoke tests
python3 tests/test_runner.py

# Run with pytest (when implemented)
pytest tests/
```

## Next Steps

- Phase 2: Additional rule-based filters (regex, length, language)
- Phase 3: External API integration (OpenAI Moderation, etc.)
- Phase 4: Advanced features (rate limiting, context controls)

## Contributing

This is an early-stage project. Contributions are welcome!

## License

MIT License - see [LICENSE](LICENSE) file for details. 