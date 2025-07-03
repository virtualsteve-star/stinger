#!/bin/bash
# Run only CI tests (<30s) for fast development feedback

echo "🚀 Running fast CI tests..."
echo "These tests verify basic functionality without AI calls"
echo ""

pytest -m "ci" -n auto --durations=10