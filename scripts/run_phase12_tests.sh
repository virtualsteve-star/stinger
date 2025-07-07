#!/bin/bash
# Automated Phase 12 Testing Suite
# Run all tests to verify PyPI publishing readiness

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}                           PHASE 12 AUTOMATED TEST SUITE                          ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\n${YELLOW}Running all Phase 12 tests to verify PyPI publishing readiness...${NC}\n"

# Track overall results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    ((TOTAL_TESTS++))
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Test $TOTAL_TESTS: $test_name${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if eval "$test_command"; then
        echo -e "\n${GREEN}✅ $test_name: PASSED${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "\n${RED}❌ $test_name: FAILED${NC}"
        ((FAILED_TESTS++))
    fi
}

# Store the current directory
PROJECT_DIR=$(pwd)

# Test 1: Pre-publish checks
echo -e "${YELLOW}Starting Phase 12 Testing Suite...${NC}"
echo -e "${YELLOW}Project Directory: $PROJECT_DIR${NC}"

# First, make sure all scripts are executable
echo -e "\n${BLUE}Preparing test scripts...${NC}"
chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true

# Test 1: Run pre-publish check
if [ -f "scripts/pre_publish_check.sh" ]; then
    run_test "Pre-Publish Checklist" "./scripts/pre_publish_check.sh"
else
    echo -e "${RED}❌ Pre-publish check script not found${NC}"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
fi

# Test 2: Test local imports and CLI
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 2: Local Import and CLI Test${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Create a test script for local testing
cat > /tmp/test_local_stinger.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
import subprocess

# Add src to path for local testing
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

try:
    # Test imports
    from stinger import GuardrailPipeline, audit, Conversation
    print("✅ Local imports successful")
    
    # Test basic functionality
    pipeline = GuardrailPipeline.from_preset('basic')
    result = pipeline.check_input("My SSN is 123-45-6789")
    if result['blocked']:
        print("✅ Local PII detection works")
    else:
        print("❌ Local PII detection failed")
        sys.exit(1)
    
    # Test CLI
    cli_result = subprocess.run(
        [sys.executable, '-m', 'stinger.cli', '--help'],
        capture_output=True,
        text=True
    )
    if cli_result.returncode == 0:
        print("✅ Local CLI works")
    else:
        print("❌ Local CLI failed")
        sys.exit(1)
        
    print("\n✅ All local tests passed")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Local test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

((TOTAL_TESTS++))
if python3 /tmp/test_local_stinger.py; then
    echo -e "\n${GREEN}✅ Local Import and CLI Test: PASSED${NC}"
    ((PASSED_TESTS++))
else
    echo -e "\n${RED}❌ Local Import and CLI Test: FAILED${NC}"
    ((FAILED_TESTS++))
fi

# Test 3: Build package
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 3: Package Build Test${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

((TOTAL_TESTS++))
if [ -f "scripts/build_package.sh" ]; then
    echo "Running package build..."
    if ./scripts/build_package.sh; then
        # Check if packages were created
        if [ -f "dist/stinger_guardrails_alpha-0.1.0a3-py3-none-any.whl" ] && [ -f "dist/stinger-guardrails-alpha-0.1.0a3.tar.gz" ]; then
            echo -e "\n${GREEN}✅ Package Build Test: PASSED${NC}"
            ((PASSED_TESTS++))
        else
            echo -e "\n${RED}❌ Package Build Test: FAILED - packages not created${NC}"
            ((FAILED_TESTS++))
        fi
    else
        echo -e "\n${RED}❌ Package Build Test: FAILED - build script error${NC}"
        ((FAILED_TESTS++))
    fi
else
    echo -e "${RED}❌ Build script not found${NC}"
    ((FAILED_TESTS++))
fi

# Test 4: Simulate package installation test
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 4: Simulated Package Installation Test${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

((TOTAL_TESTS++))
if [ -f "dist/stinger_guardrails_alpha-0.1.0a3-py3-none-any.whl" ]; then
    echo "Testing local wheel installation in virtual environment..."
    
    # Create temporary test directory
    TEST_DIR=$(mktemp -d)
    cd "$TEST_DIR"
    
    # Create virtual environment
    python3 -m venv test_venv
    source test_venv/bin/activate
    
    # Install from local wheel
    if pip install "$PROJECT_DIR/dist/stinger_guardrails_alpha-0.1.0a3-py3-none-any.whl"; then
        echo "✅ Package installed successfully"
        
        # Test imports
        if python3 -c "from stinger import GuardrailPipeline; print('✅ Import test passed')"; then
            # Test CLI
            if stinger --version; then
                echo "✅ CLI test passed"
                
                # Test functionality
                if stinger check-prompt "My SSN is 123-45-6789" 2>&1 | grep -q "BLOCKED\|blocked\|PII"; then
                    echo "✅ Functionality test passed"
                    TEST_RESULT=0
                else
                    echo "❌ Functionality test failed"
                    TEST_RESULT=1
                fi
            else
                echo "❌ CLI test failed"
                TEST_RESULT=1
            fi
        else
            echo "❌ Import test failed"
            TEST_RESULT=1
        fi
    else
        echo "❌ Package installation failed"
        TEST_RESULT=1
    fi
    
    # Cleanup
    deactivate
    cd "$PROJECT_DIR"
    rm -rf "$TEST_DIR"
    
    if [ $TEST_RESULT -eq 0 ]; then
        echo -e "\n${GREEN}✅ Simulated Package Installation Test: PASSED${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "\n${RED}❌ Simulated Package Installation Test: FAILED${NC}"
        ((FAILED_TESTS++))
    fi
else
    echo -e "${RED}❌ No wheel package found to test${NC}"
    ((FAILED_TESTS++))
fi

# Test 5: Run comprehensive verification
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 5: Comprehensive Verification (from source)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

((TOTAL_TESTS++))
if [ -f "scripts/verify_pypi_release.py" ]; then
    # Run with src in path
    if PYTHONPATH="$PROJECT_DIR/src:$PYTHONPATH" python3 scripts/verify_pypi_release.py; then
        echo -e "\n${GREEN}✅ Comprehensive Verification: PASSED${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "\n${RED}❌ Comprehensive Verification: FAILED${NC}"
        ((FAILED_TESTS++))
    fi
else
    echo -e "${RED}❌ Verification script not found${NC}"
    ((FAILED_TESTS++))
fi

# Final Summary
echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}                              FINAL TEST SUMMARY                                  ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\nTotal Tests: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED! Ready for PyPI publishing.${NC}"
    echo -e "\n${YELLOW}Next Steps:${NC}"
    echo "1. Upload to Test PyPI: ./scripts/upload_to_pypi.sh (choose option 1)"
    echo "2. Test from Test PyPI: ./scripts/test_pypi_package.sh (choose option 1)"
    echo "3. Upload to PyPI: ./scripts/upload_to_pypi.sh (choose option 2)"
    echo "4. Create GitHub Release: Tag v0.1.0a3"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please fix issues before publishing.${NC}"
    exit 1
fi