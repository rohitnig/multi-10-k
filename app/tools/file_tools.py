# app/tools/file_tools.py

import os
import logging
import chromadb
import google.generativeai as genai
from langchain.tools import tool
from sentence_transformers import SentenceTransformer

# --- CONFIGURATION ---
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
COLLECTION_NAME = "google_10k_2023"
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- RESOURCE MANAGEMENT ---
# We manage resources globally within this module for simplicity.
# This is similar to your AppState but tailored for a non-API context.
class ToolState:
    def __init__(self):
        self.embedding_model = None
        self.collection = None
        self.generation_model = None

    def get_embedding_model(self):
        if self.embedding_model is None:
            logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        return self.embedding_model

    def get_collection(self):
        if self.collection is None:
            logger.info(f"Connecting to ChromaDB at {CHROMA_HOST}...")
            chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=8000)
            self.collection = chroma_client.get_collection(name=COLLECTION_NAME)
        return self.collection

    def get_generation_model(self):
        if self.generation_model is None:
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not configured")
            genai.configure(api_key=GEMINI_API_KEY)
            self.generation_model = genai.GenerativeModel('gemini-1.5-flash')
        return self.generation_model

tool_state = ToolState()

# --- THE LANGCHAIN TOOL ---

@tool
def query_10k_report(query: str) -> str:
    """
    Searches and synthesizes information from Google's 2023 10-K financial report.
    Use this tool for any questions about Google's financial performance, business
    strategy, risk factors, or operations specifically for the year 2023. The tool
    retrieves relevant sections from the report and uses an LLM to generate a
    concise answer.
    """
    logger.info(f"Using 10-K Report Tool for query: '{query}'")

    # 1. Get necessary models and DB collection
    embedding_model = tool_state.get_embedding_model()
    collection = tool_state.get_collection()
    generation_model = tool_state.get_generation_model()

    # 2. Embed the query
    question_embedding = embedding_model.encode(query).tolist()

    # 3. Query ChromaDB
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=5 # We can hardcode this or make it a parameter
    )
    retrieved_documents = results['documents'][0]
    logger.info(f"Retrieved {len(retrieved_documents)} chunks from 10-K report.")

    # 4. Synthesize the answer with Gemini
    context = "\n\n---\n\n".join(retrieved_documents)
    prompt = f"""
    You are a financial analyst assistant. Answer the user's question based *only*
    on the provided context from a company's 10-K report. Do not use any external
    knowledge. If the answer is not in the context, state that clearly.

    Context from the 10-K report:
    ---
    {context}
    ---

    User's Question: {query}

    Synthesized Answer:
    """
    
    response = generation_model.generate_content(prompt)
    
    # A tool should return a single string as its final output
    return response.text.strip()
