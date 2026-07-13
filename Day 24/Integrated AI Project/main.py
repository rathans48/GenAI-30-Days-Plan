import os
from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from supabase import create_client, Client
from litellm import completion

app = FastAPI(title="AI SaaS Backend Gateway")
security = HTTPBearer()

# Enable CORS for frontend hosting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global clients once to prevent connection pool leaks
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class ChatRequest(BaseModel):
    message: str

class DocumentRequest(BaseModel):
    content: str

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Validates the incoming client JWT token against the Supabase Auth system"""
    token = credentials.credentials
    try:
        user = supabase.auth.get_user(token)
        return user.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
        )

@app.post("/upload")
async def ingest_document(req: DocumentRequest, user=Depends(get_current_user)):
    """Chunks text data, generates embeddings, and saves to vector store"""
    try:
        # Simple paragraph chunk strategy
        chunks = [c.strip() for c in req.content.split("\n\n") if c.strip()]
        
        for chunk in chunks:
            # Generate vectors via LiteLLM
            embedding_res = completion(
                model="openrouter/openai/text-embedding-3-small",
                input=[chunk]
            )
            vector = embedding_res['data'][0]['embedding']
            
            # Save into vector database filtered by user ID context
            supabase.table("documents").insert({
                "user_id": user.id,
                "content": chunk,
                "embedding": vector
            }).execute()
            
        return {"status": "success", "message": f"Ingested {len(chunks)} chunks cleanly."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream_endpoint(req: ChatRequest, user=Depends(get_current_user)):
    """Executes RAG similarity lookups and streams response tokens back"""
    try:
        # 1. Embed query prompt
        query_res = completion(
            model="openrouter/openai/text-embedding-3-small",
            input=[req.message]
        )
        query_vector = query_res['data'][0]['embedding']
        
        # 2. Query vector DB context using the RPC match function
        rpc_res = supabase.rpc("match_documents", {
            "query_embedding": query_vector,
            "match_threshold": 0.3,
            "match_count": 3,
            "filter_user_id": user.id
        }).execute()
        
        context_blocks = [item['content'] for item in rpc_res.data]
        context_str = "\n\n".join(context_blocks)
        
        # Log user request message to chat history table
        supabase.table("chat_history").insert({"user_id": user.id, "role": "user", "message": req.message}).execute()

        # 3. Stream token responses via LiteLLM
        def token_generator():
            system_prompt = f"You are an elite AI system assistant. Answer the user prompt strictly using the verified context below:\n\n{context_str}"
            
            response = completion(
                model="openrouter/openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": req.message}
                ],
                stream=True
            )
            
            full_response = ""
            for chunk in response:
                token = chunk.choices[0].delta.content or ""
                if token:
                    full_response += token
                    yield token
            
            # Log full assistant response once stream completes
            supabase.table("chat_history").insert({"user_id": user.id, "role": "assistant", "message": full_response}).execute()

        return StreamingResponse(token_generator(), media_type="text/event-stream")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))