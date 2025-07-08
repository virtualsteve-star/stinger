# Phase 12a: GitHub Release & Package Strategy

## Current Status
- ❌ No GitHub Releases created yet
- ❌ No GitHub Packages published
- ✅ PyPI publishing infrastructure ready (Phase 12)
- ✅ Version 0.1.0a3 tagged in code

## GitHub Release Plan

### 1. Create First Release (v0.1.0a3)

**When**: After Phase 12a documentation fixes are complete

**Release Title**: `v0.1.0a3 - Alpha Release: PyPI Ready`

**Release Notes**:
```markdown
## 🚀 Stinger v0.1.0a3 - Alpha Release

First public alpha release of Stinger, the AI Guardrails Framework!

### ✨ Features
- 🛡️ **Comprehensive Guardrails**: PII detection, toxicity filtering, prompt injection protection
- 🔒 **Security Audit Trail**: Complete logging for compliance and forensics  
- ⚡ **High Performance**: <10ms overhead with async support
- 🎯 **Simple API**: Get started in minutes with presets
- 🔧 **Extensible**: Create custom guardrails for your needs

### 📦 Installation
```bash
pip install stinger-guardrails-alpha
```

### 🚀 Quick Start
```python
from stinger import GuardrailPipeline

pipeline = GuardrailPipeline.from_preset('customer_service')
result = pipeline.check_input("My SSN is 123-45-6789")
print(f"Blocked: {result['blocked']}")  # True - PII detected!
```

### 📚 Documentation
- [Getting Started Guide](docs/GETTING_STARTED.md)
- [API Reference](docs/API_REFERENCE.md)
- [Examples](examples/getting_started/)

### 🧪 This is an Alpha Release
- API may change in future versions
- Please report issues and feedback
- Not recommended for production use yet

### 📊 What's Included
- Core guardrail framework
- 9+ guardrail types
- Conversation tracking
- Rate limiting
- Health monitoring
- Web demo application
- Management console

### 🔄 Coming Soon
- More guardrail types
- Performance optimizations
- Enhanced documentation
- Production deployment guides
```

**Assets to Attach**:
- Source code (zip)
- Source code (tar.gz)
- Optional: Pre-built wheel file

### 2. GitHub Actions Integration

The `.github/workflows/publish.yml` workflow will:
1. Trigger on release creation
2. Build packages
3. Upload to PyPI automatically

### 3. Future Releases

**v0.1.0a4** (After Phase 12a):
- All documentation fixes
- Terminology updates (filter → guardrail)
- Working examples
- Polished user experience

**v0.1.0** (First stable):
- API stability guarantee
- Production-ready
- Complete documentation
- Performance benchmarks

## GitHub Packages Strategy

### Option 1: Docker Images (Future)
```dockerfile
FROM python:3.9-slim
RUN pip install stinger-guardrails
# Ready-to-use guardrail service
```

### Option 2: GitHub Container Registry
- Host pre-configured demo applications
- Management console container
- Development environment

### Current Focus
For now, focus on:
1. **GitHub Releases** - For version tracking and PyPI triggers
2. **PyPI** - Primary distribution method
3. **Documentation** - Clear installation instructions

## Terminology Update Plan

### Files to Check for "filter" → "guardrail"
1. All files in `/examples/`
2. All files in `/demos/`
3. Documentation files
4. Code comments in examples

### Common Replacements
- "filter" → "guardrail"
- "Filter" → "Guardrail"
- "filtering" → "guardrail protection"
- "content filter" → "content guardrail"

### Exceptions (Keep as-is)
- Technical terms like "filter" in code (e.g., Python's filter() function)
- Historical references in changelogs
- Internal implementation details

## Action Items

### Immediate (Before v0.1.0a3 release)
1. [ ] Fix all documentation issues from Phase 12a
2. [ ] Update terminology (filter → guardrail) 
3. [ ] Test PyPI package works
4. [ ] Create GitHub Release
5. [ ] Verify GitHub Action triggers

### Future Considerations
1. [ ] Create release automation script
2. [ ] Add release checklist template
3. [ ] Consider GitHub Packages for containers
4. [ ] Set up release branches strategy

## Release Checklist

Before creating GitHub Release:
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Examples work
- [ ] Version numbers consistent
- [ ] CHANGELOG updated
- [ ] PyPI test successful
- [ ] No "filter" terminology in user-facing content