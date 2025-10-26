# AgentAid Agentverse - Quick Start Guide

## 🚀 Deploy in 5 Minutes

### Prerequisites
- Python 3.8+
- cloudflared (download: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)

### Step 1: Install Dependencies (1 min)
```bash
pip install fastapi uvicorn uagents-core httpx
```

### Step 2: Create Tunnels (1 min)
Open 2 terminals:

**Terminal 1:**
```bash
cloudflared tunnel --url http://localhost:8000
# Copy the URL (e.g., https://abc123.trycloudflare.com)
```

**Terminal 2:**
```bash
cloudflared tunnel --url http://localhost:8001
# Copy the URL (e.g., https://def456.trycloudflare.com)
```

### Step 3: Start Agents (1 min)
Open 2 more terminals:

**Terminal 3 - Need Agent:**
```bash
cd agentaid-marketplace/agents
export AGENT_EXTERNAL_ENDPOINT='https://abc123.trycloudflare.com'
export AGENT_SEED_PHRASE='need_agent_berkeley_1_demo_seed'
python need_agent_chat_adapter.py
```

**Terminal 4 - Supply Agent:**
```bash
cd agentaid-marketplace/agents
export AGENT_EXTERNAL_ENDPOINT='https://def456.trycloudflare.com'
export AGENT_SEED_PHRASE='supply_sf_store_1_demo_seed'
python supply_agent_chat_adapter.py
```

### Step 4: Get Registration Info (1 min)
```bash
cd agentaid-marketplace
export AGENT_EXTERNAL_ENDPOINT='https://abc123.trycloudflare.com'
python register_need_agent.py

export AGENT_EXTERNAL_ENDPOINT='https://def456.trycloudflare.com'
python register_supply_agent.py
```

### Step 5: Register on Agentverse (1 min)
1. Go to https://agentverse.ai/
2. Click **"Launch an Agent"**
3. Select **"Chat Protocol"**
4. Enter:
   - **Name**: AgentAid Need Agent (or Supply Agent)
   - **Endpoint**: Your cloudflared URL
5. Run registration script from Agentverse
6. Click **"Evaluate Registration"**
7. ✅ Done!

## 📝 Quick Test

Test your agents:
```bash
# Test Need Agent
curl https://abc123.trycloudflare.com/status

# Test Supply Agent
curl https://def456.trycloudflare.com/status
```

## 💬 Chat Examples

### Need Agent
"We need 200 blankets at Berkeley Emergency Center. Critical priority."

### Supply Agent
"What supplies do you have available?"

## 🔗 Important Links
- **Agentverse**: https://agentverse.ai/
- **Documentation**: [AGENTVERSE_DEPLOYMENT.md](AGENTVERSE_DEPLOYMENT.md)
- **Full Guide**: [AGENTVERSE_SUMMARY.md](AGENTVERSE_SUMMARY.md)

## ⚡ Windows Users
Use `deploy_to_agentverse.bat` for guided setup!

## 🆘 Troubleshooting
- **Agent not reachable**: Check cloudflared is running
- **Registration fails**: Verify endpoint URL is correct
- **Chat not working**: Check agent logs for errors

## 📚 Full Documentation
See [AGENTVERSE_DEPLOYMENT.md](AGENTVERSE_DEPLOYMENT.md) for complete instructions.
