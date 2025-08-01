"""
FastAPI application for the Multi-Agent Financial Analyst system.
Professional web interface that Steve Jobs would appreciate.
"""

import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from agent_orchestrator import create_financial_agent, execute_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with custom styling
app = FastAPI(
    title="Aegis Financial Intelligence",
    description="Next-generation AI-powered financial analysis platform",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Setup static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global agent executor (initialized on startup)
agent_executor = None

class QueryRequest(BaseModel):
    question: str
    
class QueryResponse(BaseModel):
    answer: str
    
@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    global agent_executor
    logger.info("Starting up API - initializing agent...")
    try:
        agent_executor = create_financial_agent()
        logger.info("Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main web interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api")
async def api_root():
    """API information endpoint."""
    return {
        "name": "Aegis Financial Intelligence API",
        "version": "2.0.0",
        "status": "ready",
        "agent_ready": agent_executor is not None
    }

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Execute a financial analysis query using the agent.
    
    Args:
        request: QueryRequest containing the question
        
    Returns:
        QueryResponse with the agent's answer
    """
    if not agent_executor:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        logger.info(f"Processing query: {request.question}")
        response = execute_query(agent_executor, request.question)
        return QueryResponse(answer=response["output"])
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "agent_ready": agent_executor is not None,
        "message": "API is running and agent is ready" if agent_executor else "API running but agent not initialized"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)