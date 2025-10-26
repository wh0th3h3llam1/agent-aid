# 🚨 AgentAid - Hybrid Architecture
## Fetch.ai Agents + LangChain + Smart Chat UI

---

## 🎯 What You Asked For

✅ **Fetch.ai Agents**: Supply + Need agents deployed to Agentverse  
✅ **LangChain Coordinator**: Uses Claude for smart analysis  
✅ **Chat UI**: Natural language input, no forms  
✅ **Smart Priority**: AI automatically detects urgency level  

---

## 🏗️ Architecture

```
Chat UI (Natural Language)
    ↓
LangChain + Claude (Smart Analysis)
    ↓
Fetch.ai Need Agent (Agentverse)
    ↓
Fetch.ai Supply Agents (Agentverse)
```

---

## 📁 Files Created

### Fetch.ai Agents (Ready to Deploy)
- `fetchai-agents/supply_agent_fetchai.py` - Supply agent
- `fetchai-agents/need_agent_fetchai.py` - Need agent with negotiation

### LangChain Coordinator
- `langchain-coordinator/coordinator_agent.py` - Claude-powered coordinator

### Chat UI
- `agentaid-claude-service/public/chat.html` - Beautiful chat interface

### Documentation
- `HYBRID_DEPLOYMENT_GUIDE.md` - Step-by-step deployment
- `HYBRID_ARCHITECTURE_SUMMARY.md` - Complete overview
- `start_hybrid_local.sh` - Quick start script

---

## 🚀 Quick Start (Local Testing)

### 1. Set API Key
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### 2. Start System
```bash
./start_hybrid_local.sh
```

### 3. Open Chat
```
http://localhost:3000/chat.html
```

### 4. Test Messages
```
"Emergency! Need 100 blankets in SF. 200 people affected!"
→ Priority: CRITICAL ⚠️

"We need supplies at Oakland shelter soon"
→ Priority: HIGH 🔶

"Looking for 30 blankets for community center"
→ Priority: MEDIUM 🔵
```

---

## 🌐 Deploy to Production

### Step 1: Deploy Fetch.ai Agents
1. Go to https://agentverse.ai
2. Create account
3. Deploy `supply_agent_fetchai.py` (2 instances)
4. Deploy `need_agent_fetchai.py` (1 instance)
5. Copy agent addresses

### Step 2: Configure LangChain
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export NEED_AGENT_ADDRESS="agent1qy..."
python langchain-coordinator/coordinator_agent.py
```

### Step 3: Deploy Claude Service
```bash
cd agentaid-claude-service
node server.js
```

### Step 4: Access Chat UI
```
https://your-domain.com/chat.html
```

---

## 🎨 Features

### 1. Smart Priority Detection
AI analyzes your message and automatically assigns priority:

| Keywords | Priority | Response Time |
|----------|----------|---------------|
| "emergency", "life-threatening" | CRITICAL | Immediate |
| "urgent", "ASAP", "quickly" | HIGH | <1 hour |
| Standard requests | MEDIUM | <4 hours |
| "no rush", "when available" | LOW | Flexible |

### 2. Natural Language Input
No forms! Just chat:
```
"We need 50 blankets and 20 first aid kits at 
San Francisco City Hall. About 100 people affected. 
Contact: 555-1234. This is urgent!"
```

AI extracts:
- Items: blankets, first aid kits
- Quantity: 50, 20
- Location: San Francisco City Hall
- Victim count: 100
- Contact: 555-1234
- Priority: HIGH (detected "urgent")

### 3. Multi-Agent Negotiation
1. Need agent broadcasts to all suppliers
2. Suppliers send quotes
3. Need agent evaluates:
   - Cost (40% weight)
   - Speed/ETA (30% weight)
   - Coverage (30% weight)
4. Selects best supplier
5. Shows reasoning in chat

### 4. Real-Time Updates
Chat UI polls every 3 seconds:
- "Checking for quotes..."
- "Received 2 quotes!"
- Shows all quotes with details
- Highlights selected supplier

---

## 📊 Example Flow

```
User Types:
"Emergency! Building collapse. Need 200 blankets immediately. 
500 people affected!"

↓

LangChain Analyzes:
✓ Keywords: "emergency", "immediately"
✓ Victim count: 500 (large scale)
✓ Priority: CRITICAL
✓ Items: ["blankets"]
✓ Quantity: 200

↓

Fetch.ai Need Agent:
✓ Broadcasts to 2 suppliers
✓ Waits 10 seconds
✓ Receives 2 quotes

↓

Quotes Evaluation:
Medical Depot: $6,000 (45 min, ambulance) Score: 0.89
Relief Center: $5,000 (2 hours, truck)   Score: 0.76
Selected: Medical Depot (fastest for critical)

↓

Chat UI Shows:
⚠️ CRITICAL REQUEST
📦 Medical Depot: $6,000 (45 min) ← SELECTED
📦 Relief Center: $5,000 (2 hours)

Reason: Fastest response for critical emergency
```

---

## 💰 Cost Estimates

### Development (Free)
- Local testing: $0
- Fetch.ai testnet: $0

### Production (Monthly)
- Fetch.ai Agentverse: $10-50
- Claude API (Sonnet 4): $30-100
- Cloud hosting: $20-100
- **Total: ~$60-250/month**

---

## 🔧 Troubleshooting

### "No quotes received"
- Check supply agents are running
- Verify agent addresses are correct
- Check location is within radius

### "Priority detection wrong"
- Add more context in message
- Use urgency keywords
- Check Claude API key

### "Agents not communicating"
- Verify Fetch.ai agents are funded
- Check Almanac registration
- Verify endpoints are public

---

## 📚 Documentation

- **HYBRID_DEPLOYMENT_GUIDE.md** - Full deployment steps
- **HYBRID_ARCHITECTURE_SUMMARY.md** - Architecture details
- Fetch.ai Docs: https://docs.fetch.ai
- LangChain Docs: https://python.langchain.com
- Anthropic Docs: https://docs.anthropic.com

---

## 🎉 Ready to Deploy!

Everything is set up for your hybrid approach:

1. ✅ Fetch.ai agents (supply + need)
2. ✅ LangChain coordinator with Claude
3. ✅ Smart priority detection
4. ✅ Beautiful chat UI
5. ✅ Multi-agent negotiation

**Start with local testing, then deploy to Fetch.ai Agentverse!**

---

## 🆘 Need Help?

1. Read `HYBRID_DEPLOYMENT_GUIDE.md`
2. Check `HYBRID_ARCHITECTURE_SUMMARY.md`
3. Test locally first with `./start_hybrid_local.sh`
4. Deploy one agent at a time
5. Monitor logs for errors

**Good luck with your deployment!** 🚀
