#!/bin/bash
# Test PyPI package installation and functionality

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🧪 Stinger PyPI Package Test Suite"
echo "=================================="

# Get package source (test or prod PyPI)
echo -e "\n${YELLOW}Which PyPI to test from?${NC}"
echo "1) Test PyPI"
echo "2) Production PyPI"
echo -n "Choice (1 or 2): "
read CHOICE

if [ "$CHOICE" = "1" ]; then
    PIP_INDEX="https://test.pypi.org/simple/"
    EXTRA_INDEX="--extra-index-url https://pypi.org/simple/"  # For dependencies
    SOURCE="Test PyPI"
elif [ "$CHOICE" = "2" ]; then
    PIP_INDEX=""
    EXTRA_INDEX=""
    SOURCE="PyPI"
else
    echo -e "${RED}Invalid choice${NC}"
    exit 1
fi

# Create test environment
TEST_DIR="test_pypi_install_$(date +%s)"
echo -e "\n${BLUE}Creating test environment in $TEST_DIR${NC}"
mkdir -p $TEST_DIR
cd $TEST_DIR

# Create virtual environment
echo -e "\n${BLUE}Setting up virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Test 1: Basic Installation
echo -e "\n${YELLOW}Test 1: Installing from $SOURCE${NC}"
if [ -n "$PIP_INDEX" ]; then
    pip install -i $PIP_INDEX $EXTRA_INDEX stinger-guardrails-alpha
else
    pip install stinger-guardrails-alpha
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Installation successful${NC}"
else
    echo -e "${RED}❌ Installation failed${NC}"
    deactivate
    cd ..
    rm -rf $TEST_DIR
    exit 1
fi

