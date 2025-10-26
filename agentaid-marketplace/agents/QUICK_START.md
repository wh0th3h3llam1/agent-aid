# Quick Start Guide - AgentAid Chat Protocol

## 🚀 Start Agents (Local Testing)

### 1. Start Supply Agent
```bash
cd agent-aid/agentaid-marketplace/agents
python supply_agent_chat_adapter.py
```
- Runs on: http://localhost:8001
- Has: Burn Medicine inventory (150 kits @ $75)

### 2. Start Need Agent
```bash
cd agent-aid/agentaid-marketplace/agents
export SUPPLY_AGENT_ENDPOINT="http://localhost:8001"
python need_agent_chat_adapter.py
```
- Runs on: http://localhost:8000
- Will query supply agent on port 8001

## 📤 Send Test Request

```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "version": "v1",
    "sender": "test_user",
    "target": "need_agent",
    "session": "test_123",
    "payload": "{\"messages\": [{\"type\": \"text\", \"text\": \"{\\\"items\\\": [\\\"medical supplies\\\", \\\"burn medicine\\\"], \\\"quantity_needed\\\": \\\"100\\\", \\\"location\\\": \\\"San Francisco, CA\\\", \\\"priority\\\": \\\"high\\\", \\\"coordinates\\\": {\\\"latitude\\\": 37.7749, \\\"longitude\\\": -122.4194}, \\\"request_id\\\": \\\"TEST-123\\\"}\"}]}"
  }'
```

## 📊 Expected Flow

```
User → Need Agent → Supply Agent → Need Agent → User
        (JSON)        (JSON)         (Quote)     (Recommendation)
```

## ✅ Success Indicators

**Need Agent Console:**
```
📥 NEW DISASTER RELIEF REQUEST
Request ID: TEST-123
Items: medical supplies, burn medicine
📤 Querying Medical Supply Agent at http://localhost:8001
✅ Received quote from Medical Supply Agent
```

**Supply Agent Console:**
```
📦 Received structured need request: TEST-123
💰 GENERATING QUOTE
✅ Quote generated: Coverage 100.0%, Cost $11875.00, ETA 1.9h
```

## 🌐 Deploy to Agentverse

### 1. Create Tunnels
```bash
# Terminal 1
cloudflared tunnel --url http://localhost:8000

# Terminal 2
cloudflared tunnel --url http://localhost:8001
```
Copy the URLs (e.g., `https://abc-123.trycloudflare.com`)

### 2. Set Environment Variables
```bash
# Need Agent
export AGENT_EXTERNAL_ENDPOINT="https://your-need-url.trycloudflare.com"
export AGENTVERSE_KEY="your_api_key"

# Supply Agent
export AGENT_EXTERNAL_ENDPOINT="https://your-supply-url.trycloudflare.com"
export AGENTVERSE_KEY="your_api_key"
```

### 3. Register Agents
```bash
python register_need_agent.py
python register_supply_agent.py
```

### 4. Update Need Agent Config
After registering supply agent, get its address and update:
```bash
export SUPPLY_AGENT_ENDPOINT="https://your-supply-url.trycloudflare.com"
export SUPPLY_AGENT_ADDRESS="agent1q..."  # From supply agent registration
```

## 🔧 Troubleshooting

**No quotes received:**
- Check SUPPLY_AGENT_ENDPOINT is correct
- Verify supply agent is running
- Check coordinates are within 120 km of SF (37.7749, -122.4194)

**JSON Parse Error:**
- Verify JSON is properly escaped
- Check all required fields are present
- Use a JSON validator

**Connection Timeout:**
- Supply agent may be offline
- Check firewall settings
- Increase timeout in need agent (currently 30s)

## 📝 Minimal JSON Request

```json
{
  "items": ["burn medicine"],
  "quantity_needed": "50",
  "location": "San Francisco, CA",
  "priority": "high",
  "coordinates": {
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "request_id": "REQ-DEMO-001"
}
```

## 📚 More Information

- **Full Documentation**: `CHAT_PROTOCOL_USAGE.md`
- **Integration Summary**: `INTEGRATION_SUMMARY.md`
- **Agentverse Docs**: https://docs.agentverse.ai/

---
**Need help?** Check console logs in both agents for detailed debugging information.
