# Trialtalk - Clinical Trial Conversational AI System

A modular clinical trial information system powered by FastMCP, LangChain, and Streamlit, leveraging the ClinicalTrials.gov API v2 and Google Gemini 2.5 Flash.

## Architecture

This system consists of three independent services:

### 1. **clinicaltrials-mcp** (Port 8000)
FastMCP server exposing ClinicalTrials.gov API capabilities via 8 comprehensive tools
- Streamable HTTP transport for multi-client support
- Tools, resources, and prompts for clinical trial data access
- Custom middleware for logging and rate limiting

### 2. **clinicaltrial-agent** (Port 8001)
LangChain-powered conversational agent with advanced reasoning
- LangGraph ReAct agent with Gemini 2.5 Flash integration
- Dynamic MCP tool loading and orchestration
- Memory management and conversation history
- FastAPI service with streaming support

### 3. **clinicaltrial-ui** (Port 8501)
Streamlit web interface with real-time progress tracking
- Interactive chat interface with streaming responses
- Real-time progress indicators and status tracking
- Study data visualization and analytics
- Session management and conversation history

## Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (optional, for containerized deployment)
- Gemini API key from Google AI Studio

### Environment Setup

1. **Clone and navigate to the repository**
```bash
cd Trialtalk-Agentic-Clinical-Trial-Insights
```

2. **Set up environment variables** for each service:

```bash
# MCP Server
cp clinicaltrials-mcp/.env.example clinicaltrials-mcp/.env

# Agent
cp clinicaltrial-agent/.env.example clinicaltrial-agent/.env
# Edit clinicaltrial-agent/.env and add your GEMINI_API_KEY

# UI
cp clinicaltrial-ui/.env.example clinicaltrial-ui/.env
```

### Option 1: Docker Compose (Recommended)

```bash
docker-compose up
```

Access the UI at http://localhost:8501

### Option 2: Manual Setup

**Terminal 1 - MCP Server:**
```bash
cd clinicaltrials-mcp
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip3 install -r requirements.txt
python3 server.py
```

**Terminal 2 - Agent:**
```bash
cd clinicaltrial-agent
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 -m api.main
```

**Terminal 3 - UI:**
```bash
cd clinicaltrial-ui
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
streamlit run app.py
```

## Usage Examples

### Basic Search
```
User: "Find active clinical trials for diabetes in California"
```

The system will:
1. Parse your natural language query
2. Call the appropriate MCP tools
3. Stream results in real-time
4. Display progress of each step in the UI

### Complex Queries
```
User: "Compare phase 3 lung cancer trials by enrollment size"
```

The agent uses multiple tools:
- Searches for lung cancer trials
- Filters by phase
- Analyzes enrollment data
- Provides comparative summary

### Follow-up Questions
```
User: "Show me details of the first study"
User: "What are the eligibility criteria?"
```

Context is maintained across the conversation.

## API Documentation

### MCP Server Tools (8 total)

1. **search_clinical_trials** - Search studies by multiple criteria
2. **get_study_details** - Retrieve full study information by NCT ID
3. **get_field_metadata** - List available data fields
4. **get_search_areas** - Get search area definitions
5. **get_enum_values** - List valid enumeration values
6. **get_study_size_stats** - Study JSON size statistics
7. **get_field_value_stats** - Field value distributions
8. **get_api_version** - API version information

### Agent API Endpoints

- `POST /query` - Submit a query
- `GET /stream/{session_id}` - SSE streaming endpoint
- `GET /sessions/{session_id}` - Get conversation history
- `DELETE /sessions/{session_id}` - Clear session

## Development

### Running Tests

```bash
# MCP Server tests
cd clinicaltrials-mcp
pytest tests/ -v --cov=.

# Agent tests
cd clinicaltrial-agent
pytest tests/ -v

# Integration tests
docker-compose up -d
pytest tests/test_integration.py -v
docker-compose down
```

### Project Structure

```
Trialtalk-Agentic-Clinical-Trial-Insights/
├── clinicaltrials-mcp/          # FastMCP server
│   ├── tools/                   # MCP tools (8 total)
│   ├── resources/               # Static resources
│   ├── prompts/                 # Query building prompts
│   ├── middleware/              # Custom middleware
│   ├── client_api/              # HTTP client for ClinicalTrials.gov
│   ├── server.py                # Main server entry point
│   └── config.py                # Configuration
├── clinicaltrial-agent/         # LangChain agent
│   ├── llm/                     # Gemini integration
│   ├── tools/                   # MCP tool loader
│   ├── memory/                  # Conversation management
│   ├── callbacks/               # Progress tracking
│   ├── chains/                  # Specialized chains
│   ├── api/                     # FastAPI service
│   └── agent.py                 # Main agent
├── clinicaltrial-ui/            # Streamlit UI
│   ├── components/              # UI components
│   ├── client/                  # Agent API client
│   ├── utils/                   # Utilities
│   └── app.py                   # Main Streamlit app
├── tests/                       # Integration tests
├── .docs/                       # OpenAPI specification
├── docker-compose.yml           # Multi-service orchestration
└── README.md                    # This file
```

## Framework Features Used

### FastMCP
- ✅ Streamable HTTP Transport
- ✅ Tools, Resources, Prompts
- ✅ Context Injection
- ✅ Custom Middleware
- ✅ Progress Reporting

### LangChain
- ✅ LangGraph ReAct Agent
- ✅ Streaming & Callbacks
- ✅ Tool Integration
- ✅ Memory & State Management
- ✅ Custom Chains

### Streamlit
- ✅ Session State
- ✅ Real-time Progress Tracking
- ✅ Interactive Callbacks
- ✅ Dynamic Updates
- ✅ Custom Components

## Troubleshooting

### MCP Server not starting
- Check that port 8000 is not in use
- Verify ClinicalTrials.gov API is accessible
- Review logs in the console

### Agent cannot connect to MCP server
- Ensure MCP server is running on http://localhost:8000
- Check `MCP_SERVER_URL` in agent's `.env` file
- Verify firewall settings

### Gemini API errors
- Verify `GEMINI_API_KEY` is set correctly
- Check API quota/rate limits
- Ensure you're using the correct model name

### UI not updating in real-time
- Check browser console for WebSocket/SSE errors
- Verify agent API is accessible at http://localhost:8001
- Try refreshing the Streamlit page

## Contributing

This project is structured for easy extension:

- **Add new MCP tools**: Create new files in `clinicaltrials-mcp/tools/`
- **Add new chains**: Create specialized chains in `clinicaltrial-agent/chains/`
- **Enhance UI**: Add components in `clinicaltrial-ui/components/`

## License

[Your License Here]

## Support

For questions or issues, please refer to the documentation in `.docs/` or create an issue in the repository.
