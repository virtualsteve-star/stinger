# Phase 12: PyPI Publishing and CI/CD Automation

## Overview

Complete the PyPI publishing process that was prepared in Phase 6d, including automated CI/CD publishing on releases, comprehensive documentation updates, and proper name reservation strategy execution.

## Objectives

1. **Reserve PyPI Namespace**: Secure all three package names on PyPI
2. **Publish Alpha Package**: Release stinger-guardrails-alpha to PyPI and TestPyPI
3. **CI/CD Automation**: Set up GitHub Actions for automated publishing
4. **Documentation Updates**: Update all docs to reflect published status
5. **Version Management**: Establish semantic versioning and release process

## Phase Structure

### Phase 12A: PyPI Name Reservation (Day 1)

#### Objectives
- Reserve `stinger` and `stinger-guardrails` as placeholder packages
- Publish `stinger-guardrails-alpha` with the actual framework
- Verify all packages are correctly registered

#### Tasks

1. **Build Placeholder Packages**
   ```bash
   cd placeholders
   ./build_placeholders.sh
   ```

2. **Configure PyPI Credentials**
   - Set up ~/.pypirc with API tokens
   - Or use environment variables for CI/CD

3. **Upload Placeholders to PyPI**
   ```bash
   # Reserve 'stinger' name
   cd placeholders/stinger
   python3 -m twine upload dist/*
   
   # Reserve 'stinger-guardrails' name
   cd ../stinger-guardrails
   python3 -m twine upload dist/*
   ```

4. **Build and Upload Alpha Package**
   ```bash
   cd ../..
   python3 -m build
   python3 -m twine upload dist/stinger_guardrails_alpha-*
   ```

5. **TestPyPI Upload** (for testing)
   ```bash
   python3 -m twine upload --repository testpypi dist/*
   ```

#### Validation
- Verify packages appear on https://pypi.org/project/stinger/
- Verify packages appear on https://pypi.org/project/stinger-guardrails/
- Verify packages appear on https://pypi.org/project/stinger-guardrails-alpha/
- Test installation: `pip install stinger-guardrails-alpha`

### Phase 12B: CI/CD Publishing Automation (Day 2)

#### Objectives
- Create GitHub Actions workflow for automated publishing
- Set up version tagging and release process
- Configure security and access controls

#### Implementation

1. **Create Publishing Workflow** (`.github/workflows/publish.yml`)
   ```yaml
   name: Publish to PyPI
   
   on:
     release:
       types: [published]
     push:
       tags:
         - 'v*'
   
   jobs:
     build-and-publish:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.9'
         
         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install build twine
         
         - name: Build package
           run: python -m build
         
         - name: Check package
           run: twine check dist/*
         
         - name: Publish to TestPyPI
           if: github.event_name == 'push' && contains(github.ref, 'alpha')
           env:
             TWINE_USERNAME: __token__
             TWINE_PASSWORD: ${{ secrets.TEST_PYPI_API_TOKEN }}
           run: |
             twine upload --repository testpypi dist/*
         
         - name: Publish to PyPI
           if: github.event_name == 'release' && github.event.action == 'published'
           env:
             TWINE_USERNAME: __token__
             TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
           run: |
             twine upload dist/*
   ```

2. **Create Version Bump Workflow** (`.github/workflows/version-bump.yml`)
   ```yaml
   name: Version Bump
   
   on:
     workflow_dispatch:
       inputs:
         version_type:
           description: 'Version type (patch/minor/major)'
           required: true
           default: 'patch'
   
   jobs:
     bump-version:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
           with:
             token: ${{ secrets.GITHUB_TOKEN }}
         
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.9'
         
         - name: Install bump2version
           run: pip install bump2version
         
         - name: Bump version
           run: |
             bump2version ${{ github.event.inputs.version_type }}
             git push --follow-tags
   ```

3. **Configure Repository Secrets**
   - Add `PYPI_API_TOKEN` to GitHub repository secrets
   - Add `TEST_PYPI_API_TOKEN` to GitHub repository secrets
   - Document in security guidelines

4. **Create Release Process Documentation**
   ```markdown
   # Release Process
   
   1. Ensure all tests pass on main branch
   2. Run version bump workflow or manually update version
   3. Create GitHub release with tag (e.g., v0.1.0)
   4. CI/CD automatically publishes to PyPI
   5. Verify package installation works
   ```

### Phase 12C: Documentation Updates (Day 3)

