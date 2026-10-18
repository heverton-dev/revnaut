# -*- coding: utf-8 -*-
"""
Pydantic Schemas para o Motor KeyPartners (Consignação Cirúrgica & Parcerias)
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class PartnerAgreementCreate(BaseModel):
    partner_name: str = Field(..., description="Nome do parceiro / clínica / cirurgião")
    partner_cro_uf: Optional[str] = Field(default=None, description="CRO/UF do responsável técnico")
    tier: str = Field(default="SILVER", description="Nível de parceria: SILVER | GOLD | BLACK_KOL")
    credit_limit: float = Field(default=15000.0, description="Limite de crédito consignado em R$")
    min_monthly_revenue: float = Field(default=0.0, description="Piso mínimo de faturamento mensal")
    max_turnover_days: int = Field(default=60, description="Prazo máximo de giro do estoque em dias")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class PartnerAgreementOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    partner_name: str
    partner_cro_uf: Optional[str] = None
    tier: str
    credit_limit: float
    used_credit: float
    min_monthly_revenue: float
    max_turnover_days: int
    is_active: int
    created_at: str


class ConsignmentKitCreate(BaseModel):
    serial_number: str = Field(..., description="Número de série único gravado a laser no kit")
    name: str = Field(..., description="Nome comercial do kit cirúrgico/protético")
    composition_json: Optional[str] = Field(default="{}", description="Composição em formato JSON das brocas e ferramentas")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class ConsignmentKitOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    serial_number: str
    qr_code: str
    name: str
    composition_json: Optional[str] = None
    status: str
    current_agreement_id: Optional[str] = None
    created_at: str


class LedgerItemIn(BaseModel):
    product_id: str = Field(..., description="ID ou código do produto no catálogo")
    product_name: str = Field(..., description="Descrição técnica do produto")
    anvisa_reg: str = Field(..., description="Registro ANVISA obrigatório")
    batch_number: str = Field(..., description="Lote de fabricação do produto")
    serial_number: Optional[str] = Field(default=None, description="Número de série (para kits e instrumentais)")
    quantity: int = Field(default=1, ge=1, description="Quantidade de unidades")
    unit_value: float = Field(..., ge=0.0, description="Valor unitário em R$")
    sterilization_expiry_date: str = Field(..., description="Data de validade da esterilização (YYYY-MM-DD)")


class CustodyDispatchRequest(BaseModel):
    items: List[LedgerItemIn] = Field(..., min_length=1, description="Itens para remessa em custódia")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class CustodyDispatchResponse(BaseModel):
    model_config = {"extra": "allow"}
    status: str
    agreement_id: str
    total_remittance_value: float
    updated_used_credit: float
    available_credit: float
    entries_count: int


class LedgerEntryOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    agreement_id: str
    movement_type: str
    product_id: str
    product_name: str
    anvisa_reg: str
    batch_number: str
    serial_number: Optional[str] = None
    quantity: int
    unit_value: float
    total_value: float
    sterilization_expiry_date: str
    created_at: str


class CustodySummaryResponse(BaseModel):
    model_config = {"extra": "allow"}
    agreement_id: str
    partner_name: str
    partner_cro_uf: Optional[str] = None
    tier: str
    credit_limit: float
    used_credit: float
    available_credit: float
    total_custodied_value: float
    total_items_count: int
    ledger_entries: List[LedgerEntryOut]
