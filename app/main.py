import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
# from langchain_core.prompts import hub
from langchain import hub
from tools.file_tools import query_10k_report
from langchain_community.llms import Ollama                 # <-- IMPORT THIS

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- AGENT SETUP ---

def main():
    """
    Initializes and runs the financial analyst agent.
    """
    logger.info("Initializing the Orchestrator Agent...")

    # 1. Initialize the LLM (Gemini)
    # Ensure GEMINI_API_KEY is set in your environment
    llm = Ollama(
        model="gemma:2b",                 # Use the model we pulled
        base_url="http://ollama:11434"    # Point to the ollama service in Docker
    )

    # 2. Define the list of tools the agent can use
    # For now, it's just our single 10-K report tool
    tools = [query_10k_report]
    logger.info(f"Agent is equipped with the following tools: {[tool.name for tool in tools]}")

    # 3. Get the prompt template
    # This pulls a standard "ReAct" prompt template from the LangChain Hub.
    # "ReAct" stands for Reasoning and Acting. It's a powerful way for
    # an LLM to think step-by-step: Thought -> Action -> Observation.
    prompt = hub.pull("hwchase17/react")

    # 4. Create the agent
    # This binds the LLM, the prompt, and the tools together.
    agent = create_react_agent(llm, tools, prompt)
    logger.info("Agent created successfully.")

    # 5. Create the Agent Executor
    # The executor is the runtime for the agent. It's what actually
    # calls the agent, receives the next action, executes that action
    # (by calling the tool), and passes the result back to the agent.
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    logger.info("Agent Executor is ready.")
    
    # 6. Run the agent with a sample question
    logger.info("--- Running Agent ---")
    question = "According to the 2023 10-K report, what are the main risk factors for Google?"
    response = agent_executor.invoke({"input": question})
    
    logger.info("--- Agent Run Complete ---")
    print("\nFinal Answer:")
    print(response["output"])

if __name__ == "__main__":
    main()
