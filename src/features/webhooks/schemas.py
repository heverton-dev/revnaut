# -*- coding: utf-8 -*-
"""
Pydantic Schemas para Webhooks Outbound & Portal de Desenvolvedores.
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class WebhookSubscriptionCreate(BaseModel):
    name: str = Field(..., description="Nome de identificação do integrador (ex: ERP Sankhya / Lab Prótese)")
    target_url: str = Field(..., description="URL HTTPS de destino que receberá os payloads")
    subscribed_events: List[str] = Field(
        default_factory=lambda: ["*"],
        description="Lista de eventos inscritos (ex: deal.won, keypartners.custody_changed, dentgo.order_delivered)"
    )
    signing_secret: Optional[str] = Field(None, description="Segredo compartilhado HMAC-SHA256 (gerado automaticamente se omitido)")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class WebhookSubscriptionOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    name: str
    target_url: str
    subscribed_events: List[str]
    signing_secret: str
    is_active: bool
    consecutive_failures: int
    circuit_breaker_tripped: bool
    created_at: Optional[str] = None


class WebhookSubscriptionListResponse(BaseModel):
    model_config = {"extra": "allow"}
    subscriptions: List[WebhookSubscriptionOut]
    total: int


class WebhookDeliveryLogOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    subscription_id: str
    account_id: str
    event_name: str
    target_url: str
    signature_header: str
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    latency_ms: float
    attempt: int
    success: bool
    created_at: Optional[str] = None


class WebhookDeliveryLogsListResponse(BaseModel):
    model_config = {"extra": "allow"}
    logs: List[WebhookDeliveryLogOut]
    total: int


class WebhookTestDispatchPayload(BaseModel):
    subscription_id: str = Field(..., description="ID da assinatura para disparo do teste")
    event_name: str = Field(default="dentgo.order_delivered", description="Nome do evento simulado")
    payload_data: Optional[Dict[str, Any]] = Field(default=None, description="Dados customizados para envio no corpo")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class WebhookTestDispatchResponse(BaseModel):
    model_config = {"extra": "allow"}
    success: bool
    subscription_id: str
    delivery_id: str
    signature_header: str
    status_code: int
    latency_ms: float
    circuit_breaker_tripped: bool
    response_preview: str


class WebhookResetCircuitResponse(BaseModel):
    model_config = {"extra": "allow"}
    subscription_id: str
    is_active: bool
    consecutive_failures: int
    circuit_breaker_tripped: bool
    message: str


class WebhookDeleteResponse(BaseModel):
    model_config = {"extra": "allow"}
    success: bool
    deleted_id: str

