# Phase 12a: Specific Documentation Fixes

## Package Name Fix

**Issue**: Inconsistent package name across docs
**Decision Needed**: Is it `stinger-guardrails-alpha` or `stinger-guardrails`?

### Files to Update:
- README.md (lines 5, 22, 23)
- docs/GETTING_STARTED.md (lines 10-11)
- All example files mentioning pip install

## Import Path Fixes

### README.md

**Line 79-89** - Before:
```python
from stinger import audit
```

**After**:
```python
from stinger.core import audit
```

### docs/GETTING_STARTED.md

**Line 419** - Before:
```python
from stinger import audit
```

**After**:
```python
from stinger.core import audit
```

## Directory Structure Fix

### README.md

**Line 326** - Before:
```
├── filters/        # Guardrail implementations
```

**After**:
```
├── guardrails/     # Guardrail implementations
```

## CLI Command Standardization

### docs/GETTING_STARTED.md

**Line 159** - Before:
```bash
python -m stinger.cli health
```

**After**:
```bash
stinger health
```

**Line 254** - Before:
```bash
python -m stinger.cli health --detailed
```

**After**:
```bash
stinger health --detailed
```

## YAML Configuration Format

### docs/GETTING_STARTED.md

**Lines 471-482** - Before:
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

**After**:
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

## Broken References to Remove

### README.md

**Line 261** - Remove:
```bash
python3 examples/simple_usage.py
```

**Replace with**:
```bash
python3 examples/getting_started/01_basic_installation.py
```

### docs/GETTING_STARTED.md

**Line 224** - Remove:
```bash
python tests/scenarios/run_all_tests.py --scenario customer_service
```

**Replace with**:
```bash
pytest tests/ -v -m "ci"
```

## CLI Version Support

### src/stinger/cli.py

**Add to CLI**:
```python
@click.option('--version', is_flag=True, help='Show version')
def main(version):
    if version:
        import stinger
        click.echo(f"Stinger {stinger.__version__}")
        return
```

## Quick Reference Card

Create a new section in README.md after installation:

```markdown
## 🚀 Quick Start

```python
# 1. Install
pip install stinger-guardrails-alpha

# 2. First Script
from stinger import GuardrailPipeline
pipeline = GuardrailPipeline.from_preset('customer_service')

# 3. Block dangerous content
result = pipeline.check_input("My SSN is 123-45-6789")
print(f"Blocked: {result['blocked']}")  # True

# 4. Allow safe content
result = pipeline.check_input("How do I reset my password?")
print(f"Blocked: {result['blocked']}")  # False
```

## Priority Order

1. **Package name** - Decide and fix everywhere (Critical)
2. **Import paths** - Fix audit imports (Critical)
3. **Broken references** - Remove non-existent files (Critical)
4. **CLI commands** - Standardize format (High)
5. **YAML format** - Show current structure (High)
6. **Directory names** - Fix filters → guardrails (Medium)
7. **Add version flag** - Enhance CLI (Medium)