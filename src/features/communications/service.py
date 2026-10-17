# -*- coding: utf-8 -*-
"""
Vertical Slice: Communications Schemas & Service
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field
from src.core.database import get_connection


class MessageSend(BaseModel):
    conversation_id: str = Field(..., description="ID da conversa")
    text: str = Field(..., min_length=1, description="Texto da mensagem")


class ConversationOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    contact_name: str | None = None
    company: str | None = None
    channel: str = "whatsapp"
    unread: int = 0


class MessageItemOut(BaseModel):
    model_config = {"extra": "allow"}
    id: int
    conversation_id: str
    sender: str
    text: str


class MessageSentOut(BaseModel):
    model_config = {"extra": "allow"}
    id: int
    conversation_id: str
    sender: str
    text: str
    status: str



def list_conversations() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM conversations ORDER BY updated_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_conversation_messages(chat_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC", (chat_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def send_message(conversation_id: str, text: str) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO messages (conversation_id, sender, text)
        VALUES (?, 'user', ?)
    """, (conversation_id, text))
    msg_id = cur.lastrowid
    cur.execute("UPDATE conversations SET unread = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (conversation_id,))
    conn.commit()
    conn.close()
    return {
        "id": msg_id,
        "conversation_id": conversation_id,
        "sender": "user",
        "text": text,
        "status": "sent"
    }
