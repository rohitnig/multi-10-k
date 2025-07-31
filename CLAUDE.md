# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Multi-Agent Financial Analyst** system that implements a "Mixture of Experts" (MoE) architecture using LangChain. The system evolves from a simple RAG pipeline into a sophisticated multi-agent system capable of synthesizing information from multiple sources.

### Architecture

The system follows an agentic workflow with these key components:

- **Orchestrator Agent**: Central coordinator built with FastAPI + LangChain that analyzes user queries and delegates tasks to specialized tools
- **Tool Belt**: Collection of specialized agents:
  - 10-K Report Tool (RAG pipeline with ChromaDB)
  - Web Search Tool (real-time information via Tavily API)
  - Financial Data Tool (SQL queries against PostgreSQL)
- **Backend**: Dockerized services running on GCP
- **Frontend**: SPA (Single Page Application)
- **LLM**: Ollama with Phi-3:mini model for local inference (Phase 1), with Gemini API integration for tools

### Data Flow

1. User submits complex financial query via SPA
2. Orchestrator Agent analyzes query using Gemini API
3. Agent decides which tool(s) to use based on query intent
4. Tools execute in parallel/sequence as needed:
   - 10-K Tool searches vector database for document insights
   - Web Search Tool fetches current market information
   - Financial Data Tool executes SQL queries for structured data
5. Orchestrator synthesizes responses into final answer
6. Result streams back to user interface

## Development Phases

The project follows a 4-phase implementation:

1. **Phase 1**: ✅ **COMPLETED** - Refactor existing RAG logic into LangChain Tool interface
2. **Phase 2**: Build core Orchestrator Agent with single tool integration  
3. **Phase 3**: Add Web Search and SQL Database tools with multi-tool routing
4. **Phase 4**: Enhance frontend to display agent thought processes and multi-step reasoning

### Phase 1 Achievements ✅
- **LangChain Tool Integration**: Successfully converted RAG pipeline into `query_10k_report` tool
- **Agent Architecture**: Implemented ReAct agent using LangChain with Ollama + Phi-3:mini model
- **Docker Orchestration**: Fixed and optimized multi-service Docker setup with proper health checks
- **Vector Database**: ChromaDB integration working with 10-K document ingestion
- **Model Migration**: Upgraded from Gemma:2b to Phi-3:mini for superior ReAct reasoning and format compliance
- **Advanced Output Parser**: Implemented parser with markdown stripping, log filtering, and format validation
- **ReAct Prompt Optimization**: Enhanced prompt with explicit formatting rules and few-shot examples
- **Parameter Tuning**: Optimized Ollama parameters (temperature=0.1, top_p=0.9) for consistent outputs
- **Logging Enhancement**: Added timestamps and suppressed tool noise during agent execution
- **Dependency Management**: Fixed beautifulsoup4 requirement for document ingestion
- **End-to-End Functionality**: Agent successfully answers queries with real 10-K data in single iteration

## Key Technical Considerations

- **Prompt Engineering**: Orchestrator prompts are critical for correct tool selection and user intent understanding
- **Tool Failure Handling**: System must gracefully handle API failures, SQL errors, and network issues
- **Context Management**: Multi-step queries require persistent memory/scratchpad functionality
- **State Management**: Agent workflows need to track intermediate results across tool calls

## Existing Codebase (old_app/)

The `old_app/` folder contains the original RAG pipeline implementation that will be refactored into the multi-agent system:

### Current Implementation
- **FastAPI Backend** (`main.py`): RESTful API with `/query` endpoint for 10-K Q&A
- **Vector Database**: ChromaDB for document embeddings and similarity search  
- **Document Processing** (`ingest.py`): HTML parsing and text chunking for 10-K filings
- **Embeddings**: SentenceTransformer (`all-MiniLM-L6-v2`) for semantic search
- **LLM Integration**: Google Gemini API for answer synthesis
- **Database Utilities** (`check_db.py`): ChromaDB connection testing and data inspection

