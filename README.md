# Multi-Agent Financial Analyst System

A sophisticated AI-powered financial analysis system that implements a "Mixture of Experts" (MoE) architecture using LangChain. The system evolved from a simple RAG pipeline into a multi-agent system capable of synthesizing information from multiple sources to answer complex financial queries.

## 🎯 Project Status

### ✅ Phase 1 Complete - LangChain Agent Integration
- **ReAct Agent**: Implemented reasoning agent using LangChain + Ollama/Gemma:2b
- **10-K Report Tool**: Converted RAG pipeline into specialized LangChain tool
- **Docker Orchestration**: Full containerized environment with health checks
- **Vector Search**: ChromaDB integration with Google 2023 10-K filing
- **Error Handling**: Robust parsing error recovery in agent execution

### 🚧 Upcoming Phases
- **Phase 2**: Multi-tool agent with web search capabilities
- **Phase 3**: SQL database integration for structured financial data
- **Phase 4**: Enhanced frontend with agent reasoning visualization

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  ReAct Agent     │───▶│  Tool Selection │
└─────────────────┘    │  (Gemma:2b)      │    └─────────────────┘
                       └──────────────────┘             │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Final Response  │◀───│   Synthesizer    │◀───│ 10-K Report Tool│
└─────────────────┘    │   (Gemini API)   │    │   (ChromaDB)    │
                       └──────────────────┘    └─────────────────┘
```

### Current Components
- **Orchestrator Agent**: LangChain ReAct agent with Ollama + Gemma:2b model
- **10-K Report Tool**: RAG pipeline with ChromaDB vector search + Gemini synthesis
- **Docker Services**: ChromaDB, Ollama, Agent runtime
- **Data**: Google 2023 10-K filing (HTML processed into text chunks)

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 8GB+ RAM (for Gemma:2b model)
- `GEMINI_API_KEY` environment variable

### 1. First-Time Setup
```bash
# Clone the repository
git clone <repo-url>
cd multi-10-k

# Set your Gemini API key
export GEMINI_API_KEY="your-api-key-here"

# Pull the Gemma:2b model (one-time only, ~1.7GB download)
docker compose --profile setup up
```

### 2. Start the System
```bash
# Start all services
docker compose up -d

# Run data ingestion (if ChromaDB is empty)
docker compose --profile ingest up

# Check logs
docker compose logs -f api
```

### 3. Test the Agent
```bash
# Run the agent directly
cd app/
python main.py
```

Expected output:
```
INFO:__main__:Initializing the Orchestrator Agent...
INFO:__main__:Agent is equipped with the following tools: ['query_10k_report']
INFO:__main__:Agent created successfully.
INFO:__main__:Agent Executor is ready.
INFO:__main__:--- Running Agent ---

> Entering new AgentExecutor chain...
...reasoning steps...
> Finished chain.

Final Answer:
Google's main risk factors for 2023 are market risk, competition risk, 
technological risk, regulatory risk, and cybersecurity risk.
```

## 🛠️ Development

### Project Structure
```
multi-10-k/
├── app/                    # Multi-agent system (Phase 1+)
│   ├── main.py            # ReAct agent entry point
│   ├── tools/             # LangChain tools
│   │   └── file_tools.py  # 10-K report tool
│   ├── ingest.py          # Data ingestion script
│   └── goog-20231231.htm  # Google 10-K filing
├── old_app/               # Legacy RAG system (reference)
├── tests/                 # Test suite
├── docker-compose.yml     # Service orchestration
├── Dockerfile.api         # Container definition
└── requirements.txt       # Python dependencies
```

### Available Commands
```bash
# Development workflow
docker compose up -d              # Start all services
docker compose logs -f api        # View agent logs
docker compose --profile ingest up # Re-run data ingestion
docker compose down               # Stop services

# Testing
pytest                           # Run all tests
pytest tests/test_file_tools.py  # Test specific tool
pytest -v                       # Verbose test output

# Debugging
docker exec -it rag_ollama ollama list  # Check available models
docker exec rag_chromadb curl localhost:8000/api/v1/heartbeat  # Test ChromaDB
```

### Environment Variables
- `GEMINI_API_KEY` - Required for tool synthesis (get from Google AI Studio)
- `CHROMA_HOST` - ChromaDB host (default: chromadb in Docker)
- `MOCK_MODE` - Test without Gemini API (default: false)

## 🧪 Example Queries

The agent can answer complex questions about Google's 2023 10-K filing:

```python
# Risk analysis
"What are the main risk factors facing Google in 2023?"

# Financial performance  
"How did Google's advertising revenue perform in 2023?"

# Strategic initiatives
"What new technologies is Google investing in?"

# Regulatory concerns
"What regulatory challenges does Google face?"
```

## 🔧 Troubleshooting

### Model Not Found Error
```bash
# If you see: "OllamaEndpointNotFoundError: Maybe your model is not found"
docker compose --profile setup up
```

### Ollama Health Check Failing
```bash
# Check if Ollama is working
docker exec rag_ollama ollama list
```

### Empty Query Results
```bash
# Check if ChromaDB has data
cd old_app/
python check_db.py

# Re-run ingestion if needed
docker compose --profile ingest up
```

### Container Build Issues
```bash
# Force rebuild if changes aren't picked up
docker compose build --no-cache
docker compose up -d
```

## 📊 Technical Details

### LLM Integration
- **Agent Reasoning**: Ollama + Gemma:2b (1.7GB, local inference)
- **Tool Synthesis**: Google Gemini API (cloud-based, higher quality)
- **Pattern**: ReAct (Reasoning + Acting) for step-by-step problem solving

### Vector Database
- **Technology**: ChromaDB with HTTP client
- **Embeddings**: SentenceTransformer (all-MiniLM-L6-v2)
- **Documents**: Google 2023 10-K filing, chunked into 1000-char segments
- **Search**: Semantic similarity search with top-k retrieval

### Error Handling
- **Parsing Errors**: `handle_parsing_errors=True` for graceful LLM recovery
- **Health Checks**: Docker service dependencies with proper wait conditions
- **Retry Logic**: Built into ChromaDB and Gemini API clients

## 🤝 Contributing

### Adding New Tools
1. Create tool function in `app/tools/`
2. Decorate with `@tool` from LangChain
3. Add to tools list in `main.py`
4. Write tests in `tests/`

### Testing
```bash
# Run tests with coverage
pytest --cov=app tests/

# Test individual components
pytest tests/test_file_tools.py -v
```

## 📈 Roadmap

### Phase 2 - Multi-Tool Integration
- [ ] Web search tool (Tavily API)
- [ ] Multi-tool routing logic
- [ ] Parallel tool execution

### Phase 3 - Structured Data
- [ ] PostgreSQL integration
- [ ] SQL query tool
- [ ] Financial data APIs

### Phase 4 - Frontend Enhancement
- [ ] React/Vue SPA
- [ ] Agent reasoning visualization
- [ ] Real-time query streaming

## 📄 License

[Add your license here]

## 🙋‍♀️ Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs: `docker compose logs -f api`
3. Open an issue in the repository

---

**Status**: Phase 1 Complete ✅ | Multi-agent financial analyst system ready for expansion