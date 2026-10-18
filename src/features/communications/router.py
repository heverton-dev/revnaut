# -*- coding: utf-8 -*-
"""
Vertical Slice: Communications Router
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body, status
from pydantic import BaseModel, Field
from src.features.communications import service
from src.features.communications import livekit_service
from src.features.communications.service import (
    MessageSend, ConversationOut, MessageItemOut, MessageSentOut
)

router = APIRouter(tags=["Comunicações & Telefonia VoIP"])


class MessageCreate(BaseModel):
    text: str


class RoomTokenRequest(BaseModel):
    room_name: str = Field(..., description="Nome da sala WebRTC vinculada ao Deal ou Ticket")
    identity: str = Field(..., description="Identidade única do participante")
    name: Optional[str] = Field(default=None, description="Nome legível do participante")
    deal_id: Optional[str] = Field(default=None, description="ID do Deal vinculado")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")
    ttl_seconds: Optional[int] = Field(default=3600, description="Duração do token em segundos")


class RoomTokenResponse(BaseModel):
    token: str
    room_name: str
    livekit_url: str


class VoipDialRequest(BaseModel):
    phone_number: str = Field(..., description="Número de telefone em formato E.164 (+55...)")
    room_name: str = Field(..., description="Nome da sala de destino")
    caller_id: Optional[str] = Field(default=None, description="Identificador da linha chamadora")
    deal_id: Optional[str] = Field(default=None, description="ID do Deal associado")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class VoipDialResponse(BaseModel):
    call_id: str
    room_name: str
    phone_number: str
    caller_id: str
    deal_id: Optional[str] = None
    status: str


class CallRecordingOut(BaseModel):
    id: str
    account_id: str
    room_name: str
    deal_id: Optional[str] = None
    caller_identity: str
    receiver_identity: Optional[str] = None
    call_type: str
    status: str
    duration_seconds: int = 0
    r2_recording_url: Optional[str] = None
    r2_audio_key: Optional[str] = None
    egress_id: Optional[str] = None
    created_at: str


class LiveKitWebhookResponse(BaseModel):
    success: bool
    event: Optional[str] = None
    room_name: Optional[str] = None
    deal_id: Optional[str] = None
    duration_seconds: Optional[int] = 0
    r2_audio_key: Optional[str] = None
    reason: Optional[str] = None



@router.get("/api/v1/chat/conversations", response_model=List[ConversationOut], summary="Listar Conversas")
def read_conversations():
    return service.list_conversations()


@router.get("/api/v1/chat/{chat_id}/messages", response_model=List[MessageItemOut], summary="Listar Mensagens da Conversa")
def read_messages(chat_id: str):
    return service.get_conversation_messages(chat_id)


@router.post("/api/v1/chat/messages", response_model=MessageSentOut, summary="Enviar Mensagem (Legacy)")
def create_message(payload: MessageSend):
    return service.send_message(payload.conversation_id, payload.text)


@router.post("/api/v1/conversations/{chat_id}/messages", response_model=MessageSentOut, status_code=status.HTTP_201_CREATED, summary="Enviar Mensagem na Conversa")
def send_chat_message(chat_id: str, payload: MessageCreate):
    return service.send_message(chat_id, payload.text)


@router.post("/api/v1/communications/rooms/token", response_model=RoomTokenResponse, summary="Gerar token de sala WebRTC LiveKit")
def generate_room_token(payload: RoomTokenRequest):
    token = livekit_service.generate_room_token(
        room_name=payload.room_name,
        identity=payload.identity,
        name=payload.name,
        deal_id=payload.deal_id,
        account_id=payload.account_id or "0f14ffff",
        ttl_seconds=payload.ttl_seconds or 3600,
    )
    return {
        "token": token,
        "room_name": payload.room_name,
        "livekit_url": livekit_service.LIVEKIT_URL,
    }


@router.post("/api/v1/communications/voip/dial", response_model=VoipDialResponse, summary="Disparar discagem VoIP SIP para o cliente")
def dial_sip(payload: VoipDialRequest):
    res = livekit_service.dial_sip_participant(
        phone_number=payload.phone_number,
        room_name=payload.room_name,
        caller_id=payload.caller_id,
        deal_id=payload.deal_id,
        account_id=payload.account_id or "0f14ffff",
    )
    return res


@router.post("/api/v1/communications/livekit/webhook", response_model=LiveKitWebhookResponse, summary="Webhook de eventos do LiveKit (Egress / Room Finished)")
def livekit_webhook(payload: Dict[str, Any] = Body(...)):
    return livekit_service.handle_livekit_webhook(payload)



@router.get("/api/v1/communications/deals/{deal_id}/recordings", response_model=List[CallRecordingOut], summary="Listar gravações de reuniões do Deal")
def get_deal_recordings(deal_id: str):
    return livekit_service.list_deal_recordings(deal_id=deal_id)