# Test 2: Version Check
echo -e "\n${YELLOW}Test 2: Version verification${NC}"
INSTALLED_VERSION=$(python -c "import stinger; print(stinger.__version__)" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Version check passed: $INSTALLED_VERSION${NC}"
else
    echo -e "${RED}❌ Version check failed${NC}"
fi

# Test 3: CLI Command
echo -e "\n${YELLOW}Test 3: CLI availability and commands${NC}"
which stinger > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ CLI command 'stinger' is available${NC}"
    
    # Test various CLI commands
    echo "Testing CLI commands:"
    
    # Help command
    stinger --help > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✅ stinger --help${NC}"
    else
        echo -e "  ${RED}❌ stinger --help${NC}"
    fi
    
    # Version command
    VERSION_OUTPUT=$(stinger --version 2>&1)
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✅ stinger --version: $VERSION_OUTPUT${NC}"
    else
        echo -e "  ${RED}❌ stinger --version${NC}"
    fi
    
    # Health check
    stinger health > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✅ stinger health${NC}"
    else
        echo -e "  ${RED}❌ stinger health${NC}"
    fi
    
    # Check prompt command
    OUTPUT=$(stinger check-prompt "Hello world" 2>&1)
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✅ stinger check-prompt${NC}"
    else
        echo -e "  ${RED}❌ stinger check-prompt${NC}"
    fi
    
    # Check response command
    OUTPUT=$(stinger check-response "Hello world" 2>&1)
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✅ stinger check-response${NC}"
    else
        echo -e "  ${RED}❌ stinger check-response${NC}"
    fi
    
    # Test actual guardrail functionality via CLI
    echo -e "\n  Testing guardrail functionality via CLI:"
    
    # Test 1: Input that SHOULD BE BLOCKED (negative case)
    OUTPUT=$(stinger check-prompt "My SSN is 123-45-6789" 2>&1)
    if echo "$OUTPUT" | grep -q "BLOCKED\|blocked\|PII"; then
        echo -e "  ${GREEN}✅ Input PII detection blocks correctly${NC}"
    else
        echo -e "  ${RED}❌ Input PII detection failed to block${NC}"
        echo "     Output: $OUTPUT"
    fi
    
    # Test 2: Input that SHOULD PASS (positive case)
    OUTPUT=$(stinger check-prompt "Hello, I need help with my order" 2>&1)
    if echo "$OUTPUT" | grep -q "ALLOWED\|allowed\|Passed\|passed" || ! echo "$OUTPUT" | grep -q "BLOCKED\|blocked"; then
        echo -e "  ${GREEN}✅ Safe input passes correctly${NC}"
    else
        echo -e "  ${RED}❌ Safe input incorrectly blocked${NC}"
        echo "     Output: $OUTPUT"
    fi
    
    # Test 3: Output that SHOULD BE BLOCKED (negative case)
    OUTPUT=$(stinger check-response "Here is the code: def hack_system(): pass" 2>&1)
    if echo "$OUTPUT" | grep -q "BLOCKED\|blocked\|code"; then
        echo -e "  ${GREEN}✅ Output code detection blocks correctly${NC}"
    else
        echo -e "  ${RED}❌ Output code detection failed to block${NC}"
        echo "     Output: $OUTPUT"
    fi
    
    # Test 4: Output that SHOULD PASS (positive case)
    OUTPUT=$(stinger check-response "Thank you for contacting support" 2>&1)
    if echo "$OUTPUT" | grep -q "ALLOWED\|allowed\|Passed\|passed" || ! echo "$OUTPUT" | grep -q "BLOCKED\|blocked"; then
        echo -e "  ${GREEN}✅ Safe output passes correctly${NC}"
    else
        echo -e "  ${RED}❌ Safe output incorrectly blocked${NC}"
        echo "     Output: $OUTPUT"
    fi
else
    echo -e "${RED}❌ CLI command not found${NC}"
fi

# Test 4: Basic Import Test
echo -e "\n${YELLOW}Test 4: Python imports${NC}"
python << EOF
import sys
try:
    from stinger import GuardrailPipeline
    print("✅ GuardrailPipeline import successful")
except ImportError as e:
    print(f"❌ GuardrailPipeline import failed: {e}")
    sys.exit(1)

try:
    from stinger import audit
    print("✅ Audit module import successful")
except ImportError as e:
    print(f"❌ Audit module import failed: {e}")
    sys.exit(1)

try:
    from stinger import Conversation
    print("✅ Conversation import successful")
except ImportError as e:
    print(f"❌ Conversation import failed: {e}")
    sys.exit(1)
EOF

# Test 5: Functional Test
echo -e "\n${YELLOW}Test 5: Basic functionality${NC}"
python << 'EOF'
try:
    from stinger import GuardrailPipeline
    
    # Test preset loading
    pipeline = GuardrailPipeline.from_preset('basic')
    print("✅ Preset loading works")
    
    # Test basic PII detection
    result = pipeline.check_input("My email is test@example.com")
    if result['blocked']:
        print("✅ PII detection works")
    else:
        print("❌ PII detection failed")
    
    # Test safe content
    result = pipeline.check_input("Hello world")
    if not result['blocked']:
        print("✅ Safe content passes")
    else:
        print("❌ Safe content incorrectly blocked")
        
except Exception as e:
    print(f"❌ Functional test failed: {e}")
    import traceback
    traceback.print_exc()
EOF

# Test 6: Package Metadata
echo -e "\n${YELLOW}Test 6: Package metadata${NC}"
pip show stinger-guardrails-alpha | grep -E "Name:|Version:|Summary:|Author:|License:"

# Test 7: Dependencies Check
echo -e "\n${YELLOW}Test 7: Dependencies installed${NC}"
python << EOF
required = ['pyyaml', 'jsonschema', 'cryptography']
missing = []
for pkg in required:
    try:
        __import__(pkg.replace('-', '_'))
    except ImportError:
        missing.append(pkg)

if missing:
    print(f"❌ Missing dependencies: {', '.join(missing)}")
else:
    print("✅ All core dependencies installed")
EOF

# Cleanup
echo -e "\n${BLUE}Cleaning up test environment...${NC}"
deactivate
cd ..
rm -rf $TEST_DIR

echo -e "\n${GREEN}========== Test Summary ==========${NC}"
echo "Package source: $SOURCE"
echo "All tests should show ✅ for successful publishing"
echo -e "${GREEN}==================================${NC}"