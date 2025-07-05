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