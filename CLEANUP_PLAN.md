# Stinger Repository Cleanup Plan

## Overview
Based on QA review and repository analysis, here's a comprehensive cleanup plan to remove cruft and improve maintainability.

## High Priority Cleanups

### 1. Remove node_modules from Git (CRITICAL)
**Impact**: Massive repo size reduction
```bash
# Remove from git but keep locally
git rm -r --cached demos/web_demo/node_modules/
git rm -r --cached management-console/frontend/node_modules/
```

### 2. Remove Test Backup Directory
**Path**: `demos/web_demo/test_backup_20250701_154107/`
**Contains**: 14 old test files from consolidation
```bash
rm -rf demos/web_demo/test_backup_20250701_154107/
```

### 3. Remove Legacy Scripts
```bash
# Test consolidation script (job complete)
rm demos/web_demo/consolidate_tests.py

# Legacy startup script
rm demos/web_demo/start_demo_complex_backup.py

# Old test script
rm demos/web_demo/backend/test_core_fixes.py
```

### 4. Clean Python Cache
```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
```

### 5. Remove Log Files
```bash
find . -name "*.log" -type f -delete
```

### 6. Remove Backup Files
```bash
find . -name "*.bak" -type f -delete
find . -name "*.orig" -type f -delete
find . -name "*~" -type f -delete
```

### 7. Clean One-Time Fix Scripts
**Location**: `scripts/`
```bash
# Archive or remove these one-time scripts
rm scripts/fix_action_tests.py
rm scripts/fix_async_tests.py
rm scripts/fix_docstring_quotes.py
rm scripts/fix_import_order.py
rm scripts/fix_parentheses.py
rm scripts/fix_remaining_imports.py
rm scripts/fix_simple_guardrail_calls.py
rm scripts/fix_test_imports.py
rm scripts/fix_test_imports_v2.py
rm scripts/fix_url_guardrail_calls.py
```

### 8. Clean Build Artifacts
```bash
rm -rf dist/
rm -rf placeholders/*/dist/
rm -rf build/
rm -rf *.egg-info/
```

## Update .gitignore

Add these entries to prevent future cruft:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Logs
*.log
logs/
*.log.*

# Backups
*.bak
*.orig
*~
*.swp
*.swo
.*.swp

# Test artifacts
.coverage
.coverage.*
.pytest_cache/
.tox/
htmlcov/
.hypothesis/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnp
.pnp.js

# IDE
.idea/
.vscode/
*.sublime-*
.project
.pydevproject

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary
*.tmp
*.temp
/tmp/
temp/

# Environment
.env
.env.local
.env.*.local
venv/
ENV/
env/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre
.pyre/

# pytype
.pytype/
```

## Review Placeholders Directory

The `placeholders/` directory contains:
- Empty placeholder packages
- Build scripts

**Action**: Review if these are still needed for PyPI namespace reservation. If not, remove entire directory.

## Cleanup Commands Script

Create `scripts/cleanup_repo.sh`:

```bash
#!/bin/bash
set -e

echo "🧹 Starting repository cleanup..."

# Remove node_modules from git
echo "Removing node_modules from git..."
git rm -r --cached demos/web_demo/node_modules/ 2>/dev/null || true
git rm -r --cached management-console/frontend/node_modules/ 2>/dev/null || true

# Remove test backup directory
echo "Removing test backup directory..."
rm -rf demos/web_demo/test_backup_20250701_154107/

# Remove legacy scripts
echo "Removing legacy scripts..."
rm -f demos/web_demo/consolidate_tests.py
rm -f demos/web_demo/start_demo_complex_backup.py
rm -f demos/web_demo/backend/test_core_fixes.py

# Clean Python cache
echo "Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Remove logs
echo "Removing log files..."
find . -name "*.log" -type f -delete 2>/dev/null || true

# Remove backups
echo "Removing backup files..."
find . -name "*.bak" -type f -delete 2>/dev/null || true
find . -name "*.orig" -type f -delete 2>/dev/null || true
find . -name "*~" -type f -delete 2>/dev/null || true

# Clean one-time fix scripts
echo "Cleaning one-time fix scripts..."
rm -f scripts/fix_*.py 2>/dev/null || true

# Clean build artifacts
echo "Cleaning build artifacts..."
rm -rf dist/ build/ *.egg-info/ 2>/dev/null || true
rm -rf placeholders/*/dist/ 2>/dev/null || true

echo "✅ Cleanup complete!"
echo ""
echo "Next steps:"
echo "1. Review and update .gitignore"
echo "2. Commit these changes"
echo "3. Consider removing placeholders/ directory if not needed"
```

## Summary

This cleanup will:
1. **Reduce repo size dramatically** (removing node_modules alone saves hundreds of MB)
2. **Remove ~30+ unnecessary files**
3. **Eliminate confusion** from old test files and scripts
4. **Improve clone/pull times**
5. **Follow best practices** for version control

## Execution Order

1. First, update `.gitignore` to prevent re-adding these files
2. Run the cleanup script or commands
3. Review the changes with `git status`
4. Commit with message: "Clean up repository: remove node_modules, old tests, and build artifacts"
5. Push to dev branch

This addresses all findings from both the QA report and my analysis.