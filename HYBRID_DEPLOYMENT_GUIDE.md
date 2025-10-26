# Hybrid Deployment Guide
## Fetch.ai Agents + LangChain Coordinator + Chat UI

This guide shows how to deploy the hybrid architecture:
- **Fetch.ai Agentverse**: Supply agents + Need agent (public endpoints)
- **LangChain**: Coordination agent with Claude (local/cloud)
- **Chat UI**: Natural language interface with smart priority detection

---

## Architecture

```
User Chat Input
    ↓
LangChain Coordinator (Claude Sonnet 4)
    ├─ Analyzes request
    ├─ Determines priority (critical/high/medium/low)
    ├─ Extracts structured data
    ↓
Fetch.ai Need Agent (Agentverse)
    ├─ Broadcasts to suppliers
    ├─ Collects quotes
    ├─ Evaluates & negotiates
    ↓
Fetch.ai Supply Agents (Agentverse)
    ├─ Check inventory
    ├─ Calculate costs & ETA
    ├─ Send quotes
    ↓
Chat UI displays quotes + selection
```

---

## Step 1: Deploy to Fetch.ai Agentverse

### 1.1 Create Account
1. Go to https://agentverse.ai
2. Sign up / Log in
3. Get your agent wallet address

### 1.2 Deploy Supply Agent 1 (Medical Emergency)

```bash
# Set environment variables
export SUPPLIER_NAME="medical_emergency_depot"
export SUPPLIER_LABEL="Medical Emergency Depot"
export AGENT_SEED="your_unique_seed_phrase_medical_123"
export SUPPLIER_LAT="37.7749"
export SUPPLIER_LON="-122.4194"
export SUPPLIER_RADIUS_KM="200.0"
export SUPPLIER_LEAD_H="1.0"
export SUPPLIER_DELIVERY_MODE="ambulance"

# Deploy
cd fetchai-agents
python supply_agent_fetchai.py
```

**Copy the agent address** from output (e.g., `agent1qw...`)

### 1.3 Deploy Supply Agent 2 (Community Relief)

```bash
export SUPPLIER_NAME="community_relief_center"
export SUPPLIER_LABEL="Community Relief Center"
export AGENT_SEED="your_unique_seed_phrase_community_456"
export SUPPLIER_LAT="37.8044"
export SUPPLIER_LON="-122.2712"
export SUPPLIER_RADIUS_KM="150.0"
export SUPPLIER_LEAD_H="1.5"
export SUPPLIER_DELIVERY_MODE="truck"

python supply_agent_fetchai.py
```

**Copy the agent address**

### 1.4 Deploy Need Agent

```bash
export NEED_AGENT_NAME="need_agent_coordinator"
export AGENT_SEED="your_unique_seed_phrase_need_789"
export SUPPLIER_ADDRESSES="agent1qw...,agent1qx..."  # Paste supply agent addresses

python need_agent_fetchai.py
```

**Copy the need agent address**

---

## Step 2: Configure LangChain Coordinator

### 2.1 Set Environment Variables

```bash
# Anthropic API Key
export ANTHROPIC_API_KEY="sk-ant-..."

# Fetch.ai Need Agent Address
export NEED_AGENT_ADDRESS="agent1qy..."  # From Step 1.4

# Claude Service URL
export CLAUDE_SERVICE_URL="http://localhost:3000"
```

### 2.2 Install Dependencies

```bash
cd langchain-coordinator
pip install anthropic httpx
```

### 2.3 Run Coordinator

```bash
python coordinator_agent.py
```

---

## Step 3: Start Claude Service

```bash
cd agentaid-claude-service
node server.js
```

---

## Step 4: Access Chat UI

Open browser: **http://localhost:3000/chat.html**

---

## Testing the System

### Test 1: Critical Priority
```
Emergency! Need 100 blankets immediately in San Francisco. 
Life-threatening situation. 200 people affected. Contact: 555-1234
```

**Expected**: Priority = CRITICAL

