# -*- coding: utf-8 -*-
"""
Pydantic Schemas para o Motor KeyPartners (Consignação Cirúrgica & Parcerias)
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
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


class SurgicalOrderCreate(BaseModel):
    agreement_id: str = Field(..., description="ID do acordo de parceria da clínica")
    patient_identifier: Optional[str] = Field(default=None, description="Identificador anônimo do paciente")
    surgery_date: str = Field(..., description="Data prevista para a cirurgia (YYYY-MM-DD)")
    field_consultant_id: Optional[str] = Field(default=None, description="ID do consultor comercial externo")
    items: List[LedgerItemIn] = Field(..., min_length=1, description="Grade de implantes e instrumentais solicitados")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class SurgicalOrderApproveRequest(BaseModel):
    inside_analyst_id: Optional[str] = Field(default="usr-inside-01", description="ID do analista interno que homologa a remessa")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class ConsumedItemIn(BaseModel):
    product_id: str = Field(..., description="Código do produto utilizado")
    product_name: str = Field(..., description="Descrição técnica")
    anvisa_reg: str = Field(..., description="Registro ANVISA")
    batch_number: str = Field(..., description="Lote do produto instalado no paciente")
    quantity: int = Field(default=1, ge=1, description="Quantidade consumida")
    unit_value: float = Field(..., ge=0.0, description="Valor unitário acordado em R$")
    patient_notes: Optional[str] = Field(default=None, description="Observações clínicas / torque / sítio cirúrgico")


class SurgicalPostopReportRequest(BaseModel):
    consumed_items: List[ConsumedItemIn] = Field(..., min_length=1, description="Itens efetivamente instalados no paciente")
    seal_photo_r2_key: Optional[str] = Field(default=None, description="Chave R2 da foto comprobatória do lacre dos itens não utilizados")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class SurgicalPostopReportResponse(BaseModel):
    model_config = {"extra": "allow"}
    status: str
    order_id: str
    agreement_id: str
    billed_amount: float
    cfop: str
    consumed_units: int
    retained_units: int
    billing_order_id: str


class SurgicalOrderOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    agreement_id: str
    patient_identifier: Optional[str] = None
    surgery_date: str
    status: str
    field_consultant_id: Optional[str] = None
    inside_analyst_id: Optional[str] = None
    remitted_items_json: str
    consumed_items_json: str
    returned_items_json: str
    seal_photo_r2_key: Optional[str] = None
    billing_order_id: Optional[str] = None
    created_at: str
    updated_at: str


class KolContractCreate(BaseModel):
    kol_name: str = Field(..., description="Nome completo do cirurgião KOL / Embaixador")
    cro_uf: str = Field(..., description="CRO/UF do cirurgião")
    equipment_name: str = Field(..., description="Nome do equipamento cedido em comodato")
    asset_tag: str = Field(..., description="Número de patrimônio físico do equipamento")
    min_monthly_implants_target: int = Field(default=20, ge=1, description="Meta mínima mensal de implantes")
    clinical_lectures_quota: int = Field(default=1, ge=0, description="Cota de palestras ou aulas clínicas por período")
    agreement_id: Optional[str] = Field(default=None, description="Vínculo opcional com acordo de consignação")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class KolConsumptionRecordRequest(BaseModel):
    consumed_implants_count: int = Field(..., ge=0, description="Total de implantes consumidos no mês")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class KolConsumptionRecordResponse(BaseModel):
    model_config = {"extra": "allow"}
    compliance_status: str
    current_month_consumption: int
    min_monthly_implants_target: int
    regional_alert: bool
    alert_message: Optional[str] = None


class KolEvidenceSubmitRequest(BaseModel):
    r2_key: str = Field(..., description="Chave R2 do arquivo comprobatório submetido")
    title: str = Field(..., description="Título ou descrição do caso clínico / vídeo")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class KolEvidenceSubmitResponse(BaseModel):
    model_config = {"extra": "allow"}
    success: bool
    contract_id: str
    evidence_r2_keys_json: str


class KolContractOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    agreement_id: Optional[str] = None
    kol_name: str
    cro_uf: str
    equipment_name: str
    asset_tag: str
    min_monthly_implants_target: int
    clinical_lectures_quota: int
    current_month_consumption: int
    compliance_status: str
    evidence_r2_keys_json: str
    created_at: str
    updated_at: str


class LoyaltyPointsCreditRequest(BaseModel):
    partner_id: str = Field(..., description="ID do parceiro ou cirurgiao")
    partner_name: str = Field(..., description="Nome do parceiro")
    implants_count: int = Field(..., ge=1, description="Quantidade de implantes faturados")
    event_origin: Optional[str] = Field(default="deal.won", description="Origem do credito: deal.won | keypartners.postop_reported")
    reference_id: Optional[str] = Field(default=None, description="ID de referencia do deal ou cirurgia")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class LoyaltyPointsCreditResponse(BaseModel):
    model_config = {"extra": "allow"}
    wallet_id: str
    partner_id: str
    partner_name: str
    points_earned: int
    points_balance: int
    lifetime_points: int
    implants_billed_total: int
    previous_tier: str
    current_tier: str
    tier_promoted: bool
    transaction_id: str


class LoyaltyRedemptionRequest(BaseModel):
    partner_id: str = Field(..., description="ID do parceiro ou cirurgiao")
    reward_type_or_id: str = Field(..., description="ID ou tipo da recompensa tecnica")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class LoyaltyRedemptionResponse(BaseModel):
    model_config = {"extra": "allow"}
    partner_id: str
    reward_name: str
    reward_type: str
    points_debited: int
    points_balance_remaining: int
    voucher_code: str
    monetary_value_equivalent: float
    transaction_id: str
    redeemed_at: str


class LoyaltyWalletResponse(BaseModel):
    model_config = {"extra": "allow"}
    wallet_id: Optional[str] = None
    partner_id: str
    partner_name: str
    points_balance: int
    lifetime_points: int
    current_tier: str
    implants_billed_total: int
    transactions: List[Dict[str, Any]] = Field(default_factory=list)


class LoyaltyRewardItem(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    name: str
    reward_type: str
    points_cost: int
    monetary_value_equivalent: float
    is_active: int


