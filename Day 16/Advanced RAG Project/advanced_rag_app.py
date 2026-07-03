import os
import streamlit as st
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
import re
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


load_dotenv()

# --- 1. MOCK PRODUCTION KNOWLEDGE DATABASE ---
KNOWLEDGE_BASE = [
    {
        "id": "doc_001",
        "category": "source_code",
        "content": "def init_adapter_v2(): This function initializes the physical hardware bridge for IoT filtering. It establishes connection pool thresholds at a default capacity of 50 sockets and opens an event loop monitoring incoming frames."
    },
    {
        "id": "doc_002",
        "category": "troubleshooting",
        "content": "ERROR_CODE_402: Connection pool exhaustion detected in production login loop routes. This critical system failure happens when database socket connections fail to close properly, dropping the entire pool completely every 4 hours."
    },
    {
        "id": "doc_003",
        "category": "documentation",
        "content": "DevMind system pricing structures and billing guidelines. Bulk volume discounts are dynamically applied for corporate engineering teams scale operations beyond 50 active workspace user accounts."
    }
]

# --- 2. ADVANCED HYBRID RETRIEVAL & RE-RANKING ENGINE ---

def production_hybrid_retriever(query: str, category_filter: str) -> list:
    """
    Executes metadata filtering, sparse lexical keyword matching, 
    and simulates deep re-ranking across context chunks.
    """
    # Step A: Apply Strict Metadata Filtering
    filtered_docs = KNOWLEDGE_BASE
    if category_filter != "All Categories":
        filtered_docs = [doc for doc in KNOWLEDGE_BASE if doc["category"] == category_filter]
    
    if not filtered_docs:
        return []

    tokenized_corpus = [re.findall(r'\w+', doc["content"].lower()) for doc in filtered_docs]
    bm25 = BM25Okapi(tokenized_corpus)
    
    tokenized_query = re.findall(r'\w+', query.lower())
    if not tokenized_query:
        return []
        
    bm25_scores = bm25.get_scores(tokenized_query)
    
    # Step C: Simulate Dense Re-ranking via Semantic Overlap Scoring
    re_ranked_candidates = []
    for idx, doc in enumerate(filtered_docs):
        query_words = set(tokenized_query)
        content_words = set(re.findall(r'\w+', doc["content"].lower()))
        semantic_overlap = len(query_words.intersection(content_words))
        
        # Combined Score Calculation
        final_rank_score = bm25_scores[idx] + (semantic_overlap * 1.5)
        
        re_ranked_candidates.append({
            "doc": doc,
            "rank_score": final_rank_score
        })
    
    # Sort candidates dynamically by their structural relevancy score descending
    re_ranked_candidates.sort(key=lambda x: x["rank_score"], reverse=True)
    
    # Return documents that clear the relevance floor
    return [candidate["doc"] for candidate in re_ranked_candidates if candidate["rank_score"] > 0]


# --- 3. STREAMLIT INTERFACE RENDERING LAYER ---

st.set_page_config(page_title="DevMind Production RAG Engine", page_icon="🎯", layout="wide")

st.title("🎯 DevMind Advanced Hybrid RAG Engine")
st.caption("Production Blueprint: Metadata Filtering + BM25 Sparse Search + Semantic Re-ranking")
st.write("---")

# Layout Splitter: Sidebar controls
with st.sidebar:
    st.header("⚙️ Search Governance Filters")
    category_selection = st.selectbox(
        "Metadata Category Filter",
        ["All Categories", "source_code", "troubleshooting", "documentation"]
    )
    st.write("---")
    st.markdown("### Active System State Context:")
    st.info("Checkpointer Thread Session: `devmind_rag_session_1`")

# Main Interface Workspace Layout
query_input = st.text_input(
    "Enter your engineering query or code lookup variable:",
    placeholder="e.g., init_adapter_v2 or pool exhaustion failure code"
)

if query_input:
    with st.spinner("Executing hybrid retrieval search and matrix re-ranking..."):
        # 1. Trigger Retrieval Chain
        retrieved_contexts = production_hybrid_retriever(query_input, category_selection)
        
        if not retrieved_contexts:
            st.warning("⚠️ No highly relevant reference documents cleared the retrieval ranking threshold filters.")
        else:
            # Display Found Context Blocks
            st.subheader("📚 Top Re-Ranked Reference Contexts Cleared for Generation:")
            for rank, doc in enumerate(retrieved_contexts):
                with st.expander(f"Rank #{rank+1} | ID: {doc['id']} | Category: {doc['category']}", expanded=True):
                    st.write(doc["content"])
            
            # 2. Compile System Prompts and Generate Completion via OpenRouter Gateway
            system_instruction = (
                "You are DevMind's production-tier knowledge synthesis agent. "
                "Synthesize a highly accurate, direct response to the user's query utilizing ONLY the "
                "provided re-ranked reference contexts. Cite the document ID explicitly for all facts used. "
                "If the contexts do not contain data to verify the answer, state that you lack sufficient facts."
            )
            
            context_string = "\n\n".join([f"Source [{d['id']}]: {d['content']}" for d in retrieved_contexts])
            
            llm = ChatOpenAI(
                model="openrouter/free",
                openai_api_base="https://openrouter.ai/api/v1",
                openai_api_key=os.getenv("OPENROUTER_API_KEY"),
                temperature=0.1
            )
            
            # Fire LLM execution boundary
            generation_response = llm.invoke([
                SystemMessage(content=system_instruction),
                HumanMessage(content=f"Context Pass:\n{context_string}\n\nUser Query: {query_input}")
            ]).content
            
            st.write("---")
            st.subheader("🤖 Synthesized Engineering Status Report:")
            st.success(generation_response)