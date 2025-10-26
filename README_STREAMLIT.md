# AgentAid Streamlit Application

A Python-based disaster response coordination platform built with Streamlit, featuring AI-powered request processing and intelligent agent coordination.

## Features

- 🤖 **Claude AI Integration**: Natural language processing for disaster request extraction
- 🌍 **Geocoding Service**: Automatic address geocoding using OpenStreetMap Nominatim
- 🔍 **Intelligent Follow-up**: AI-powered follow-up questions for incomplete requests
- 📊 **Vector Database**: Simple in-memory vector database for similarity search
- 🤝 **Agent Integration**: Seamless integration with existing uAgent system
- 📱 **Streamlit UI**: Clean, responsive web interface

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the project root:

```bash
# Required: Anthropic Claude API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Geocoding service configuration
GEOCODING_PROVIDER=opencage  # or 'google'
OPENCAGE_API_KEY=your_opencage_key  # if using OpenCage
GOOGLE_MAPS_API_KEY=your_google_key  # if using Google Maps
```

### 3. Run the Application

```bash
streamlit run streamlit_app.py
```

The application will be available at `http://localhost:8501`

## Architecture

### Core Components

1. **Streamlit App** (`streamlit_app.py`)
   - Main application interface
   - Form handling and user interaction
   - Request processing pipeline

2. **Claude Service** (`services/claude_service.py`)
   - AI-powered disaster data extraction
   - Natural language processing
   - Follow-up question generation

3. **Geocoding Service** (`services/geocoding_service.py`)
   - Address to coordinates conversion
   - Distance calculations
   - Location-based search

4. **Follow-up Service** (`services/followup_service.py`)
   - Intelligent completeness checking
   - Session management
   - Data merging

5. **Vector Database** (`services/vector_db.py`)
   - In-memory vector storage
   - Similarity search
   - Request retrieval

6. **Agent Integration** (`services/agent_integration.py`)
   - Communication with uAgent system
   - Request forwarding
   - Status updates

## Usage

### Submitting a Disaster Request

1. **Fill out the form** with disaster needs:
   - Items needed (be specific)
   - Quantity details
   - Location (specific address)
   - Contact information
   - Number of people affected
   - Priority level

2. **AI Processing**: The system will:
   - Extract structured data using Claude AI
   - Check for completeness
   - Geocode the location
   - Store in vector database

3. **Follow-up Questions**: If information is incomplete:
   - System will ask specific questions
   - User provides additional details
   - Data is merged intelligently

4. **Agent Coordination**: Complete requests are:
   - Sent to the uAgent system
   - Processed by coordination agents
   - Matched with supply agents

### System Status

The sidebar shows:
- Service health status
- Request statistics
- Priority breakdown
- Active agent counts

### Recent Requests

View and track:
- Submitted requests
- Processing status
- Similar requests
- Agent coordination progress

## API Integration

The application integrates with the existing Node.js Claude service:

- **Health Check**: `GET /health`
- **Request Processing**: `POST /api/extract`
- **Agent Updates**: `POST /api/uagent/update`
- **Pending Requests**: `GET /api/uagent/pending-requests`

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ANTHROPIC_API_KEY` | Claude AI API key | Yes | - |
| `GEOCODING_PROVIDER` | Geocoding service | No | `opencage` |
| `OPENCAGE_API_KEY` | OpenCage API key | No | - |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | No | - |

### Service URLs

- **Claude Service**: `http://localhost:3000`
- **Streamlit App**: `http://localhost:8501`
- **Agent System**: Various ports (8000-8003)

## Development

### Project Structure

```
agent-aid/
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt            # Python dependencies
├── services/                  # Service modules
│   ├── __init__.py
│   ├── claude_service.py     # Claude AI integration
│   ├── geocoding_service.py  # Address geocoding
│   ├── followup_service.py   # Follow-up questions
│   ├── vector_db.py          # Vector database
│   └── agent_integration.py  # uAgent integration
└── README_STREAMLIT.md       # This file
```

### Adding New Features

1. **New Services**: Add to `services/` directory
2. **UI Components**: Modify `streamlit_app.py`
3. **API Integration**: Update `agent_integration.py`

### Testing

```bash
# Run tests
pytest

# Code formatting
black .

# Linting
flake8
```

## Troubleshooting

### Common Issues

1. **Claude API Key Missing**
   - Set `ANTHROPIC_API_KEY` environment variable
   - Check API key validity

2. **Geocoding Failures**
   - Check internet connection
   - Verify API keys (if using paid services)
   - Nominatim is free but has rate limits

3. **Agent Integration Issues**
   - Ensure Node.js Claude service is running
   - Check service URLs and ports
   - Verify network connectivity

4. **Streamlit Issues**
   - Check Python version (3.8+)
   - Verify all dependencies installed
   - Clear browser cache

### Logs and Debugging

- Check Streamlit logs in terminal
- Monitor service health in sidebar
- Use browser developer tools for frontend issues

## Performance

### Optimization Tips

1. **Vector Database**: In-memory storage for development
2. **Geocoding**: Rate limiting to respect API limits
3. **Claude API**: Efficient prompt engineering
4. **Streamlit**: Session state management

### Scaling Considerations

- Replace in-memory vector DB with persistent storage
- Implement caching for geocoding results
- Add database for request persistence
- Consider Redis for session management

## Security

### Best Practices

1. **API Keys**: Store in environment variables
2. **Data Privacy**: No sensitive data in logs
3. **Rate Limiting**: Respect API limits
4. **Input Validation**: Sanitize user inputs

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

This project is part of the AgentAid disaster response platform.

## Support

For issues and questions:
- Check troubleshooting section
- Review service logs
- Test individual components
- Verify environment setup
