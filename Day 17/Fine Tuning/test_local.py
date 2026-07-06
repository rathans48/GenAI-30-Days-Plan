from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Point directly to your local D-drive execution engine
local_model = ChatOpenAI(
    model="phi3:mini",             # Change to the exact tag you downloaded (e.g., "llama3.2:3b")
    openai_api_base="http://localhost:11434/v1",
    openai_api_key="ollama"         # Required placeholder token
)

response = local_model.invoke([
    SystemMessage(content="You are a strict, no-fluff debugging compiler assistant."),
    HumanMessage(content="Explain why a database pool timeout happens in 1 short sentence.")
])

print(f"\n🤖 Local Model Output:\n{response.content}")