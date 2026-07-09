import os
import time
import asyncio
import hashlib
import redis.asyncio as redis
from supabase import create_client, Client
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
import jwt
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

print("🔄 Loading environment configuration matrices...")
load_dotenv()

# DIAGNOSTIC SANITY CHECK
print(f"DEBUG: SUPABASE_URL is currently -> [{os.getenv('SUPABASE_URL')}]")
print(f"DEBUG: Length of URL string is -> {len(os.getenv('SUPABASE_URL'))}")
print(f"DEBUG: Does it end with a space? -> {os.getenv('SUPABASE_URL').endswith(' ')}")


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

# --- HYBRID DATABASE CONNECTIONS ---
print("⚙️ Initializing Supabase Postgres client handles...")
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

print("⚙️ Initializing Async Redis connection pool handles...")
redis_client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

@app.on_event("startup")
async def startup_event():
    """Fires telemetry on application boot to confirm connectivity layers."""
    print("\n" + "="*60)
    print("🚀 DEVMIND PRODUCTION SERVER ONLINE")
    try:
        # Ping Redis to verify connection actively
        await redis_client.ping()
        print("✅ Redis Caching Layer: CONNECTED & ONLINE")
    except Exception as e:
        print(f"❌ Redis Caching Layer: CONNECTION CRASHED -> {e}")
        
    print("✅ Supabase Relational Layer: CLIENT DEPLOYED")
    print(f"📡 API Gateway running on http://127.0.0.1:8000")
    print("="*60 + "\n")

# --- CORE UTILITIES ---
def generate_cache_key(prompt: str) -> str:
    return f"devmind_cache:{hashlib.sha256(prompt.lower().encode()).hexdigest()}"

def verify_token(request: Request, token: str = Depends(oauth2_scheme)):
    if not token:
        token = request.query_params.get("token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing session token mapping.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid.")

@app.get("/mock-token")
def get_mock_token():
    return {"access_token": jwt.encode({"sub": "rathan_s_dev"}, SECRET_KEY, algorithm=ALGORITHM), "token_type": "bearer"}

# --- ASYNC STREAMER ENGINE ---
async def llm_token_streamer(user_prompt: str, user_id: str):
    cache_key = generate_cache_key(user_prompt)
    
    # Check Cache
    try:
        cached_response = await redis_client.get(cache_key)
        if cached_response:
            print(f"⚡ [CACHE HIT] Serving sub-millisecond data stream for user: {user_id}")
            yield f"data: [CACHED_STREAM] {cached_response}\n\n"
            return
    except Exception as e:
        print(f"⚠️ Cache read skip: {e}")

    # Miss -> Write Input Prompt to Postgres
    print(f"📡 [CACHE MISS] Routing directly to OpenRouter network for user: {user_id}")
    try:
        supabase.table("chat_messages").insert({"user_id": user_id, "role": "user", "content": user_prompt}).execute()
    except Exception as e:
        print(f"⚠️ Postgres user-message write error: {e}")

    llm = ChatOpenAI(
        model="openrouter/free", 
        openai_api_base="https://openrouter.ai/api/v1", 
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        streaming=True
    )
    full_generated_response = ""
    
    try:
        async for chunk in llm.astream([HumanMessage(content=user_prompt)]):
            if chunk.content:
                full_generated_response += chunk.content
                yield f"data: {chunk.content}\n\n"
                await asyncio.sleep(0.01)
                
        # --- SAFE POST-STREAM SYNCHRONIZATION ---
        try:
            # Fix Deprecation: Swap out .setex() for modern .set(..., ex=seconds)
            await redis_client.set(cache_key, full_generated_response, ex=86400)
            
            # Safe Assistant Message Insert
            supabase.table("chat_messages").insert({"user_id": user_id, "role": "assistant", "content": full_generated_response}).execute()
            print("💾 [SYNC SUCCESS] Relational tables updated. Redis cache updated for 24 hours.")
        except Exception as db_err:
            print(f"⚠️ Post-stream sync warning (Database sync skipped): {db_err}")
        
    except Exception as e:
        print(f"❌ Core streaming process crash: {e}")
        yield f"data: [BACKEND ERROR: {str(e)}]\n\n"

@app.get("/api/stream-query")
async def stream_query_endpoint(prompt: str, request: Request, token: str = Depends(oauth2_scheme)):
    current_user = verify_token(request, token)
    return StreamingResponse(llm_token_streamer(prompt, current_user), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)