import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
# Import the engine assets from your previous script
from semantic_search import corpus, get_embedding_local, vocabulary

if __name__ == "__main__":
    # 1. Collect all data labels and calculate vectors
    labels = ["Doc 1 (Consensus)", "Doc 2 (Loops)", "Doc 3 (Sharding)", "Doc 4 (Orchestrate)"]
    
    # Calculate corpus vectors
    vectors = [get_embedding_local(doc, vocabulary) for doc in corpus]
    
    # Add our test queries to see where they land in the pizza shop map!
    queries = [
        "How do multi-agent server nodes maintain state balance when a cluster crashes?",
        "What happens to the consensus layer when multiple instances suffer unexpected crashes?",
        "Are there specific protocols handling transactional microservice backends?",
        "Bake the chocolate chip cookies at 180°C until the crust is golden brown."
    ]
    query_labels = ["Query 1 (Crash)", "Query 2 (Mutliple)", "Query 3 (Protocols)", "Query 4 (Cookies)"]
    
    for q in queries:
        vectors.append(get_embedding_local(q, vocabulary))
    
    all_labels = labels + query_labels
    matrix = np.array(vectors)
    
    # 2. Execute PCA to squash 45 dimensions down to 2 dimensions
    pca = PCA(n_components=2)
    coords = pca.fit_transform(matrix)
    
    # 3. Plot the map using Matplotlib
    plt.figure(figsize=(10, 8))
    
    # Separate the map points into components
    x = coords[:, 0]
    y = coords[:, 1]
    
    # Plot original documents (Blue)
    plt.scatter(x[:4], y[:4], color='#1f77b4', s=150, label='Corpus Documents', zorder=3)
    
    # Plot test queries (Red)
    plt.scatter(x[4:], y[4:], color='#d62728', s=150, marker='*', label='User Queries', zorder=3)
    
    # Annotate points with text labels
    for i, label in enumerate(all_labels):
        plt.annotate(
            label, 
            (x[i], y[i]), 
            textcoords="offset points", 
            xytext=(0,10), 
            ha='center', 
            fontsize=9,
            weight='bold' if "Query" in label else 'normal'
        )
        
    plt.title("Day 5: Local 2D Vector Space Map (PCA)", fontsize=14, pad=15)
    plt.xlabel("Principal Component 1", fontsize=11)
    plt.ylabel("Principal Component 2", fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='lower left')
    
    print("Generating vector coordinate map graph...")
    plt.show()