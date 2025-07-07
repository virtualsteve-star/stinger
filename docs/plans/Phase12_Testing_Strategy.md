# Phase 12 PyPI Publishing - Testing Strategy

## Overview
This document outlines how we'll verify that the PyPI publishing worked correctly.

## Testing Phases

### 1. Pre-Publish Verification
Run before uploading to catch issues early:

```bash
./scripts/pre_publish_check.sh
```

This verifies:
- Version consistency across all files
- Clean git working directory
- Tests pass locally
- Package structure is correct
- Documentation is up to date

### 2. Test PyPI Upload
First upload to Test PyPI to verify the package:

```bash
# Build the package
./scripts/build_package.sh

# Upload to Test PyPI
./scripts/upload_to_pypi.sh
# Choose option 1 (Test PyPI)
```

### 3. Test PyPI Installation Test
Test installation from Test PyPI:

```bash
# Run automated test
./scripts/test_pypi_package.sh
# Choose option 1 (Test PyPI)
```

This tests:
- Package installs successfully
- Version is correct
- CLI commands work
- All imports resolve
- Basic functionality works
- Dependencies are installed

### 4. Production PyPI Upload
After Test PyPI verification:

```bash
./scripts/upload_to_pypi.sh
# Choose option 2 (Production PyPI)
```

### 5. Production Verification
Comprehensive verification after production upload:

```bash
# Quick test
./scripts/test_pypi_package.sh
# Choose option 2 (Production PyPI)

# Comprehensive test
pip install stinger-guardrails-alpha
python3 scripts/verify_pypi_release.py
```

### 6. Real-World Test
Create a fresh project to test as a real user would:

```bash
# Create new project
mkdir test-stinger-project
cd test-stinger-project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install from PyPI
pip install stinger-guardrails-alpha

# Create test script
cat > test_stinger.py << 'EOF'
from stinger import GuardrailPipeline

# Test basic functionality
pipeline = GuardrailPipeline.from_preset('customer_service')

# Test PII detection
result = pipeline.check_input("My SSN is 123-45-6789")
print(f"PII Detection: {'✅ Blocked' if result['blocked'] else '❌ Failed'}")

# Test safe content
result = pipeline.check_input("Hello, I need help")
print(f"Safe Content: {'✅ Passed' if not result['blocked'] else '❌ Failed'}")

# Test CLI
import subprocess
try:
    subprocess.run(['stinger', '--version'], check=True)
    print("CLI Command: ✅ Works")
except:
    print("CLI Command: ❌ Failed")
EOF

# Run test
python test_stinger.py
```

## Success Criteria

### ✅ Package Metadata
- Package name: `stinger-guardrails-alpha`
- Version: `0.1.0a3`
- Author and description correct
- License shows as MIT
- Homepage links to GitHub

### ✅ Installation
- `pip install stinger-guardrails-alpha` works
- No dependency conflicts
- Installs on Python 3.8+

### ✅ Functionality
- All imports work (`from stinger import ...`)
- CLI command `stinger` is available
- Presets load correctly
- Guardrails function as expected
- Audit trail works

### ✅ Package Contents
- All source files included
- Data files (YAML configs) included
- Examples accessible
- Documentation readable

## Troubleshooting

### If Test Fails

1. **Import Errors**
   - Check package_data in pyproject.toml
   - Verify all __init__.py files exist
   - Check relative imports

2. **Missing Files**
   - Verify MANIFEST.in if needed
   - Check setuptools.package-data config
   - Ensure files aren't in .gitignore

3. **CLI Not Found**
   - Check project.scripts in pyproject.toml
   - Verify entry point is correct
   - Test with `python -m stinger.cli`

4. **Version Mismatch**
   - Run version update across all files
   - Rebuild package
   - Clear pip cache if needed

## Automated CI Test

Once manual testing passes, the GitHub Action will automatically test on every release:

1. Trigger by creating a GitHub release
2. Action builds and uploads to PyPI
3. Consider adding post-upload verification step

## Timeline

1. **Pre-publish checks**: 5 minutes
2. **Test PyPI upload & test**: 10 minutes
3. **Production upload**: 5 minutes
4. **Verification suite**: 10 minutes
5. **Real-world test**: 5 minutes

Total: ~35 minutes for complete verification

## Next Steps

After successful publishing:
1. Update README badges (version, PyPI)
2. Announce release on relevant channels
3. Monitor PyPI download stats
4. Gather user feedback
5. Plan next release (0.1.0a4 or 0.1.0)