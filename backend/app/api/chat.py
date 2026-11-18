import uuid
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models.models import ChatSession, ChatMessage, Trip, User
from app.schemas.schemas import ChatQueryRequest, ChatMessageOut, ChatSessionOut
from app.api.auth import get_current_user
from app.services.ai_service import generate_conversational_response

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])

def _load_context(session: ChatSession) -> dict:
    """Safely load context_state from JSON string or dict."""
    raw = session.context_state
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return {}

def _save_context(session: ChatSession, state: dict):
    """Safely save context_state as JSON string (SQLite TEXT column)."""
    try:
        session.context_state = json.dumps(state, ensure_ascii=False)
    except Exception:
        session.context_state = "{}"

@router.post("/message")
def send_chat_message(
    req: ChatQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create or load session
    session_id = req.session_id
    if not session_id:
        session_id = f"chat_{uuid.uuid4().hex[:12]}"
        title_snippet = req.message[:40] + ("..." if len(req.message) > 40 else "")
        session = ChatSession(
            id=session_id,
            trip_id=req.trip_id,
            user_id=current_user.id,
            title=title_snippet,
            context_state="{}"
        )
        db.add(session)
        db.commit()
    else:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            session = ChatSession(
                id=session_id,
                trip_id=req.trip_id,
                user_id=current_user.id,
                title="Travel Assistant Conversation",
                context_state="{}"
            )
            db.add(session)
            db.commit()

    # Save user message
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=req.message
    )
    db.add(user_msg)
    db.commit()

    # Trip context
    trip_ctx = None
    if req.trip_id:
        trip = db.query(Trip).filter(Trip.id == req.trip_id).first()
        if trip:
            trip_ctx = {
                "id": trip.id,
                "destination": trip.destination,
                "total_budget": trip.total_budget,
                "travellers_count": trip.travellers_count,
                "travel_style": trip.travel_style
            }

    # Fetch recent conversation history
    past_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(20)
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in past_messages]

    # Load persistent memory from session
    session_memory = _load_context(session)

    # Generate AI response
    ai_resp = generate_conversational_response(
        user_message=req.message,
        trip_context=trip_ctx,
        conversation_history=history,
        session_memory=session_memory,
        force_deep_search=req.deep_search
    )

    # Persist updated memory back
    _save_context(session, ai_resp.get("memory", session_memory))

    # Serialize structured_data to JSON string for storage
    structured_data = ai_resp.get("structured_data")
    structured_data_str = None
    if structured_data:
        try:
            structured_data_str = json.dumps(structured_data, ensure_ascii=False)
        except Exception:
            structured_data_str = None

    # Save assistant message
    asst_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=ai_resp["content"],
        structured_type=ai_resp.get("structured_type"),
        structured_data=structured_data_str
    )
    db.add(asst_msg)
    db.commit()
    db.refresh(asst_msg)

    # Parse structured_data back to dict for response
    parsed_structured = None
    if asst_msg.structured_data:
        try:
            parsed_structured = json.loads(asst_msg.structured_data) if isinstance(asst_msg.structured_data, str) else asst_msg.structured_data
        except Exception:
            parsed_structured = None

    return {
        "session_id": session_id,
        "message": {
            "id": asst_msg.id,
            "role": "assistant",
            "content": asst_msg.content,
            "structured_type": asst_msg.structured_type,
            "structured_data": parsed_structured,
            "created_at": str(asst_msg.created_at)
        },
        "memory": ai_resp.get("memory", {}),
        "suggested_actions": ai_resp.get("suggested_actions", [])
    }

@router.get("/sessions", response_model=List[ChatSessionOut])
def get_user_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.updated_at.desc()).all()

@router.get("/sessions/{session_id}")
def get_chat_session_detail(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    msgs_out = []
    for m in messages:
        parsed_data = None
        if m.structured_data:
            try:
                parsed_data = json.loads(m.structured_data) if isinstance(m.structured_data, str) else m.structured_data
            except Exception:
                parsed_data = None
        msgs_out.append({
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "structured_type": m.structured_type,
            "structured_data": parsed_data,
            "created_at": str(m.created_at)
        })

    return {
        "id": session.id,
        "title": session.title,
        "context_state": _load_context(session),
        "messages": msgs_out,
        "created_at": str(session.created_at),
        "updated_at": str(session.updated_at)
    }

@router.delete("/sessions/{session_id}")
def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    db.delete(session)
    db.commit()
    return {"status": "deleted", "session_id": session_id}
