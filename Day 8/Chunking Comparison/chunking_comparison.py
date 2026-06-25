import os
import re
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Client Configurations
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
chroma_client = chromadb.Client()

def clean_and_reset_db():
    for name in ["fixed_space", "recursive_space", "semantic_space"]:
        try: chroma_client.delete_collection(name)
        except: pass
    return (
        chroma_client.create_collection("fixed_space"),
        chroma_client.create_collection("recursive_space"),
        chroma_client.create_collection("semantic_space")
    )

fixed_db, recursive_db, semantic_db = clean_and_reset_db()

# --- 1. FIXED-SIZE CHUNKING STRATEGY ---
def split_fixed(text, chunk_size=150, overlap=30):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        slice_data = text[i:i + chunk_size].strip()
        if slice_data:
            chunks.append(slice_data)
    return chunks

# --- 2. RECURSIVE CHARACTER CHUNKING STRATEGY ---
def split_recursive(text, max_size=200):
    # Mimicking LangChain's recursive separation behavior safely
    separators = ["\n\n", "\n", ". ", " "]
    
    def recursive_loop(text_block, current_seps):
        if len(text_block) <= max_size or not current_seps:
            return [text_block]
            
        sep = current_seps[0]
        fragments = text_block.split(sep)
        final_chunks = []
        current_chunk = ""
        
        for frag in fragments:
            if len(current_chunk) + len(frag) + len(sep) <= max_size:
                current_chunk += (sep if current_chunk else "") + frag
            else:
                if current_chunk:
                    final_chunks.append(current_chunk.strip())
                # Handle cases where a single fragment exceeds max_size
                if len(frag) > max_size:
                    final_chunks.extend(recursive_loop(frag, current_seps[1:]))
                else:
                    current_chunk = frag
        if current_chunk:
            final_chunks.append(current_chunk.strip())
        return final_chunks

    return recursive_loop(text, separators)

# --- 3. SEMANTIC CHUNKING STRATEGY ---
def split_semantic(text):
    # Splits by sentences first, then groups them based on punctuation anchors
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Check if adding a sentence crosses a logical concept boundary length
        if len(current_chunk) + len(sentence) > 250:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence
            
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# --- INGESTION & COMPARISON PIPELINE ---
with open("sample_policy.txt", "r", encoding="utf-8") as f:
    raw_document = f.read()

# Generate split matrices
fixed_chunks = split_fixed(raw_document)
recursive_chunks = split_recursive(raw_document)
semantic_chunks = split_semantic(raw_document)

# Populate vector database spaces
fixed_db.add(documents=fixed_chunks, ids=[f"fix_{i}" for i in range(len(fixed_chunks))])
recursive_db.add(documents=recursive_chunks, ids=[f"rec_{i}" for i in range(len(recursive_chunks))])
semantic_db.add(documents=semantic_chunks, ids=[f"sem_{i}" for i in range(len(semantic_chunks))])

print(f"📋 Ingestion Metrics Breakdown:")
print(f" -> Fixed Strategy Chunks: {len(fixed_chunks)}")
print(f" -> Recursive Strategy Chunks: {len(recursive_chunks)}")
print(f" -> Semantic Strategy Chunks: {len(semantic_chunks)}\n")

# --- COMPARATIVE RETRIEVAL EVALUATION ---
def evaluate_retrieval_quality(user_query):
    print(f"🔎 Target Search Query: '{user_query}'")
    print("=" * 60)
    
    # Query all spaces simultaneously
    res_fix = fixed_db.query(query_texts=[user_query], n_results=1)['documents'][0][0]
    res_rec = recursive_db.query(query_texts=[user_query], n_results=1)['documents'][0][0]
    res_sem = semantic_db.query(query_texts=[user_query], n_results=1)['documents'][0][0]
    
    print(f"🛑 [FIXED CHUNK MATCH]:\n\"{res_fix}\"\n" + "-"*40)
    print(f"🔷 [RECURSIVE CHUNK MATCH]:\n\"{res_rec}\"\n" + "-"*40)
    print(f"🟢 [SEMANTIC CHUNK MATCH]:\n\"{res_sem}\"\n" + "="*60)

# Run Comparative Analysis
evaluate_retrieval_quality("What happens if a pod tries to scale manually?")