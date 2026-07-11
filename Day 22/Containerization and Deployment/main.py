import os
import asyncio
from fastapi import FastAPI, Request, Depends
from fastapi.responses import StreamingResponse
from litellm import completion
from router import check_semantic_cache, add_to_semantic_cache, determine_model_route, langfuse
from dotenv import load_dotenv
from langfuse import get_client, propagate_attributes
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI(title="DevMind Intelligent LLMOps Gateway")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           
    allow_credentials=True,
    allow_methods=["*"],           
    allow_headers=["*"],
)

langfuse = get_client()

# ... (Keep your existing CORS, JWT authentication, and startup code blocks here) ...

async def optimized_llm_streamer(user_prompt: str, user_id: str):
    # Establish the top-level active root span frame context
    with langfuse.start_as_current_observation(
        as_type="span", 
        name="streamed_query_pipeline",
        input=user_prompt # Automatically populates trace level input parameters
    ) as root_span:
        
        # Propagates tracking identities natively to any child observations inside the block
        with propagate_attributes(user_id=user_id, session_id="devmind_session_v1"):
            
            # 1. Check Intelligent Semantic Cache
            cached_hit = check_semantic_cache(user_prompt)
            if cached_hit:
                print(f"🎯 [SEMANTIC CACHE HIT] Bypassing LLM network computation for user: {user_id}")
                root_span.update(output=cached_hit) # Save data to trace view
                yield f"data: [SEMANTIC_CACHE_HIT] {cached_hit}\n\n"
                return

            # 2. Cache Miss -> Route dynamically based on evaluation metrics
            selected_model = determine_model_route(user_prompt)
            
            # Nest an interior child generation observation for the LLM calculation
            with langfuse.start_as_current_observation(
                as_type="generation", 
                name="llm_generation",
                model=selected_model,
                input=user_prompt
            ) as generation_span:
                
                full_response_text = ""
                
                try:
                    # 3. Stream from LiteLLM
                    response = completion(
                        model=selected_model,
                        messages=[{"role": "user", "content": user_prompt}],
                        stream=True,
                        max_tokens=500
                    )
                    
                    for chunk in response:
                        token = chunk.choices[0].delta.content
                        if token:
                            full_response_text += token
                            yield f"data: {token}\n\n"
                            await asyncio.sleep(0.01)
                            
                    # 4. Post-Stream Synchronization
                    add_to_semantic_cache(user_prompt, full_response_text)
                    
                    # Update text outputs cleanly on their respective context levels
                    generation_span.update(output=full_response_text)
                    root_span.update(output=full_response_text)
                    print("💾 [OP_SYNC] Semantic cache and Langfuse traces successfully synchronized.")
                    
                except Exception as e:
                    generation_span.update(level="ERROR", status_message=str(e))
                    yield f"data: [GATEWAY ERROR: {str(e)}]\n\n"

@app.get("/mock-token")
def get_mock_token():
    """Generates an immediate localized session signature token for development testing."""
    import jwt
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "production_fallback_secure_hash_secret_string")
    return {"access_token": jwt.encode({"sub": "rathan_s_dev"}, SECRET_KEY, algorithm="HS256"), "token_type": "bearer"}

@app.get("/api/stream-query")
async def stream_query_endpoint(prompt: str, request: Request):
    # For local validation, dummy user context extracted
    current_user = "rathan_s_dev" 
    return StreamingResponse(optimized_llm_streamer(prompt, current_user), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)