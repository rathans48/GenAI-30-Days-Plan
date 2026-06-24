import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

# Load environmental variables for OpenRouter API routing
load_dotenv(".env")

# Initialize client connection targeting OpenRouter gateway
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def build_and_query_rag():
    # 1. Read the raw text file asset
    source_file = os.path.join(os.path.dirname(__file__), "company_policy.txt")
    if not os.path.exists(source_file):
        print(f"Error: Could not locate source data file at {source_file}")
        return
        
    with open(source_file, "r", encoding="utf-8") as f:
        raw_text = f.read()
        
    # Split the manual entries cleanly by section blocks to serve as separate index entries
    chunks = [chunk.strip() for chunk in raw_text.split("\n\n") if chunk.strip()]
    
    # 2. Initialize Persistent Local Vector Store (Day 6 foundations)
    db_path = os.path.join(os.path.dirname(__file__), "chroma_storage")
    chroma_client = chromadb.PersistentClient(path=db_path)
    
    collection_name = "knowledge_base_qa"
    try:
        chroma_client.delete_collection(name=collection_name)
    except Exception:
        pass
        
    collection = chroma_client.create_collection(name=collection_name)
    
    # Ingest chunks into local local database index
    doc_ids = [f"sec_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, ids=doc_ids)
    print(f"Successfully processed and indexed {len(chunks)} structural context chunks.")
    
    # 3. Accept User Input Prompt
    user_query = "What is the exact time window in minutes for initializing the primary failover pipeline?"
    print(f"\nUser Question: '{user_query}'")
    
    # 4. Retrieval Layer: Look up the top relevant chunk based on Euclidean proximity
    retrieval_results = collection.query(query_texts=[user_query], n_results=1)
    retrieved_context = retrieval_results['documents'][0][0]
    
    print("\n--- [System Retrieval Vector Match Found] ---")
    print(f"Retrieved Context Source:\n{retrieved_context}\n")
    
    # 5. Generation Layer: Construct grounded context payload using custom System constraints
    messages = [
        {
            "role": "system",
            "content": (
                "You are an internal corporate knowledge assistant. Answer the user's question using ONLY "
                "the provided text background context. If the answer cannot be confidently deduced from the "
                "context, state clearly that the documentation does not contain the answer. Stay concise."
                f"\n\nBACKGROUND CONTEXT DOCUMENTATION:\n{retrieved_context}"
            )
        },
        {"role": "user", "content": user_query}
    ]
    
    # 6. Stream the final response to the screen (Day 3 foundations)
    print("--- [Streaming Grounded Response via OpenRouter Free Tier] ---")
    try:
        stream = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            stream=True,
            extra_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "GenAI 30 Day Plan Day 7 Project",
            }
        )
        
        for chunk in stream:
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                content = getattr(delta, 'content', None)
                if content:
                    print(content, end="", flush=True)
                    continue
            if hasattr(chunk, 'text'):
                print(chunk.text, end="", flush=True)
        print("\n\n--- Ingestion & Answer Synthesis Complete ---")
        
    except Exception as e:
        print(f"\nGeneration Pipeline Interrupted: {e}")

if __name__ == "__main__":
    build_and_query_rag()