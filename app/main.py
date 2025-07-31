import os
import logging
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.schema import AgentAction, AgentFinish
from tools.file_tools import query_10k_report
from langchain_community.llms import Ollama

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CUSTOM OUTPUT PARSER ---

class MarkdownStripReActOutputParser(ReActSingleInputOutputParser):
    """Custom ReAct output parser that strips markdown formatting before parsing."""
    
    def parse(self, text: str):
        # Strip markdown formatting from the text
        cleaned_text = self._strip_markdown(text)
        # Use the parent parser on the cleaned text
        return super().parse(cleaned_text)
    
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

# --- AGENT SETUP ---

def main():
    """
    Initializes and runs the financial analyst agent.
    """
    logger.info("Initializing the Orchestrator Agent...")

    # 1. Initialize the LLM with optimized parameters for consistency
    llm = Ollama(
        model="gemma:2b",
        base_url="http://ollama:11434",
        temperature=0.1,      # Lower temperature for more consistent formatting
        top_p=0.9,           # Reduce randomness in token selection
        repeat_penalty=1.1   # Prevent repetitive outputs
    )

    # 2. Define the list of tools the agent can use
    # For now, it's just our single 10-K report tool
    tools = [query_10k_report]
    logger.info(f"Agent is equipped with the following tools: {[tool.name for tool in tools]}")

    # 3. Create custom ReAct prompt optimized for Gemma's formatting
    # This addresses the specific issue of Gemma producing both Action and Final Answer
    prompt_template = """You are a meticulous financial analyst assistant. Your job is to answer questions about a company's 10-K report by reasoning step-by-step. You can use external tools or respond directly — but you must follow strict formatting rules. You MUST base your 'Thought' and 'Final Answer' ONLY on the information from the 'Observation'. Do not use any other knowledge. If the answer is not in the Observation, you must state that the information is not available.

You have access to the following tools:

{tools}

🔁 Decision Rule (ReAct format)

At each step, you must decide:

    🤖 If you need to use a tool → use this EXACT format (NO markdown, NO bold):

Thought: Do I need to use a tool? Yes.
Action: [tool name from this list: {tool_names}]
Action Input: [input to the tool]
Observation: [tool result will appear here]

    🧠 If you are ready to respond → use this EXACT format (NO markdown, NO bold):

Thought: Do I need to use a tool? No. I have the final answer.
Final Answer: [your response to the user]

⚠️ CRITICAL: Use plain text only. NO **bold**, NO *italics*, NO markdown formatting.

❌ Important Rule (DO NOT BREAK)

At every step, you must produce either an Action OR a Final Answer, never both.
✅ Correct Examples (EXACT format to copy)

Example 1: Uses a tool

Question: What were the total revenues for the last fiscal year?
Thought: I need to find the revenue figure in the 10-K report.
Action: query_10k_report
Action Input: total revenues for the last fiscal year

Example 2: Provides a final answer  

Question: What are the main risk factors?
Thought: The previous observation gave the list of risk factors. I can now answer.
Final Answer: The main risk factors are market volatility, regulatory pressure, and increased competition.

🚫 WRONG FORMAT (DO NOT USE):
**Action:** query_10k_report
**Action Input:** search query
**Final Answer:** response text

❌ Incorrect Example (Do NOT do this)

Question: Were there any major legal proceedings?
Thought: I should check the 10-K for legal proceedings.
Action: query_10k_report
Action Input: major legal proceedings
Final Answer: Yes, there was a major proceeding related to antitrust.

🚫 This is WRONG — you cannot output both an Action and Final Answer in the same step.

Begin!

Previous conversation:

{agent_scratchpad}

Current question:

{input}

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
