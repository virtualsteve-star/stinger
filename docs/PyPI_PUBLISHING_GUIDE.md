# PyPI Publishing Guide for Stinger

## Overview
This guide documents the process for publishing the Stinger Guardrails Framework to PyPI.

## Package Details
- **Package Name**: stinger-guardrails-alpha
- **Current Version**: 0.1.0a1
- **License**: MIT
- **Python Requirements**: >=3.8

## Prerequisites

1. Install build tools:
   ```bash
   pip install build twine
   ```

2. Set up PyPI credentials (one-time setup):
   ```bash
   # Create ~/.pypirc file with your PyPI credentials
   # Or use keyring for secure credential storage
   ```

## Build Process

1. Clean previous builds:
   ```bash
   rm -rf dist/ build/ *.egg-info
   ```

2. Build the package:
   ```bash
   python3 -m build
   ```

3. Validate the build:
   ```bash
   python3 -m twine check dist/*
   ```

## Publishing to Test PyPI

1. Upload to Test PyPI first:
   ```bash
   python3 -m twine upload --repository testpypi dist/*
   ```

2. Test installation from Test PyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ stinger-guardrails-alpha
   ```

## Publishing to Production PyPI

1. Once validated on Test PyPI, upload to production:
   ```bash
   python3 -m twine upload dist/*
   ```

2. Verify installation:
   ```bash
   pip install stinger-guardrails-alpha
   ```

## Installation Options

The package supports several installation configurations:

```bash
# Basic installation (core functionality only)
pip install stinger-guardrails-alpha

# With AI features (includes OpenAI)
pip install stinger-guardrails-alpha[ai]

# For development (includes testing tools)
pip install stinger-guardrails-alpha[dev]

# For web demo
pip install stinger-guardrails-alpha[web-demo]

# Everything
pip install stinger-guardrails-alpha[all]
```

## Version Management

Current versioning strategy:
- Alpha releases: 0.1.0a1, 0.1.0a2, etc.
- Beta releases: 0.1.0b1, 0.1.0b2, etc.
- Release candidates: 0.1.0rc1, 0.1.0rc2, etc.
- Production: 0.1.0, 0.2.0, etc.

## Important Notes

1. **Alpha Status**: The package is currently in alpha. Use the `-alpha` suffix to indicate this is not production-ready.

2. **Dependencies**: Core dependencies are minimal (PyYAML, jsonschema, cryptography). Additional features require optional dependencies.

3. **Package Data**: All YAML configs, keyword lists, and data files are included automatically via MANIFEST.in.

4. **Known Issue**: When testing locally, avoid running imports from the project root directory as `stinger.py` may conflict with the package namespace.

## Troubleshooting

1. **Import Errors**: Test imports from a clean directory, not the project root.

2. **Missing Files**: Ensure MANIFEST.in includes all necessary data files.

3. **Version Conflicts**: Use virtual environments for testing.

## Next Steps After Publishing

1. Update README with PyPI badges
2. Add installation instructions to documentation
3. Create GitHub release matching PyPI version
4. Monitor for installation issues

## Security Considerations

1. Never commit PyPI credentials to the repository
2. Use 2FA on PyPI account
3. Consider using API tokens instead of passwords
4. Review package contents before publishing

---

Last Updated: 2025-07-01