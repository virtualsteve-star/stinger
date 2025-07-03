#!/bin/bash
# Local CI Check Script
# Run this before creating PRs to catch CI issues early

set -e  # Exit on first error

echo "🔍 Running local CI checks..."
echo "================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Must run from Stinger root directory"
    exit 1
fi

# 1. Black formatting
echo ""
echo "1️⃣  Checking Black formatting..."
if python3 -m black --check src/ tests/; then
    echo "✅ Black formatting OK"
else
    echo "❌ Black formatting issues found!"
    echo "   Run: python3 -m black src/ tests/"
    exit 1
fi

# 2. Import ordering
echo ""
echo "2️⃣  Checking import ordering..."
if python3 -m isort --check-only --diff src/ tests/; then
    echo "✅ Import ordering OK"
else
    echo "❌ Import ordering issues found!"
    echo "   Run: python3 -m isort src/ tests/"
    exit 1
fi

# 3. Flake8 linting
echo ""
echo "3️⃣  Running flake8..."
if ! python3 -c "import flake8" 2>/dev/null; then
    echo "⚠️  Flake8 not installed. Install with: pip install flake8"
    echo "   Skipping flake8 check..."
else
    if python3 -m flake8 src/ tests/; then
        echo "✅ Flake8 checks passed"
    else
        echo "❌ Flake8 issues found!"
        exit 1
    fi
fi

# 4. Python 3.8 syntax check (if available)
echo ""
echo "4️⃣  Checking Python 3.8 compatibility..."
if command -v python3.8 &> /dev/null; then
    if python3.8 -m py_compile src/stinger/core/*.py; then
        echo "✅ Python 3.8 syntax OK"
    else
        echo "❌ Python 3.8 syntax errors found!"
        exit 1
    fi
else
    echo "⚠️  Python 3.8 not found, skipping compatibility check"
fi

# 5. Run tests
echo ""
echo "5️⃣  Running pytest..."
if python3 -m pytest --tb=short; then
    echo "✅ All tests passed"
else
    echo "❌ Test failures found!"
    exit 1
fi

# 6. Check for common issues
echo ""
echo "6️⃣  Checking for common issues..."

# Check for boolean comparisons
if grep -r "== True\|== False" src/ tests/ --include="*.py" | grep -v ".flake8"; then
    echo "⚠️  Found boolean comparisons using '=='. Use 'is' instead."
fi

# Check for undefined names (basic check)
if grep -r "name 'filter'" tests/ --include="*.py" | grep -v "guardrail"; then
    echo "⚠️  Found possible undefined 'filter' (should be 'guardrail'?)"
fi

echo ""
echo "================================"
echo "✅ All local CI checks complete!"
echo ""
echo "Ready to create PR? Run:"
echo "  git push origin dev"
echo "  gh pr create --base main --head dev"
echo ""