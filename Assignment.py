from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

app = FastAPI()
session_store = []
chat_store = {}

class SessionCreateRequest(BaseModel):
    session_user: str = Field(..., min_length=1)

class SessionResponse(BaseModel):
    session_id: int
    session_user: str
    created_at: str

class MessageCreateRequest(BaseModel):
    role: str
    content: str = Field(..., min_length=1)

class Message(BaseModel):
    role: str
    content: str

@app.post("/sessions", response_model=SessionResponse)
def create_session(req: SessionCreateRequest):
    username = req.session_user.strip().lower()
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    
    session_id = len(session_store) + 1
    created_at = datetime.utcnow().isoformat()

    session_data = {
        "session_id": session_id,
        "session_user": username,
        "created_at": created_at
    }
    session_store.append(session_data)
    chat_store[session_id] = []

    return session_data

@app.post("/sessions/{session_id}/messages")
def add_message(
    session_id: int = Path(...),
    message: MessageCreateRequest = ...
):
    if session_id not in chat_store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if message.role not in ("user", "assistant"):
        raise HTTPException(status_code=400, detail="Invalid role")
    
    chat_store[session_id].append({
        "role": message.role,
        "content": message.content
    })
    return {"status": "message added"}

@app.get("/sessions/{session_id}/messages", response_model=List[Message])
def get_messages(session_id: int, role: Optional[str] = Query(None)):
    if session_id not in chat_store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = chat_store[session_id]
    if role:
        if role not in ("user", "assistant"):
            raise HTTPException(status_code=400, detail="Invalid role filter")
        messages = [msg for msg in messages if msg["role"] == role]

    return messages
