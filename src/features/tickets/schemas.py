# -*- coding: utf-8 -*-
"""
Vertical Slice: Tickets Schemas
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=2)
    customer_name: str = Field(..., min_length=2)
    priority: str = Field(default="media", pattern="^(alta|media|baixa)$")
    category: str = Field(default="Suporte Técnico")
    status: str = Field(default="aberto", pattern="^(aberto|em_andamento|resolvido)$")


class TicketStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(aberto|em_andamento|resolvido)$")


class TicketOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    title: str
    customer_name: str
    priority: str
    status: str
    category: str
    created_at: str


class SurgicalSosTriggerRequest(BaseModel):
    customer_name: str = Field(..., description="Nome do cirurgião solicitante")
    customer_phone: str = Field(..., description="Telefone WhatsApp do cirurgião/instrumentadora (+55...)")
    cro_uf: str = Field(..., description="CRO/UF do cirurgião habilitado")
    procedure_details: str = Field(..., description="Descrição técnica da intercorrência cirúrgica")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class SurgicalSosResponse(BaseModel):
    model_config = {"extra": "allow"}
    ticket_id: str
    title: str
    priority: str
    livekit_room_url: str
    customer_name: str
    customer_phone: str
    cro_uf: str
    status: str
    created_at: str


class SurgicalSosDentgoDispatchRequest(BaseModel):
    product_id: str = Field(..., description="Código do implante ou instrumental cirúrgico de emergência")
    quantity: int = Field(default=1, ge=1, description="Quantidade necessária")
    delivery_address: str = Field(..., description="Endereço exato do hospital/sala cirúrgica")
    delivery_lat: float = Field(..., description="Latitude geográfica")
    delivery_lng: float = Field(..., description="Longitude geográfica")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class SurgicalSosDentgoDispatchResponse(BaseModel):
    model_config = {"extra": "allow"}
    ticket_id: str
    dentgo_order_id: str
    status: str
    estimated_eta_minutes: int
    hub_id: str
    total_amount: float


class SurgicalSosTicketOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    title: str
    customer_name: str
    priority: str
    status: str
    category: str
    livekit_room_url: Optional[str] = None
    customer_phone: Optional[str] = None
    cro_uf: Optional[str] = None
    dentgo_order_id: Optional[str] = None
    clinical_notes: Optional[str] = None
    created_at: str

