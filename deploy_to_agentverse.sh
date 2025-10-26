#!/bin/bash
# Quick deployment script for Agentverse

echo "=========================================="
echo "🚨 AgentAid Agentverse Deployment"
echo "=========================================="

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared not found. Please install it first:"
    echo "   https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo ""
echo "📦 Installing dependencies..."
pip install fastapi uvicorn uagents-core httpx

echo ""
echo "=========================================="
echo "Step 1: Create Public Tunnels"
echo "=========================================="
echo ""
echo "Open TWO new terminal windows and run:"
echo ""
echo "Terminal 1 (Need Agent):"
echo "  cloudflared tunnel --url http://localhost:8000"
echo ""
echo "Terminal 2 (Supply Agent):"
echo "  cloudflared tunnel --url http://localhost:8001"
echo ""
read -p "Press Enter when both tunnels are running..."

echo ""
echo "=========================================="
echo "Step 2: Set Environment Variables"
echo "=========================================="
echo ""
read -p "Enter Need Agent tunnel URL (e.g., https://abc123.trycloudflare.com): " NEED_URL
read -p "Enter Supply Agent tunnel URL (e.g., https://def456.trycloudflare.com): " SUPPLY_URL

export AGENT_EXTERNAL_ENDPOINT="$NEED_URL"
export AGENT_SEED_PHRASE="need_agent_berkeley_1_demo_seed"
export PORT=8000

echo ""
echo "✅ Environment variables set"

echo ""
echo "=========================================="
echo "Step 3: Start Agents"
echo "=========================================="
echo ""
echo "Open TWO more terminal windows and run:"
echo ""
echo "Terminal 3 (Need Agent):"
echo "  cd agentaid-marketplace/agents"
echo "  export AGENT_EXTERNAL_ENDPOINT='$NEED_URL'"
echo "  export AGENT_SEED_PHRASE='need_agent_berkeley_1_demo_seed'"
echo "  python need_agent_chat_adapter.py"
echo ""
echo "Terminal 4 (Supply Agent):"
echo "  cd agentaid-marketplace/agents"
echo "  export AGENT_EXTERNAL_ENDPOINT='$SUPPLY_URL'"
echo "  export AGENT_SEED_PHRASE='supply_sf_store_1_demo_seed'"
echo "  export SUPPLIER_LABEL='SF Depot'"
echo "  python supply_agent_chat_adapter.py"
echo ""
read -p "Press Enter when both agents are running..."

echo ""
echo "=========================================="
echo "Step 4: Test Endpoints"
echo "=========================================="
echo ""
echo "Testing Need Agent..."
curl -s "$NEED_URL/status" | python -m json.tool

echo ""
echo "Testing Supply Agent..."
curl -s "$SUPPLY_URL/status" | python -m json.tool

echo ""
echo "=========================================="
echo "Step 5: Register on Agentverse"
echo "=========================================="
echo ""
echo "Run the registration scripts:"
echo ""
echo "For Need Agent:"
echo "  cd agentaid-marketplace"
echo "  export AGENT_EXTERNAL_ENDPOINT='$NEED_URL'"
echo "  python register_need_agent.py"
echo ""
echo "For Supply Agent:"
echo "  export AGENT_EXTERNAL_ENDPOINT='$SUPPLY_URL'"
echo "  python register_supply_agent.py"
echo ""
echo "Then follow the instructions to complete registration on Agentverse"
echo ""
echo "=========================================="
echo "✅ Deployment Guide Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Go to https://agentverse.ai/"
echo "2. Click 'Launch an Agent'"
echo "3. Select 'Chat Protocol'"
echo "4. Use the URLs and information from the registration scripts"
echo "5. Test your agents in ASI:One chat"
echo ""
echo "For detailed instructions, see: AGENTVERSE_DEPLOYMENT.md"
echo "=========================================="
