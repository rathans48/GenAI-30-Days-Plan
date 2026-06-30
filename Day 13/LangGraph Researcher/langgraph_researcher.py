import os
from typing import TypedDict, Annotated, Literal
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# --- 1. DEFINE STATE ARCHITECTURE ---
class AgentState(TypedDict):
    # This keeps a running list of all communications, appending new additions automatically
    messages: Annotated[list[BaseMessage], lambda x, y: x + y]
    topic: str
    search_approved: bool

# --- 2. INITIALIZE SERVICES & CHAT CORE ---
# Directing OpenRouter payloads through LangChain's ChatOpenAI wrapper
llm = ChatOpenAI(
    model="openrouter/free",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.2
)

search_tool = TavilySearch()

# --- 3. DEFINE GRAPH NODES (OPERATIONAL STEPS) ---

def oracle_node(state: AgentState):
    """Processes message arrays and evaluates if web verification is needed."""
    print("🎬 [NODE] Oracle thinking...")
    system_instruction = (
        "You are an expert research analyst. Look at the conversation history carefully.\n"
        "1. If the history DOES NOT contain a 'Search Observation', reply with the exact phrase 'NEED_SEARCH'.\n"
        "2. If the history ALREADY contains a 'Search Observation', DO NOT say 'NEED_SEARCH'. Instead, use that "
        "observation to write a final comprehensive summary citing the data provided."
    )
    
    combined_messages = [{"role": "system", "content": system_instruction}] + state["messages"]
    response = llm.invoke(combined_messages)
    return {"messages": [response]}

def web_search_node(state: AgentState):
    """Executes search queries safely using the extracted topic vector."""
    print("🛠️ [NODE] Executing Live Tavily Web Search...")
    search_result = search_tool.invoke({"query": state["topic"]})
    return {"messages": [HumanMessage(content=f"Search Observation: {search_result}")]}

# --- 4. DEFINE CONDITIONAL ROUTING EDGES ---

def route_decision(state: AgentState) -> Literal["search_branch", "__end__"]:
    """Determines whether the graph steps into tool nodes or finishes."""
    last_message = state["messages"][-1].content
    if "NEED_SEARCH" in last_message:
        return "search_branch"
    return "__end__"

# --- 5. ASSEMBLE THE WORKFLOW GRAPH ---

workflow = StateGraph(AgentState)

# Register Nodes
workflow.add_node("oracle", oracle_node)
workflow.add_node("web_search", web_search_node)

# Map Edges
workflow.add_edge(START, "oracle")

# Add Conditional Route with explicit destination targets
workflow.add_conditional_edges(
    "oracle",
    route_decision,
    {
        "search_branch": "web_search",
        "__end__": END
    }
)

# Complete the loop back to the analyst after data collection
workflow.add_edge("web_search", "oracle")

# Initialize persistent memory saver for human-in-the-loop interrupts
memory = MemorySaver()

# Compile graph with a breakpoint BEFORE running the web_search node
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["web_search"]
)

# --- 6. EXECUTION RUNTIME WITH HUMAN INTERRUPT INTERACTION ---

if __name__ == "__main__":
    # Print clean ASCII map layout of your compiled graph architecture
    print("\n🗺️ LANGGRAPH ARCHITECTURE MAP:")
    print(app.get_graph().draw_ascii())
    print("=" * 60)

    config = {"configurable": {"thread_id": "devmind_session_1"}}
    initial_input = {
        "topic": "ProtonMail server upgrades 2026 tech spec changes",
        "messages": [HumanMessage(content="What are the recent tech spec changes for ProtonMail servers?")]
    }

    # Turn 1: Run the graph until it encounters a registered breakpoint interrupt
    print("🚀 Initiating Graph Stream...")
    for event in app.stream(initial_input, config, stream_mode="values"):
        if "messages" in event:
            print(f"Update: Last message was {len(event['messages'])} entries deep.")

    # Inspect why the graph paused
    snapshot = app.get_state(config)
    if snapshot.next:
        print("\n🛑 GRAPH INTERRUPTED! Execution frozen before node:", snapshot.next)
        print("Model requested a search. Do you approve? (y/n)")
        
        user_choice = input(">> ").strip().lower()
        
        if user_choice == "y":
            print("\n✅ Approval granted. Resuming execution chain...")
            # Turn 2: Resume stream by passing None as input, maintaining the thread context
            for event in app.stream(None, config, stream_mode="values"):
                if "messages" in event:
                    final_reply = event["messages"][-1].content
            
            print("\n🎯 FINAL AGENT SUMMARY REPORT:")
            print(final_reply)
        else:
            print("\n❌ Action rejected. Halting agent lifecycle.")