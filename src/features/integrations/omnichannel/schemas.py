# -*- coding: utf-8 -*-
"""
Schemas OpenAPI 3.1 & Pydantic para Gateway Omnichannel (Evolution, Chatwoot, Mautic).
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class OmnichannelWebhookResponse(BaseModel):
    success: bool
    event: str
    channel: str
    contact_id: Optional[int] = None
    score_updated: Optional[int] = None
    message: str


class EvolutionWebhookPayload(BaseModel):
    model_config = {"extra": "allow"}
    event: str = Field(..., description="Tipo do evento Evolution API (ex: 'messages.upsert')")
    instance: Optional[str] = "revnaut-evolution"
    data: Optional[Dict[str, Any]] = None


class ChatwootWebhookPayload(BaseModel):
    model_config = {"extra": "allow"}
    event: str = Field(..., description="Tipo do evento Chatwoot (ex: 'message_created')")
    account: Optional[Dict[str, Any]] = None
    conversation: Optional[Dict[str, Any]] = None
    sender: Optional[Dict[str, Any]] = None
    content: Optional[str] = None


class MauticWebhookPayload(BaseModel):
    model_config = {"extra": "allow"}
    event: str = Field(..., description="Tipo do evento Mautic (ex: 'lead.changepoints')")
    lead: Optional[Dict[str, Any]] = None
    points: Optional[int] = None


class MauticCampaignActionResponse(BaseModel):
    model_config = {"extra": "allow"}
    success: bool = True
    action: str
    campaign_id: Optional[int] = None
    contact_id: Optional[int] = None
    consultant_id: Optional[str] = None
    dispatched_instance: Optional[str] = None
    rendered_message: Optional[str] = None
    timestamp: Optional[float] = None


class WhatsappInstanceCreate(BaseModel):
    instance_name: str = Field(..., description="Nome único da instância na Evolution API v2")
    consultant_user_id: Optional[str] = Field(default=None, description="ID do usuário consultor de vendas")
    phone_number: Optional[str] = Field(default=None, description="Número de telefone conectado (+55...)")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class WhatsappInstanceOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    instance_name: str
    consultant_user_id: Optional[str] = None
    shard_node_url: str
    phone_number: Optional[str] = None
    status: str
    qr_code_base64: Optional[str] = None
    created_at: str
    updated_at: str


class EvolutionWebhookResponse(BaseModel):
    model_config = {"extra": "allow"}
    success: bool = True
    event: str
    action: Optional[str] = None
    sos_call_link: Optional[str] = None
    remote_jid: Optional[str] = None
    phone: Optional[str] = None
    response_message: Optional[str] = None
    status: Optional[str] = None
    media_r2_key: Optional[str] = None


class Omnichannel360ContextOut(BaseModel):
    model_config = {"extra": "allow"}
    contact_identifier: str
    contact: Optional[Dict[str, Any]] = None
    cro_uf: Optional[str] = None
    agreement: Optional[Dict[str, Any]] = None
    consignments_in_field: List[Dict[str, Any]] = Field(default_factory=list)
    active_dentgo_orders: List[Dict[str, Any]] = Field(default_factory=list)
    is_synced_chatwoot: bool = True


class ChatwootSyncResponse(BaseModel):
    model_config = {"extra": "allow"}
    status: str
    contact_id: int
    chatwoot_contact_id: int
    source_id: str
    synced_at: str



