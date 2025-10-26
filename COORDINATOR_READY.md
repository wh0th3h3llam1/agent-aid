# ✅ LangChain Coordinator - READY TO USE!

## 🎉 Your Coordinator is Configured!

I've created a **fully configured** LangChain coordinator with your Fetch.ai agent addresses hardcoded and ready to use.

---

## 📍 Your Agent Addresses (Configured)

✅ **Need Agent**:  
`agent1q2h8e88wru7sl7hfy4kkrjrf4p4zqghtu7umsw2r2twkewcscnrwymnjju9`

✅ **Supply Agent**:  
`agent1qd0kdf9py6ehfjqq6s969dcv90sj9jg594yk252926pp2z85r82z6aepahg`

These are **hardcoded** in the coordinator - no need to set environment variables for agent addresses!

---

## 🚀 Quick Start (3 Steps)

### Step 1: Set Your Anthropic API Key

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

*(Get your key from: https://console.anthropic.com)*

### Step 2: Install Dependencies

```bash
cd langchain-coordinator
pip install -r requirements.txt
```

### Step 3: Test It!

```bash
./test_coordinator.sh
```

**Expected output**:
```
🧪 Testing LangChain Coordinator
================================

✅ Anthropic API Key found

🧪 Running in TEST MODE
   Will process one sample message and exit

================================

============================================================
🧠 LangChain Coordination Agent - CONFIGURED
============================================================
   Claude Model: claude-sonnet-4-20250514
   Need Agent: agent1q2h8e88wru7sl7hfy4kkrjrf4p4zqghtu7umsw2r2twkewcscnrwymnjju9
   Supply Agent: agent1qd0kdf9py6ehfjqq6s969dcv90sj9jg594yk252926pp2z85r82z6aepahg
============================================================

🤖 Claude Analysis:
   Items: ['blankets']
   Priority: CRITICAL
   Quantity: 100
   Location: San Francisco
   Victim Count: 200
   Urgency Indicators: ['Emergency', 'urgently']

✅ Request stored: REQ-1234567890
✅ Successfully forwarded to need agent
```

---

## 📁 Files Created

```
langchain-coordinator/
├── coordinator_configured.py    ← Main file (YOUR AGENTS HARDCODED)
├── start_coordinator.sh         ← Production startup script
├── test_coordinator.sh          ← Test script
├── README.md                    ← Full documentation
└── requirements.txt             ← Dependencies
```

---

## 🧪 Test Mode vs Production Mode

### Test Mode (Quick Test)
```bash
./test_coordinator.sh
```
- Processes ONE sample message
- Shows Claude analysis
- Exits immediately
- Perfect for testing API key

### Production Mode (Continuous)
```bash
./start_coordinator.sh
```
- Polls for chat messages every 3 seconds
- Processes all incoming requests
- Runs continuously
- Press Ctrl+C to stop

---

## 💡 What the Coordinator Does

### 1. Receives User Input
```
User: "Emergency! Need 100 blankets in San Francisco. 
       200 people affected."
```

### 2. Analyzes with Claude AI
```
🤖 Claude Analysis:
   Items: ['blankets']
   Priority: CRITICAL (auto-detected!)
   Quantity: 100
   Location: San Francisco
   Victim Count: 200
   Urgency Indicators: ['Emergency', '200 people']
```

### 3. Forwards to Your Fetch.ai Need Agent
```
📤 Forwarding to Need Agent...
   Address: agent1q2h8e88wru7sl7...
✅ Successfully forwarded
```

### 4. Need Agent Coordinates with Supply Agent
```
Need Agent → Supply Agent → Quote → Back to User
```

---

## 🎯 Priority Detection (Automatic!)

The coordinator automatically detects priority:

| Input | Detected Priority |
|-------|-------------------|
| "Emergency! 500 people need help!" | **CRITICAL** ⚠️ |
| "We urgently need supplies ASAP" | **HIGH** 🔶 |
| "Looking for 30 blankets" | **MEDIUM** 🔵 |
| "Can you provide when available?" | **LOW** 🟢 |

**No manual selection needed!** Claude understands urgency from context.

---

## 🔧 Configuration

### Hardcoded in coordinator_configured.py

```python
# Your specific agent addresses
NEED_AGENT_ADDRESS = "agent1q2h8e88wru7sl7hfy4kkrjrf4p4zqghtu7umsw2r2twkewcscnrwymnjju9"
SUPPLY_AGENT_ADDRESS = "agent1qd0kdf9py6ehfjqq6s969dcv90sj9jg594yk252926pp2z85r82z6aepahg"

# Reads from environment
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_SERVICE_URL = os.getenv("CLAUDE_SERVICE_URL", "http://localhost:3000")
```

### Only Need to Set

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

That's it! Agent addresses are already configured.

---

## 📊 Complete System Flow

```
User Types in Chat UI
    ↓
Claude Service receives message
    ↓
LangChain Coordinator polls for messages
    ↓
Claude AI analyzes & detects priority
    ↓
Forwards to Need Agent (agent1q2h8e88...)
    ↓
Need Agent broadcasts to Supply Agent (agent1qd0kdf9...)
    ↓
Supply Agent sends quote
    ↓
Need Agent evaluates & selects
    ↓
Results shown in Chat UI
```

---

## 🐛 Troubleshooting

### Error: "ANTHROPIC_API_KEY not set"

**Solution**:
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### Error: "Cannot connect to Claude service"

**Solution**: Start Claude service first:
```bash
cd agentaid-claude-service
node server.js
```

Then in another terminal:
```bash
cd langchain-coordinator
./start_coordinator.sh
```

### Error: "Invalid API Key"

**Solution**:
1. Go to https://console.anthropic.com
2. Check your API key
3. Make sure it starts with `sk-ant-`
4. Regenerate if needed

### No errors but nothing happens

**Check**:
1. Is Claude service running? `curl http://localhost:3000/health`
2. Are Fetch.ai agents deployed and running?
3. Check coordinator logs for messages

---

## ✅ Verification Checklist

Before running in production:

- [ ] Anthropic API key is set
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test mode works (`./test_coordinator.sh`)
- [ ] Claude service is running
- [ ] Fetch.ai agents are deployed
- [ ] Agent addresses are correct

---

## 🎯 Next Steps

### 1. Test the Coordinator
```bash
cd langchain-coordinator
export ANTHROPIC_API_KEY="sk-ant-..."
./test_coordinator.sh
```

### 2. Start Full System

**Terminal 1** - Claude Service:
```bash
cd agentaid-claude-service
node server.js
```

**Terminal 2** - LangChain Coordinator:
```bash
cd langchain-coordinator
export ANTHROPIC_API_KEY="sk-ant-..."
./start_coordinator.sh
```

**Terminal 3** - Open Chat UI:
```bash
open http://localhost:3000/chat.html
```

### 3. Submit Test Request

In chat UI, type:
```
Emergency! Need 100 blankets in San Francisco. 
200 people affected. Contact: 555-1234
```

Watch the coordinator logs to see:
- Claude analysis
- Priority detection
- Forwarding to need agent

---

## 💰 Cost Estimate

### Testing (100 requests)
- Claude API: ~$0.50
- Fetch.ai testnet: Free
- **Total: ~$0.50**

### Production (1000 requests/day)
- Claude API: ~$150/month
- Fetch.ai mainnet: ~$10-50/month
- **Total: ~$160-200/month**

### Optimization
- Use Claude Haiku: Save 90% (~$15/month)
- Cache requests: Save 30%

---

## 📚 Documentation

- **README.md** - Full coordinator documentation
- **LANGCHAIN_SETUP.md** - Complete setup guide
- **INTEGRATION_GUIDE.md** - System integration

---

## 🎉 You're Ready!

Your LangChain coordinator is **fully configured** with your Fetch.ai agent addresses!

**Just run**:
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
cd langchain-coordinator
./test_coordinator.sh
```

**Then start production**:
```bash
./start_coordinator.sh
```

**That's it! 🚀**

---

## 📞 Need Help?

1. Check `langchain-coordinator/README.md` for details
2. Review logs for error messages
3. Test with `./test_coordinator.sh` first
4. Verify API key is correct
5. Ensure Claude service is running

**Your coordinator is ready to coordinate disaster relief! 🌟**
