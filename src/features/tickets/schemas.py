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


class AnvisaRmaClaimCreate(BaseModel):
    surgeon_cro_uf: str = Field(..., description="CRO/UF do cirurgião solicitante")
    surgeon_name: Optional[str] = Field(None, description="Nome do cirurgião")
    agreement_id: Optional[str] = Field(None, description="ID do termo de consignação KeyPartners (se houver)")
    patient_identifier: Optional[str] = Field(None, description="Iniciais ou prontuário anonimizado do paciente")
    product_id: str = Field(..., description="Código de referência do implante")
    product_name: str = Field(..., description="Descrição comercial do implante")
    batch_number: str = Field(..., description="Número do lote fabril gravado no blister/cartucho")
    serial_number: Optional[str] = Field(None, description="Número de série individual do implante")
    fdi_tooth_region: str = Field(..., description="Região dentária anatômica FDI (ex: 11, 21, 36, 46)")
    insertion_torque_ncm: float = Field(..., ge=0.0, description="Torque de inserção em N.cm aplicado na instalação")
    surgery_date: str = Field(..., description="Data da cirurgia de instalação (YYYY-MM-DD)")
    explant_date: str = Field(..., description="Data da perda/explante (YYYY-MM-DD)")
    failure_reason: str = Field(
        ...,
        description="Classificação técnica da queixa: loss_of_osseointegration | fracture | contamination | periimplantitis"
    )
    radiograph_r2_key: str = Field(..., description="Chave R2 do exame radiográfico comprobatório da não-osseointegração")
    notes: Optional[str] = Field(None, description="Parecer clínico cirúrgico detalhado")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class AnvisaRmaClaimOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    ticket_id: str
    agreement_id: Optional[str] = None
    surgeon_name: Optional[str] = None
    surgeon_cro_uf: str
    patient_identifier: Optional[str] = None
    product_id: str
    product_name: str
    batch_number: str
    serial_number: Optional[str] = None
    fdi_tooth_region: str
    insertion_torque_ncm: float
    surgery_date: str
    explant_date: str
    failure_reason: str
    radiograph_r2_key: str
    status: str
    warranty_approved: bool
    replacement_order_id: Optional[str] = None
    quarantine_triggered: bool
    batch_failure_rate_percent: float
    notes: Optional[str] = None
    created_at: str


class AnvisaBatchQuarantineOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    batch_number: str
    product_id: Optional[str] = None
    total_distributed: int
    total_failures: int
    failure_rate_percent: float
    status: str
    reason: str
    blocked_at: str
    unblocked_at: Optional[str] = None


