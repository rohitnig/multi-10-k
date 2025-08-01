import os
import sys
import logging
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.schema import AgentAction, AgentFinish
from tools.file_tools import query_10k_report
from tools.web_tools import web_search_tool
from tools.sql_tools import sql_database_tool
from langchain_openai import ChatOpenAI

# --- CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# --- CUSTOM OUTPUT PARSER ---

class MarkdownStripReActOutputParser(ReActSingleInputOutputParser):
    """Custom ReAct output parser that strips markdown formatting and validates format before parsing."""
    
    def parse(self, text: str):
        # Strip markdown formatting from the text
        cleaned_text = self._strip_markdown(text)
        # Validate and clean the format
        validated_text = self._validate_format(cleaned_text)
        # Use the parent parser on the cleaned text
        return super().parse(validated_text)
    
    def _strip_markdown(self, text: str) -> str:
        """Remove markdown formatting from text."""
        # Remove bold formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        # Remove italic formatting
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        # Clean up any remaining asterisks at the beginning of lines
        text = re.sub(r'^\*+\s*', '', text, flags=re.MULTILINE)
        # Clean up any trailing asterisks
        text = re.sub(r'\s*\*+$', '', text, flags=re.MULTILINE)
        return text
    
    def _validate_format(self, text: str) -> str:
        """Validate and clean the ReAct format."""
        lines = text.strip().split('\n')
        cleaned_lines = []
        in_action_input = False
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and log messages that interfere with parsing
            if not line or 'INFO:' in line or 'ERROR:' in line or 'WARNING:' in line:
                continue
                
            # Check if we're starting an Action Input line
            if line.startswith('Action Input:'):
                in_action_input = True
                # Extract only the input part, remove any embedded results
                if ']' in line and 'Based on' in line:
                    # Extract just the part before "Based on" or similar result text
                    action_part = line.split('Based on')[0].split('According to')[0].split('The provided')[0]
                    cleaned_lines.append(action_part.rstrip())
                else:
                    cleaned_lines.append(line)
                continue
                    
            # If we're in Action Input and see result text, skip it
            if in_action_input and ('Based on' in line or '*' in line or 'Google' in line):
                continue
                
            # Reset flag when we see other ReAct components
            if line.startswith(('Thought:', 'Action:', 'Observation:', 'Final Answer:')):
                in_action_input = False
                
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

# --- AGENT SETUP ---

