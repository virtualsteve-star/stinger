#!/bin/bash
# Upload packages to PyPI or Test PyPI

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📦 Stinger PyPI Upload Script"
echo "============================"

# Check if dist directory exists
if [ ! -d "dist" ]; then
    echo -e "${RED}Error: dist/ directory not found. Run ./scripts/build_package.sh first${NC}"
    exit 1
fi

# Check for packages
PACKAGES=$(ls dist/*.whl dist/*.tar.gz 2>/dev/null | wc -l)
if [ $PACKAGES -eq 0 ]; then
    echo -e "${RED}Error: No packages found in dist/. Run ./scripts/build_package.sh first${NC}"
    exit 1
fi

echo -e "\nFound packages:"
ls -la dist/

# Ask which PyPI to use
echo -e "\n${YELLOW}Which PyPI repository?${NC}"
echo "1) Test PyPI (recommended for testing)"
echo "2) Production PyPI"
echo -n "Choice (1 or 2): "
read CHOICE

if [ "$CHOICE" = "1" ]; then
    REPO="testpypi"
    REPO_URL="https://test.pypi.org/pypi"
    echo -e "\n${GREEN}Using Test PyPI${NC}"
elif [ "$CHOICE" = "2" ]; then
    REPO="pypi"
    REPO_URL="https://pypi.org/pypi"
    echo -e "\n${YELLOW}Using Production PyPI${NC}"
else
    echo -e "${RED}Invalid choice${NC}"
    exit 1
fi

# Confirm upload
echo -e "\n${YELLOW}About to upload to $REPO:${NC}"
ls dist/*.whl dist/*.tar.gz
echo -n -e "\n${YELLOW}Continue? (y/N): ${NC}"
read CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Upload cancelled"
    exit 0
fi

# Upload
echo -e "\n${GREEN}Uploading...${NC}"
if [ "$REPO" = "testpypi" ]; then
    python3 -m twine upload --repository testpypi dist/*
else
    python3 -m twine upload dist/*
fi

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Upload successful!${NC}"
    echo -e "\nPackage URL: ${REPO_URL}/stinger-guardrails-alpha/"
    
    if [ "$REPO" = "testpypi" ]; then
        echo -e "\nTo install from Test PyPI:"
        echo "pip install -i https://test.pypi.org/simple/ stinger-guardrails-alpha"
    else
        echo -e "\nTo install from PyPI:"
        echo "pip install stinger-guardrails-alpha"
    fi
else
    echo -e "\n${RED}❌ Upload failed${NC}"
    exit 1
fi