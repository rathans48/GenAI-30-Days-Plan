import os
import re
from openai import OpenAI
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Initialize core clients via OpenRouter (using a free fast reasoning model)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
MODEL_SLUG = "openrouter/free"

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# --- 1. DEFINING CORE TOOLS ---

def web_search(query: str) -> str:
    """Executes a live web search to retrieve real-time facts."""
    try:
        # Strip external matching quotes if passed by the LLM
        clean_query = query.strip("'\"")
        response = tavily.search(query=clean_query, max_results=1)
        
        if response and response.get('results'):
            # ✅ Tavily uses 'content' for the matching text block
            return response['results'][0].get('content', 'No content snippet found.')
        return "Search Error: No results returned."
    except Exception as e:
        return f"Search Error: {e}"

def calculator(expression: str) -> str:
    """Safely evaluates basic arithmetic string expressions."""
    try:
        # Clean expression of unsafe characters
        clean_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        return str(eval(clean_expr))
    except Exception as e:
        return f"Math Error: {e}"

# Tool routing map
AVAILABLE_TOOLS = {
    "web_search": web_search,
    "calculator": calculator
}

# --- 2. THE SYSTEM SYSTEM PROMPT (The ReAct Blueprint) ---

SYSTEM_PROMPT = """
You are an autonomous execution agent that solves problems using a step-by-step Reason-and-Act (ReAct) loop.
You have access to the following tools:

- web_search[query]: Run this when you need real-time information, current facts, or up-to-date events.
- calculator[expression]: Run this when you need to calculate exact mathematical operations.

CRITICAL FORMATTING RULES:
You must respond using ONLY this exact structural template. Do not skip steps.
Thought: Write out your current reasoning or what you plan to discover.
Action: tool_name[parameter]
Observation: (This will be provided to you by the system, do not fake it)

When you have collected all necessary observations to definitively answer the user, output:
Final Answer: Your ultimate comprehensive response to the user.

Let's begin!
"""

# --- 3. THE CORE AGENT EXECUTION LOOP ---

def run_agent(user_prompt: str, max_turns: int = 5):
    print(f"\n🚀 User Intent Received: '{user_prompt}'")
    print("-" * 60)
    
    # Initialize short-term memory state tracking
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    for turn in range(1, max_turns + 1):
        print(f"🎬 [TURN {turn}] Thinking...")
        
        # Call the LLM reasoning engine
        response = client.chat.completions.create(
            model=MODEL_SLUG,
            messages=messages,
            temperature=0.0  # Force deterministic action picking
        )
        
        llm_output = response.choices[0].message.content
        print(f"\n🤖 Agent Output:\n{llm_output}\n")
        
        # Append the agent's thought/action output to conversation state history
        messages.append({"role": "assistant", "content": llm_output})
        
        # Check if the agent reached its final answer destination
        if "Final Answer:" in llm_output:
            print("✅ Execution Complete.")
            break
            
        # Parse out Tool Call Actions using Regular Expressions: tool_name[parameter]
        action_match = re.search(r"Action:\s*(\w+)\[(.*?)\]", llm_output)
        
        if action_match:
            tool_name = action_match.group(1)
            tool_param = action_match.group(2).strip("'\"")
            
            if tool_name in AVAILABLE_TOOLS:
                print(f"🛠️ [System Intercept] Invoking tool '{tool_name}' with parameter: '{tool_param}'")
                # Run the selected Python function
                observation_result = AVAILABLE_TOOLS[tool_name](tool_param)
                print(f"👁️ [System Observation]: {observation_result}\n" + "-"*40)
                
                # Append the real world observation data point back into memory history loop
                messages.append({"role": "user", "content": f"Observation: {observation_result}"})
            else:
                error_msg = f"Observation: Error - Tool '{tool_name}' is not available."
                print(f"❌ {error_msg}")
                messages.append({"role": "user", "content": error_msg})
        else:
            # If the model fails to follow format or gets stuck without an action/final answer
            error_msg = "Observation: System Error - You must specify an Action: tool_name[param] or give a Final Answer:"
            messages.append({"role": "user", "content": error_msg})
            
    else:
        print("⚠️ Maximum execution loop iterations reached without final closure.")

# --- 4. RUNNING TEST ANCHORS ---

if __name__ == "__main__":
    # Test case requiring BOTH tools in sequence: Web Search -> Calculator
    complex_query = "Find out how many tracking servers ProtonMail utilizes as of recent tech reviews and multiply that number by 12.5"
    run_agent(complex_query)