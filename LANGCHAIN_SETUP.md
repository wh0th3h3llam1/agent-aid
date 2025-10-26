# 🧠 LangChain Coordinator Setup Guide
## Smart Coordination with Claude AI

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Get Anthropic API Key](#get-anthropic-api-key)
4. [Install Dependencies](#install-dependencies)
5. [Configure Coordinator](#configure-coordinator)
6. [Understanding the Code](#understanding-the-code)
7. [Run Coordinator](#run-coordinator)
8. [Test Priority Detection](#test-priority-detection)
9. [Customize Behavior](#customize-behavior)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The LangChain coordinator uses **Claude Sonnet 4** to:
- 📝 Analyze natural language disaster requests
- 🎯 Automatically detect priority levels (critical/high/medium/low)
- 📊 Extract structured data (items, quantities, location, contact)
- 🤝 Forward requests to Fetch.ai need agent
- 💬 Provide intelligent responses

**No manual priority selection needed!** Claude understands urgency from context.

---

## Prerequisites

### Required Software
```bash
# Python 3.9 or higher
python --version

# pip package manager
pip --version
```

### Required Accounts
- **Anthropic Account** (for Claude API)
- **Fetch.ai Agents** (deployed from previous step)

### Required Information
- Fetch.ai Need Agent Address (from FETCHAI_DEPLOYMENT.md)
- Claude Service URL (default: http://localhost:3000)

---

## Get Anthropic API Key

### Step 1: Create Anthropic Account

1. Go to **https://console.anthropic.com**
2. Click **"Sign Up"**
3. Enter your email and password
4. Verify your email address
5. Complete profile setup

### Step 2: Add Payment Method

Claude API requires a payment method (even for free tier):

1. Go to **"Settings"** → **"Billing"**
2. Click **"Add Payment Method"**
3. Enter credit card details
4. Set spending limit (recommended: $50/month)

**Note**: Free tier includes $5 credit for testing.

### Step 3: Generate API Key

1. Go to **"API Keys"** section
2. Click **"Create Key"**
3. Give it a name: `AgentAid Coordinator`
4. Set permissions: **Full Access**
5. Click **"Create"**
6. **Copy the API key immediately!**
   ```
   sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
7. **Save it securely** - you won't see it again!

### Step 4: Test API Key

```bash
# Test with curl
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: sk-ant-api03-xxx..." \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

Expected response:
```json
{
  "content": [{"text": "Hello! How can I help you today?", "type": "text"}],
  "model": "claude-sonnet-4-20250514",
  ...
}
```

---

## Install Dependencies

### Step 1: Navigate to Coordinator Directory

```bash
cd langchain-coordinator
```

### Step 2: Install Required Packages

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install individually:
pip install anthropic>=0.18.0
pip install httpx>=0.25.0
pip install uagents>=0.12.0
pip install pydantic>=2.0.0
```

### Step 3: Verify Installation

```bash
# Test imports
python -c "import anthropic; import httpx; print('✅ All dependencies installed')"
```

---

## Configure Coordinator

### Step 1: Set Environment Variables

Create a configuration file `coordinator.env`:

```bash
# Anthropic API Key (REQUIRED)
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"

# Fetch.ai Need Agent Address (REQUIRED)
export NEED_AGENT_ADDRESS="agent1qy7j9l5n4o6p8r0t1v..."

# Claude Service URL (default: localhost)
export CLAUDE_SERVICE_URL="http://localhost:3000"

# Optional: Enable test mode
export TEST_MODE="false"
```

### Step 2: Load Configuration

```bash
# Load environment variables
source coordinator.env

# Verify they're set
echo $ANTHROPIC_API_KEY
echo $NEED_AGENT_ADDRESS
echo $CLAUDE_SERVICE_URL
```

### Step 3: Secure Your API Key

**Important**: Never commit API keys to git!

```bash
# Add to .gitignore
echo "coordinator.env" >> .gitignore
echo "*.env" >> .gitignore

# Verify
cat .gitignore
```

---

## Understanding the Code

### Architecture Overview

```
User Input (Natural Language)
    ↓
CoordinatorAgent.analyze_request()
    ↓
Claude API (Sonnet 4)
    ├─ Extracts: items, quantity, location, contact
    ├─ Detects: priority based on urgency indicators
    └─ Returns: Structured JSON
    ↓
CoordinatorAgent.send_to_need_agent()
    ↓
Fetch.ai Need Agent (via Claude Service)
    ↓
Supply Agents respond with quotes
```

### Key Components

#### 1. Request Analysis (Claude AI)

```python
async def analyze_request(self, user_input: str) -> Dict[str, Any]:
    """Use Claude to analyze the disaster request"""
    
    prompt = f"""Analyze this disaster relief request and extract structured information.

User Request: "{user_input}"

Extract and return JSON with:
1. items: list of items needed
2. quantity: estimated quantity
3. priority: "critical", "high", "medium", or "low"
4. location: any location mentioned
5. contact: phone/email if mentioned
6. victim_count: estimated number affected
7. urgency_indicators: keywords indicating priority

Priority Guidelines:
- CRITICAL: Life-threatening, immediate danger, "urgent", "emergency"
- HIGH: Significant need, time-sensitive, "ASAP", "quickly"
- MEDIUM: Important but not immediate
- LOW: General request, flexible timing
"""
```

#### 2. Priority Detection Logic

Claude analyzes these indicators:

| Priority | Keywords | Characteristics |
|----------|----------|----------------|
| **CRITICAL** | emergency, urgent, life-threatening, immediate | Medical emergencies, >100 victims, dangerous situations |
| **HIGH** | ASAP, quickly, soon, urgent | Time-sensitive, 50-100 victims, shelter needs |
| **MEDIUM** | need, require, looking for | Standard requests, 10-50 people, general supplies |
| **LOW** | when available, no rush, planning | Small scale (<10), flexible timing, non-essential |

#### 3. Data Extraction

Claude extracts:
- **Items**: ["blankets", "water bottles", "first aid kits"]
- **Quantity**: 50, 100, 200, etc.
- **Location**: "San Francisco", "Oakland shelter", addresses
- **Contact**: Phone numbers, emails
- **Victim Count**: Number of people affected
- **Urgency Indicators**: Keywords that triggered priority

#### 4. Forwarding to Need Agent

```python
async def send_to_need_agent(self, request_data: Dict[str, Any]) -> bool:
    """Send request to Fetch.ai need agent"""
    
    # Via Claude service as intermediary
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            f"{CLAUDE_SERVICE_URL}/api/uagent/forward-to-need-agent",
            json={
                "need_agent_address": NEED_AGENT_ADDRESS,
                "request_data": request_data
            }
        )
```

---

## Run Coordinator

### Method 1: Direct Execution

```bash
# Make sure environment variables are set
source coordinator.env

# Run coordinator
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
   Service: http://localhost:3000
   Need Agent: agent1qy7j9l5n4o6p8r0t1v...
```

### Method 2: Test Mode

Test with a sample message without polling:

```bash
export TEST_MODE="true"
python coordinator_agent.py
```

Output:
```
🤖 Claude Analysis:
   Items: ['blankets']
   Priority: CRITICAL
   Quantity: 100
   Urgency Indicators: ['Emergency', 'urgently', '200 people']

✅ Request stored: REQ-1234567890
```

### Method 3: Background Service

Run as a background service:

```bash
# Using nohup
nohup python coordinator_agent.py > coordinator.log 2>&1 &

# Save PID
echo $! > coordinator.pid

# Check status
tail -f coordinator.log

# Stop
kill $(cat coordinator.pid)
```

### Method 4: Using systemd (Linux)

Create `/etc/systemd/system/agentaid-coordinator.service`:

```ini
[Unit]
Description=AgentAid LangChain Coordinator
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/agent-aid/langchain-coordinator
Environment="ANTHROPIC_API_KEY=sk-ant-..."
Environment="NEED_AGENT_ADDRESS=agent1qy..."
Environment="CLAUDE_SERVICE_URL=http://localhost:3000"
ExecStart=/usr/bin/python3 coordinator_agent.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable agentaid-coordinator
sudo systemctl start agentaid-coordinator
sudo systemctl status agentaid-coordinator
```

---

## Test Priority Detection

### Test 1: Critical Priority

```bash
# Input
"Emergency! Building collapse in San Francisco. Need 200 blankets 
and 50 first aid kits immediately. 500 people affected. 
Life-threatening situation!"

# Expected Output
🤖 Claude Analysis:
   Items: ['blankets', 'first aid kits']
   Priority: CRITICAL ⚠️
   Quantity: 200
   Urgency Indicators: ['Emergency', 'immediately', 'Life-threatening', '500 people']
```

### Test 2: High Priority

```bash
# Input
"We urgently need medical supplies at Oakland shelter. 
About 100 people waiting. Please send ASAP. Contact: 555-1234"

# Expected Output
🤖 Claude Analysis:
   Items: ['medical supplies']
   Priority: HIGH 🔶
   Quantity: estimated
   Urgency Indicators: ['urgently', 'ASAP', '100 people']
```

### Test 3: Medium Priority

```bash
# Input
"Looking for 30 blankets for community center in Berkeley. 
We have about 20 people. Contact: shelter@example.com"

# Expected Output
🤖 Claude Analysis:
   Items: ['blankets']
   Priority: MEDIUM 🔵
   Quantity: 30
   Urgency Indicators: []
```

### Test 4: Low Priority

```bash
# Input
"Can you provide some water bottles when available? 
No rush, just planning ahead for next week."

# Expected Output
🤖 Claude Analysis:
   Items: ['water bottles']
   Priority: LOW 🟢
   Quantity: estimated
   Urgency Indicators: ['when available', 'No rush']
```

---

## Customize Behavior

### Adjust Priority Weights

Edit `coordinator_agent.py`:

```python
# Change priority detection sensitivity
CRITICAL_THRESHOLD = 0.8  # Higher = stricter
HIGH_THRESHOLD = 0.6
MEDIUM_THRESHOLD = 0.4
```

### Add Custom Keywords

```python
# Add domain-specific urgency keywords
CRITICAL_KEYWORDS = [
    "emergency", "urgent", "life-threatening", "immediate",
    "critical", "dire", "severe", "catastrophic"  # Add more
]

HIGH_KEYWORDS = [
    "ASAP", "quickly", "soon", "urgent",
    "time-sensitive", "pressing", "important"  # Add more
]
```

### Modify Prompt Template

```python
prompt = f"""Analyze this disaster relief request...

Additional Context:
- Organization: Red Cross
- Region: California
- Season: Winter (prioritize cold weather items)

Extract and return JSON with:
...
"""
```

### Change Claude Model

```python
# Use different Claude model
response = client.messages.create(
    model="claude-3-opus-20240229",  # More powerful
    # or
    model="claude-3-haiku-20240307",  # Faster, cheaper
    max_tokens=1024,
    messages=[...]
)
```

### Add Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('coordinator.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Request analyzed: %s", analysis)
```

---

## Troubleshooting

### "Invalid API Key" Error

**Problem**: Authentication failed

**Solutions**:
```bash
# Verify API key is set
echo $ANTHROPIC_API_KEY

# Check key format (should start with sk-ant-)
# Regenerate key in Anthropic console if needed

# Test key directly
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

### "Rate Limit Exceeded" Error

**Problem**: Too many API requests

**Solutions**:
```python
# Add rate limiting
import asyncio
from asyncio import Semaphore

semaphore = Semaphore(5)  # Max 5 concurrent requests

async def analyze_request(self, user_input: str):
    async with semaphore:
        # Your code here
        await asyncio.sleep(0.5)  # Add delay
```

### Priority Detection Inaccurate

**Problem**: Claude assigns wrong priority

**Solutions**:
1. Add more context to prompt
2. Provide examples in prompt:
   ```python
   prompt = f"""...
   
   Examples:
   - "Emergency! 500 people" → CRITICAL
   - "Need supplies ASAP" → HIGH
   - "Looking for blankets" → MEDIUM
   - "When available" → LOW
   
   Now analyze: "{user_input}"
   """
   ```
3. Use Claude Opus for better understanding
4. Add domain-specific keywords

### "Connection Refused" Error

**Problem**: Can't connect to Claude service

**Solutions**:
```bash
# Check if Claude service is running
curl http://localhost:3000/health

# Start Claude service
cd agentaid-claude-service
node server.js

# Check firewall
sudo ufw status
sudo ufw allow 3000
```

### JSON Parsing Error

**Problem**: Claude returns invalid JSON

**Solutions**:
```python
# Add better JSON extraction
try:
    # Try to extract JSON from markdown code blocks
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    
    analysis = json.loads(content)
except json.JSONDecodeError as e:
    logger.error(f"JSON parse error: {e}")
    # Return default structure
    analysis = {
        "items": ["blankets"],
        "quantity": 50,
        "priority": "medium",
        ...
    }
```

### High API Costs

**Problem**: Claude API bills are too high

**Solutions**:
1. **Use cheaper model**:
   ```python
   model="claude-3-haiku-20240307"  # 10x cheaper
   ```

2. **Reduce max_tokens**:
   ```python
   max_tokens=512  # Instead of 1024
   ```

3. **Cache common requests**:
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def analyze_cached(user_input: str):
       return analyze_request(user_input)
   ```

4. **Set spending limits** in Anthropic console

---

## Monitoring & Maintenance

### Check Coordinator Status

```bash
# Check if running
ps aux | grep coordinator_agent.py

# Check logs
tail -f coordinator.log

# Monitor API usage
# Go to https://console.anthropic.com/usage
```

### Performance Metrics

```python
# Add timing
import time

start = time.time()
analysis = await self.analyze_request(user_input)
duration = time.time() - start

logger.info(f"Analysis took {duration:.2f}s")
```

### Error Tracking

```python
# Add error counter
error_count = 0
success_count = 0

try:
    result = await self.process_chat_message(msg)
    success_count += 1
except Exception as e:
    error_count += 1
    logger.error(f"Error: {e}")

# Log stats every 100 requests
if (success_count + error_count) % 100 == 0:
    logger.info(f"Stats: {success_count} success, {error_count} errors")
```

---

## Best Practices

### Security
- ✅ Never commit API keys to git
- ✅ Use environment variables
- ✅ Rotate API keys regularly
- ✅ Set spending limits
- ✅ Monitor API usage

### Performance
- ✅ Use Haiku model for simple tasks
- ✅ Cache common requests
- ✅ Implement rate limiting
- ✅ Use async/await properly
- ✅ Monitor response times

### Reliability
- ✅ Add retry logic for API calls
- ✅ Handle errors gracefully
- ✅ Log all requests/responses
- ✅ Set up health checks
- ✅ Use process manager (PM2, systemd)

---

## Cost Optimization

### Model Comparison

| Model | Cost per 1M tokens | Speed | Quality |
|-------|-------------------|-------|---------|
| Claude 3 Haiku | $0.25 | Fast | Good |
| Claude 3 Sonnet | $3.00 | Medium | Better |
| Claude 3 Opus | $15.00 | Slow | Best |
| **Sonnet 4** | **$3.00** | **Fast** | **Best** |

### Estimated Costs

**Scenario**: 1000 requests/day

- Average request: 500 tokens input, 200 tokens output
- Total: 700 tokens per request
- Daily: 700,000 tokens
- Monthly: 21M tokens

**Cost with Sonnet 4**:
- Input: 21M × $3/1M = $63
- Output: 6M × $15/1M = $90
- **Total: ~$153/month**

**Cost with Haiku**:
- Input: 21M × $0.25/1M = $5.25
- Output: 6M × $1.25/1M = $7.50
- **Total: ~$13/month**

---

## Next Steps

After setting up the coordinator:

1. ✅ Test priority detection with various inputs
2. ✅ Verify connection to Claude service
3. ✅ Confirm forwarding to Fetch.ai need agent
4. ✅ Monitor API usage and costs
5. ✅ Proceed to integration (see INTEGRATION_GUIDE.md)

---

## Resources

- **Anthropic Docs**: https://docs.anthropic.com
- **Claude API Reference**: https://docs.anthropic.com/claude/reference
- **LangChain Docs**: https://python.langchain.com
- **API Console**: https://console.anthropic.com
- **Pricing**: https://www.anthropic.com/pricing

**Your LangChain coordinator is ready! 🧠**
