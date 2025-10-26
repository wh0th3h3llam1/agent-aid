#!/bin/bash
# Start LangChain Coordinator - Chat Protocol Version

echo "🚀 Starting LangChain Coordinator (Chat Protocol)"
echo "=================================================="
echo ""

# Try to load API key from .env files
if [ -f "../agentaid-claude-service/.env" ]; then
    export $(grep ANTHROPIC_API_KEY ../agentaid-claude-service/.env | xargs)
    echo "✅ Loaded API key from agentaid-claude-service/.env"
elif [ -f "../agentaid-marketplace/.env" ]; then
    export $(grep ANTHROPIC_API_KEY ../agentaid-marketplace/.env | xargs)
    echo "✅ Loaded API key from agentaid-marketplace/.env"
fi

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ERROR: ANTHROPIC_API_KEY not set!"
    echo ""
    echo "Please set your Anthropic API key:"
    echo "   export ANTHROPIC_API_KEY='sk-ant-your-key-here'"
    echo ""
    echo "Get your key from: https://console.anthropic.com"
    exit 1
fi

echo "✅ Anthropic API Key: ${ANTHROPIC_API_KEY:0:20}..."
echo ""

# Display configured addresses
echo "📍 Configured Addresses:"
echo "   Need Agent:   agent1q2h8e88wru7sl7hfy4kkrjrf4p4zqghtu7umsw2r2twkewcscnrwymnjju9"
echo "   Supply Agent: agent1qd0kdf9py6ehfjqq6s969dcv90sj9jg594yk252926pp2z85r82z6aepahg"
echo ""

# Set Claude service URL (default to localhost)
export CLAUDE_SERVICE_URL="${CLAUDE_SERVICE_URL:-http://localhost:3000}"
echo "🌐 Claude Service: $CLAUDE_SERVICE_URL"
echo ""

# Check if Claude service is running
echo "🔍 Checking Claude service..."
if curl -s "$CLAUDE_SERVICE_URL/health" > /dev/null 2>&1; then
    echo "✅ Claude service is running"
else
    echo "⚠️  Claude service not responding at $CLAUDE_SERVICE_URL"
    echo "   Make sure to start it first:"
    echo "   cd agentaid-claude-service && node server.js"
    echo ""
    echo "   Continue anyway? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "=================================================="
echo "🧠 Starting Coordinator (Chat Protocol)..."
echo "=================================================="
echo ""

# Disable test mode for production
export TEST_MODE="false"

# Get the full path to python3
PYTHON_PATH=$(which python3)

# Run the coordinator
$PYTHON_PATH coordinator_chat_protocol.py
