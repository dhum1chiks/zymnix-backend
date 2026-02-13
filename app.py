"""
FastAPI backend for Zymnix AI Consultant chatbot.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
try:
    from .rag_engine import get_rag_engine
except (ImportError, ValueError):
    from rag_engine import get_rag_engine
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Zymnix AI Consultant API",
    description="RAG-based AI consultant for Zymnix business automation",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",
        "https://*.vercel.app",
        "https://zymnix.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class Message(BaseModel):
    """Chat message model."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    chat_history: Optional[List[Message]] = []


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    tokens_used: Optional[Dict[str, int]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str
    documents_loaded: int


# Initialize RAG engine on startup
@app.on_event("startup")
async def startup_event():
    """Initialize RAG engine when server starts."""
    print("🚀 Starting Zymnix AI Consultant API...")
    try:
        rag = get_rag_engine()
        doc_count = rag.collection.count()
        if doc_count == 0:
            print("⚠️  Vector database is empty. Running automatic ingestion...")
            from ingest_data import main as run_ingestion
            run_ingestion()
            doc_count = rag.collection.count()
            print(f"✅ Auto-ingestion complete. Loaded {doc_count} chunks.")
        else:
            print(f"✅ RAG engine loaded with {doc_count} knowledge chunks")
    except Exception as e:
        print(f"❌ Error initializing RAG engine: {e}")


# API Endpoints
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns status and number of documents in vector DB.
    """
    try:
        rag = get_rag_engine()
        doc_count = rag.collection.count()
        
        return HealthResponse(
            status="healthy",
            message="Zymnix AI Consultant is running",
            documents_loaded=doc_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for conversing with Zymnix AI Consultant.
    
    Args:
        request: ChatRequest with user message and optional chat history
    
    Returns:
        ChatResponse with assistant's reply
    """
    try:
        rag = get_rag_engine()
        
        # Convert Pydantic models to dicts for RAG engine
        history = [{"role": msg.role, "content": msg.content} for msg in request.chat_history]
        
        # Generate response
        result = rag.generate_response(
            query=request.message,
            chat_history=history if history else None
        )
        
        return ChatResponse(
            response=result["response"],
            tokens_used=result["tokens"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.get("/api/greeting")
async def get_greeting():
    """Get the initial greeting message."""
    try:
        rag = get_rag_engine()
        return {"greeting": rag.get_greeting()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting greeting: {str(e)}")


# Development server runner
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
