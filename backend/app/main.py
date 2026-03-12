from dotenv import load_dotenv
import os

# Load environment variables first
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import timedelta
import os

from app.db import get_db, init_db
from app.models import User, ChatHistory
from app.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.rag import rag_pipeline
from app.search import keyword_search

# Initialize FastAPI app
app = FastAPI(
    title="LexQuery - AI Legal Assistant",
    description="Legal search engine and AI chatbot using RAG",
    version="1.0.0"
)

# CORS configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    email: str


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    mode: Optional[str] = "research"  # Default to research


class ChatRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3
    mode: Optional[str] = "advice"  # Default to advice


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    query: str
    mode: str


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Database initialized")


# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "LexQuery API is running",
        "version": "1.0.0",
        "endpoints": ["/auth/register", "/auth/login", "/search", "/chat", "/history"]
    }

# Dummy user for guest mode
GUEST_USER_ID = 1  # Using ID 1 as default guest user

def get_guest_user(db: Session = Depends(get_db)):
    # Ensure guest user exists
    guest = db.query(User).filter(User.username == "guest").first()
    if not guest:
        guest = User(
            username="guest", 
            email="guest@lexquery.com", 
            hashed_password="hashed_guest_password"
        )
        db.add(guest)
        db.commit()
        db.refresh(guest)
    return guest

# Search endpoint - NOW USES RAG (Research Mode - Deterministic)
@app.post("/search")
async def search(
    search_request: SearchRequest,
    current_user: User = Depends(get_guest_user),
    db: Session = Depends(get_db)
):
    """Deterministic Legal Search (Bypasses LLM)"""
    mode = "research"
    result = rag_pipeline(search_request.query, search_request.top_k, mode=mode)
    
    # Save to history
    chat_history = ChatHistory(
        user_id=current_user.id,
        query=search_request.query,
        response=result["answer"],
        mode=mode
    )
    db.add(chat_history)
    db.commit()
    
    return {
        "query": search_request.query,
        "results": result["sources"],
        "answer": result["answer"],
        "count": len(result["sources"]),
        "mode": mode,
        "type": result.get("type", "semantic")
    }


# Chat endpoint (RAG) - Advice Mode (AI Reasoning)
@app.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_guest_user),
    db: Session = Depends(get_db)
):
    """AI Lawyer Chat using RAG and reasoning with context awareness"""
    mode = "advice"
    
    # 1. Fetch last 5 user-assistant pairs (10 messages total) from history
    history_records = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id,
        ChatHistory.mode == mode
    ).order_by(ChatHistory.created_at.desc()).limit(5).all()
    
    # 2. Format history for RAG (reverse to get chronological order)
    chat_history = []
    for h in reversed(history_records):
        chat_history.append({"role": "user", "content": h.query})
        chat_history.append({"role": "assistant", "content": h.response})
    
    # 3. Process query with history
    result = rag_pipeline(
        chat_request.query, 
        chat_request.top_k, 
        mode=mode, 
        chat_history=chat_history
    )
    
    # 4. Save to history
    chat_history_new = ChatHistory(
        user_id=current_user.id,
        query=chat_request.query,
        response=result["answer"],
        mode=mode
    )
    db.add(chat_history_new)
    db.commit()
    
    # Ensure result has mode for response model
    result["mode"] = mode
    return result


# History endpoint
@app.get("/history")
async def get_history(
    limit: int = 20,
    current_user: User = Depends(get_guest_user),  # Use guest user
    db: Session = Depends(get_db)
):
    """Get user's chat history"""
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.created_at.desc()).limit(limit).all()
    
    return {
        "history": [
            {
                "id": h.id,
                "query": h.query,
                "response": h.response,
                "mode": h.mode,
                "created_at": h.created_at.isoformat()
            }
            for h in history
        ]
    }


# User profile endpoint
@app.get("/profile")
async def get_profile(current_user: User = Depends(get_guest_user)):
    """Get current user profile"""
    return {
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
