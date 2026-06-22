import numpy as np

# Move these to the global level so visualize_search.py can import them!
corpus = [
    "Distributed consensus protocols like Raft ensure fault tolerance across networked system instances.",
    "Asynchronous event loops in microservice backends improve concurrent throughput metrics significantly.",
    "Relational database sharding distributes transactional workloads across multiple physical server nodes.",
    "Container orchestration layers automate the deployment, scaling, and operational lifecycle of applications."
]

raw_vocab = " ".join(corpus).lower().replace(".", "").split()
vocabulary = list(set(raw_vocab))

def get_embedding_local(text: str, vocabulary: list) -> np.ndarray:
    tokens = text.lower().replace(".", "").replace("?", "").split()
    vector = np.zeros(len(vocabulary))
    
    semantic_synonyms = {
        "multi-agent": ["distributed", "consensus", "raft", "networked"],
        "crashes": ["fault", "tolerance", "instances"],
        "server": ["physical", "server", "nodes"],
        "balance": ["sharding", "distributes", "workloads"]
    }
    
    for word in tokens:
        if word in vocabulary:
            vector[vocabulary.index(word)] += 1.0
        if word in semantic_synonyms:
            for synonym in semantic_synonyms[word]:
                if synonym in vocabulary:
                    vector[vocabulary.index(synonym)] += 0.8
                    
    return vector

def calculate_cosine_similarity(vec_a, vec_b) -> float:
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

if __name__ == "__main__":
    print(f"Initialized local embedding space with {len(vocabulary)} dimensional vectors.")
    print("Pre-computing corpus vector embeddings locally...")
    
    corpus_embeddings = [get_embedding_local(doc, vocabulary) for doc in corpus]
    print("Successfully embedded all documents.\n")
    
    user_query = "How do multi-agent server nodes maintain state balance when a cluster crashes?"
    print(f"User Query: '{user_query}'")
    
    query_embedding = get_embedding_local(user_query, vocabulary)
    
    print("\n--- Semantic Ranking Results ---")
    rankings = []
    for i, doc_emb in enumerate(corpus_embeddings):
        similarity_score = calculate_cosine_similarity(query_embedding, doc_emb)
        rankings.append((similarity_score, corpus[i]))
        
    rankings.sort(key=lambda x: x[0], reverse=True)
    for score, text in rankings:
        print(f"[{score:.4f}] ──► {text}")