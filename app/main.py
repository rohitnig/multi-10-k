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
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and log messages that interfere with parsing
            if not line or 'INFO:' in line or 'ERROR:' in line or 'WARNING:' in line:
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

# --- AGENT SETUP ---

def main():
    """
    Initializes and runs the financial analyst agent.
    """
    logger.info("Initializing the Orchestrator Agent...")

    # 1. Initialize the LLM with optimized parameters for consistency
    llm = Ollama(
        model="phi3:mini",
        base_url="http://ollama:11434",
        temperature=0.1,      # Lower temperature for more consistent formatting
        top_p=0.9,           # Reduce randomness in token selection
        repeat_penalty=1.1   # Prevent repetitive outputs
    )

    # 2. Define the list of tools the agent can use
    # For now, it's just our single 10-K report tool
    tools = [query_10k_report]
    logger.info(f"Agent is equipped with the following tools: {[tool.name for tool in tools]}")

    # 3. Create custom ReAct prompt optimized for Phi-3's formatting
    # This addresses the specific issue of models producing both Action and Final Answer
    prompt_template = """
You are a helpful financial analyst assistant.

Your job is to answer user questions about a company’s 10-K report. To do this, you can either use tools to retrieve relevant data or give a final answer if you already have the information.

You can use the following tools:
{tools}

To use a tool, follow this exact format:

Thought: Do I need to use a tool? Yes  
Action: [tool_name from {tool_names}]  
Action Input: [description of what to search or extract]  
Observation: [result from the tool]

If you are ready to answer the user, use this format:

Thought: Do I need to use a tool? No. I have the final answer.  
Final Answer: [your complete response here]

CRITICAL FORMATTING RULES:  
1. You must either use a tool (with Action) or give a final answer — **never both at the same time**
2. Always start your response with "Thought:" 
3. If giving a final answer, use exactly: "Final Answer: [your response]"
4. Keep responses concise and well-formatted

---

Example 1 (using a tool):

Question: What are the revenue trends over the past 3 years?  
Thought: I need to retrieve revenue data.  
Action: query_10k_report  
Action Input: [search for revenue trends over 3 years]  
Observation: [Revenue in 2021: $X; 2022: $Y; 2023: $Z]

---

Example 2 (giving a final answer):

Question: What are the main risk factors?  
Thought: I already have a summary of the risks from earlier.  
Final Answer: The key risks include [brief summary from the report].

---

Example 3 (❌ WRONG — do not do this):

Action: query_10k_report  
Action Input: [search input]  
Final Answer: [an answer here]  
(This is invalid — Action and Final Answer must not appear together.)

---

Begin!

Previous steps:  
{agent_scratchpad}

Question: {input}  
Thought:
"""

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
