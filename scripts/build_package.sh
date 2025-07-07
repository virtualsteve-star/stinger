#!/bin/bash
# Build distribution packages for PyPI

echo "🏗️  Building Stinger distribution packages..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ src/*.egg-info

# Install build dependencies if needed
echo "Checking build dependencies..."
pip3 install --upgrade build twine

# Build the package
echo "Building packages..."
python3 -m build

# Check the built packages
echo -e "\n📦 Built packages:"
ls -la dist/

# Check package contents
echo -e "\n📋 Package contents check:"
python3 -m twine check dist/*

echo -e "\n✅ Build complete! Packages ready for upload."
echo "To upload to Test PyPI: python3 -m twine upload --repository testpypi dist/*"
echo "To upload to PyPI: python3 -m twine upload dist/*"