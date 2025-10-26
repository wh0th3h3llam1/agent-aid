# 🔗 Integration & Coordination Guide
## Making Everything Work Together Perfectly

---

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Flow](#architecture-flow)
3. [Component Integration](#component-integration)
4. [Step-by-Step Setup](#step-by-step-setup)
5. [Testing the Complete System](#testing-the-complete-system)
6. [Monitoring & Debugging](#monitoring--debugging)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## System Overview

### Complete Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                       │
│              Chat UI (chat.html)                        │
│  "Emergency! Need 100 blankets in SF. 200 affected."   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP POST
                     ↓
┌─────────────────────────────────────────────────────────┐
│              CLAUDE SERVICE (Node.js)                   │
│  • Receives chat messages                               │
│  • Stores requests in SQLite                            │
│  • Provides API endpoints                               │
└────────────────────┬────────────────────────────────────┘
                     │ Polling (3s)
                     ↓
┌─────────────────────────────────────────────────────────┐
│         LANGCHAIN COORDINATOR (Python)                  │
│  • Polls for new messages                               │
│  • Analyzes with Claude Sonnet 4                        │
│  • Detects priority automatically                       │
│  • Extracts structured data                             │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP POST
                     ↓
┌─────────────────────────────────────────────────────────┐
│        FETCH.AI NEED AGENT (Agentverse)                 │
│  • Receives disaster request                            │
│  • Broadcasts to all suppliers                          │
│  • Waits 10s for quotes                                 │
│  • Evaluates & negotiates                               │
└────────────────────┬────────────────────────────────────┘
                     │ uAgent Messages
         ┌───────────┴───────────┐
         ↓                       ↓
┌──────────────────┐    ┌──────────────────┐
│ SUPPLY AGENT 1   │    │ SUPPLY AGENT 2   │
│ (Agentverse)     │    │ (Agentverse)     │
│                  │    │                  │
│ Medical Depot    │    │ Relief Center    │
│ • Check inv      │    │ • Check inv      │
│ • Calc cost/ETA  │    │ • Calc cost/ETA  │
│ • Send quote     │    │ • Send quote     │
└──────────────────┘    └──────────────────┘
         │                       │
         └───────────┬───────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│        FETCH.AI NEED AGENT (Evaluation)                 │
│  • Collects all quotes                                  │
│  • Scores: cost (40%) + ETA (30%) + coverage (30%)     │
│  • Selects best supplier                                │
│  • Sends result to Claude service                       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP POST
                     ↓
┌─────────────────────────────────────────────────────────┐
│              CLAUDE SERVICE (Storage)                   │
│  • Stores quotes & selection                            │
│  • Makes available via API                              │
└────────────────────┬────────────────────────────────────┘
                     │ Polling (3s)
                     ↓
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                       │
│  ✅ Quotes received!                                    │
│  📦 Medical Depot: $3,000 (1h)                          │
│  📦 Relief Center: $2,500 (1.5h) ← SELECTED             │
└─────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Role | Technology |
|-----------|------|------------|
| **Chat UI** | User interface, displays results | HTML/CSS/JavaScript |
| **Claude Service** | API backend, data storage | Node.js + SQLite |
| **LangChain Coordinator** | NLP analysis, priority detection | Python + Claude API |
| **Need Agent** | Coordination, negotiation | Fetch.ai uAgents |
| **Supply Agents** | Inventory, quotes | Fetch.ai uAgents |

---

## Architecture Flow

### Timeline of a Request

```
Time    Component              Action
────────────────────────────────────────────────────────────
0:00    User                   Types: "Emergency! Need blankets"
0:01    Chat UI                POST /api/extract
0:01    Claude Service         Stores request, returns ID
0:01    Chat UI                Shows "Request received"
0:01    Chat UI                Starts polling for quotes

0:03    LangChain Coordinator  Polls /api/chat/pending
0:03    LangChain Coordinator  Analyzes with Claude
0:04    LangChain Coordinator  Priority: CRITICAL detected
0:04    LangChain Coordinator  Forwards to Need Agent

0:05    Need Agent             Receives request
0:05    Need Agent             Broadcasts to Supply Agents
0:06    Supply Agent 1         Checks inventory
0:06    Supply Agent 1         Sends quote: $3,000 (1h)
0:07    Supply Agent 2         Checks inventory
0:07    Supply Agent 2         Sends quote: $2,500 (1.5h)

0:15    Need Agent             Collects all quotes (waited 10s)
0:15    Need Agent             Evaluates: Agent 2 wins (best value)
0:15    Need Agent             Sends result to Claude Service

0:16    Chat UI                Polls /api/uagent/updates
0:16    Chat UI                Receives 2 quotes
0:16    Chat UI                Displays quotes + selection
0:16    User                   Sees results!
```

**Total Time**: ~15-20 seconds from input to results

---

## Component Integration

### 1. Chat UI ↔ Claude Service

**Connection**: HTTP REST API

**Endpoints Used**:
```javascript
// Submit request
POST /api/extract
Body: { input: "user message", source: "chat" }
Response: { success: true, data: { request_id: "REQ-123" } }

// Poll for quotes
GET /api/uagent/updates
Response: { success: true, updates: [...] }

// Check health
GET /health
Response: { service: "AgentAid Claude Service" }
```

**Configuration**:
```javascript
// In chat.html
const CLAUDE_SERVICE_URL = window.location.origin; // http://localhost:3000
```

### 2. Claude Service ↔ LangChain Coordinator

**Connection**: HTTP Polling

**Flow**:
```python
# LangChain polls every 3 seconds
async with httpx.AsyncClient() as client:
    response = await client.get(f"{CLAUDE_SERVICE_URL}/api/chat/pending")
    messages = response.json().get("messages", [])
    
    for msg in messages:
        result = await self.process_chat_message(msg["text"])
```

**Configuration**:
```bash
# In coordinator.env
export CLAUDE_SERVICE_URL="http://localhost:3000"
```

### 3. LangChain Coordinator ↔ Fetch.ai Need Agent

**Connection**: HTTP POST via Claude Service

**Flow**:
```python
# LangChain forwards to Need Agent
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{CLAUDE_SERVICE_URL}/api/uagent/forward-to-need-agent",
        json={
            "need_agent_address": NEED_AGENT_ADDRESS,
            "request_data": {
                "request_id": "REQ-123",
                "items": ["blankets"],
                "quantity": 100,
                "priority": "critical",
                ...
            }
        }
    )
```

**Configuration**:
```bash
# In coordinator.env
export NEED_AGENT_ADDRESS="agent1qy7j9l5n4o6p8r0t1v..."
```

### 4. Need Agent ↔ Supply Agents

**Connection**: Fetch.ai uAgent Messages

**Flow**:
```python
# Need Agent broadcasts
for supplier_addr in SUPPLIER_ADDRESSES:
    await ctx.send(supplier_addr, QuoteRequest(...))

# Supply Agents respond
@protocol.on_message(model=QuoteRequest, replies=QuoteResponse)
async def handle_quote_request(ctx: Context, sender: str, msg: QuoteRequest):
    # Calculate quote
    await ctx.send(sender, QuoteResponse(...))
```

**Configuration**:
```bash
# In Need Agent environment
export SUPPLIER_ADDRESSES="agent1qw...,agent1qx..."
```

### 5. Need Agent ↔ Claude Service

**Connection**: HTTP POST for results

**Flow**:
```python
# Need Agent sends negotiation result
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{CLAUDE_SERVICE_URL}/api/uagent/update",
        json={
            "request_id": "REQ-123",
            "agent_id": "need_agent_coordinator",
            "type": "negotiation_complete",
            "data": {
                "selected_supplier": "community_relief_center",
                "reasoning": "Best value...",
                ...
            }
        }
    )
```

---

## Step-by-Step Setup

### Prerequisites Checklist

Before starting, ensure you have:

- ✅ Fetch.ai agents deployed (see FETCHAI_DEPLOYMENT.md)
- ✅ Agent addresses saved
- ✅ Anthropic API key (see LANGCHAIN_SETUP.md)
- ✅ Node.js installed
- ✅ Python 3.9+ installed

### Step 1: Setup Database

```bash
cd agentaid-marketplace/db
python init_db.py
```

Expected output:
```
📊 Creating database: agent_aid.db
✅ Database schema created
✅ Database initialization complete
```

### Step 2: Add Inventory to Suppliers

```bash
cd agentaid-marketplace
python -c "
from services.inventory_db import connect, add_inventory_item, get_supplier_config

conn = connect('db/agent_aid.db')

# Medical Emergency Depot
medical = get_supplier_config(conn, 'medical_emergency_depot')
if medical:
    add_inventory_item(conn, medical['id'], 'blankets', 300, 'unit', 30.0, 'emergency')
    add_inventory_item(conn, medical['id'], 'first aid kit', 100, 'kit', 50.0, 'medical')
    add_inventory_item(conn, medical['id'], 'water bottles', 500, 'bottle', 2.0, 'supplies')
    print('✅ Medical depot inventory added')

# Community Relief Center
community = get_supplier_config(conn, 'community_relief_center')
if community:
    add_inventory_item(conn, community['id'], 'blankets', 150, 'unit', 25.0, 'emergency')
    add_inventory_item(conn, community['id'], 'food packages', 200, 'package', 20.0, 'food')
    add_inventory_item(conn, community['id'], 'water bottles', 300, 'bottle', 1.5, 'supplies')
    print('✅ Community center inventory added')

conn.close()
"
```

### Step 3: Configure Environment Variables

Create `config.env` in project root:

```bash
# Anthropic API Key
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"

# Fetch.ai Agent Addresses
export MEDICAL_AGENT_ADDRESS="agent1qw5h7k3l2m4n6p8r9s..."
export COMMUNITY_AGENT_ADDRESS="agent1qx6i8k4m3n5o7q9t0u..."
export NEED_AGENT_ADDRESS="agent1qy7j9l5n4o6p8r0t1v..."

# For Need Agent
export SUPPLIER_ADDRESSES="$MEDICAL_AGENT_ADDRESS,$COMMUNITY_AGENT_ADDRESS"

# Claude Service
export CLAUDE_SERVICE_URL="http://localhost:3000"

# Optional
export TEST_MODE="false"
```

Load configuration:
```bash
source config.env
```

### Step 4: Start Claude Service

```bash
# Terminal 1
cd agentaid-claude-service
npm install  # First time only
node server.js
```

Expected output:
```
🚀 AgentAid Claude Service
   Port: 3000
   Database: ../agentaid-marketplace/db/agent_aid.db
✅ Server running on http://localhost:3000
```

Verify:
```bash
curl http://localhost:3000/health
# Should return: {"service":"AgentAid Claude Service"}
```

### Step 5: Start LangChain Coordinator

```bash
# Terminal 2
cd langchain-coordinator
source ../config.env
python coordinator_agent.py
```

Expected output:
```
============================================================
🧠 LangChain Coordination Agent
============================================================
   Claude Model: claude-sonnet-4-20250514
   Service: http://localhost:3000
   Need Agent: agent1qy7j9l5n4o6p8r0t1v...
============================================================

🔄 Coordinator polling for chat messages...
```

### Step 6: Verify Fetch.ai Agents

Check all agents are running in Agentverse:

1. Go to https://agentverse.ai/agents
2. Verify status of all 3 agents:
   - ✅ medical_emergency_depot: Running
   - ✅ community_relief_center: Running
   - ✅ need_agent_coordinator: Running

### Step 7: Open Chat UI

```bash
# Open in browser
open http://localhost:3000/chat.html

# Or manually navigate to:
http://localhost:3000/chat.html
```

---

## Testing the Complete System

### Test 1: Critical Priority Request

**Input** (in Chat UI):
```
Emergency! Building collapse in San Francisco. 
Need 100 blankets immediately. 500 people affected. 
Life-threatening situation! Contact: 555-1234
```

**Expected Flow**:

1. **Chat UI** (0-1s):
   ```
   ✅ Request received!
   Request ID: REQ-1234567890
   Items: blankets
   Priority: CRITICAL
   
   I'm coordinating with suppliers now...
   ```

2. **LangChain Coordinator** (3-4s):
   ```
   🤖 Claude Analysis:
      Items: ['blankets']
      Priority: CRITICAL
      Quantity: 100
      Urgency Indicators: ['Emergency', 'immediately', 'Life-threatening']
   
   ✅ Request stored: REQ-1234567890
   ✅ Forwarded to need agent
   ```

3. **Need Agent** (5-15s):
   ```
   🚨 Received disaster request: REQ-1234567890
      Items: ['blankets']
      Priority: critical
   
   📢 Broadcasting to 2 suppliers...
   
   💰 Received quote from Medical Emergency Depot
      Cost: $3,000, ETA: 1h
   
   💰 Received quote from Community Relief Center
      Cost: $2,500, ETA: 1.5h
   
   🤝 Evaluating 2 quotes...
      📊 Medical Depot: Score=0.82
      📊 Relief Center: Score=0.89 ✓
   
   ✅ Selected: Community Relief Center
   ```

4. **Chat UI** (16-20s):
   ```
   🎉 Received 2 quote(s)!
   
   📦 Medical Emergency Depot
      Items: 100 blankets @ $30
      Total: $3,000
      ETA: 1.0 hours
      Delivery: ambulance
   
   📦 Community Relief Center ← SELECTED
      Items: 100 blankets @ $25
      Total: $2,500
      ETA: 1.5 hours
      Delivery: truck
   
   Our AI agent selected Community Relief Center
   Reason: Best balance of cost and coverage
   ```

### Test 2: High Priority Request

**Input**:
```
We urgently need medical supplies at Oakland shelter. 
About 50 people waiting. Please send ASAP.
```

**Expected Priority**: HIGH 🔶

### Test 3: Medium Priority Request

**Input**:
```
Looking for 30 blankets for community center in Berkeley.
Contact: shelter@example.com
```

**Expected Priority**: MEDIUM 🔵

### Test 4: Low Priority Request

**Input**:
```
Can you provide some water bottles when available? 
No rush, just planning ahead.
```

**Expected Priority**: LOW 🟢

---

## Monitoring & Debugging

### Monitor All Components

#### 1. Claude Service Logs

```bash
# Terminal 1
cd agentaid-claude-service
node server.js

# Watch for:
# - POST /api/extract (new requests)
# - GET /api/uagent/updates (UI polling)
# - POST /api/uagent/update (agent updates)
```

#### 2. LangChain Coordinator Logs

```bash
# Terminal 2
cd langchain-coordinator
python coordinator_agent.py

# Watch for:
# - 🤖 Claude Analysis (request analysis)
# - ✅ Request stored (forwarded to service)
# - ✅ Forwarded to need agent (sent to Fetch.ai)
```

#### 3. Fetch.ai Agent Logs

In Agentverse dashboard:
1. Go to **Agents**
2. Click on agent name
3. View **Logs** tab

Watch for:
- Need Agent: "Received disaster request", "Broadcasting", "Selected"
- Supply Agents: "Received quote request", "Quote ready"

#### 4. Database Queries

```bash
# Check requests
sqlite3 agentaid-marketplace/db/agent_aid.db "SELECT * FROM requests ORDER BY timestamp DESC LIMIT 5;"

# Check updates
sqlite3 agentaid-marketplace/db/agent_aid.db "SELECT * FROM agent_updates ORDER BY received_at DESC LIMIT 10;"

# Check inventory
sqlite3 agentaid-marketplace/db/agent_aid.db "SELECT s.label, i.name, i.qty FROM suppliers s JOIN items i ON s.id = i.supplier_id;"
```

### Debug Checklist

When something doesn't work:

1. **Check all services are running**:
   ```bash
   # Claude Service
   curl http://localhost:3000/health
   
   # LangChain Coordinator
   ps aux | grep coordinator_agent.py
   
   # Fetch.ai Agents
   # Check Agentverse dashboard
   ```

2. **Verify environment variables**:
   ```bash
   echo $ANTHROPIC_API_KEY
   echo $NEED_AGENT_ADDRESS
   echo $SUPPLIER_ADDRESSES
   ```

3. **Check network connectivity**:
   ```bash
   # Claude API
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "content-type: application/json" \
     -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
   
   # Fetch.ai Agentverse
   curl https://agentverse.ai
   ```

4. **Review logs for errors**:
   ```bash
   # Claude Service
   tail -f agentaid-claude-service/server.log
   
   # LangChain Coordinator
   tail -f langchain-coordinator/coordinator.log
   
   # Fetch.ai Agents
   # Check Agentverse dashboard logs
   ```

### Common Issues & Solutions

#### Issue: "No quotes received"

**Symptoms**: Chat UI shows "Waiting for quotes..." forever

**Debug**:
```bash
# 1. Check if supply agents are running
# Go to Agentverse → Agents → Check status

# 2. Check if need agent received request
# Agentverse → need_agent_coordinator → Logs
# Look for: "Received disaster request"

# 3. Check if need agent broadcasted
# Look for: "Broadcasting to 2 suppliers"

# 4. Check if supply agents received request
# Agentverse → medical_emergency_depot → Logs
# Look for: "Received quote request"

# 5. Check database
sqlite3 agentaid-marketplace/db/agent_aid.db "SELECT * FROM agent_updates WHERE type='quote';"
```

**Solutions**:
- Verify SUPPLIER_ADDRESSES in need agent config
- Check supply agent addresses are correct
- Ensure all agents have FET tokens
- Verify agents are registered in Almanac

#### Issue: "Wrong priority detected"

**Symptoms**: Claude assigns incorrect priority level

**Debug**:
```bash
# Check LangChain coordinator logs
tail -f langchain-coordinator/coordinator.log

# Look for:
# 🤖 Claude Analysis:
#    Priority: X
#    Urgency Indicators: [...]
```

**Solutions**:
- Add more urgency keywords to message
- Customize priority detection in coordinator_agent.py
- Use Claude Opus for better understanding
- Add examples to prompt template

#### Issue: "Connection refused"

**Symptoms**: LangChain can't connect to Claude service

**Debug**:
```bash
# Check if Claude service is running
curl http://localhost:3000/health

# Check port
lsof -i :3000

# Check firewall
sudo ufw status
```

**Solutions**:
- Start Claude service: `node server.js`
- Check CLAUDE_SERVICE_URL environment variable
- Allow port 3000 in firewall
- Verify localhost resolution

---

## Production Deployment

### Architecture for Production

```
Internet
    ↓
Load Balancer (HTTPS)
    ↓
┌─────────────────────────────────┐
│  Web Server (Nginx/Apache)      │
│  - Serves chat.html              │
│  - Proxies to Claude Service    │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Claude Service (Node.js)       │
│  - PM2 process manager           │
│  - PostgreSQL database           │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  LangChain Coordinator (Python) │
│  - systemd service               │
│  - Logging to file               │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Fetch.ai Agentverse (Cloud)    │
│  - Need Agent                    │
│  - Supply Agent 1                │
│  - Supply Agent 2                │
└─────────────────────────────────┘
```

### Deployment Steps

#### 1. Setup Cloud Server

```bash
# Ubuntu 22.04 LTS recommended
# Minimum: 2 CPU, 4GB RAM, 20GB disk

# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python
sudo apt install -y python3.10 python3-pip

# Install Nginx
sudo apt install -y nginx

# Install PM2
sudo npm install -g pm2
```

#### 2. Deploy Claude Service

```bash
# Clone repository
git clone https://github.com/yourusername/agent-aid.git
cd agent-aid/agentaid-claude-service

# Install dependencies
npm install --production

# Setup PM2
pm2 start server.js --name agentaid-service
pm2 save
pm2 startup

# Configure Nginx
sudo nano /etc/nginx/sites-available/agentaid

# Add:
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        root /path/to/agent-aid/agentaid-claude-service/public;
        try_files $uri $uri/ /chat.html;
    }
    
    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/agentaid /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 3. Deploy LangChain Coordinator

```bash
# Create systemd service
sudo nano /etc/systemd/system/agentaid-coordinator.service

# Add:
[Unit]
Description=AgentAid LangChain Coordinator
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/agent-aid/langchain-coordinator
Environment="ANTHROPIC_API_KEY=sk-ant-..."
Environment="NEED_AGENT_ADDRESS=agent1qy..."
Environment="CLAUDE_SERVICE_URL=http://localhost:3000"
ExecStart=/usr/bin/python3 coordinator_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable agentaid-coordinator
sudo systemctl start agentaid-coordinator
sudo systemctl status agentaid-coordinator
```

#### 4. Setup SSL (HTTPS)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

#### 5. Setup Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Setup log rotation
sudo nano /etc/logrotate.d/agentaid

# Add:
/path/to/agent-aid/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}

# Setup alerts (optional)
# Use services like UptimeRobot, Pingdom, or custom scripts
```

### Environment Variables for Production

```bash
# /etc/environment or ~/.bashrc
export NODE_ENV=production
export ANTHROPIC_API_KEY="sk-ant-..."
export NEED_AGENT_ADDRESS="agent1qy..."
export MEDICAL_AGENT_ADDRESS="agent1qw..."
export COMMUNITY_AGENT_ADDRESS="agent1qx..."
export SUPPLIER_ADDRESSES="agent1qw...,agent1qx..."
export CLAUDE_SERVICE_URL="http://localhost:3000"
export DATABASE_PATH="/var/lib/agentaid/agent_aid.db"
```

### Security Checklist

- ✅ Use HTTPS (SSL certificate)
- ✅ Set up firewall (ufw)
- ✅ Use environment variables for secrets
- ✅ Enable rate limiting
- ✅ Set up authentication (if needed)
- ✅ Regular security updates
- ✅ Backup database regularly
- ✅ Monitor logs for suspicious activity

---

## Troubleshooting

### Complete System Not Working

**Step-by-step diagnosis**:

1. **Test each component individually**:
   ```bash
   # Claude Service
   curl http://localhost:3000/health
   
   # LangChain Coordinator
   ps aux | grep coordinator
   
   # Fetch.ai Agents
   # Check Agentverse dashboard
   ```

2. **Test connections**:
   ```bash
   # LangChain → Claude Service
   curl http://localhost:3000/api/chat/pending
   
   # Claude Service → Database
   sqlite3 agentaid-marketplace/db/agent_aid.db ".tables"
   
   # Need Agent → Supply Agents
   # Check Agentverse logs
   ```

3. **Check data flow**:
   ```bash
   # Submit test request
   curl -X POST http://localhost:3000/api/extract \
     -H "Content-Type: application/json" \
     -d '{"input":"Test request","source":"test"}'
   
   # Check if stored
   sqlite3 agentaid-marketplace/db/agent_aid.db "SELECT * FROM requests ORDER BY timestamp DESC LIMIT 1;"
   
   # Check if LangChain processed
   # Look in coordinator logs
   
   # Check if quotes received
   curl http://localhost:3000/api/uagent/updates
   ```

### Performance Issues

**Symptoms**: Slow response times

**Solutions**:
- Use Claude Haiku instead of Sonnet
- Add caching for common requests
- Optimize database queries
- Increase server resources
- Use CDN for static files

### High Costs

**Symptoms**: Unexpected API bills

**Solutions**:
- Monitor API usage in Anthropic console
- Set spending limits
- Use cheaper Claude model
- Implement request caching
- Optimize prompt length

---

## Best Practices

### Development
- ✅ Test locally before deploying
- ✅ Use version control (git)
- ✅ Document changes
- ✅ Keep dependencies updated
- ✅ Write tests for critical paths

### Operations
- ✅ Monitor all services
- ✅ Set up alerts
- ✅ Regular backups
- ✅ Log rotation
- ✅ Performance monitoring

### Security
- ✅ Never commit secrets
- ✅ Use HTTPS in production
- ✅ Regular security audits
- ✅ Keep software updated
- ✅ Implement rate limiting

---

## Success Criteria

Your system is working perfectly when:

- ✅ Chat UI loads without errors
- ✅ Messages submit successfully
- ✅ Priority is detected automatically
- ✅ Quotes appear within 15-20 seconds
- ✅ All 3 Fetch.ai agents show "Running"
- ✅ LangChain coordinator is polling
- ✅ Database stores all data correctly
- ✅ No errors in any logs

---

## Next Steps

After successful integration:

1. ✅ Test with various request types
2. ✅ Monitor performance metrics
3. ✅ Optimize based on usage
4. ✅ Add more supply agents
5. ✅ Implement additional features
6. ✅ Scale for production load

**Congratulations! Your system is fully integrated! 🎉**
