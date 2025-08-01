import os
from langchain_community.tools.tavily_search import TavilySearchResults

# Get the web search tool with API key
api_key = os.getenv("TAVILY_API_KEY")
if not api_key:
    raise ValueError("TAVILY_API_KEY environment variable is required")

web_search_tool = TavilySearchResults(api_key=api_key)
