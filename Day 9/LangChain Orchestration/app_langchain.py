import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# Ensure target workspace paths exist safely
UPLOAD_DIR = "temp_pdf_vault"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="Day 9: LangChain Refactored RAG", page_icon="🦜", layout="wide")
st.title("🦜 Day 9: LangChain Modular RAG Dashboard")
st.subheader("Refactored Week 1 PDF Intelligence Engine")

# --- 1. SINGLETON RESOURCE CONNECTIONS (CACHED) ---
@st.cache_resource
def initialize_llm_infrastructure():
    embeddings_engine = OpenAIEmbeddings(
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        model="openai/text-embedding-3-small"
    )
    llm_node = ChatOpenAI(
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        model="openrouter/free",
        temperature=0.0
    )
    return embeddings_engine, llm_node

embeddings, llm = initialize_llm_infrastructure()

# --- 2. THE CHUNKING & INGESTION BLOCK ---
def process_pdf_with_langchain(uploaded_file_bytes):
    # Save incoming stream bytes cleanly to local disk cache
    temp_path = os.path.join(UPLOAD_DIR, uploaded_file_bytes.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file_bytes.getbuffer())
        
    # LangChain Document Loader auto-extracts page layout and positions metadata
    loader = PyPDFLoader(temp_path)
    raw_docs = loader.load()
    
    # Recursive parsing to maintain sentence structure bounds
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " "]
    )
    split_docs = text_splitter.split_documents(raw_docs)
    
    # Instantiate standalone Chroma DB instance from processed documents
    vector_db = Chroma.from_documents(split_docs, embeddings)
    return vector_db.as_retriever(search_kwargs={"k": 2})

# --- 3. DASHBOARD VISUAL INTERFACE LAYOUT ---
file_asset = st.file_uploader("Drop your target operational PDF asset here:", type=["pdf"])

if file_asset:
    # Initialize retriever once per new file state change
    if "retriever" not in st.session_state or st.session_state.get("current_file") != file_asset.name:
        with st.spinner("LangChain Ingestion: Slicing document frames and generating vector collection..."):
            st.session_state.retriever = process_pdf_with_langchain(file_asset)
            st.session_state.current_file = file_asset.name
        st.success(f"Successfully vectorized and indexed {file_asset.name} via LangChain!")

    # Prompt Template Architecture
    system_template = """You are an engineering system auditor. Answer the query using ONLY the context provided.
If the truth cannot be found within the text blocks, state clearly that the facts are omitted.

CONTEXT FACT PACKAGES:
{context}

USER QUERY: {question}
FINAL GROUNDED ANSWER:"""

    prompt = ChatPromptTemplate.from_template(system_template)
    
    def format_docs(docs):
        return "\n\n".join(f"[Source Page: {d.metadata.get('page', 0) + 1}] {d.page_content}" for d in docs)

    # Composing the Composable LCEL Pipeline
    lcel_chain = (
        {"context": st.session_state.retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # --- 4. QUERY EXECUTION INTERACTION ---
    user_query = st.text_input("Enter your compliance or system question here:")
    if user_query:
        with st.spinner("Routing query vectors through LCEL execution graph..."):
            answer = lcel_chain.invoke(user_query)
        
        st.markdown("### 🤖 Grounded Generation Response:")
        st.info(answer)