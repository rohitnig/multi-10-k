# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Multi-Agent Financial Analyst** system that implements a "Mixture of Experts" (MoE) architecture using LangChain. The system has evolved from a simple RAG pipeline into a sophisticated multi-agent system capable of synthesizing information from multiple sources.

### Current Architecture

The system follows a ReAct agentic workflow with these key components:

- **Orchestrator Agent**: Central coordinator using OpenAI GPT-4o-mini for reasoning and tool selection
- **Tool Belt**: Collection of specialized tools:
  - **10-K Report Tool**: RAG pipeline with ChromaDB + Gemini API synthesis (toggleable)
  - **Web Search Tool**: Real-time information via Tavily API  
  - **SQL Database Tool**: Queries against SQLite financial database
- **Backend**: Dockerized services with profile-based orchestration
- **LLM Stack**: OpenAI GPT-4o-mini for agent reasoning, Gemini API for 10K synthesis

### Tool Selection Logic

The agent uses **dynamic prompt engineering** to decide which tools to use:
- Prompt examples are generated based on available tools
- When `ENABLE_10K_RAG=false`, only web search examples are shown
- Agent learns tool selection from few-shot examples in the prompt template

## Development Commands

### Service Orchestration (Profile-Based)

The system uses Docker Compose profiles for clean service separation:

```bash
# Run ingestion only (ChromaDB + ingestion process)
docker compose --profile ingest up

# Run agent/API only (ChromaDB + API service)  
docker compose --profile api up -d

# Run everything together
docker compose up -d

# View agent logs
docker compose logs -f api

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

### Data Management

```bash
# Ingest 10K data (required for RAG tool)
docker compose --profile ingest up

# Check ChromaDB data
cd old_app/
python check_db.py

# Check database contents
docker compose logs chromadb
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

**Web Search Tool** (`app/tools/web_tools.py`):
- Tavily API integration for real-time information
- Always available (cannot be disabled)

**SQL Database Tool** (`app/tools/sql_tools.py`):  
- SQLite database queries using LangChain SQL utilities
- Natural language to SQL translation
- Financial data queries (revenue, profit, etc.)

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

**Main Agent Logic:**
- `app/main.py`: ReAct agent implementation and orchestration
- `app/tools/`: Tool implementations (file_tools.py, web_tools.py, sql_tools.py)

**Data and Configuration:**
- `app/goog-20231231.htm`: Google 2023 10-K filing for ingestion
- `app/ingest.py`: ChromaDB data ingestion script
- `docker-compose.yml`: Service orchestration with profiles

**Legacy Reference:**
- `old_app/`: Original RAG implementation (FastAPI-based)

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
- **SQL queries failing**: Ensure `financials.db` exists and is accessible

## Current Status

**✅ Phase 2+ Complete**: Multi-tool agent with intelligent routing
- **Tool Integration**: Web search, 10K RAG, SQL database tools
- **OpenAI Migration**: Upgraded from local Ollama to OpenAI API for speed
- **Profile-Based Services**: Clean separation of ingestion vs. runtime
- **Dynamic Prompting**: Tool examples adapt to available functionality
- **Toggle Architecture**: 10K RAG can be disabled for faster web-only queries

**Key Achievement**: The system demonstrates that web search can often replace RAG for publicly available documents, providing faster responses with current information.