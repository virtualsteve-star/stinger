#!/bin/bash
# Run efficacy tests - validates real AI behavior

echo "🧪 Running efficacy tests (may take 5-10 minutes)..."
echo "These tests validate real AI guardrail behavior"
echo ""

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERROR: OPENAI_API_KEY not set!"
    echo "Please set your OpenAI API key:"
    echo "  export OPENAI_API_KEY='your-key-here'"
    exit 1
fi

pytest -m "efficacy" --durations=20