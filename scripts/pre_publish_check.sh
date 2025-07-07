#!/bin/bash
# Pre-publish checklist for PyPI release

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "📋 Stinger Pre-Publish Checklist"
echo "================================"

CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to run a check
run_check() {
    local check_name="$1"
    local check_command="$2"
    local check_description="$3"
    
    echo -n "Checking $check_name... "
    
    if eval "$check_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $check_description"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}❌${NC} $check_description"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# 1. Check version consistency
echo -e "\n${BLUE}1. Version Consistency${NC}"
PYPROJECT_VERSION=$(grep -E "^version = " pyproject.toml | cut -d'"' -f2)
INIT_VERSION=$(grep -E "^__version__ = " src/stinger/__init__.py | cut -d'"' -f2)
BUMP_VERSION=$(grep -E "^current_version = " .bumpversion.cfg | cut -d' ' -f3)

if [ "$PYPROJECT_VERSION" = "$INIT_VERSION" ] && [ "$PYPROJECT_VERSION" = "$BUMP_VERSION" ]; then
    echo -e "${GREEN}✅${NC} Version consistent: $PYPROJECT_VERSION"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}❌${NC} Version mismatch:"
    echo "   pyproject.toml: $PYPROJECT_VERSION"
    echo "   __init__.py: $INIT_VERSION"
    echo "   .bumpversion.cfg: $BUMP_VERSION"
    ((CHECKS_FAILED++))
fi

# 2. Check for uncommitted changes
echo -e "\n${BLUE}2. Git Status${NC}"
run_check "uncommitted changes" "[ -z \"\$(git status --porcelain)\" ]" "Working directory clean"

# 3. Check tests pass
echo -e "\n${BLUE}3. Tests${NC}"
run_check "pytest" "python3 -m pytest tests/test_simple_pii_detection_guardrail.py -v -q" "Core tests pass"

# 4. Check imports work
echo -e "\n${BLUE}4. Import Check${NC}"
run_check "imports" "python3 -c 'from stinger import GuardrailPipeline, audit, Conversation'" "Core imports work"

# 5. Check CLI entry point
echo -e "\n${BLUE}5. CLI Entry Point${NC}"
run_check "CLI" "python3 -m stinger.cli --help" "CLI entry point works"

# 6. Check package structure
echo -e "\n${BLUE}6. Package Structure${NC}"
run_check "src layout" "[ -d src/stinger ]" "Source directory exists"
run_check "init file" "[ -f src/stinger/__init__.py ]" "Package init exists"
run_check "CLI module" "[ -f src/stinger/cli.py ]" "CLI module exists"

# 7. Check documentation
echo -e "\n${BLUE}7. Documentation${NC}"
run_check "README" "[ -f README.md ]" "README.md exists"
run_check "LICENSE" "[ -f LICENSE ]" "LICENSE file exists"
run_check "CHANGELOG" "grep -q '0.1.0a3' CHANGELOG.md" "CHANGELOG updated for current version"

# 8. Check build dependencies
echo -e "\n${BLUE}8. Build Dependencies${NC}"
run_check "build module" "python3 -c 'import build'" "build module installed"
run_check "twine module" "python3 -c 'import twine'" "twine module installed"

# 9. Check PyPI credentials
echo -e "\n${BLUE}9. PyPI Configuration${NC}"
if [ -f ~/.pypirc ]; then
    echo -e "${GREEN}✅${NC} .pypirc file exists"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠️${NC}  .pypirc not found - will need to enter credentials"
fi

# 10. Check for existing dist files
echo -e "\n${BLUE}10. Distribution Files${NC}"
if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
    echo -e "${YELLOW}⚠️${NC}  Existing files in dist/ - consider cleaning"
    ls -la dist/
else
    echo -e "${GREEN}✅${NC} dist/ directory clean"
    ((CHECKS_PASSED++))
fi

# Summary
echo -e "\n${BLUE}========== Summary ==========${NC}"
echo -e "Checks passed: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "Checks failed: ${RED}$CHECKS_FAILED${NC}"

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ All checks passed! Ready to build and publish.${NC}"
    echo -e "\nNext steps:"
    echo "1. Run: ./scripts/build_package.sh"
    echo "2. Run: ./scripts/upload_to_pypi.sh"
    exit 0
else
    echo -e "\n${RED}❌ Some checks failed. Please fix before publishing.${NC}"
    exit 1
fi