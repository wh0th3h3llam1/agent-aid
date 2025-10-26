# 🚨 AgentAid - AI-Powered Disaster Response Platform

## 📋 Overview

AgentAid is an AI-driven disaster response coordination platform that connects victims, aid workers, and suppliers through intelligent agents and automated workflows. The system uses Claude AI for natural language processing and Fetch.ai uAgent framework for autonomous agent coordination.

## 🎯 What You'll Get

- **Beautiful Disaster Response UI**: Modern, intuitive interface for reporting needs
- **AI-Powered Coordination**: Claude AI + Fetch.ai agents work together
- **Real-time Tracking**: Monitor request status and agent activities
- **Multi-Supplier Coordination**: System coordinates between multiple suppliers
- **Geographic Intelligence**: Automatic location processing and optimization

## 🚀 Quick Start Guide

### Prerequisites

Before you begin, make sure you have:

- **Python 3.8+** installed
- **Node.js 18+** and npm installed
- **Anthropic API Key** (get from https://console.anthropic.com/)
- **Git** (to clone the repository)

### Step 1: Clone and Setup

```bash
# Clone the repository (if not already done)
git clone <your-repo-url>
cd agent-aid

# Run the automated setup
python setup.py
```

### Step 2: Configure API Keys

```bash
# Add your Anthropic API key
echo "ANTHROPIC_API_KEY=your_actual_api_key_here" >> agentaid-claude-service/.env
```

**Important**: Replace `your_actual_api_key_here` with your real Anthropic API key from https://console.anthropic.com/

### Step 3: Setup Dummy Suppliers (Recommended for Testing)

```bash
# Initialize the database
python agentaid-marketplace/db/init_db.py

# Set up dummy suppliers with inventory for testing
python agentaid-marketplace/db/setup_dummy_suppliers.py
```

This creates two suppliers:
- **Emergency Medical Depot**: 500 blankets, 10 ambulances, burn medicine
- **Family & Child Supplies**: 50 blankets, baby food, diapers

### Step 4: Start the System

```bash
# Start all services with dummy suppliers (FIXED VERSION)
python start_agents_fixed.py
```

**Note**: If you encounter "Services stopped" messages, use the fixed version above which handles port conflicts and agent communication properly.

This will start:
- Claude Service (Port 3000)
- Coordination Agent (Port 8002)
- Need Agent (Port 8000)
- Supply Agents (Ports 8001, 8003)

### Step 5: Access the UI

Open your browser and go to:
**http://localhost:3000/disaster-response.html**

## 🧪 Testing the System

### 1. **UI Testing (Recommended)**

Open the disaster response UI and try these test scenarios:

#### Test Scenario 1: Blanket Request
```
We need 100 blankets at the community center. This is urgent! 
There are about 200 people affected. Contact: 555-EMERGENCY
```

#### Test Scenario 2: Medical Supplies
```
Medical supplies needed at the hospital. Critical situation! 
We need burn medicine and pain relief. Contact: 555-MEDICAL
```

#### Test Scenario 3: Baby Supplies
```
We need baby food and diapers at the shelter. 
About 50 families with children. Contact: 555-FAMILY
```

### 2. **API Testing**

Test the system using curl commands:

```bash
# Test health check
curl http://localhost:3000/health

# Test disaster extraction
curl -X POST http://localhost:3000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"input": "We need 100 blankets at the community center. This is urgent!", "source": "test"}'

# Check pending requests
curl http://localhost:3000/api/uagent/pending-requests

# Get system statistics
curl http://localhost:3000/api/stats
```

### 3. **Automated Testing**

Run the comprehensive test suite:

```bash
# Test the complete integration
python test_integration.py

# Test the dummy scenario specifically
python test_dummy_scenario.py

# Run the demo scenario
python demo_blanket_scenario.py
```

## 🎮 Using the UI

### 1. Fill Out the Disaster Report Form

The UI has a beautiful, intuitive form with:

- **What do you need?** - Describe items in natural language
- **Quantity Details** - Specify amounts (optional)
- **Location** - Enter address or location
- **Contact Information** - Phone or email (optional)
- **Number of People Affected** - Estimated count (optional)
- **Priority Level** - Critical, High, Medium, or Low

### 2. Watch the AI Coordination

After submitting, you'll see:

1. **Claude AI Processing**: Extracts structured data from your text
2. **Agent Coordination**: Need and supply agents work together
3. **Supplier Matching**: System finds best suppliers for your needs
4. **Real-time Status**: Track your request through the system

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. "Claude service not accessible"
```bash
# Check if Claude service is running
curl http://localhost:3000/health

# If not running, restart:
python start_dummy_agents.py
```

#### 2. "Anthropic API key not found"
```bash
# Check your .env file
cat agentaid-claude-service/.env

# Make sure it contains:
ANTHROPIC_API_KEY=your_actual_api_key_here
```

#### 3. "Agents not responding" or "Services stopped"
```bash
# Check if all services are running
ps aux | grep python
ps aux | grep node

# Kill existing processes and restart with fixed version:
pkill -f "python.*agent" && pkill -f "node.*server"
python start_agents_fixed.py
```

#### 4. "Database not found"
```bash
# Set up the database and dummy suppliers
python agentaid-marketplace/db/init_db.py
python agentaid-marketplace/db/setup_dummy_suppliers.py
```

#### 5. "Import errors"
```bash
# Install missing dependencies
pip install uagents anthropic

# Check if all dependencies are installed
python debug_agents.py
```

### Port Conflicts

If you get port conflicts, check what's using the ports:

```bash
# Check port usage
lsof -i :3000  # Claude service
lsof -i :8000  # Need agent
lsof -i :8001  # Supply agent 1
lsof -i :8002  # Coordination agent
lsof -i :8003  # Supply agent 2
```

## 📊 Understanding the Results

### What Happens When You Submit a Request

1. **Claude AI** extracts structured data:
   ```json
   {
     "items": ["blankets"],
     "quantity_needed": "100",
     "location": "community center",
     "priority": "high",
     "victim_count": 200
   }
   ```

2. **Coordination Agent** routes to appropriate agents

3. **Need Agent** evaluates priority and requirements

4. **Supply Agents** respond with quotes:
   - Emergency Medical: 100 blankets @ $25 each
   - Family & Child: 50 blankets @ $20 each

5. **System selects** optimal supplier based on:
   - Coverage percentage
   - Delivery time
   - Cost
   - Geographic proximity

### Expected Results

For a 100-blanket request:
- **Emergency Medical**: ✅ Can provide 100 blankets, 1.5h delivery
- **Family & Child**: ✅ Can provide 50 blankets, 2h delivery
- **System Choice**: Emergency Medical (100% coverage, faster delivery)

## 🎯 Key Features Demonstrated

- **Natural Language Processing**: Describe needs in plain English
- **AI Agent Coordination**: Multiple AI agents work together
- **Multi-Supplier Management**: System coordinates between suppliers
- **Geographic Optimization**: Closest/fastest supplier gets priority
- **Inventory Management**: Prevents over-allocation
- **Real-time Tracking**: Monitor request status
- **Priority Handling**: Critical, High, Medium, Low priorities

## 🚀 Advanced Testing

### Custom Suppliers

To add your own suppliers, modify the inventory:

```bash
# Edit the supplier setup
python agentaid-marketplace/db/setup_dummy_suppliers.py
```

### Different Scenarios

Try different disaster scenarios:

- **Fire Emergency**: "We need fire extinguishers and burn medicine"
- **Flood Response**: "We need sandbags and emergency shelter"
- **Medical Crisis**: "We need oxygen tanks and medical supplies"
- **Family Emergency**: "We need baby formula and diapers"

### API Integration

The system also provides REST APIs:

```bash
# Get all requests
curl http://localhost:3000/api/requests

# Get pending requests for agents
curl http://localhost:3000/api/uagent/pending-requests

# Submit request via API
curl -X POST http://localhost:3000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"input": "We need 100 blankets", "source": "api"}'
```

## 📈 Monitoring and Logs

### Check System Status

```bash
# Health check
curl http://localhost:3000/health

# System statistics
curl http://localhost:3000/api/stats
```

### View Logs

- **Claude Service**: Check console output
- **Agents**: Check individual agent logs
- **Database**: SQLite file in `agentaid-marketplace/db/`

## 🎉 Success Criteria

The system is working correctly when:

1. ✅ UI loads at http://localhost:3000/disaster-response.html
2. ✅ You can submit disaster requests
3. ✅ Claude AI extracts data correctly
4. ✅ Agents coordinate and respond
5. ✅ Suppliers provide quotes
6. ✅ System selects optimal supplier
7. ✅ Request is fulfilled and confirmed

## 🧪 Test Scenarios

### Scenario 1: Blanket Request (100 blankets)
**Input**: "We need 100 blankets at the community center. This is urgent!"
**Expected**: System coordinates between suppliers to fulfill request

### Scenario 2: Medical Emergency
**Input**: "Medical supplies needed at the hospital. Critical situation!"
**Expected**: Emergency Medical supplier responds with medical supplies

### Scenario 3: Family Emergency
**Input**: "We need baby food and diapers at the shelter."
**Expected**: Family & Child supplier responds with baby supplies

### Scenario 4: Mixed Request
**Input**: "We need blankets, medical supplies, and baby food at the shelter."
**Expected**: Multiple suppliers coordinate to fulfill different items

## 🆘 Getting Help

### If Something Goes Wrong

1. **Check the logs** in the console where you started the services
2. **Verify API keys** are set correctly
3. **Test individual components** using the test scripts
4. **Restart services** if needed
5. **Check port conflicts** and resolve them

### Common Commands

```bash
# Restart everything (FIXED VERSION)
python start_agents_fixed.py

# Test the system
python test_integration.py

# Check health
curl http://localhost:3000/health

# Debug agents
python debug_agents.py

# Debug agent output (if agents keep stopping)
python debug_agent_output.py

# View database
sqlite3 agentaid-marketplace/db/agent_aid.db
```

## 🚀 Next Steps

Once you have the system running:

1. **Try different scenarios** with the UI
2. **Add more suppliers** with different inventory
3. **Test with real disaster scenarios**
4. **Scale to production** deployment
5. **Integrate with real suppliers**

## 📋 Quick Reference

### Start System
```bash
python start_dummy_agents.py
```

### Access UI
```
http://localhost:3000/disaster-response.html
```

### Test API
```bash
curl http://localhost:3000/health
```

### Stop System
```
Press Ctrl+C in the terminal where you started the services
```

---

**AgentAid** - Transforming disaster response through AI coordination 🤖🚨

**Ready to save lives with AI? Start the system and try the UI!** 🚀