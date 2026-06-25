import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialize clients
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
chroma_client = chromadb.Client() # In-memory collection for rapid day 8 prototyping

# Create clean semantic index space
try:
    chroma_client.delete_collection("hierarchical_rag")
except:
    pass
collection = chroma_client.create_collection("hierarchical_rag")

# In-memory Document Store mapping: {child_id: parent_text_context}
parent_document_store = {}

def process_and_index_hierarchical(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1. Parent Chunking: Split data by macro structural headers
    parent_sections = [section.strip() for section in content.split("\n\n") if section.strip()]
    
    child_id_counter = 0
    
    for p_idx, parent_text in enumerate(parent_sections):
        # 2. Child Chunking: Slice each parent chunk into tiny, overlapping sliding frames
        child_size = 120
        overlap = 30
        
        for i in range(0, len(parent_text), child_size - overlap):
            child_text = parent_text[i:i + child_size].strip()
            if len(child_text) < 40: # Skip fragments too tiny to hold semantic value
                continue
                
            c_id = f"child_{child_id_counter}"
            
            # Map child identity key directly to its massive Parent Context
            parent_document_store[c_id] = parent_text
            
            # Index only the highly specific child text string to the vector database
            collection.add(
                documents=[child_text],
                ids=[c_id]
            )
            child_id_counter += 1
            
    print(f"🧬 Ingestion Complete: Extracted {len(parent_sections)} Parents into {child_id_counter} Embedded Child Leaves.")

# Execute file ingestion
process_and_index_hierarchical("sample_policy.txt")

# --- HIERARCHICAL RETRIEVAL PIPELINE ---
def hierarchical_rag_query(user_query):
    # Step A: Query the database to find the closest precision child node match
    results = collection.query(query_texts=[user_query], n_results=1)
    
    if not results['ids'] or not results['ids'][0]:
        return "No matching context found."
        
    matched_child_id = results['ids'][0][0]
    matched_child_text = results['documents'][0][0]
    
    print(f"\n🎯 [Vector Match Triggered]: {matched_child_id}")
    print(f"👉 Tiny Child Segment Matched: \"{matched_child_text}\"")
    
    # Step B: Look up the parent map to capture the massive structural section
    retrieved_parent_context = parent_document_store[matched_child_id]
    print(f"📦 [Parent Context Substituted]: Passing full context block to LLM...")
    
    # Step C: Synthesize final answer via OpenRouter using grounded rules
    messages = [
        {
            "role": "system",
            "content": f"You are a strict security assistant. Answer using ONLY the provided context.\n\nCONTEXT:\n{retrieved_parent_context}"
        },
        {"role": "user", "content": user_query}
    ]
    
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages
    )
    return response.choices[0].message.content

# --- TEST EXECUTION ---
query = "What happens if a pod tries to scale manually?"
answer = hierarchical_rag_query(query)

print("\n🤖 Final Grounded Answer:")
print(answer)