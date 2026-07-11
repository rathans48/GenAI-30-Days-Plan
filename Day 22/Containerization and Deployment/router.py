import os
import numpy as np
from litellm import embedding, token_counter
from langfuse import get_client
from dotenv import load_dotenv

load_dotenv()

# Initialize Langfuse Observability Client
langfuse = get_client()

# Mock in-memory vector database for semantic caching demonstration
# (Maps embedding vectors to their generated text responses)
SEMANTIC_CACHE_DB = []
SIMILARITY_THRESHOLD = 0.88 # 88% semantic match requirement

def get_embedding(text: str) -> list:
    """Generates a text embedding array using a standard lightweight model."""
    response = embedding(
        model="openrouter/openai/text-embedding-3-small", 
        input=[text]
    )
    return response['data'][0]['embedding']

def check_semantic_cache(user_prompt: str) -> str | None:
    """Calculates cosine similarity against previous prompts to intercept queries."""
    if not SEMANTIC_CACHE_DB:
        return None
        
    current_vector = np.array(get_embedding(user_prompt))
    
    for cached_item in SEMANTIC_CACHE_DB:
        cached_vector = np.array(cached_item["vector"])
        
        # Calculate Cosine Similarity
        dot_product = np.dot(current_vector, cached_vector)
        norm_a = np.linalg.norm(current_vector)
        norm_b = np.linalg.norm(cached_vector)
        similarity = dot_product / (norm_a * norm_b)
        
        if similarity >= SIMILARITY_THRESHOLD:
            return cached_item["response"]
            
    return None

def add_to_semantic_cache(prompt: str, response: str):
    """Commits a prompt embedding vector and response string to the cache array."""
    try:
        vector = get_embedding(prompt)
        SEMANTIC_CACHE_DB.append({"vector": vector, "response": response})
    except Exception as e:
        print(f"⚠️ Failed to cache vector: {e}")

def determine_model_route(user_prompt: str) -> str:
    """Evaluates query structural complexity to select the most cost-efficient model."""
    # 1. Evaluate token volume
    token_count = token_counter(model="gpt-4o", text=user_prompt)
    
    # 2. Check for high-complexity engineering keywords
    complex_keywords = ["optimize", "architect", "benchmark", "debug", "refactor", "security fault"]
    has_complex_intent = any(keyword in user_prompt.lower() for keyword in complex_keywords)
    
    # Decision Matrix Routing
    if token_count > 150 or has_complex_intent:
        print(f"🧠 [ROUTER] High complexity detected (Tokens: {token_count}). Routing to gpt-4o.")
        return "openrouter/openai/gpt-4o"
    else:
        print(f"⚡ [ROUTER] Low complexity detected (Tokens: {token_count}). Routing to gpt-4o-mini.")
        return "openrouter/openai/gpt-4o-mini"