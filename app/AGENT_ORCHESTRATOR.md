# Agent Orchestrator Module

The `agent_orchestrator.py` module is the heart of the Aegis Financial Intelligence system, providing a clean, reusable interface for creating and executing financial analysis agents.

## Overview

This module implements a sophisticated multi-agent system using LangChain's ReAct (Reasoning + Acting) pattern with OpenAI GPT-4o-mini. It provides two main functions that abstract away all the complexity of agent creation, tool management, and execution.

## Core Functions

### `create_financial_agent() -> AgentExecutor`

Creates and configures a complete financial analysis agent with all tools and settings.

**Features:**
- **Environment Validation**: Automatically checks for required API keys
- **Dynamic Tool Loading**: Conditionally loads tools based on environment settings
- **Custom Output Parser**: Handles LLM formatting issues with `MarkdownStripReActOutputParser`
- **Optimized Prompting**: Uses dynamic prompt templates with tool-specific examples

**Returns:** A fully configured `AgentExecutor` ready for queries

**Raises:** `SystemExit` if required environment variables are missing

### `execute_query(agent_executor: AgentExecutor, question: str) -> dict`

Executes a financial analysis query using the configured agent.

**Parameters:**
- `agent_executor`: The agent created by `create_financial_agent()`
- `question`: The financial question to analyze

**Returns:** Dictionary containing the agent's response with key `"output"`

## Architecture Details

### Tool Management

The system supports three specialized tools:

1. **Web Search Tool** (`tavily_search_results_json`)
   - Always available
   - Provides real-time market information
   - Uses Tavily API for current data

2. **SQL Database Tool** (`sql_database_query`)
   - Always available
   - Queries internal financial database
   - Handles quarterly financial data

3. **10-K Document Tool** (`query_10k_report`)
   - Conditionally loaded based on `ENABLE_10K_RAG` environment variable
   - Performs document analysis using ChromaDB + Gemini API
   - Can be disabled for faster web-only operation

### Dynamic Prompt Engineering

The agent uses sophisticated prompt engineering with:

- **Conditional Examples**: Prompt examples adapt based on available tools
- **Multi-Tool Patterns**: Demonstrates tool switching and combination strategies
- **Strict Formatting Rules**: Ensures consistent ReAct format output
- **Error Prevention**: Built-in rules to prevent common LLM mistakes

### Custom Output Parser

The `MarkdownStripReActOutputParser` class handles common LLM output issues:

- **Markdown Removal**: Strips bold/italic formatting that confuses parsing
- **Format Validation**: Cleans up malformed ReAct structures
- **Log Filtering**: Removes log messages that interfere with parsing
- **Input Sanitization**: Prevents tool results from being mixed into inputs

## Usage Examples

### Basic Usage (CLI)

```python
from agent_orchestrator import create_financial_agent, execute_query

# Create the agent once
agent = create_financial_agent()

# Execute multiple queries
question = "What are Google's main risk factors for 2023?"
response = execute_query(agent, question)
print(response["output"])
```

### Web API Usage

```python
from fastapi import FastAPI
from agent_orchestrator import create_financial_agent, execute_query

app = FastAPI()
agent_executor = None

@app.on_event("startup")
async def startup():
    global agent_executor
    agent_executor = create_financial_agent()

@app.post("/query")
async def query_agent(request: QueryRequest):
    response = execute_query(agent_executor, request.question)
    return {"answer": response["output"]}
```

## Environment Configuration

### Required Variables

```bash
OPENAI_API_KEY="sk-..."      # OpenAI GPT-4o-mini access
TAVILY_API_KEY="tvly-..."    # Web search functionality
```

### Optional Variables

```bash
GEMINI_API_KEY="AI..."       # Required only if ENABLE_10K_RAG=true
ENABLE_10K_RAG="false"       # Toggle document analysis tool
MOCK_MODE="false"            # Testing mode (not implemented)
```

## Error Handling

### Graceful Degradation

The system is designed to handle various failure scenarios:

1. **Missing API Keys**: Clear error messages with specific missing variables
2. **Tool Failures**: `handle_parsing_errors=True` allows recovery from LLM formatting issues
3. **Iteration Limits**: `max_iterations=6` prevents infinite loops
4. **Service Dependencies**: Proper health checks ensure services are ready

### Logging

Comprehensive logging throughout the module:

```python
import logging
logger = logging.getLogger(__name__)

# Examples of logged events:
logger.info("10K RAG functionality: ENABLED")
logger.info("Agent is equipped with the following tools: ['web_search', 'sql_query']")
logger.info("Agent created successfully with custom markdown-stripping parser")
```

## Performance Optimizations

### LLM Configuration

```python
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,      # Lower temperature for consistent formatting
    top_p=0.9            # Reduce randomness in token selection
)
```

### Agent Settings

```python
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True,                    # Detailed logging
    handle_parsing_errors=True,      # Graceful error recovery
    max_iterations=6                 # Prevent infinite loops
)
```

## Extending the Module

### Adding New Tools

1. Create your tool following LangChain patterns:

```python
from langchain.tools import tool

@tool
def my_new_tool(query: str) -> str:
    """Tool description for the agent."""
    # Tool implementation
    return result
```

2. Import and add to the tools list in `create_financial_agent()`:

```python
from tools.my_new_tool import my_new_tool

def create_financial_agent():
    # ... existing code ...
    tools = [web_search_tool, sql_database_tool, my_new_tool]
    # ... rest of function ...
```

3. Update prompt examples to include your new tool:

```python
def _build_prompt_examples(enable_10k_rag: bool) -> str:
    examples = []
    
    # Add example for your new tool
    examples.append("""Example - Using my new tool:
    Thought: I need to use the new functionality.
    Action: my_new_tool
    Action Input: specific query here""")
    
    return "\n\n".join(examples)
```

### Customizing the Agent

The module is designed for easy customization:

- **Different LLM**: Replace `ChatOpenAI` with any LangChain-compatible model
- **Custom Prompts**: Modify `_create_prompt_template()` for different domains
- **Tool Selection Logic**: Add conditional loading based on new environment variables
- **Output Processing**: Extend `MarkdownStripReActOutputParser` for custom formatting

## Testing

The module is designed to be easily testable:

```python
import pytest
from unittest.mock import patch, MagicMock

def test_agent_creation():
    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'TAVILY_API_KEY': 'test-key'
    }):
        agent = create_financial_agent()
        assert agent is not None

def test_query_execution():
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {"output": "Test response"}
    
    result = execute_query(mock_agent, "Test question")
    assert result["output"] == "Test response"
```

## Best Practices

### Resource Management

- **Single Agent Instance**: Create the agent once and reuse for multiple queries
- **Environment Validation**: Always validate environment variables at startup
- **Graceful Shutdown**: Ensure proper cleanup of resources

### Production Deployment

- **Health Checks**: Monitor agent creation success
- **Rate Limiting**: Implement request throttling for API endpoints
- **Caching**: Consider caching results for repeated queries
- **Monitoring**: Log performance metrics and error rates

This module represents the culmination of sophisticated AI agent design, providing a clean interface while handling the complexity of multi-tool coordination, dynamic prompting, and error recovery.