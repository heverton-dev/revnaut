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
