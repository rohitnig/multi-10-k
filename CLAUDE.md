# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Multi-Agent Financial Analyst** system that implements a "Mixture of Experts" (MoE) architecture using LangChain. The system has evolved from a simple RAG pipeline into a sophisticated multi-agent system capable of synthesizing information from multiple sources.

### Current Architecture

The system follows a ReAct agentic workflow with these key components:

- **Web Interface**: Professional Apple-inspired UI with real-time interactions
- **Agent Orchestrator**: Modular core (`agent_orchestrator.py`) used by both CLI and web interfaces
- **Orchestrator Agent**: Central coordinator using OpenAI GPT-4o-mini for reasoning and tool selection
- **Tool Belt**: Collection of specialized tools:
  - **10-K Report Tool**: RAG pipeline with ChromaDB + Gemini API synthesis (toggleable)
  - **Web Search Tool**: Real-time information via Tavily API  
  - **SQL Database Tool**: Queries against SQLite financial database
- **Backend**: Dockerized services with profile-based orchestration + FastAPI web server
- **LLM Stack**: OpenAI GPT-4o-mini for agent reasoning, Gemini API for 10K synthesis

### Tool Selection Logic

The agent uses **dynamic prompt engineering** to decide which tools to use:
- Prompt examples are generated based on available tools
- When `ENABLE_10K_RAG=false`, only web search examples are shown
- Agent learns tool selection from few-shot examples in the prompt template

## Development Commands

### Web Interface (Primary)

The system now features a stunning professional web interface:

```bash
# Start the web interface
docker compose --profile api up -d

# Access the interface
open http://localhost:8000

# View logs
docker compose logs -f api
```

### Service Orchestration (Profile-Based)

The system uses Docker Compose profiles for clean service separation:

```bash
# Run ingestion only (ChromaDB + ingestion process)
docker compose --profile ingest up

# Run web API (ChromaDB + Web Interface)  
docker compose --profile api up -d

# Run everything together
docker compose up -d

# Clean restart
docker compose down && docker compose --profile api up -d
```

### Tool Configuration

Toggle 10K RAG functionality:
```bash
# Enable 10K RAG tool
ENABLE_10K_RAG=true docker compose --profile api up -d

# Disable 10K RAG tool (web search only)
ENABLE_10K_RAG=false docker compose --profile api up -d
```

### Testing

```bash
# Run all tests
pytest

# Test specific tool
pytest tests/test_file_tools.py -v

# Run tests with coverage
pytest --cov=app tests/
```

### Local Development

```bash
# Run the web interface locally
cd app/
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Run the agent directly (CLI mode)
cd app/
python main.py

# Setup database for SQL tool
python db_setup.py

# Run data ingestion for 10K RAG tool
python ingest.py
```

### Data Management

```bash
# Ingest 10K data (required for RAG tool)
docker compose --profile ingest up

# Check ChromaDB data
docker compose logs chromadb

# Check SQLite database
sqlite3 app/financials.db ".tables"
sqlite3 app/financials.db "SELECT * FROM quarterly_financials;"
```

## Architecture Deep Dive

### Agent Flow
1. **Query Analysis**: OpenAI GPT-4o-mini analyzes user query using ReAct pattern
2. **Tool Selection**: Dynamic prompt guides tool choice based on available tools
3. **Tool Execution**: Selected tools execute (web search, 10K RAG, SQL queries)
4. **Response Synthesis**: Agent combines tool outputs into final answer

### Tool Architecture

**10K Report Tool** (`app/tools/file_tools.py`):
- ChromaDB vector search with SentenceTransformer embeddings
- Gemini API for document synthesis
- Lazy-loaded resources with ToolState singleton pattern
- Configurable via `ENABLE_10K_RAG` environment variable
- Can be disabled for faster web-only operation

**Web Search Tool** (`app/tools/web_tools.py`):
- Tavily API integration for real-time information via `TavilySearchResults`
- Always available (cannot be disabled)
- Provides current market data and real-time information

**SQL Database Tool** (`app/tools/sql_tools.py`):  
- SQLite database queries using `QuerySQLDataBaseTool` from LangChain
- Natural language to SQL translation
- Contains `quarterly_financials` table with revenue/profit data (2023-2024)
- Handles structured financial data queries

