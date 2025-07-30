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
- **LLM**: Gemini API for natural language processing

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

1. **Phase 1**: Refactor existing RAG logic into LangChain Tool interface
2. **Phase 2**: Build core Orchestrator Agent with single tool integration
3. **Phase 3**: Add Web Search and SQL Database tools with multi-tool routing
4. **Phase 4**: Enhance frontend to display agent thought processes and multi-step reasoning

## Key Technical Considerations

- **Prompt Engineering**: Orchestrator prompts are critical for correct tool selection and user intent understanding
- **Tool Failure Handling**: System must gracefully handle API failures, SQL errors, and network issues
- **Context Management**: Multi-step queries require persistent memory/scratchpad functionality
- **State Management**: Agent workflows need to track intermediate results across tool calls

## Project Status

Currently in planning phase - only project-plan.txt exists. No implementation files are present yet.