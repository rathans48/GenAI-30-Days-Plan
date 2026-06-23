import os
import chromadb

def run_vector_db_demo():
    # 1. Initialize a persistent local ChromaDB storage layer on your disk
    # This automatically creates a database folder structure inside your directory
    db_path = os.path.join(os.path.dirname(__file__), "chroma_storage")
    client = chromadb.PersistentClient(path=db_path)
    
    print(f"Initialized persistent database engine at: {db_path}")
    
    # 2. Create a clean collection (think of this like a table in SQL or a collection in MongoDB)
    # If it already exists from a previous run, reset it to keep data fresh
    collection_name = "pizza_shop_knowledge_base"
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass
        
    collection = client.create_collection(name=collection_name)
    
    # 3. Define our abstract operational corpus documents
    documents = [
        "Distributed consensus protocols like Raft ensure fault tolerance across networked system instances.",
        "Asynchronous event loops in microservice backends improve concurrent throughput metrics significantly.",
        "Relational database sharding distributes transactional workloads across multiple physical server nodes.",
        "Container orchestration layers automate the deployment, scaling, and operational lifecycle of applications.",
        "Load balancers distribute incoming application traffic across healthy web server groups to maintain uptime.",
        "In-memory key-value caches like Redis minimize read latency by bypassing heavy relational database lookups."
    ]
    
    # Unique IDs are strictly required by vector databases to track specific data elements
    doc_ids = [f"doc_{i}" for i in range(len(documents))]
    
    print(f"Ingesting and indexing {len(documents)} documents into ChromaDB...")
    
    # 4. Add the files to the database
    # ChromaDB automatically handles tokenizing, embedding, and HNSW indexing under the hood!
    collection.add(
        documents=documents,
        ids=doc_ids
    )
    print("Ingestion and indexing sequence finalized completely.")
    
    # 5. Execute a target semantic search query
    user_query = "What happens when multiple backend database nodes get overloaded with transaction volume?"
    print(f"\nUser Query: '{user_query}'")
    
    # Query the collection for the top 2 closest conceptual matches (n_results=2)
    results = collection.query(
        query_texts=[user_query],
        n_results=2
    )
    
    print("\n--- ChromaDB Vector Database Retrieval Matrix ---")
    # Unpack and render the matching documents alongside their calculated distance metrics
    for i in range(len(results['documents'][0])):
        doc_text = results['documents'][0][i]
        doc_id = results['ids'][0][i]
        # Distance measures error space (lower values mean closer semantic alignment)
        distance = results['distances'][0][i]
        
        print(f"[{i+1}] ID: {doc_id} | Distance Score: {distance:.4f}")
        print(f"    Text: {doc_text}\n")

if __name__ == "__main__":
    run_vector_db_demo()