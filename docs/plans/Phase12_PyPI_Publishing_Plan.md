# Phase 12: PyPI Publishing and CI/CD Automation

## Overview
Publish Stinger to PyPI as `stinger-guardrails` package and set up automated CI/CD for future releases.

## Goals
1. Make Stinger easily installable via `pip install stinger-guardrails`
2. Establish automated release process through GitHub Actions
3. Maintain both Test PyPI and Production PyPI releases
4. Update all documentation to reflect pip installation

## Package Names Strategy
- **Primary**: `stinger-guardrails` (most descriptive and available)
- **Already taken**: `stinger` (by another project)
- **Alpha releases**: Use version suffix (e.g., 0.1.0a2)

## Implementation Steps

### Step 1: Package Preparation
- [x] Review pyproject.toml configuration
- [ ] Update package metadata (description, keywords, classifiers)
- [ ] Ensure all dependencies are correctly specified
- [ ] Verify entry points (CLI commands)

### Step 2: Build and Test Locally
- [ ] Build distribution packages (wheel and sdist)
- [ ] Test installation in fresh virtual environment
- [ ] Verify CLI commands work after pip install
- [ ] Check all imports resolve correctly

### Step 3: Test PyPI Upload
- [ ] Create Test PyPI account/token
- [ ] Upload to Test PyPI
- [ ] Test installation from Test PyPI
- [ ] Verify package contents and functionality

### Step 4: Production PyPI Upload
- [ ] Create PyPI account/token
- [ ] Upload version 0.1.0a2
- [ ] Test installation from PyPI
- [ ] Verify package page displays correctly

### Step 5: GitHub Actions Automation
- [ ] Create `.github/workflows/publish.yml`
- [ ] Set up PyPI token as GitHub secret
- [ ] Configure trigger on version tags
- [ ] Test automated publishing with test release

### Step 6: Documentation Updates
- [ ] Update README with pip installation instructions
- [ ] Update getting_started.md
- [ ] Add RELEASING.md with release process
- [ ] Update CHANGELOG

## Technical Details

### Package Structure
```
stinger-guardrails/
├── src/
│   └── stinger/        # Package code
├── tests/              # Test suite
├── examples/           # Example scripts
├── docs/               # Documentation
├── pyproject.toml      # Package configuration
├── README.md           # Package description
└── LICENSE             # MIT License
```

### Version Strategy
- Current: 0.1.0a1
- Next: 0.1.0a2 (this release)
- Future: 0.1.0 (first stable)

### Dependencies Management
- Use pyproject.toml for all package metadata
- Specify minimum Python version (3.8+)
- Include optional dependencies groups

## Success Criteria
1. `pip install stinger-guardrails` works from PyPI
2. All CLI commands function correctly
3. Documentation reflects pip installation
4. GitHub Actions publishes on tag push
5. Test PyPI used for release testing

## Timeline
- Day 1: Package preparation and local testing
- Day 2: Test PyPI upload and verification
- Day 3: Production PyPI release
- Day 4: GitHub Actions setup and documentation

## Notes
- PyPI doesn't allow deletion of releases (only yanking)
- Test thoroughly on Test PyPI first
- Keep PyPI tokens secure (use GitHub secrets)
- Consider adding shields.io badges to README