#### Objectives
- Update all documentation to reflect published status
- Create installation guides for pip install
- Update README with PyPI badges
- Document the release process

#### Tasks

1. **Update README.md**
   ```markdown
   # Stinger Guardrails Framework
   
   [![PyPI version](https://badge.fury.io/py/stinger-guardrails-alpha.svg)](https://badge.fury.io/py/stinger-guardrails-alpha)
   [![Python Versions](https://img.shields.io/pypi/pyversions/stinger-guardrails-alpha.svg)](https://pypi.org/project/stinger-guardrails-alpha/)
   [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
   
   ## Installation
   
   ```bash
   pip install stinger-guardrails-alpha
   ```
   
   For development:
   ```bash
   pip install stinger-guardrails-alpha[dev]
   ```
   ```

2. **Update GETTING_STARTED.md**
   - Change from local installation to pip install
   - Update all code examples
   - Add troubleshooting section

3. **Update Phase Documentation**
   - Mark Phase 6d as complete
   - Update Phase 12 with completion status
   - Archive old publishing plans

4. **Create RELEASE_NOTES.md**
   ```markdown
   # Release Notes
   
   ## v0.1.0-alpha.1 (2025-01-XX)
   
   ### 🎉 Initial Alpha Release
   
   First public release of Stinger Guardrails Framework!
   
   ### Features
   - 9 built-in guardrails (PII, toxicity, prompt injection, etc.)
   - AI-powered and regex-based detection options
   - Conversation-aware filtering
   - Comprehensive audit logging
   - Easy configuration via YAML
   - FastAPI integration examples
   
   ### Installation
   ```bash
   pip install stinger-guardrails-alpha
   ```
   ```

5. **Update PyPI Package Description**
   - Enhance long_description in pyproject.toml
   - Add project URLs (documentation, issues, etc.)
   - Include classifiers and keywords

### Phase 12D: Testing and Validation (Day 4)

#### Objectives
- Test complete installation process
- Verify CI/CD pipeline works correctly
- Validate documentation accuracy
- Ensure smooth user experience

#### Tasks

1. **Installation Testing**
   ```bash
   # Create fresh virtual environment
   python3 -m venv test_install
   source test_install/bin/activate
   
   # Install from PyPI
   pip install stinger-guardrails-alpha
   
   # Run quickstart
   python -m stinger setup
   
   # Test basic functionality
   stinger demo
   ```

2. **CI/CD Pipeline Testing**
   - Create test release (alpha version)
   - Verify GitHub Actions workflow triggers
   - Confirm package appears on TestPyPI
   - Test automated version bumping

3. **Documentation Validation**
   - Follow all installation guides
   - Test all code examples
   - Verify links work correctly
   - Check PyPI page rendering

4. **User Experience Testing**
   - Fresh user installation flow
   - Verify all dependencies install
   - Test on Python 3.8, 3.9, 3.10, 3.11
   - Document any issues found

## Success Criteria

1. **PyPI Publishing**
   - [ ] All three package names reserved on PyPI
   - [ ] stinger-guardrails-alpha installable via pip
   - [ ] Package metadata displays correctly on PyPI

2. **CI/CD Automation**
   - [ ] GitHub Actions workflow triggers on release
   - [ ] Automated publishing works without manual intervention
   - [ ] Version management is automated

3. **Documentation**
   - [ ] README shows PyPI badges and pip install
   - [ ] All guides updated for pip installation
   - [ ] Release process documented

4. **Testing**
   - [ ] Package installs cleanly on all Python versions
   - [ ] No dependency conflicts
   - [ ] Examples work with pip-installed package

## Risk Mitigation

1. **Name Conflicts**: Reserve names immediately in Phase 12A
2. **Security**: Use API tokens, never passwords
3. **Version Conflicts**: Test thoroughly before publishing
4. **Documentation Drift**: Update all docs in same PR

## Timeline

- **Day 1**: PyPI name reservation and initial publishing
- **Day 2**: CI/CD automation setup
- **Day 3**: Documentation updates
- **Day 4**: Testing and validation

Total Duration: 4 days

## Dependencies

- PyPI account with API tokens
- GitHub repository secrets configured
- All tests passing on main branch
- Version number decided (0.1.0-alpha.1)

## Next Steps

After Phase 12 completion:
1. Monitor package downloads and user feedback
2. Plan transition from alpha to beta
3. Consider consolidating to main package name
4. Implement user feedback and bug fixes