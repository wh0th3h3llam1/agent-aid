#!/bin/bash
echo "🚀 Starting LangChain Coordinator"
echo "=================================="

# Load API key from parent directory .env file
if [ -f "../agentaid-claude-service/.env" ]; then
    export $(grep ANTHROPIC_API_KEY ../agentaid-claude-service/.env | xargs)
    echo "✅ Loaded API key from .env"
else
    echo "⚠️  No .env file found, using environment variable"
fi

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY not set!"
    exit 1
fi

echo "✅ API Key: ${ANTHROPIC_API_KEY:0:20}..."
echo ""
echo "🧠 Starting coordinator..."
echo "   Press Ctrl+C to stop"
echo ""

python3 coordinator_configured.py
