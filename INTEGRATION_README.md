# AgentAid - Integrated Disaster Response Platform

## 🚨 Overview

AgentAid is an AI-driven disaster response coordination platform that connects victims, aid workers, and suppliers through intelligent agents and automated workflows. The system uses Claude AI for natural language processing and Fetch.ai uAgent framework for autonomous agent coordination.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend UI   │───▶│  Claude Service  │───▶│ Coordination    │
│ (Disaster Form) │    │   (Extraction)   │    │    Agent        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   Need Agent    │
                                              │  (Assessment)  │
                                              └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │  Supply Agents  │
                                              │ (Logistics)    │
                                              └─────────────────┘
```

## 🚀 Quick Start

### 1. Setup
```bash
# Run the setup script
python setup.py

# Add your Anthropic API key to agentaid-claude-service/.env
echo "ANTHROPIC_API_KEY=your_key_here" >> agentaid-claude-service/.env
```

### 2. Start All Services
```bash
# Start the integrated platform
python start_agentaid.py
```

### 3. Access the Platform
- **Disaster Response UI**: http://localhost:3000/disaster-response.html
- **Claude Service API**: http://localhost:3000/health
- **Coordination Agent**: Port 8002
- **Need Agent**: Port 8000
- **Supply Agents**: Ports 8001, 8003

## 📋 Components

### 1. Frontend UI (`disaster-response.html`)
- **Purpose**: User interface for disaster victims to report needs
- **Features**:
  - Natural language input for disaster reports
  - Priority level selection (Critical, High, Medium, Low)
  - Real-time status tracking
  - Agent coordination visualization

### 2. Claude Service (`agentaid-claude-service/`)
- **Purpose**: AI-powered extraction and processing of disaster reports
- **Features**:
  - Natural language to structured data conversion
  - Geocoding and location processing
  - Intelligent follow-up questions
  - Integration with Fetch.ai agents

### 3. Coordination Agent (`coordination_agent.py`)
- **Purpose**: Central coordinator managing need and supply agents
- **Features**:
  - Monitors Claude service for new requests
  - Assigns requests to appropriate agents
  - Tracks agent status and capabilities
  - Manages request lifecycle

### 4. Need Agent (`need_agent.py`)
- **Purpose**: Evaluates disaster needs and prioritizes requests
- **Features**:
  - Disaster assessment and prioritization
  - Risk evaluation using external intelligence
  - Quote request management
  - Allocation optimization

### 5. Supply Agents (`supply_agent.py`)
- **Purpose**: Manages inventory and logistics coordination
- **Features**:
  - Inventory management
  - Logistics planning
  - Supplier coordination
  - Delivery optimization

## 🔄 Workflow

1. **Victim Reports Need**: User fills out disaster form with natural language
2. **Claude Extracts Data**: AI processes text into structured JSON
3. **Coordination Agent**: Receives request and assigns to agents
4. **Need Agent**: Evaluates priority and requirements
5. **Supply Agents**: Check inventory and provide quotes
6. **Allocation**: Best matches are selected and confirmed
7. **Tracking**: Real-time status updates throughout process

## 🛠️ Configuration

### Environment Variables

#### Claude Service (`.env`)
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key
PORT=3000
NODE_ENV=development
```

#### Coordination Agent
```bash
COORDINATOR_NAME=coordination_agent_1
COORDINATOR_SEED=coordination_agent_1_demo_seed
COORDINATOR_PORT=8002
CLAUDE_SERVICE_URL=http://localhost:3000
```

#### Need Agent
```bash
NEEDER_NAME=need_agent_berkeley_1
NEEDER_SEED=need_agent_berkeley_1_demo_seed
NEEDER_PORT=8000
NEED_LAT=37.8715
NEED_LON=-122.2730
NEED_LABEL=Berkeley Emergency Center
```

#### Supply Agents
```bash
SUPPLIER_NAME=supply_sf_store_1
SUPPLIER_SEED=supply_sf_store_1_demo_seed
SUPPLIER_PORT=8001
SUPPLIER_LAT=37.78
SUPPLIER_LON=-122.42
SUPPLIER_LABEL=SF Depot
```

## 📊 API Endpoints

### Claude Service
- `GET /health` - Service health check
- `POST /api/extract` - Extract disaster data from text
- `GET /api/uagent/pending-requests` - Get pending requests for agents
- `POST /api/uagent/claim-request` - Claim a request
- `POST /api/uagent/update` - Update request status

### Coordination Agent
- Monitors Claude service automatically
- Manages agent assignments
- Tracks request lifecycle

## 🧪 Testing

### Manual Testing
1. Open http://localhost:3000/disaster-response.html
2. Fill out a disaster report:
   ```
   We need 50 blankets and 100 water bottles at the community center. 
   This is urgent! There are about 200 people affected. 
   Contact: 555-1234
   ```
3. Submit and watch the agent coordination process

### API Testing
```bash
# Test Claude service
curl -X POST http://localhost:3000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"input": "We need medical supplies at the hospital. This is critical!"}'

# Check health
curl http://localhost:3000/health
```

## 🔧 Troubleshooting

### Common Issues

1. **Claude Service Not Starting**
   - Check if Anthropic API key is set
   - Verify Node.js dependencies: `cd agentaid-claude-service && npm install`

2. **Agents Not Connecting**
   - Check agent addresses in environment variables
   - Verify all services are running on correct ports

3. **Database Issues**
   - Database is created automatically on first run
   - Check file permissions in `agentaid-marketplace/db/`

### Logs
- Claude Service: Check console output
- Agents: Check individual agent logs
- Coordination Agent: Monitors all services

## 🚀 Deployment

### Production Setup
1. Set up proper environment variables
2. Configure reverse proxy (nginx)
3. Set up monitoring and logging
4. Configure database backups
5. Set up SSL certificates

### Docker Deployment (Future)
```dockerfile
# Docker setup for production deployment
# (To be implemented)
```

## 📈 Monitoring

### Health Checks
- Claude Service: `/health` endpoint
- Agents: Status monitoring via coordination agent
- Database: SQLite file monitoring

### Metrics
- Request processing time
- Agent response rates
- Success/failure rates
- Geographic coverage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Create an issue on GitHub
4. Contact the development team

---

**AgentAid** - Transforming disaster response through AI coordination 🤖🚨
