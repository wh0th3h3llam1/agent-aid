#!/bin/bash
# Quick start for local testing (before Fetch.ai deployment)

echo "🚀 Starting Hybrid AgentAid System (Local Mode)"
echo "================================================"

# Check if Anthropic API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set!"
    echo "   Get your key from: https://console.anthropic.com"
    echo "   Then run: export ANTHROPIC_API_KEY='sk-ant-...'"
    exit 1
fi

# Start Claude service
echo ""
echo "📦 Starting Claude Service..."
cd agentaid-claude-service
node server.js &
CLAUDE_PID=$!
sleep 3

# Start supply agents (local mode for testing)
echo ""
echo "🏥 Starting Medical Emergency Depot..."
cd ../fetchai-agents
SUPPLIER_NAME="medical_emergency_depot" \
SUPPLIER_LABEL="Medical Emergency Depot" \
AGENT_SEED="local_medical_seed_123" \
SUPPLIER_LAT="37.7749" \
SUPPLIER_LON="-122.4194" \
python supply_agent_fetchai.py &
MEDICAL_PID=$!
sleep 2

echo ""
echo "🏪 Starting Community Relief Center..."
SUPPLIER_NAME="community_relief_center" \
SUPPLIER_LABEL="Community Relief Center" \
AGENT_SEED="local_community_seed_456" \
SUPPLIER_LAT="37.8044" \
SUPPLIER_LON="-122.2712" \
python supply_agent_fetchai.py &
COMMUNITY_PID=$!
sleep 2

# Note: Need agent and coordinator would go here
# For now, the polling agents work without them

echo ""
echo "================================================"
echo "✅ System Started!"
echo "================================================"
echo ""
echo "🌐 Open Chat UI:"
echo "   👉 http://localhost:3000/chat.html"
echo ""
echo "📊 Test Messages:"
echo "   Critical: 'Emergency! Need 100 blankets in SF. 200 people affected.'"
echo "   High: 'Urgently need medical supplies at Oakland shelter'"
echo "   Medium: 'Looking for 30 blankets for community center'"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for interrupt
trap "echo ''; echo '🛑 Stopping services...'; kill $CLAUDE_PID $MEDICAL_PID $COMMUNITY_PID 2>/dev/null; exit" INT
wait
