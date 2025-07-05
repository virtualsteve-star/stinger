# Stinger Repository Cleanup Report

## Summary
The repository is generally well-organized, but there are some items that could be cleaned up to reduce clutter.

## Items to Clean Up

### 1. Python Cache Files (__pycache__)
Found multiple `__pycache__` directories throughout the codebase:
- `./tests/ci/__pycache__/`
- `./tests/integration/__pycache__/`
- `./tests/shared/__pycache__/`
- And many more...

**Recommendation**: Add `__pycache__/` to `.gitignore` and remove all existing cache directories.

### 2. Log Files
Found numerous log files that should not be in version control:
- `./logs/*.log`
- `./demos/web_demo/*.log`
- `./demos/web_demo/backend/*.log`
- `./examples/getting_started/audit.log`

**Recommendation**: Add `*.log` to `.gitignore` and remove all log files.

### 3. Test Backup Directory
- `./demos/web_demo/test_backup_20250701_154107/` - Contains 14 old test files

**Recommendation**: Remove this backup directory.

### 4. Build Artifacts
- `./dist/stinger_guardrails_alpha-0.1.0a1.tar.gz`
- `./placeholders/stinger/dist/stinger-0.0.1.tar.gz`
- `./placeholders/stinger-guardrails/dist/stinger_guardrails-0.0.1.tar.gz`

**Recommendation**: Add `dist/` to `.gitignore` and remove these files.

### 5. Backup Files
- `./tests/test_simple.py.bak`
- `./tests/test_global_rate_limiting_simple.py.bak`

**Recommendation**: Remove `.bak` files and add `*.bak` to `.gitignore`.

### 6. One-off Fix Scripts
The `scripts/` directory contains many one-time fix scripts that are no longer needed:
- `fix_action_tests.py`
- `fix_async_tests.py`
- `fix_docstring_quotes.py`
- `fix_import_order.py`
- `fix_parentheses.py`
- `fix_remaining_imports.py`
- `fix_simple_guardrail_calls.py`
- `fix_test_imports_v2.py`
- `fix_test_imports.py`
- `fix_url_guardrail_calls.py`

**Recommendation**: Archive or remove these one-time fix scripts.

### 7. Web Demo node_modules
- `./demos/web_demo/node_modules/` - This appears to be committed to the repo

**Recommendation**: Add `node_modules/` to `.gitignore` and remove from version control.

### 8. Placeholders Directory
- `./placeholders/` - Contains placeholder packages

**Recommendation**: Evaluate if these are still needed. If not, remove them.

## Recommended .gitignore Additions

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

# Logs
*.log
logs/

# Backups
*.bak
*.orig
*~
*.swp
*.swo

# Test artifacts
.coverage
.pytest_cache/
.tox/
htmlcov/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.idea/
.vscode/
*.sublime-*

# OS
.DS_Store
Thumbs.db

# Temporary
*.tmp
*.temp
/tmp/
```

## Clean Commands

To clean up, run these commands:

```bash
# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Remove logs
find . -name "*.log" -type f -delete

# Remove backup files
find . -name "*.bak" -type f -delete

# Remove test backup directory
rm -rf ./demos/web_demo/test_backup_20250701_154107/

# Remove dist files (after confirming they're not needed)
rm -rf ./dist/
rm -rf ./placeholders/*/dist/

# Remove node_modules from git (if tracked)
git rm -r --cached demos/web_demo/node_modules/
```

## Summary

The repository structure is good, but cleaning up these items would:
1. Reduce repository size
2. Improve clone/pull times
3. Remove confusion from old/temporary files
4. Follow best practices for version control

Most importantly, updating `.gitignore` will prevent these issues from recurring.