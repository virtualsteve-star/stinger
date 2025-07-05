#!/bin/bash
# Run complete test suite - REQUIRED before pushing to main

echo "🎯 Running ALL tests (may take 30+ minutes)..."
echo "This is REQUIRED before pushing to main!"
echo ""

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERROR: OPENAI_API_KEY not set!"
    echo "This is an AI product - we MUST test AI behavior before release!"
    echo "Please set your OpenAI API key:"
    echo "  export OPENAI_API_KEY='your-key-here'"
    exit 1
fi

echo "Running all test tiers:"
echo "  - CI tests (fast, no AI)"
echo "  - Efficacy tests (AI behavior validation)"
echo "  - Performance tests (load and scale)"
echo ""

pytest --durations=50