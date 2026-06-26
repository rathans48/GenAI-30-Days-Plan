import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# 1. Initialize Core Models via OpenRouter Specifications
embeddings = OpenAIEmbeddings(
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    model="openai/text-embedding-3-small" # Standard vectorized scaling model
)

llm = ChatOpenAI(
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    model="openrouter/free",
    temperature=0.0
)

# 2. Document Loading & Splitting Layers
# Points to your existing Day 8 data file path safely
file_path = os.path.join("..", "..", "Day 8", "Chunking Comparison", "sample_policy.txt")
loader = TextLoader(file_path, encoding="utf-8")
raw_documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=40,
    separators=["\n\n", "\n", ". ", " "]
)
documents = text_splitter.split_documents(raw_documents)
print(f"📦 LangChain Splitter: Created {len(documents)} document context chunks.")

# 3. Vector Storage & Retriever Generation
# Initializes an ephemeral in-memory Chroma instance wrapped directly by LangChain
vector_store = Chroma.from_documents(documents, embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# 4. Constructing Prompt Architecture
system_template = """You are a strict security compliance agent. 
Answer the user's question using ONLY the provided background context documentation.
If the answer cannot be confidently deduced from the text, state that the facts are unavailable.

BACKGROUND CONTEXT DOCUMENTATION:
{context}

User Question: {question}
Answer:"""

prompt = ChatPromptTemplate.from_template(system_template)

# Helper function to format retrieved chunks cleanly into the prompt string
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 5. The Composed LCEL Pipeline Blueprint
# RunnablePassthrough allows us to pass the raw user query directly through to the prompt
lcel_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 6. Chain Execution
query = "What happens if a pod tries to scale manually?"
print(f"\n🔎 Querying Pipeline: '{query}'")

response = lcel_chain.invoke(query)

print("\n🤖 Final Grounded Answer via LCEL:")
print(response)