### Architecture Components
- **AppState Class**: Lazy-loaded singleton for models and connections (embedding model, ChromaDB client, Gemini model)
- **Document Chunking**: RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
- **Mock Mode**: Environment variable for testing without Gemini API calls
- **Error Handling**: Rate limiting and graceful API error responses

## Development Commands

### Multi-Agent System (Current - Phase 1 Complete)
```bash
# First-time setup: Pull the Phi-3:mini model (one-time only)
docker compose --profile setup up

# Start all services (ChromaDB, Ollama, Agent)
docker compose up -d

# Run with data ingestion (if ChromaDB is empty)
docker compose --profile ingest up

# View logs for debugging (now with timestamps)
docker compose logs -f api
docker compose logs -f chromadb  
docker compose logs -f ollama

# Stop all services
docker compose down

# Run the agent directly (requires services running)
cd app/
python main.py
```

### Legacy RAG System (old_app/ - for reference)
```bash
# Navigate to old_app directory first
cd old_app/

# Start legacy FastAPI + ChromaDB system
docker compose up

# Direct API testing against legacy system
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "What are the main risks facing Google?", "top_k": 3}'
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_file_tools.py

# Run tests with verbose output
pytest -v
```

### Environment Variables
- `GEMINI_API_KEY`: Required for tool LLM synthesis (used by query_10k_report tool)
- `CHROMA_HOST`: ChromaDB host (default: chromadb for Docker, localhost for local)
- `MOCK_MODE`: Enable testing without Gemini API (default: false)

## Troubleshooting

### Common Docker Issues

**Model Not Found Error**
```
OllamaEndpointNotFoundError: Maybe your model is not found and you should pull the model with `ollama pull phi3:mini`
```
Solution: Run the setup profile once to download the model:
```bash
docker compose --profile setup up
```
Or pull directly if the setup service has networking issues:
```bash
docker exec rag_ollama ollama pull phi3:mini
```

**Ollama Health Check Failing**
If Ollama container is marked as unhealthy, check if the health check command works:
```bash
docker exec rag_ollama ollama list
```

**ChromaDB Connection Issues**
Ensure ChromaDB is healthy before starting other services:
```bash
docker compose up chromadb
# Wait for healthy status, then start other services
docker compose up -d
```

**Missing beautifulsoup4 Dependency**
If ingestion fails with `ModuleNotFoundError: No module named 'bs4'`:
```bash
# Rebuild the ingestion container after updating requirements.txt
docker compose build ingestion_runner
docker compose --profile ingest up
```

**Container Build Issues**
Force rebuild containers if Dockerfile changes aren't being picked up:
```bash
docker compose build --no-cache
docker compose up -d
```

**ReAct Parsing Errors**
If agent gets stuck in parsing loops or format errors, the enhanced output parser should handle this automatically by:
- Stripping markdown formatting
- Filtering interfering log messages
- Validating ReAct format structure

Check logs for parsing details:
```bash
docker compose logs -f api
```

**Log Interference Issues**
If you see "Invalid Format" errors, ensure tool logging isn't interfering with agent responses. The system now suppresses tool logs during execution and filters them in the parser.

### Data Ingestion Issues
If the agent can't find relevant documents, ensure the 10-K data is properly ingested:
```bash
# Check if ChromaDB has data
cd old_app/
python check_db.py

# Re-run ingestion if needed  
docker compose --profile ingest up
```

## Project Status - Phase 1 Complete

✅ **COMPLETED**: Multi-agent financial analyst system with LangChain integration
- **Architecture**: ReAct agent with specialized 10-K report tool
- **LLM Integration**: Ollama + Phi-3:mini for agent reasoning, Gemini for tool synthesis  
- **Vector Database**: ChromaDB with Google 2023 10-K filing
- **Containerization**: Full Docker orchestration with health checks
- **Testing**: Pytest suite with mocked dependencies

**Ready for Phase 2**: Expand to multi-tool agent with web search and SQL database integration.