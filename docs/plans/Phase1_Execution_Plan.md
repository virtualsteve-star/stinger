# Phase 1 Execution Plan – Minimal Scaffolding & Testing

**Status: ✅ COMPLETED**  
**Version: 0.0.1**  
**Start Date**: 2025-06-22  
**Completion Date**: 2025-06-23  
**See: [VERSION_HISTORY.md](../VERSION_HISTORY.md) for detailed release notes**

## Summary of Achievements
- All success criteria met and exceeded
- Completed in ~1 hour (vs planned 5-6 hours)
- Added bonus features: KeywordBlockGuardrail, pipeline chaining, GitHub repo setup
- All 12 smoke tests passing
- Ready for Phase 2 development

---

**Goal**: Get basic framework working with pass-through functionality and minimal test coverage.

## 1. Project Structure

```
stinger/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── pipeline.py          # FilterPipeline class
│   │   ├── base_filter.py       # BaseGuardrail abstract class
│   │   └── config.py            # ConfigLoader class
│   ├── filters/
│   │   ├── __init__.py
│   │   └── pass_through.py      # Simple pass-through filter
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py        # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_corpus/
│   │   └── smoke_test.jsonl     # 10 simple test cases
│   ├── test_pipeline.py
│   ├── test_config.py
│   └── test_runner.py           # Simple test runner
├── configs/
│   └── minimal.yaml             # Basic configuration
├── requirements.txt
├── setup.py
└── README.md
```

## 2. Core Implementation (Minimal)

### 2.1 BaseGuardrail Class
```python
# Simple abstract base class
class BaseGuardrail:
    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get('enabled', True)
    
    async def run(self, content: str) -> FilterResult:
        raise NotImplementedError
    
    def validate_config(self) -> bool:
        return True
```

### 2.2 FilterResult Class
```python
# Simple result class
@dataclass
class FilterResult:
    action: str  # 'allow', 'block', 'warn', 'modify'
    confidence: float = 1.0
    reason: str = ""
    modified_content: str = None
```

### 2.3 FilterPipeline Class
```python
# Basic pipeline that runs filters in order
class FilterPipeline:
    def __init__(self, guardrails: List[BaseGuardrail]):
        self.guardrails = filters
    
    async def process(self, content: str) -> PipelineResult:
        # Simple sequential processing
        # Return first 'block' or final 'allow'
```

### 2.4 ConfigLoader Class
```python
# Basic YAML loader with minimal validation
class ConfigLoader:
    def load(self, config_path: str) -> dict:
        # Load YAML, basic syntax validation
        # Return config dict
```

## 3. Pass-Through Filter

```python
# Simplest possible filter - just passes content through
class PassThroughGuardrail(BaseGuardrail):
    async def run(self, content: str) -> FilterResult:
        return FilterResult(action='allow', reason='pass_through')
```

## 4. Minimal Configuration

```yaml
# configs/minimal.yaml
version: "1.0"
pipeline:
  input:
    - name: "pass_through"
      type: "pass_through"
      enabled: true
      on_error: "allow"  # Simple error handling
```

## 5. Test Corpus (10 Cases)

```jsonl
# tests/test_corpus/smoke_test.jsonl
{"input": "Hello world", "expected": "allow", "description": "Basic English text"}
{"input": "", "expected": "allow", "description": "Empty string"}
{"input": "Test with numbers 123", "expected": "allow", "description": "Text with numbers"}
{"input": "Special chars: !@#$%", "expected": "allow", "description": "Special characters"}
{"input": "Unicode: 你好世界", "expected": "allow", "description": "Unicode text"}
{"input": "Very long text " * 100, "expected": "allow", "description": "Long text"}
{"input": "URL: https://example.com", "expected": "allow", "description": "Contains URL"}
{"input": "Email: test@example.com", "expected": "allow", "description": "Contains email"}
{"input": "Mixed: 123 !@# 你好 https://test.com", "expected": "allow", "description": "Mixed content"}
{"input": None, "expected": "allow", "description": "None input"}
```

## 6. Test Runner (Simple)

```python
# tests/test_runner.py
async def run_smoke_test():
    # Load config
    # Create pipeline with pass-through filter
    # Run all test cases
    # Report pass/fail
    # Return success/failure
```

## 7. Implementation Steps

### Step 1: Basic Structure (1 hour)
- Create directory structure
- Create `__init__.py` files
- Set up `requirements.txt` with minimal dependencies (`pyyaml`, `pytest`, `pytest-asyncio`)

### Step 2: Core Classes (2 hours)
- Implement `BaseGuardrail` abstract class
- Implement `FilterResult` dataclass
- Implement `FilterPipeline` with basic sequential processing
- Implement `ConfigLoader` with YAML loading

### Step 3: Pass-Through Filter (30 minutes)
- Implement `PassThroughGuardrail` class
- Test basic instantiation and running

### Step 4: Configuration (30 minutes)
- Create `minimal.yaml` config
- Test config loading and validation

### Step 5: Test Framework (1 hour)
- Create test corpus with 10 simple cases
- Implement basic test runner
- Write unit tests for core classes

### Step 6: Integration Test (30 minutes)
- End-to-end test: load config → create pipeline → process test cases
- Verify all smoke tests pass

## 8. Success Criteria

- [ ] All 10 smoke tests pass
- [ ] Pipeline processes input → output unchanged (pass-through works)
- [ ] Config validation rejects invalid YAML
- [ ] Basic error handling works (filter crashes don't crash pipeline)
- [ ] Can run `python -m pytest tests/` successfully

## 9. Dependencies

```
pyyaml>=6.0
pytest>=7.0
pytest-asyncio>=0.21.0
```

## 10. What We're NOT Doing in Phase 1

- Complex error handling (just basic try/catch)
- Circuit breakers
- External API calls
- Complex validation
- Performance optimization
- Logging/metrics
- CLI interface

## 11. Next Phase Preparation

This minimal foundation will let us:
- Verify the basic architecture works
- Test the configuration system
- Ensure the pipeline can handle multiple filters
- Have a working test framework for Phase 2

**Estimated Time**: 5-6 hours total
**Risk Level**: Low (simple pass-through functionality) 