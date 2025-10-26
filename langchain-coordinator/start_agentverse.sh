#!/bin/bash
# Start LangChain Coordinator with Agentverse API Key

echo "🚀 Starting LangChain Coordinator (Agentverse)"
echo "=============================================="
echo ""

# Load Anthropic API key
if [ -f "../agentaid-claude-service/.env" ]; then
    export $(grep ANTHROPIC_API_KEY ../agentaid-claude-service/.env | xargs)
    echo "✅ Loaded Anthropic API key"
elif [ -f "../agentaid-marketplace/.env" ]; then
    export $(grep ANTHROPIC_API_KEY ../agentaid-marketplace/.env | xargs)
    echo "✅ Loaded Anthropic API key"
fi

# Set Agentverse API key
export AGENTVERSE_API_KEY="eyJhbGciOiJSUzI1NiJ9.eyJleHAiOjE3NjE0NTk5NzEsImlhdCI6MTc2MTQ1NjM3MSwiaXNzIjoiZmV0Y2guYWkiLCJqdGkiOiI5NGE4MDYwOTQ5NzNhOWNkMDBkMWU1MDEiLCJzY29wZSI6IiIsInN1YiI6IjlhYzEwODJiZDk1Nzg3MjNiMTNkZDBkOTE1MDBmODQxNjk0ZjQ4NzQ4YzRhYjU1NCJ9.aVVYcTIAKOB7OLRRDEBc2iR7jdo9WFpI1u3Fh_AJuNmVCCj0liaTzQjWg4TwznXxJJsp4ingCZ6nyySbxaKZUW5NycZdbuRUcyCpGntyAdVzC5kwLupVAnIuQ8sC7j0B29wYEBYfGEiwOkY1Sfjh9oKZenK5dF75303d-y-mgmGpcygQmkEY7WR_LVS57VRL-MkPEh7rXKh9ZMtsC-CuRRlzL5SAZDD39Pmr50WKUiBfVJMbOun330y0BjpaUQjdGIHHFIN9yQfE8HMJIqmKK4PbwUn9MBj0GA0R_gl5WQTJIsiAiyaZjtulbUZhhDbpDxbQ5sJqfpmcKNg-O2Wtkg"
echo "✅ Agentverse API key set"

# Set Claude service URL
export CLAUDE_SERVICE_URL="${CLAUDE_SERVICE_URL:-http://localhost:3000}"

# Check API keys
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ERROR: ANTHROPIC_API_KEY not set!"
    exit 1
fi

echo "✅ Anthropic API Key: ${ANTHROPIC_API_KEY:0:20}..."
echo "✅ Agentverse API Key: ${AGENTVERSE_API_KEY:0:20}..."
echo ""

echo "📍 Agent Addresses:"
echo "   Need Agent:   agent1q2h8e88wru7sl7hfy4kkrjrf4p4zqghtu7umsw2r2twkewcscnrwymnjju9"
echo "   Supply Agent: agent1qd0kdf9py6ehfjqq6s969dcv90sj9jg594yk252926pp2z85r82z6aepahg"
echo ""

# Check Claude service
echo "🔍 Checking Claude service..."
if curl -s "$CLAUDE_SERVICE_URL/health" > /dev/null 2>&1; then
    echo "✅ Claude service is running"
else
    echo "⚠️  Claude service not responding"
fi

echo ""
echo "=============================================="
echo "🧠 Starting Coordinator (Agentverse)..."
echo "=============================================="
echo ""

# Disable test mode
export TEST_MODE="false"

# Get python path
PYTHON_PATH=$(which python3)

# Run the coordinator
$PYTHON_PATH coordinator_agentverse.py