### Prompt Engineering

The system uses **dynamic prompt templating** in `main.py`:
- Examples are conditionally included based on enabled tools
- Prevents agent confusion when tools are unavailable
- ReAct format with strict formatting rules

### Error Handling

- **Parsing Errors**: `MarkdownStripReActOutputParser` cleans LLM output
- **Iteration Limits**: `max_iterations=6` prevents infinite loops
- **Tool Failures**: `handle_parsing_errors=True` for graceful recovery
- **Service Dependencies**: Docker health checks ensure proper startup order

## Environment Variables

**Required:**
- `OPENAI_API_KEY`: Main agent reasoning (GPT-4o-mini)
- `TAVILY_API_KEY`: Web search functionality

**Conditional:**
- `GEMINI_API_KEY`: Required only when `ENABLE_10K_RAG=true`

**Optional:**
- `ENABLE_10K_RAG`: Toggle 10K RAG tool (default: false)
- `CHROMA_HOST`: ChromaDB host (default: chromadb for Docker)
- `MOCK_MODE`: Testing without API calls (default: false)

## Key Files and Locations

**Core Architecture:**
- `app/agent_orchestrator.py`: **Main module** - Agent creation and execution logic
- `app/main.py`: CLI entry point (simplified, uses agent_orchestrator)
- `app/api.py`: FastAPI web server with professional UI
- `app/tools/`: Tool implementations (file_tools.py, web_tools.py, sql_tools.py)

**Web Interface:**
- `app/templates/index.html`: Professional Apple-inspired web interface
- `app/static/css/style.css`: Sophisticated styling with animations and gradients
- `app/static/js/app.js`: Interactive JavaScript with real-time features

**Data and Configuration:**
- `app/goog-20231231.htm`: Google 2023 10-K filing for ingestion
- `app/ingest.py`: ChromaDB data ingestion script
- `app/db_setup.py`: SQLite database initialization
- `app/financials.db`: SQLite database with quarterly financial data
- `docker-compose.yml`: Service orchestration with profiles
- `requirements.txt`: Updated with Jinja2 for templates

**Testing:**
- `tests/test_file_tools.py`: Unit tests for 10K RAG tool with comprehensive mocking

## Troubleshooting

### Agent Performance
- **Slow responses**: Ensure using OpenAI API (not Ollama)
- **Iteration timeouts**: Check `max_iterations` setting in main.py
- **Tool selection errors**: Verify dynamic prompt generation

### Service Issues
- **Profile conflicts**: Use specific profiles (`--profile api` or `--profile ingest`)
- **Network errors**: Run `docker compose down` and restart services
- **ChromaDB connection**: Ensure ChromaDB is healthy before starting agent

### Tool-Specific Issues
- **10K RAG not working**: Verify `ENABLE_10K_RAG=true` and `GEMINI_API_KEY` set
- **Web search failing**: Check `TAVILY_API_KEY` environment variable
- **SQL queries failing**: Run `python app/db_setup.py` to create/populate `financials.db`
- **Agent parsing errors**: Check `MarkdownStripReActOutputParser` logs for format issues

## Current Status

**✅ PROJECT COMPLETE**: Production-Ready Financial Intelligence Platform
- **Professional Web UI**: Apple-inspired interface with real-time interactions and smooth animations
- **Modular Architecture**: `agent_orchestrator.py` enables code reuse across CLI and web interfaces
- **Multi-Tool Integration**: Web search, 10K RAG, SQL database tools working seamlessly together
- **OpenAI Migration**: Using GPT-4o-mini for fast, reliable agent reasoning
- **Production Services**: Docker orchestration with health checks and profile-based deployment
- **Dynamic Prompting**: Tool examples adapt based on `ENABLE_10K_RAG` setting
- **Toggle Architecture**: 10K RAG can be disabled for faster web-only operation
- **Custom Parser**: `MarkdownStripReActOutputParser` handles LLM output formatting issues
- **Complete Documentation**: Comprehensive guides for users, developers, and operators

**🎯 Status**: **PRODUCTION READY** - A sophisticated financial analysis platform combining elegant Apple-inspired UI design with powerful multi-agent AI architecture, ready for enterprise deployment.