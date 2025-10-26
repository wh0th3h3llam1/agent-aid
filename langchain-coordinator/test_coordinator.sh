#!/bin/bash
# Test the LangChain Coordinator with a sample message

echo "🧪 Testing LangChain Coordinator"
echo "================================"
echo ""

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ERROR: ANTHROPIC_API_KEY not set!"
    echo "   Please run: export ANTHROPIC_API_KEY='sk-ant-your-key-here'"
    exit 1
fi

echo "✅ Anthropic API Key found"
echo ""

# Set test mode
export TEST_MODE="true"
export CLAUDE_SERVICE_URL="${CLAUDE_SERVICE_URL:-http://localhost:3000}"

echo "🧪 Running in TEST MODE"
echo "   Will process one sample message and exit"
echo ""
echo "================================"
echo ""

# Run the coordinator in test mode
python3 coordinator_configured.py
