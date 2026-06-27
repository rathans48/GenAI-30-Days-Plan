import os
import streamlit as st
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

# 1. Page Configuration & Aesthetic Setup
st.set_page_config(page_title="Day 7: Advanced RAG Dashboard", page_icon="🤖", layout="wide")
load_dotenv(".env")

# Design a clean terminal-style dark theme title layout
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 1100px; }
    h1 { font-family: 'DM Mono', monospace; letter-spacing: -0.02em; }
    </style>
""", unsafe_allow_html=True)

# 2. State & Client Initializations
@st.cache_resource
def get_api_client():
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

@st.cache_resource
def get_vector_client():
    db_path = os.path.join(os.path.dirname(__file__), "chroma_storage_ui")
    return chromadb.PersistentClient(path=db_path)

client = get_api_client()
chroma_client = get_vector_client()

# --- SIDEBAR INTERFACE ---
st.sidebar.title("◈ Navigation Hub")
mode = st.sidebar.radio(
    "Choose Knowledge Source:",
    ["🏢 Mock Company Policy (Text Chunks)", "📄 Upload Custom PDF Document"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**GenAI 30-Day Mastery: Day 7 Portfolio Piece**\n\n"
    "This system processes files into vector matrices using local embedding logic, "
    "retrieves context based on query distance metrics, and answers via a grounded "
    "streaming endpoint."
)

# --- CORE LOGIC HELPER FUNCTIONS ---
def initialize_collection(name):
    """Safely handles collection resetting to guarantee clean semantic spaces."""
    try:
        chroma_client.delete_collection(name=name)
    except Exception:
        pass
    return chroma_client.create_collection(name=name)

def generate_rag_response(context, query):
    """Executes the final text completion API call using strict grounding rules."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert document evaluation assistant. Answer the user's question using "
                "ONLY the provided background documentation context. If the true answer cannot be confidently "
                "deduced from the provided text, state clearly that the document does not contain the facts. "
                "Keep answers highly crisp, professional, and well-structured using markdown."
                f"\n\nBACKGROUND CONTEXT DOCUMENTATION:\n{context}"
            )
        },
        {"role": "user", "content": query}
    ]
    
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        stream=False, # Standard collection block for direct UI rendering
        extra_headers={
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "GenAI Day 7 Streamlit App",
        }
    )
    return response.choices[0].message.content

# --- RENDERING DASHBOARD LOGIC ---
st.title("🤖 Advanced Retrieval-Augmented Generation Dashboard")

if mode == "🏢 Mock Company Policy (Text Chunks)":
    st.subheader("Scenario A: Baseline Operational Text Analysis")
    
    # Give the user a clear choice of input method
    input_method = st.radio("Select Input Method:", ["Use Default Sample Policy", "Upload Custom Text File (.txt)", "Type Raw Notes Manually"])
    
    policy_text = ""
    
    if input_method == "Use Default Sample Policy":
        policy_text = (
            "Section A1: Remote Work Infrastructure and Hardware Allocation\n"
            "The corporate engineering infrastructure grants full remote flexibility. Engineering team instances "
            "are allocated a standard equipment credit of 1500 USD per fiscal cycle for dedicated local testing hardware. "
            "All peripheral requisition logs must be submitted through the internal asset gateway before the third Friday of each operating quarter.\n\n"
            "Section B2: System Outage Response and Failover Escalation Protocols\n"
            "When a cluster crash or core database infrastructure failure occurs, on-call support instances must initialize "
            "the primary failover pipeline within 8 minutes. If the service bottleneck cannot be resolved by standard "
            "automated rolling updates, the on-call engineer must escalate the incident ticket directly to the Infrastructure "
            "Operations Director via the secure alert system."
        )
        with st.expander("👁️ View Core Active Knowledge Base Text"):
            st.code(policy_text, language="text")
            
    elif input_method == "Upload Custom Text File (.txt)":
        uploaded_txt = st.file_uploader("Upload a text file:", type=["txt"])
        if uploaded_txt is not None:
            policy_text = uploaded_txt.read().decode("utf-8")
            st.success("✅ Text file loaded successfully!")
            with st.expander("👁️ Review Uploaded File Contents"):
                st.text(policy_text)
                
    else:
        policy_text = st.text_area("Paste or type your custom documentation blocks here (Separate large topics with double Enters):", height=200)

    # Ingestion Trigger Button
    if policy_text:
        if st.button("🔄 Ingest & Index Text Data"):
            with st.spinner("Processing local vector coordinates..."):
                # Split entries cleanly by paragraph breaks
                chunks = [c.strip() for c in policy_text.split("\n\n") if c.strip()]
                if chunks:
                    collection = initialize_collection("policy_kb")
                    collection.add(documents=chunks, ids=[f"p_{i}" for i in range(len(chunks))])
                    st.success(f"Successfully processed and indexed {len(chunks)} structural context chunks!")
                else:
                    st.error("Please ensure your input contains readable text structures.")

    # Search Interface
    query = st.text_input("🔎 Enter your question:")
    if query:
        try:
            collection = chroma_client.get_collection("policy_kb")
            retrieval = collection.query(query_texts=[query], n_results=1)
            context = retrieval['documents'][0][0]
            
            st.markdown("### 💡 Closest Spatial Document Match Located:")
            st.info(context)
            
            with st.spinner("Synthesizing grounded response..."):
                answer = generate_rag_response(context, query)
                st.markdown("### 🤖 Assistant Response:")
                st.write(answer)
        except Exception:
            st.warning("Please click the 'Ingest & Index Text Data' button above to initialize the database cluster first.")

else:
    st.subheader("Scenario B: Scalable Multi-Page Document Ingestion")
    
    uploaded_file = st.file_uploader("Upload a local PDF file to populate the search index:", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("📥 Parse & Index PDF Elements"):
            with st.spinner("Extracting text layers page by page..."):
                reader = PdfReader(uploaded_file)
                chunks = []
                for idx, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
                        for p in paragraphs:
                            chunks.append(f"[Page {idx + 1}] {p}")
                
                if chunks:
                    collection = initialize_collection("pdf_kb")
                    collection.add(documents=chunks, ids=[f"pdf_c_{i}" for i in range(len(chunks))])
                    st.success(f"Successfully indexed {len(chunks)} custom text layers into ChromaDB!")
                else:
                    st.error("Could not find extractable character layers inside that file.")
                    
        # Search Interface
        pdf_query = st.text_input("🔎 Enter your question regarding the uploaded PDF contents:")
        if pdf_query:
            try:
                collection = chroma_client.get_collection("pdf_kb")
                retrieval = collection.query(query_texts=[pdf_query], n_results=1)
                context = retrieval['documents'][0][0]
                
                st.markdown("### 💡 Closest Spatial Document Match Located:")
                st.info(context)
                
                with st.spinner("Synthesizing grounded response..."):
                    answer = generate_rag_response(context, pdf_query)
                    st.markdown("### 🤖 Assistant Response:")
                    st.write(answer)
            except Exception:
                st.warning("Please ensure you have uploaded a PDF and clicked the 'Parse & Index PDF Elements' button above.")