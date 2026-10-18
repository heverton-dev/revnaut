# -*- coding: utf-8 -*-
"""
Vertical Slice: Deals & Pipeline
Schemas tipados OpenAPI 3.1
"""

from pydantic import BaseModel, Field


class DealCreate(BaseModel):
    title: str = Field(..., description="Título da oportunidade comercial")
    value: float = Field(..., gt=0, description="Valor do negócio em Reais")
    company: str = Field(..., description="Nome da empresa")
    contact_name: str = Field(..., description="Nome do contato decisor")
    pipeline_id: int | None = Field(default=None, description="ID do funil/pipeline de vendas")
    stage_id: int = Field(default=101, description="ID do estágio inicial no funil")
    priority: str = Field(default="media", pattern="^(baixa|media|alta)$")


class DealMove(BaseModel):
    stage_id: int = Field(..., description="Novo ID de estágio no funil")


class DealUpdate(BaseModel):
    title: str | None = Field(default=None, description="Título da oportunidade comercial")
    value: float | None = Field(default=None, gt=0, description="Novo valor do negócio em Reais")
    priority: str | None = Field(default=None, pattern="^(baixa|media|alta)$")
    expected_close_date: str | None = Field(default=None, description="Data estimada de fechamento (AAAA-MM-DD)")
    comment: str | None = Field(default=None, description="Comentário para auditoria")


class PipelineItemOut(BaseModel):
    id: int
    name: str


class PipelineMetricsOut(BaseModel):
    mrr: float
    pipelineTotal: float
    closedWonMRR: float = 0.0
    totalDeals: int = 0
    conversionRate: float = 0.0


class DealsListResponse(BaseModel):
    stages: list[dict]
    deals: list[dict]


class DealCreateResponse(BaseModel):
    model_config = {"extra": "allow"}
    status: str
    id: str
    title: str | None = None
    value: float | None = None
    company: str | None = None
    contact_name: str | None = None
    pipeline_id: int | None = None
    stage_id: int | None = None
    priority: str | None = None
    owner_id: str | None = None
    team_id: str | None = None



class DealMoveResponse(BaseModel):
    status: str
    deal_id: str
    new_stage_id: int


class DealDetailOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str | None = None
    value: float | None = None
    priority: str | None = None
    expected_close_date: str | None = None


class DealTimelineResponse(BaseModel):
    deal_id: str
    timeline: list[dict]


class DealApproveCreditResponse(BaseModel):
    deal_id: str
    credit_approved: bool = True
    message: str
    credit_limit: float | None = None


class ProductCatalogItemOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    sku: str
    name: str
    category: str
    anvisa_reg: str | None = None
    prosthetic_platform: str | None = None
    diameter: float | None = None
    length: float | None = None
    recommended_torque: int | None = 35
    base_price: float
    is_active: int = 1


class PriceTableOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    table_key: str
    name: str
    discount_factor: float
    is_active: int = 1


class ProposalItem(BaseModel):
    sku: str = Field(..., description="SKU do produto no catálogo")
    quantity: int = Field(default=1, gt=0, description="Quantidade de unidades")


class CalculateProposalRequest(BaseModel):
    deal_id: str = Field(..., description="ID do Deal vinculado")
    table_key: str = Field(default="BALCAO", description="Tabela de preço: BALCAO | FRANQUIA | DISTRIBUIDOR | UNIVERSIDADE_ENSINO | KOL_PARCEIRO")
    items: list[ProposalItem] = Field(..., min_length=1, description="Lista de itens e quantidades")
    requested_discount_pct: float = Field(default=0.0, ge=0.0, le=100.0, description="Percentual de desconto solicitado")
    user_id: str | None = Field(default=None, description="ID do usuário que está propondo")
    user_role: str | None = Field(default="consultor", description="Cargo do usuário para validação de alçada RBAC")
    account_id: str | None = Field(default="0f14ffff", description="ID do tenant")


class CalculateProposalResponse(BaseModel):
    model_config = {"extra": "allow"}
    status: str
    requires_approval: bool
    base_value: float
    final_value: float
    requested_discount_pct: float
    max_allowed_pct: float
    request_id: str | None = None


class ApproveDiscountRequest(BaseModel):
    request_id: str = Field(..., description="ID da solicitação de desconto")
    approver_user_id: str = Field(..., description="ID do gestor aprovador")
    account_id: str | None = Field(default="0f14ffff", description="ID do tenant")


class ApproveDiscountResponse(BaseModel):
    model_config = {"extra": "allow"}
    success: bool
    request_id: str
    deal_id: str
    status: str


class GenerateContractRequest(BaseModel):
    deal_id: str = Field(..., description="ID do Deal vinculado")
    contract_type: str = Field(default="fornecimento_implantes", description="Tipo de contrato: fornecimento_implantes | termo_consignacao | proposta")
    signer_name: str | None = Field(default=None, description="Nome do cirurgião signatário")
    signer_email: str | None = Field(default=None, description="E-mail do signatário")
    signer_phone: str | None = Field(default=None, description="WhatsApp/Telefone para envio do link de assinatura")
    account_id: str | None = Field(default="0f14ffff", description="ID do tenant")


class GenerateContractResponse(BaseModel):
    model_config = {"extra": "allow"}
    contract_id: str
    deal_id: str
    documenso_document_id: str
    status: str
    original_pdf_r2_key: str
    signing_url: str


class DealContractOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    deal_id: str
    documenso_document_id: str | None = None
    title: str
    contract_type: str
    status: str
    original_pdf_r2_key: str | None = None
    signed_pdf_r2_key: str | None = None
    signed_pdf_url: str | None = None
    sha256_hash: str | None = None
    signer_name: str | None = None
    signer_email: str | None = None
    signer_phone: str | None = None
    signing_url: str | None = None
    created_at: str
    signed_at: str | None = None


class DocumensoWebhookResponse(BaseModel):
    model_config = {"extra": "allow"}
    success: bool
    deal_id: str | None = None
    contract_status: str
    new_stage_id: int | None = None
    sha256_hash: str | None = None





