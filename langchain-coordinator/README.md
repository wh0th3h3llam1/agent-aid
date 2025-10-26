# 🧠 LangChain Coordinator - CONFIGURED

## Your Agent Addresses

✅ **Need Agent**: `agent1q2h8e88wru7sl7hfy4kkrjrf4p4zqghtu7umsw2r2twkewcscnrwymnjju9`  
✅ **Supply Agent**: `agent1qd0kdf9py6ehfjqq6s969dcv90sj9jg594yk252926pp2z85r82z6aepahg`

These addresses are **hardcoded** in `coordinator_configured.py` - ready to use!

---

## 🚀 Quick Start

### 1. Set Your Anthropic API Key

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

Get your key from: https://console.anthropic.com

### 2. Test the Coordinator

```bash
cd langchain-coordinator
./test_coordinator.sh
```

This will:
- ✅ Verify your API key works
- ✅ Test Claude analysis with a sample message
- ✅ Show priority detection in action
- ✅ Exit after one test

### 3. Start the Coordinator (Production)

```bash
./start_coordinator.sh
```

This will:
- ✅ Check if Claude service is running
- ✅ Start polling for chat messages
- ✅ Forward requests to your Fetch.ai agents
- ✅ Run continuously (press Ctrl+C to stop)

---

## 📋 Prerequisites

### Required
- ✅ Python 3.9+
- ✅ Anthropic API key (in environment)
- ✅ Dependencies installed: `pip install -r requirements.txt`

### Optional (for full system)
- Claude service running at http://localhost:3000
- Fetch.ai agents deployed and running

---

## 🧪 Test Mode

Test the coordinator without needing the full system:

```bash
export TEST_MODE="true"
python3 coordinator_configured.py
```

Expected output:
```
============================================================
🧠 LangChain Coordination Agent - CONFIGURED
============================================================
   Claude Model: claude-sonnet-4-20250514
   Service: http://localhost:3000
   Need Agent: agent1q2h8e88wru7sl7hfy4kkrjrf4p4zqghtu7umsw2r2twkewcscnrwymnjju9
   Supply Agent: agent1qd0kdf9py6ehfjqq6s969dcv90sj9jg594yk252926pp2z85r82z6aepahg
============================================================

✅ Anthropic API Key: sk-ant-api03-xxxxx...

🧪 TEST MODE - Processing sample message...

======================================================================
📨 New Message: Emergency! We need 100 blankets urgently in San Fr...
======================================================================

🤖 Claude Analysis:
   Items: ['blankets']
   Priority: CRITICAL
   Quantity: 100
   Location: San Francisco
   Victim Count: 200
   Urgency Indicators: ['Emergency', 'urgently', '200 people']

✅ Request stored: REQ-1234567890

📤 Forwarding to Need Agent...
   Address: agent1q2h8e88wru7sl7...
✅ Successfully forwarded to need agent

📊 Result: {
  "success": true,
  "request_id": "REQ-1234567890",
  "analysis": {
    "items": ["blankets"],
    "priority": "critical",
    "quantity": 100,
    ...
  }
}
```

---

## 🔄 Production Mode

Run continuously and poll for chat messages:

```bash
python3 coordinator_configured.py
```

Or use the startup script:

```bash
./start_coordinator.sh
```

The coordinator will:
1. Poll Claude service every 3 seconds
2. Check for new chat messages
3. Analyze each message with Claude
4. Detect priority automatically
5. Forward to your Fetch.ai need agent
6. Send response back to chat UI

---

## 📊 Priority Detection

The coordinator automatically detects priority based on keywords:

| Priority | Keywords | Example |
|----------|----------|---------|
| **CRITICAL** | emergency, urgent, life-threatening | "Emergency! 500 people need help!" |
| **HIGH** | ASAP, quickly, urgent | "We urgently need supplies ASAP" |
| **MEDIUM** | need, require, looking for | "Looking for 30 blankets" |
| **LOW** | when available, no rush | "Can you provide when available?" |

---

## 🔧 Configuration

### Agent Addresses (Hardcoded)

In `coordinator_configured.py`:

```python
NEED_AGENT_ADDRESS = "agent1q2h8e88wru7sl7hfy4kkrjrf4p4zqghtu7umsw2r2twkewcscnrwymnjju9"
SUPPLY_AGENT_ADDRESS = "agent1qd0kdf9py6ehfjqq6s969dcv90sj9jg594yk252926pp2z85r82z6aepahg"
```

### Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional
export CLAUDE_SERVICE_URL="http://localhost:3000"  # Default
export TEST_MODE="true"  # For testing only
```

---

## 📁 Files

```
langchain-coordinator/
├── coordinator_configured.py    ← Main coordinator (YOUR AGENTS)
├── coordinator_agent.py         ← Generic version (template)
├── start_coordinator.sh         ← Production startup script
├── test_coordinator.sh          ← Test script
├── requirements.txt             ← Python dependencies
└── README.md                    ← This file
```

---

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY not set"

**Solution**:
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### "Cannot connect to Claude service"

**Solution**: Start the Claude service first:
```bash
cd ../agentaid-claude-service
node server.js
```

### "Invalid API Key"

**Solution**: 
1. Check your key at https://console.anthropic.com
2. Make sure it starts with `sk-ant-`
3. Regenerate if needed

### "Failed to forward to need agent"

**Possible causes**:
1. Claude service not running
2. Need agent not deployed on Fetch.ai
3. Network connectivity issues

**Check**:
```bash
# Test Claude service
curl http://localhost:3000/health

# Verify agent address
echo "agent1q2h8e88wru7sl7hfy4kkrjrf4p4zqghtu7umsw2r2twkewcscnrwymnjju9"
```

---

## 📊 Example Usage

### Test with Sample Message

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export TEST_MODE="true"
python3 coordinator_configured.py
```

### Run in Production

```bash
# Terminal 1: Start Claude service
cd ../agentaid-claude-service
node server.js

# Terminal 2: Start coordinator
cd ../langchain-coordinator
export ANTHROPIC_API_KEY="sk-ant-..."
./start_coordinator.sh
```

### Send Test Request via Chat UI

1. Open http://localhost:3000/chat.html
2. Type: "Emergency! Need 100 blankets in San Francisco"
3. Watch coordinator logs for analysis
4. See quotes appear in UI

---

## 💡 What It Does

1. **Receives** chat messages from users
2. **Analyzes** with Claude AI to extract:
   - Items needed
   - Quantities
   - Priority level (auto-detected!)
   - Location
   - Contact info
   - Victim count
3. **Forwards** structured request to your Fetch.ai need agent
4. **Coordinates** with supply agent via need agent
5. **Returns** results to chat UI

---

## 🎯 Next Steps

After testing the coordinator:

1. ✅ Verify it connects to Claude API
2. ✅ Test priority detection with different messages
3. ✅ Start Claude service
4. ✅ Run coordinator in production mode
5. ✅ Open chat UI and submit requests
6. ✅ Monitor logs for agent communication

---

## 📞 Support

If you encounter issues:

1. Check logs for error messages
2. Verify API key is correct
3. Ensure Claude service is running
4. Test with `./test_coordinator.sh` first
5. Check Fetch.ai agents are deployed

---

**Your coordinator is ready to use! 🚀**

Just set your `ANTHROPIC_API_KEY` and run `./start_coordinator.sh`