### Test 2: High Priority
```
We urgently need medical supplies at Oakland shelter. 
About 50 people waiting. Please send ASAP.
```

**Expected**: Priority = HIGH

### Test 3: Medium Priority
```
Looking for 30 blankets for community center in Berkeley. 
Contact: shelter@example.com
```

**Expected**: Priority = MEDIUM

### Test 4: Low Priority
```
Can you provide some water bottles when available? 
No rush, just planning ahead.
```

**Expected**: Priority = LOW

---

## Priority Detection Logic

Claude analyzes these indicators:

**CRITICAL**:
- Keywords: "emergency", "urgent", "life-threatening", "immediate"
- Medical emergencies
- Large victim counts (>100)
- Dangerous situations

**HIGH**:
- Keywords: "ASAP", "quickly", "soon", "urgent"
- Time-sensitive needs
- Moderate victim counts (50-100)
- Shelter requests

**MEDIUM**:
- Standard requests
- Small-medium groups (10-50)
- General supplies
- No urgency indicators

**LOW**:
- Keywords: "when available", "no rush", "planning"
- Small scale (<10)
- Flexible timing
- Non-essential items

---

## Monitoring

### Check Agent Status
```bash
# Fetch.ai agents
curl https://agentverse.ai/api/agents/{agent_address}

# LangChain coordinator
# Check console output for Claude analysis

# Quotes
curl http://localhost:3000/api/uagent/updates
```

### View Logs
- **Fetch.ai**: Agentverse dashboard
- **LangChain**: Terminal output
- **Claude Service**: Terminal output

---

## Advantages of Hybrid Approach

✅ **Fetch.ai Agents**:
- Public endpoints (no local resolution issues)
- Registered in Almanac
- Can communicate globally
- Persistent addresses

✅ **LangChain Coordinator**:
- Advanced NLP with Claude
- Smart priority detection
- Flexible logic
- Easy to modify

✅ **Chat UI**:
- Natural language input
- No forms to fill
- AI understands context
- Real-time updates

---

## Troubleshooting

### Agents not communicating
1. Check agent addresses are correct
2. Verify agents are funded (need FET tokens)
3. Check Almanac registration
4. Verify endpoints are accessible

### Priority detection wrong
1. Check ANTHROPIC_API_KEY is set
2. Verify Claude model access
3. Add more context in message
4. Check coordinator logs

### No quotes received
1. Verify supply agents are running
2. Check location is within radius
3. Verify inventory exists
4. Check agent logs

---

## Production Deployment

### Fetch.ai Agents
- Deploy to Agentverse (managed hosting)
- Or run on your own servers with public IPs
- Fund wallets with FET tokens
- Register in Almanac

### LangChain Coordinator
- Deploy to cloud (AWS, GCP, Azure)
- Set environment variables
- Use process manager (PM2, systemd)
- Monitor with logging service

### Claude Service
- Deploy to cloud with SSL
- Use environment variables for secrets
- Set up database backup
- Configure CORS for production

---

## Cost Estimates

**Fetch.ai**:
- Agent registration: ~1 FET
- Message sending: ~0.001 FET per message
- Monthly: ~$10-50 depending on volume

**Claude API**:
- Sonnet 4: ~$3 per million input tokens
- Average request: ~500 tokens = $0.0015
- 1000 requests/day = ~$1.50/day = $45/month

**Hosting**:
- Cloud VM: $20-100/month
- Database: $10-50/month

**Total**: ~$100-250/month for production

---

## Next Steps

1. ✅ Deploy agents to Fetch.ai Agentverse
2. ✅ Configure LangChain coordinator
3. ✅ Test chat UI with various priorities
4. 📊 Add analytics dashboard
5. 🔔 Add notifications (SMS, email)
6. 🗺️ Add map visualization
7. 📱 Create mobile app
8. 🤝 Add multi-agent negotiation rounds

---

## Support

- Fetch.ai Docs: https://docs.fetch.ai
- LangChain Docs: https://python.langchain.com
- Anthropic Docs: https://docs.anthropic.com