def main():
    """
    Initializes and runs the financial analyst agent.
    """
    # Check for 10K RAG toggle
    enable_10k_rag = os.getenv("ENABLE_10K_RAG", "true").lower() == "true"
    logger.info(f"10K RAG functionality: {'ENABLED' if enable_10k_rag else 'DISABLED'}")
    
    # Check for required environment variables
    required_env_vars = ["TAVILY_API_KEY", "OPENAI_API_KEY"]
    if enable_10k_rag:
        required_env_vars.append("GEMINI_API_KEY")
    
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    logger.info("Initializing the Orchestrator Agent...")

    # 1. Initialize the LLM with optimized parameters for consistency
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,      # Lower temperature for more consistent formatting
        top_p=0.9            # Reduce randomness in token selection
    )

    # 2. Define the list of tools the agent can use
    tools = [ web_search_tool, sql_database_tool ]

    # Conditionally add 10K RAG tool if enabled
    if enable_10k_rag:
        tools.append(query_10k_report)
        logger.info("10K RAG tool added to agent toolkit")
    else:
        logger.info("10K RAG tool disabled - skipping")
    
    logger.info(f"Agent is equipped with the following tools: {[tool.name for tool in tools]}")

    # 3. Create custom ReAct prompt optimized for Phi-3's formatting
    # Build dynamic examples based on available tools
    examples = []
    
    # Always include SQL database example first (generic)
    examples.append("""Example 1 - Using SQL database for structured data:
Thought: I need sales performance data from our internal database. The SQL database contains quarterly business metrics.
Action: sql_database_query
Action Input: SELECT SUM(revenue) FROM sales_data WHERE quarter = 'Q1'""")
    
    if enable_10k_rag:
        examples.append("""Example 2 - Using document analysis tool:
Thought: I need policy details from our company handbook. The document tool can search through stored documents.
Action: query_10k_report
Action Input: employee vacation policy procedures""")
    
    # Always include web search example since it's always available
    examples.append("""Example 3 - Using web search tool:
Thought: I need current weather conditions for planning. Web search provides real-time information.
Action: tavily_search_results_json
Action Input: current weather forecast Seattle today""")
    
    # Add multi-tool switching example
    examples.append("""Example 4 - Multi-tool approach (tool switching):
Thought: I need information about our return policy. Let me try the document search first.
Action: query_10k_report
Action Input: customer return policy guidelines
Observation: [Tool doesn't find specific policy details]
Thought: The document search didn't yield the specific policy. Let me try the database for return statistics instead.
Action: sql_database_query
Action Input: SELECT policy_type, details FROM policies WHERE category = 'returns'""")
    
    # Add multi-component methodology example (generic principles)
    examples.append("""Example 5 - Multi-component query methodology:
Thought: This question asks about restaurant performance and has multiple parts that need different data sources. Let me break this down:
1) Internal sales metrics from our database
2) Customer feedback from stored reviews  
3) Current market trends via web search

Thought: First component needs internal data - SQL database has our sales metrics.
Action: sql_database_query
Action Input: SELECT AVG(daily_sales) FROM restaurant_data WHERE month = 'January'

Thought: Second component needs stored document analysis - document tool can search reviews.
Action: query_10k_report
Action Input: customer satisfaction ratings menu feedback

Thought: Third component needs current market info - web search provides real-time trends.
Action: tavily_search_results_json
Action Input: restaurant industry trends 2024 consumer preferences

Thought: Now I have all three data components. I need to synthesize these findings into a comprehensive restaurant performance analysis addressing all parts of the original question.""")
    
    examples_text = "\n\n".join(examples)
    
    prompt_template = f"""
You are a helpful financial assistant designed to answer complex user questions by using tools and reasoning through the results.

You may use the following tools:
{{tools}}

CRITICAL: Follow this exact format for EVERY step:

Thought: [your reasoning here]
Action: [ONLY the tool name from {{tool_names}}]
Action Input: [ONLY the input - no explanations, no "Wait for Observation" text]

Then wait for Observation, then continue with next Thought.

When ready to answer:
Thought: I have all the information needed.
Final Answer: [complete answer here]

❗ STRICT RULES:

1. NEVER put tool results in "Action Input" - that's for the tool's input only
2. NEVER call the same tool twice with the same input
3. After each tool call, WAIT for "Observation:" before your next "Thought:"
4. If you have sufficient information, provide Final Answer immediately
5. Action Input must be SHORT and SPECIFIC - just the query, nothing else
   ❌ WRONG: "SELECT * FROM table Wait for Observation"
   ✅ CORRECT: "SELECT * FROM table"
6. If a tool doesn't find the information after 1-2 attempts, try a DIFFERENT tool
7. For profit/financial queries: try SQL database first, then 10K reports, then web search
8. If 10K search fails repeatedly, switch to sql_database_query or web search

🎯 FOR COMPLEX MULTI-PART QUERIES:
9. FIRST: Break down the question into numbered components (1, 2, 3, etc.)
10. Address EACH component systematically using the appropriate tool
11. NEVER skip components - if question mentions "internal data", use SQL database
12. ALWAYS synthesize ALL gathered information in your Final Answer
13. If asked for recommendations/analysis, provide synthesis, not just raw data

EXAMPLES WITH ACTUAL TOOLS:

{examples_text}

WRONG ❌:
Action Input: [long text with results mixed in]
Action: search_api (this tool doesn't exist!)

CORRECT ✅:
Action Input: short specific query only

---

Begin!

Previous steps:
{{agent_scratchpad}}

Question: {{input}}
Thought:"""

    prompt = PromptTemplate(
        input_variables=["input", "agent_scratchpad", "tool_names", "tools"],
        template=prompt_template
    )

    # 4. Create the agent with custom output parser
    # This binds the LLM, the prompt, and the tools together.
    agent = create_react_agent(llm, tools, prompt, output_parser=MarkdownStripReActOutputParser())
    logger.info("Agent created successfully with custom markdown-stripping parser.")

    # 5. Create the Agent Executor
    # The executor is the runtime for the agent. It's what actually
    # calls the agent, receives the next action, executes that action
    # (by calling the tool), and passes the result back to the agent.
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True,
        max_iterations=6#,  # Allow enough iterations for multi-step queries
        #max_execution_time=60  # 60 second timeout
    )
    logger.info("Agent Executor is ready.")
    
    # 6. Run the agent with a sample question
    logger.info("--- Running Agent ---")
    question = ("I'm considering investing in Google after their strong 2023 performance. "
                "Can you provide a comprehensive investment analysis? I need: "
                "1) Our internal quarterly profit data for 2023 to compare against, "
                "2) Google's major business risks from their official filings, and "
                "3) Current market sentiment and stock price trends. "
                "Please synthesize this into an investment recommendation.")
    logger.info("Invoking the agend on : " + question)
    response = agent_executor.invoke({"input": question})
    
    logger.info("--- Agent Run Complete ---")
    print("\nFinal Answer:")
    print(response["output"])

if __name__ == "__main__":
    main()
