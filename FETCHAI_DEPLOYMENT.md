# 🤖 Fetch.ai Agent Deployment Guide
## Deploy Supply & Need Agents to Agentverse

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Create Fetch.ai Account](#create-fetchai-account)
3. [Deploy Supply Agent 1](#deploy-supply-agent-1)
4. [Deploy Supply Agent 2](#deploy-supply-agent-2)
5. [Deploy Need Agent](#deploy-need-agent)
6. [Register in Almanac](#register-in-almanac)
7. [Get Agent Addresses](#get-agent-addresses)
8. [Test Agents](#test-agents)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools
```bash
# Python 3.9+
python --version

# pip
pip --version

# uagents library
pip install uagents
```

### Required Accounts
- Fetch.ai Agentverse account (free)
- FET tokens for registration (testnet is free)

---

## Create Fetch.ai Account

### Step 1: Sign Up for Agentverse

1. Go to **https://agentverse.ai**
2. Click **"Sign Up"** or **"Get Started"**
3. Choose authentication method:
   - Email + Password
   - Google Account
   - GitHub Account
4. Verify your email
5. Complete profile setup

### Step 2: Create Wallet

1. In Agentverse dashboard, go to **"Wallet"**
2. Click **"Create New Wallet"**
3. **IMPORTANT**: Save your seed phrase securely!
   ```
   Example: word1 word2 word3 ... word12
   ```
4. Confirm seed phrase
5. Set wallet password
6. Copy your wallet address (starts with `fetch1...`)

### Step 3: Get Testnet FET Tokens

1. Go to **https://faucet.fetch.ai**
2. Paste your wallet address
3. Click **"Request Tokens"**
4. Wait 30-60 seconds
5. Check balance in Agentverse wallet
6. You should receive ~100 FET (testnet)

---

## Deploy Supply Agent 1

### Medical Emergency Depot

#### Step 1: Prepare Agent Code

```bash
cd fetchai-agents
```

Open `supply_agent_fetchai.py` and verify configuration at the top:

```python
# Agent configuration
SUPPLIER_NAME = os.getenv("SUPPLIER_NAME", "medical_emergency_depot")
SUPPLIER_LABEL = os.getenv("SUPPLIER_LABEL", "Medical Emergency Depot")
SEED = os.getenv("AGENT_SEED", "supply_medical_seed_phrase_123")
```

#### Step 2: Create Unique Seed Phrase

Generate a unique seed phrase for this agent:

```bash
# Option 1: Use Python
python -c "import secrets; print(' '.join([secrets.token_hex(2) for _ in range(12)]))"

# Option 2: Manual
# Create 12 random words, e.g.:
# "apple banana cherry date elephant fig grape honey ice juice kiwi lemon"
```

**Save this seed phrase!** You'll need it to redeploy the agent.

#### Step 3: Set Environment Variables

```bash
export SUPPLIER_NAME="medical_emergency_depot"
export SUPPLIER_LABEL="Medical Emergency Depot"
export AGENT_SEED="your_unique_seed_phrase_here"
export SUPPLIER_LAT="37.7749"      # San Francisco
export SUPPLIER_LON="-122.4194"
export SUPPLIER_RADIUS_KM="200.0"
export SUPPLIER_LEAD_H="1.0"
export SUPPLIER_DELIVERY_MODE="ambulance"
```

#### Step 4: Run Agent Locally (Test)

```bash
python supply_agent_fetchai.py
```

You should see:
```
🚀 Medical Emergency Depot started
   Address: agent1qw5h7k3l2m4n6p8r9s...
   Inventory: ['blankets', 'first aid kit', 'water bottles', 'flashlight']
   Location: (37.7749, -122.4194)
   Radius: 200.0 km
```

**Copy the agent address!** (starts with `agent1q...`)

Press `Ctrl+C` to stop.

#### Step 5: Deploy to Agentverse

##### Option A: Via Agentverse Dashboard (Recommended)

1. Go to **https://agentverse.ai/agents**
2. Click **"Create New Agent"**
3. Choose **"Upload Python Code"**
4. Upload `supply_agent_fetchai.py`
5. Set environment variables:
   ```
   SUPPLIER_NAME=medical_emergency_depot
   SUPPLIER_LABEL=Medical Emergency Depot
   AGENT_SEED=your_seed_phrase
   SUPPLIER_LAT=37.7749
   SUPPLIER_LON=-122.4194
   SUPPLIER_RADIUS_KM=200.0
   SUPPLIER_LEAD_H=1.0
   SUPPLIER_DELIVERY_MODE=ambulance
   ```
6. Click **"Deploy"**
7. Wait 30-60 seconds
8. Agent status should show **"Running"**

##### Option B: Via CLI

```bash
# Install Agentverse CLI
pip install agentverse-cli

# Login
agentverse login

# Deploy
agentverse deploy supply_agent_fetchai.py \
  --name "medical_emergency_depot" \
  --env SUPPLIER_NAME=medical_emergency_depot \
  --env SUPPLIER_LABEL="Medical Emergency Depot" \
  --env AGENT_SEED="your_seed_phrase" \
  --env SUPPLIER_LAT=37.7749 \
  --env SUPPLIER_LON=-122.4194 \
  --env SUPPLIER_RADIUS_KM=200.0 \
  --env SUPPLIER_LEAD_H=1.0 \
  --env SUPPLIER_DELIVERY_MODE=ambulance
```

#### Step 6: Verify Deployment

1. In Agentverse dashboard, go to **"Agents"**
2. Find **"medical_emergency_depot"**
3. Check status: Should be **"Running"** (green)
4. Click on agent to view details
5. Copy the **Agent Address** (you'll need this later)
6. Check logs for startup message

---

## Deploy Supply Agent 2

### Community Relief Center

Follow the same steps as Supply Agent 1, but with different configuration:

#### Environment Variables

```bash
export SUPPLIER_NAME="community_relief_center"
export SUPPLIER_LABEL="Community Relief Center"
export AGENT_SEED="your_different_seed_phrase_here"  # MUST BE DIFFERENT!
export SUPPLIER_LAT="37.8044"      # Oakland
export SUPPLIER_LON="-122.2712"
export SUPPLIER_RADIUS_KM="150.0"
export SUPPLIER_LEAD_H="1.5"
export SUPPLIER_DELIVERY_MODE="truck"
```

#### Deploy to Agentverse

Use the same deployment method (Dashboard or CLI) with the new environment variables.

**Important**: Each agent MUST have a unique seed phrase!

---

## Deploy Need Agent

### Coordinator Agent

#### Step 1: Get Supply Agent Addresses

Before deploying the need agent, you need the addresses of both supply agents:

```bash
# From Agentverse dashboard, copy both addresses:
SUPPLY_AGENT_1=agent1qw5h7k3l2m4n6p8r9s...  # Medical Emergency
SUPPLY_AGENT_2=agent1qx6i8k4m3n5o7q9t0u...  # Community Relief
```

#### Step 2: Set Environment Variables

```bash
export NEED_AGENT_NAME="need_agent_coordinator"
export AGENT_SEED="your_need_agent_seed_phrase"  # UNIQUE!
export SUPPLIER_ADDRESSES="agent1qw...,agent1qx..."  # Both supply agents
```

#### Step 3: Deploy to Agentverse

##### Via Dashboard:

1. Go to **https://agentverse.ai/agents**
2. Click **"Create New Agent"**
3. Upload `need_agent_fetchai.py`
4. Set environment variables:
   ```
   NEED_AGENT_NAME=need_agent_coordinator
   AGENT_SEED=your_need_seed_phrase
   SUPPLIER_ADDRESSES=agent1qw...,agent1qx...
   ```
5. Click **"Deploy"**
6. Wait for **"Running"** status

##### Via CLI:

```bash
agentverse deploy need_agent_fetchai.py \
  --name "need_agent_coordinator" \
  --env NEED_AGENT_NAME=need_agent_coordinator \
  --env AGENT_SEED="your_need_seed_phrase" \
  --env SUPPLIER_ADDRESSES="agent1qw...,agent1qx..."
```

#### Step 4: Copy Need Agent Address

From Agentverse dashboard:
1. Go to **"Agents"**
2. Click on **"need_agent_coordinator"**
3. Copy the **Agent Address** (starts with `agent1qy...`)
4. **Save this address** - you'll need it for LangChain coordinator!

---

## Register in Almanac

The Almanac is Fetch.ai's agent registry. Registration makes your agents discoverable.

### Automatic Registration (Recommended)

Agents deployed to Agentverse are automatically registered in the Almanac.

To verify:
1. Go to **https://explore.fetch.ai**
2. Search for your agent address
3. You should see agent details and status

### Manual Registration (If Needed)

If running agents locally, register manually:

```python
from uagents import Agent
from uagents.setup import register_agent_with_almanac

agent = Agent(name="my_agent", seed="my_seed")
register_agent_with_almanac(agent)
```

---

## Get Agent Addresses

### Summary of All Addresses

After deployment, you should have 3 agent addresses:

```bash
# Supply Agent 1 (Medical Emergency Depot)
MEDICAL_AGENT_ADDRESS=agent1qw5h7k3l2m4n6p8r9s...

# Supply Agent 2 (Community Relief Center)
COMMUNITY_AGENT_ADDRESS=agent1qx6i8k4m3n5o7q9t0u...

# Need Agent (Coordinator)
NEED_AGENT_ADDRESS=agent1qy7j9l5n4o6p8r0t1v...
```

### Save to Configuration File


Create a file `agent_addresses.env`:

```bash
# Fetch.ai Agent Addresses
export MEDICAL_AGENT_ADDRESS="agent1qw..."
export COMMUNITY_AGENT_ADDRESS="agent1qx..."
export NEED_AGENT_ADDRESS="agent1qy..."

# For LangChain Coordinator
export SUPPLIER_ADDRESSES="agent1qw...,agent1qx..."
```

Load it when needed:
```bash
source agent_addresses.env
```

---

## Test Agents

### Test 1: Check Agent Status

```bash
# Via Agentverse Dashboard
# Go to https://agentverse.ai/agents
# All 3 agents should show "Running" status

# Via API
curl https://agentverse.ai/api/v1/agents/{agent_address}
```

### Test 2: Send Test Message to Supply Agent

```python
from uagents import Agent, Context, Model

class QuoteRequest(Model):
    request_id: str
    items: list
    quantity: int
    location: dict
    priority: str

# Create test agent
test_agent = Agent(name="test", seed="test_seed")

@test_agent.on_event("startup")
async def send_test_request(ctx: Context):
    # Send to supply agent
    await ctx.send(
        "agent1qw...",  # Supply agent address
        QuoteRequest(
            request_id="TEST-001",
            items=["blankets"],
            quantity=50,
            location={"coordinates": {"latitude": 37.7749, "longitude": -122.4194}},
            priority="high"
        )
    )
    print("Test request sent!")

test_agent.run()
```

### Test 3: Check Logs

In Agentverse dashboard:
1. Go to **"Agents"**
2. Click on agent name
3. Go to **"Logs"** tab
4. You should see:
   - Startup messages
   - Received messages
   - Sent responses

---

## Troubleshooting

### Agent Won't Start

**Problem**: Agent status shows "Error" or "Stopped"

**Solutions**:
1. Check logs in Agentverse dashboard
2. Verify all environment variables are set
3. Ensure seed phrase is valid (12 words)
4. Check Python syntax in agent code
5. Verify uagents library version: `pip install uagents --upgrade`

### Agent Not Receiving Messages

**Problem**: Agent is running but not responding to messages

**Solutions**:
1. Verify agent is registered in Almanac: https://explore.fetch.ai
2. Check sender is using correct agent address
3. Verify message model matches (QuoteRequest, etc.)
4. Check agent logs for errors
5. Ensure wallet has FET tokens for message processing

### "Insufficient Funds" Error

**Problem**: Agent can't send messages due to low balance

**Solutions**:
1. Check wallet balance in Agentverse
2. Get more testnet tokens: https://faucet.fetch.ai
3. For mainnet: Purchase FET tokens
4. Verify wallet address is correct

### Agent Address Changed

**Problem**: Agent address is different after redeployment

**Solutions**:
1. Use the SAME seed phrase for consistent address
2. Update addresses in configuration files
3. Update LangChain coordinator with new address
4. Re-register in Almanac if needed

### Messages Not Reaching Need Agent

**Problem**: Supply agents send quotes but need agent doesn't receive them

**Solutions**:
1. Verify SUPPLIER_ADDRESSES in need agent config
2. Check both supply agent addresses are correct
3. Ensure all agents are running
4. Check need agent logs for incoming messages
5. Verify message models match between agents

---

## Best Practices

### Security
- ✅ Never commit seed phrases to git
- ✅ Use environment variables for secrets
- ✅ Keep wallet seed phrase in secure location
- ✅ Use different seed phrases for each agent
- ✅ Regularly backup seed phrases

### Monitoring
- ✅ Check agent status daily
- ✅ Monitor wallet balance
- ✅ Review logs for errors
- ✅ Set up alerts for agent downtime
- ✅ Track message success rates

### Maintenance
- ✅ Update uagents library regularly
- ✅ Test agents after updates
- ✅ Keep documentation updated
- ✅ Version control agent code
- ✅ Maintain staging environment

---

## Cost Estimates

### Testnet (Free)
- Agent deployment: Free
- Message sending: Free
- Almanac registration: Free
- FET tokens: Free from faucet

### Mainnet (Production)
- Agent deployment: ~1 FET (~$0.30)
- Message sending: ~0.001 FET per message (~$0.0003)
- Almanac registration: ~0.1 FET (~$0.03)
- Monthly estimate: ~$10-50 depending on message volume

---

## Next Steps

After deploying all agents:

1. ✅ Save all 3 agent addresses
2. ✅ Verify agents are running in Agentverse
3. ✅ Test message sending/receiving
4. ✅ Configure LangChain coordinator (see LANGCHAIN_SETUP.md)
5. ✅ Integrate with Claude service (see INTEGRATION_GUIDE.md)

---

## Resources

- **Fetch.ai Docs**: https://docs.fetch.ai
- **Agentverse**: https://agentverse.ai
- **Almanac Explorer**: https://explore.fetch.ai
- **Testnet Faucet**: https://faucet.fetch.ai
- **uAgents GitHub**: https://github.com/fetchai/uAgents
- **Community Discord**: https://discord.gg/fetchai

---

## Support

If you encounter issues:

1. Check Fetch.ai documentation
2. Review agent logs in Agentverse
3. Ask in Fetch.ai Discord community
4. Open issue on GitHub
5. Contact Fetch.ai support

**Your agents are now deployed and ready! 🚀**
