# Releasing Stinger

This document describes how to release new versions of Stinger to PyPI.

## Prerequisites

1. PyPI account with access to `stinger-guardrails-alpha` package
2. Test PyPI account for testing releases
3. GitHub repository admin access for creating releases
4. API tokens configured as GitHub secrets:
   - `PYPI_API_TOKEN` - for production PyPI
   - `TEST_PYPI_API_TOKEN` - for Test PyPI

## Release Process

### 1. Update Version Numbers

Use bumpversion to update all version references:

```bash
# For alpha releases (e.g., 0.1.0a3 → 0.1.0a4)
bumpversion build

# For beta releases (e.g., 0.1.0a4 → 0.1.0b1)
bumpversion release --new-values b

# For release candidates (e.g., 0.1.0b1 → 0.1.0rc1)
bumpversion release --new-values rc

# For production releases (e.g., 0.1.0rc1 → 0.1.0)
bumpversion release --new-values prod
```

Or manually update:
- `pyproject.toml` - version field
- `src/stinger/__init__.py` - __version__ variable
- `.bumpversion.cfg` - current_version field

### 2. Update CHANGELOG.md

Add a new section with:
- Version number and date
- Summary of changes
- Major features
- Bug fixes
- Breaking changes (if any)

### 3. Build and Test Locally

```bash
# Run the build script
./scripts/build_package.sh

# Test installation in a fresh virtual environment
python3 -m venv test_env
source test_env/bin/activate
pip install dist/stinger_guardrails_alpha-*.whl
stinger demo  # Test CLI works
python -c "from stinger import GuardrailPipeline; print('Import works!')"
deactivate
rm -rf test_env
```

### 4. Test on Test PyPI (Recommended)

```bash
# Upload to Test PyPI
python3 -m twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install -i https://test.pypi.org/simple/ stinger-guardrails-alpha==VERSION
```

### 5. Create GitHub Release

1. Go to https://github.com/virtualsteve-star/stinger/releases
2. Click "Draft a new release"
3. Create a new tag (e.g., `v0.1.0a3`)
4. Set release title (e.g., "v0.1.0a3 - PyPI Publishing & Management Console")
5. Copy relevant CHANGELOG entries to release description
6. Check "This is a pre-release" for alpha/beta versions
7. Click "Publish release"

This will automatically trigger the GitHub Action to publish to PyPI.

### 6. Manual PyPI Upload (if needed)

If the GitHub Action fails or for manual upload:

```bash
# Ensure you have the latest build
./scripts/build_package.sh

# Upload to PyPI
python3 -m twine upload dist/*
```

### 7. Verify Release

```bash
# Wait a few minutes for PyPI to update
pip install --upgrade stinger-guardrails-alpha

# Verify correct version
python -c "import stinger; print(stinger.__version__)"
```

### 8. Update Documentation

After successful release:
1. Update README.md if needed
2. Update installation instructions
3. Announce on relevant channels

## Troubleshooting

### Build Errors
- Ensure all dependencies in pyproject.toml are correct
- Check for syntax errors in Python files
- Verify all data files are included in package

### Upload Errors
- Check API token is correct and has upload permissions
- Ensure package name is not taken (for new packages)
- Verify version number hasn't been used before

### Installation Errors
- Test with `--no-cache-dir` flag
- Check Python version compatibility
- Verify all dependencies are available on PyPI

## Notes

- PyPI doesn't allow re-uploading the same version (can only yank)
- Always test on Test PyPI first for new package configurations
- Keep API tokens secure and rotate periodically
- Consider using trusted publishers (GitHub OIDC) in the future