# -*- coding: utf-8 -*-
"""
Vertical Slice: Communications Router
"""

from fastapi import APIRouter, status
from pydantic import BaseModel
from src.features.communications import service
from src.features.communications.service import MessageSend

router = APIRouter(tags=["Comunicações & WhatsApp"])


class MessageCreate(BaseModel):
    text: str


@router.get("/api/v1/chat/conversations", summary="Listar Conversas")
def read_conversations():
    return service.list_conversations()


@router.get("/api/v1/chat/{chat_id}/messages", summary="Listar Mensagens da Conversa")
def read_messages(chat_id: str):
    return service.get_conversation_messages(chat_id)


@router.post("/api/v1/chat/messages", summary="Enviar Mensagem (Legacy)")
def create_message(payload: MessageSend):
    return service.send_message(payload.conversation_id, payload.text)


@router.post("/api/v1/conversations/{chat_id}/messages", status_code=status.HTTP_201_CREATED, summary="Enviar Mensagem na Conversa")
def send_chat_message(chat_id: str, payload: MessageCreate):
    return service.send_message(chat_id, payload.text)
