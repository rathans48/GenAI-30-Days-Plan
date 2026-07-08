import os
import time
import asyncio
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
import jwt
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

app = FastAPI(title="DevMind Production Core API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "devmind_fallback_secure_hash_secret")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# --- 1. IN-MEMORY RATE LIMITER STORAGE ---
# Tracks: { user_id: [timestamp1, timestamp2, ...] }
RATE_LIMIT_WINDOW = 60  # Window size in seconds
MAX_REQUESTS_PER_WINDOW = 5  # Allow max 5 queries per minute
user_request_history = {}

def rate_limiter_guard(user_id: str):
    """Enforces a rolling window rate limit gate to block API spamming."""
    current_time = time.time()
    
    if user_id not in user_request_history:
        user_request_history[user_id] = []
        
    # Clear out timestamps that have expired past our 60-second window
    user_request_history[user_id] = [
        t for t in user_request_history[user_id] if current_time - t < RATE_LIMIT_WINDOW
    ]
    
    if len(user_request_history[user_id]) >= MAX_REQUESTS_PER_WINDOW:
        print(f"⚠️ [RATE LIMIT TRIGGERED] User '{user_id}' blocked due to request flooding.")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 5 queries per minute allowed."
        )
        
    # Log the cleared request timestamp
    user_request_history[user_id].append(current_time)

# --- 2. SECURITY & AUTHENTICATION VALIDATOR ---
def verify_token(request: Request, token: str = Depends(oauth2_scheme)):
    if not token:
        token = request.query_params.get("token")
        
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing session token mapping.")
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user: str = payload.get("sub")
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token.")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid.")

@app.get("/mock-token")
def get_mock_token():
    return {"access_token": jwt.encode({"sub": "rathan_s_dev"}, SECRET_KEY, algorithm=ALGORITHM), "token_type": "bearer"}

# --- 3. ASYNC STREAMER WITH COMPLIANCE COST LOGGING ---
async def llm_token_streamer(user_prompt: str, user_id: str):
    """Streams tokens asynchronously and calculates execution costs on close."""
    llm = ChatOpenAI(
        model="openrouter/free",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        streaming=True
    )
    
    # Cost Baseline Tracking Primitives (Using standard llama3 pricing rules as a proxy tracker)
    PRICE_PER_1K_PROMPT_TOKENS = 0.00015 
    PRICE_PER_1K_COMPLETION_TOKENS = 0.0006
    
    generated_token_count = 0
    print(f"📡 [STREAM START] Processing request pipeline for User: {user_id}")
    
    try:
        async for chunk in llm.astream([HumanMessage(content=user_prompt)]):
            if chunk.content:
                generated_token_count += 1
                yield f"data: {chunk.content}\n\n"
                await asyncio.sleep(0.01)
                
        # --- 4. PRODUCTION COST LOGGING SUMMARY ---
        # Approximate input token overhead based on text split averages
        estimated_input_tokens = len(user_prompt.split()) * 1.3 
        prompt_cost = (estimated_input_tokens / 1000) * PRICE_PER_1K_PROMPT_TOKENS
        completion_cost = (generated_token_count / 1000) * PRICE_PER_1K_COMPLETION_TOKENS
        total_transaction_cost = prompt_cost + completion_cost
        
        print("\n" + "="*50)
        print("📊 DEVMIND TRANSACTION AGENTMETRIC LOG:")
        print(f"• Target Active User ID : {user_id}")
        print(f"• Input Chunks Logged  : {estimated_input_tokens:.0f} prompt tokens")
        print(f"• Output Chunks Streamed: {generated_token_count} completion tokens")
        print(f"• Total Computed Cost   : ${total_transaction_cost:.6f}")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"❌ [ASYNC BACKEND ERROR] Pipeline crashed mid-stream: {e}")
        yield f"data: [BACKEND ERROR: {str(e)}]\n\n"

# --- 5. ENFORCED ENDPOINT ROUTING ---
@app.get("/api/stream-query")
async def stream_query_endpoint(
    prompt: str, 
    request: Request, 
    token: str = Depends(oauth2_scheme)
):
    # A. Execute authentication validation
    current_user = verify_token(request, token)
    
    # B. Execute Rate Limiting check
    rate_limiter_guard(current_user)
    
    # C. Dispatch the asynchronous token stream
    return StreamingResponse(llm_token_streamer(prompt, current_user), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)