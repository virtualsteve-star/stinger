#!/bin/bash
# Build placeholder packages to reserve PyPI names

set -e

echo "Building placeholder packages..."

# Build stinger placeholder
echo "Building stinger placeholder..."
cd stinger
python3 -m build
cd ..

# Build stinger-guardrails placeholder  
echo "Building stinger-guardrails placeholder..."
cd stinger-guardrails
python3 -m build
cd ..

echo "Done! Placeholder packages built."
echo ""
echo "To upload to PyPI and reserve the names:"
echo "1. cd stinger && python3 -m twine upload dist/*"
echo "2. cd ../stinger-guardrails && python3 -m twine upload dist/*"
echo ""
echo "Note: You'll need PyPI credentials configured."