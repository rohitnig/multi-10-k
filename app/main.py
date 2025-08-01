import logging
from agent_orchestrator import create_financial_agent, execute_query

# --- CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    """
    Initializes and runs the financial analyst agent.
    """
    # Create the agent
    agent_executor = create_financial_agent()
    
    # Run the agent with a sample question
    logger.info("--- Running Agent ---")
    question = ("I'm considering investing in Google after their strong 2023 performance. "
                "Can you provide a comprehensive investment analysis? I need: "
                "1) Our internal quarterly profit data for 2023 to compare against, "
                "2) Google's major business risks from their official filings, and "
                "3) Current market sentiment and stock price trends. "
                "Please synthesize this into an investment recommendation.")
    
    logger.info("Invoking the agent on: " + question)
    response = execute_query(agent_executor, question)
    
    logger.info("--- Agent Run Complete ---")
    print("\nFinal Answer:")
    print(response["output"])

if __name__ == "__main__":
    main()
