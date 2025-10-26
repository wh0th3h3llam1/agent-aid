# AgentAid Agentverse Deployment Guide

This guide explains how to deploy the Need Agent and Supply Agent to Agentverse using the Chat Protocol integration.

## Prerequisites

1. **Agentverse Account**: Sign up at [Agentverse](https://agentverse.ai/)
2. **Public Endpoint**: Use cloudflared, ngrok, or similar tunneling service
3. **Python 3.8+** with required packages
4. **Node.js 18+** (for some dependencies)

## Installation

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install fastapi uvicorn uagents-core httpx

# Or install from requirements
pip install -r agentaid-marketplace/requirements.txt
```

### 2. Install uagents_core

```bash
pip install uagents-core
```

## Deployment Steps

### Step 1: Create Public Endpoints

You need public URLs for your agents. Use cloudflared tunnel:

#### For Need Agent (Port 8000)
```bash
cloudflared tunnel --url http://localhost:8000
```

Copy the generated URL (e.g., `https://abc123.trycloudflare.com`)

#### For Supply Agent (Port 8001)
```bash
cloudflared tunnel --url http://localhost:8001
```

Copy the generated URL (e.g., `https://def456.trycloudflare.com`)

### Step 2: Set Environment Variables

#### Need Agent Environment Variables
```bash
export AGENT_SEED_PHRASE="need_agent_berkeley_1_demo_seed"
export AGENT_EXTERNAL_ENDPOINT="https://your-need-agent-url.trycloudflare.com"
export PORT=8000
```

#### Supply Agent Environment Variables
```bash
export AGENT_SEED_PHRASE="supply_sf_store_1_demo_seed"
export AGENT_EXTERNAL_ENDPOINT="https://your-supply-agent-url.trycloudflare.com"
export SUPPLIER_LABEL="SF Depot"
export PORT=8001
```

### Step 3: Run the Agents Locally

#### Terminal 1: Run Need Agent
```bash
cd agentaid-marketplace/agents
python need_agent_chat_adapter.py
```

Verify it's running: `http://localhost:8000/status`

#### Terminal 2: Run Supply Agent
```bash
cd agentaid-marketplace/agents
python supply_agent_chat_adapter.py
```

Verify it's running: `http://localhost:8001/status`

### Step 4: Register on Agentverse

#### Register Need Agent

1. Go to [Agentverse](https://agentverse.ai/)
2. Navigate to **Agents** tab
3. Click **Launch an Agent**
4. Select **Chat Protocol**
5. Enter:
   - **Agent Name**: `AgentAid Need Agent`
   - **Agent Public Endpoint URL**: Your cloudflared URL for port 8000
6. Run the provided registration script (see below)
7. Click **Evaluate Registration**

#### Register Supply Agent

1. Repeat the same process
2. Enter:
   - **Agent Name**: `AgentAid Supply Agent`
   - **Agent Public Endpoint URL**: Your cloudflared URL for port 8001
3. Run the provided registration script
4. Click **Evaluate Registration**

## Registration Scripts

### Need Agent Registration Script

Create a file `register_need_agent.py`:

```python
import os
from uagents_core.identity import Identity
from uagents_core.registration import register_agent_with_agentverse

# Configuration
AGENT_SEED_PHRASE = os.environ.get("AGENT_SEED_PHRASE", "need_agent_berkeley_1_demo_seed")
AGENT_ENDPOINT = os.environ.get("AGENT_EXTERNAL_ENDPOINT", "http://localhost:8000")
AGENTVERSE_API_KEY = os.environ.get("AGENTVERSE_API_KEY")

# Create identity
identity = Identity.from_seed(AGENT_SEED_PHRASE, 0)

# Agent metadata
name = "AgentAid Need Agent"
readme = """# AgentAid Need Agent
Disaster relief need management agent that broadcasts emergency requests to supply agents.
"""

# Register
print(f"Registering agent: {name}")
print(f"Agent address: {identity.address}")
print(f"Endpoint: {AGENT_ENDPOINT}")

register_agent_with_agentverse(
    identity=identity,
    name=name,
    readme=readme,
    endpoint=AGENT_ENDPOINT,
    api_key=AGENTVERSE_API_KEY
)

print("✅ Registration complete!")
```

Run it:
```bash
export AGENTVERSE_API_KEY="your_api_key_here"
python register_need_agent.py
```

### Supply Agent Registration Script

Create a file `register_supply_agent.py`:

```python
import os
from uagents_core.identity import Identity
from uagents_core.registration import register_agent_with_agentverse

# Configuration
AGENT_SEED_PHRASE = os.environ.get("AGENT_SEED_PHRASE", "supply_sf_store_1_demo_seed")
AGENT_ENDPOINT = os.environ.get("AGENT_EXTERNAL_ENDPOINT", "http://localhost:8001")
AGENTVERSE_API_KEY = os.environ.get("AGENTVERSE_API_KEY")

# Create identity
identity = Identity.from_seed(AGENT_SEED_PHRASE, 0)

# Agent metadata
name = "AgentAid Supply Agent"
readme = """# AgentAid Supply Agent
Disaster relief supply management agent with inventory tracking and smart quoting.
"""

# Register
print(f"Registering agent: {name}")
print(f"Agent address: {identity.address}")
print(f"Endpoint: {AGENT_ENDPOINT}")

register_agent_with_agentverse(
    identity=identity,
    name=name,
    readme=readme,
    endpoint=AGENT_ENDPOINT,
    api_key=AGENTVERSE_API_KEY
)

print("✅ Registration complete!")
```

Run it:
```bash
export AGENTVERSE_API_KEY="your_api_key_here"
python register_supply_agent.py
```

## Verification

### 1. Check Agent Status

Visit your agent's `/status` endpoint:
- Need Agent: `https://your-need-agent-url.trycloudflare.com/status`
- Supply Agent: `https://your-supply-agent-url.trycloudflare.com/status`

### 2. Test Chat Protocol

Use curl to test:

```bash
# Test Need Agent
curl -X POST https://your-need-agent-url.trycloudflare.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "test_user",
    "message": "We need 200 blankets at Berkeley Emergency Center. Critical priority."
  }'

# Test Supply Agent
curl -X POST https://your-supply-agent-url.trycloudflare.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "test_user",
    "message": "What supplies do you have available?"
  }'
```

### 3. Chat in Agentverse

1. Go to your agent's dashboard in Agentverse
2. Click **Chat with Agent**
3. You'll be redirected to ASI:One chat UI
4. Send test messages to interact with your agent

## Agent Capabilities

### Need Agent
- 🆘 Emergency need broadcasting
- 📊 Quote evaluation and scoring
- 🎯 Smart resource allocation
- 🌍 Location-aware matching
- ⚡ Priority management

### Supply Agent
- 📦 Real-time inventory management
- 💰 Smart quote generation
- 🚚 Delivery coordination
- 🌍 Radius-based service
- ⚡ Priority pricing

## Example Interactions

### Need Agent Examples

**Message**: "We need 200 blankets at Berkeley Emergency Center, 37.8715, -122.2730. This is critical priority."

**Response**: Agent will parse the request, broadcast to supply agents, and provide status updates.

### Supply Agent Examples

**Message**: "What supplies do you have available?"

**Response**: Agent will provide current inventory status with quantities and units.

**Message**: "Quote for 200 blankets to Berkeley, critical priority"

**Response**: Agent will generate a quote with coverage, ETA, and cost.

## Troubleshooting

### Agent Not Reachable
- Check if cloudflared tunnel is running
- Verify the public URL is correct
- Ensure the agent is running locally
- Check firewall settings

### Registration Fails
- Verify AGENTVERSE_API_KEY is set correctly
- Check AGENT_SEED_PHRASE is consistent
- Ensure endpoint URL is publicly accessible
- Try the `/status` endpoint first

### Chat Messages Not Working
- Verify Chat Protocol implementation
- Check agent logs for errors
- Test with curl first
- Ensure uagents_core is installed

## Production Deployment

For production deployment:

1. **Use Persistent Hosting**: Deploy to cloud (AWS, GCP, Azure)
2. **Set Up SSL**: Use proper SSL certificates
3. **Database**: Use production database for inventory
4. **Monitoring**: Set up logging and monitoring
5. **Scaling**: Use load balancers for high traffic
6. **Security**: Implement authentication and rate limiting

## Resources

- [Agentverse Documentation](https://docs.agentverse.ai/)
- [Chat Protocol Integration](https://docs.agentverse.ai/documentation/launch-agents/connect-your-agents-chat-protocol-integration)
- [uAgents Framework](https://fetch.ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

For issues or questions:
1. Check agent logs
2. Verify environment variables
3. Test endpoints manually
4. Review Agentverse documentation
5. Check the AgentAid repository

## Next Steps

After successful deployment:
1. Monitor agent performance in Agentverse dashboard
2. Analyze interactions and optimize responses
3. Add more supply agents for better coverage
4. Integrate with coordination agent
5. Set up telemetry and analytics

---

**Note**: Keep your seed phrases and API keys secure. Never commit them to version control.
