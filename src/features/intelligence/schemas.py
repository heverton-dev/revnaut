# -*- coding: utf-8 -*-
"""
Vertical Slice: Intelligence Schemas
Tipagem estrita para Grafo Clínico KOL e Radar Anti-Churn Odontológico (RFM).
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ContactInstitutionCreate(BaseModel):
    contact_id: int = Field(..., description="ID do Cirurgião-Dentista")
    institution_id: str = Field(..., description="ID da Instituição / Clínica / Polo")
    relationship_type: str = Field(
        default="operates_at",
        description="Tipo de vínculo: operates_at | partner_cadcam | teaches_at | kol_speaker"
    )
    role_title: Optional[str] = Field(None, description="Cargo ou papel (ex: Professor Titular, Cirurgião Parceiro)")
    is_kol: bool = Field(default=False, description="Flag indicando se atua como Key Opinion Leader / Speaker")
    notes: Optional[str] = Field(None, description="Observações clínicas ou acadêmicas")


class ContactInstitutionOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    contact_id: int
    institution_id: str
    relationship_type: str
    role_title: Optional[str] = None
    is_kol: bool = False
    notes: Optional[str] = None
    created_at: str
    institution_name: Optional[str] = None
    institution_type: Optional[str] = None
    contact_name: Optional[str] = None
    contact_cro: Optional[str] = None


class ClinicalGraphNode(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    label: str
    node_type: str = Field(..., description="surgeon | clinic | cadcam_lab | university | radiology")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ClinicalGraphEdge(BaseModel):
    model_config = {"extra": "allow"}
    source: str
    target: str
    relationship: str
    is_kol: bool = False
    label: str


class ClinicalGraphResponse(BaseModel):
    model_config = {"extra": "allow"}
    nodes: List[ClinicalGraphNode]
    edges: List[ClinicalGraphEdge]
    total_nodes: int
    total_edges: int
    kol_speakers_count: int


class KOLSpeakerItem(BaseModel):
    model_config = {"extra": "allow"}
    contact_id: int
    name: str
    cro: Optional[str] = None
    uf: Optional[str] = None
    institutions_count: int
    teaching_institutions: List[str] = Field(default_factory=list)
    affiliated_clinics: List[str] = Field(default_factory=list)
    cadcam_labs: List[str] = Field(default_factory=list)
    monthly_volume: int = 0
    kol_badge: str = "KOL Speaker Master"


class KOLSpeakerResponse(BaseModel):
    model_config = {"extra": "allow"}
    total_kols: int
    speakers: List[KOLSpeakerItem]


class ChurnRiskItem(BaseModel):
    model_config = {"extra": "allow"}
    contact_id: int
    name: str
    cro: Optional[str] = None
    clinic_name: Optional[str] = None
    uf: Optional[str] = None
    tier: str = "Tier B"
    monthly_implant_volume: int = 0
    avg_reorder_interval_days: int = 20
    days_since_last_order: int = 0
    days_overdue: int = 0
    last_order_date: Optional[str] = None
    churn_risk_score: int = 0
    churn_risk_level: str = "baixo"  # baixo | medio | alto | critico
    recommended_action: str = "Manter cadência padrão"


class ChurnRiskSummary(BaseModel):
    model_config = {"extra": "allow"}
    total_monitored: int
    critical_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int


class ChurnRiskResponse(BaseModel):
    model_config = {"extra": "allow"}
    summary: ChurnRiskSummary
    radar: List[ChurnRiskItem]


class IntelligenceOperationResponse(BaseModel):
    model_config = {"extra": "allow"}
    success: bool = True
    message: str


class TranscriptionSegment(BaseModel):
    model_config = {"extra": "allow"}
    speaker: str
    start: float
    end: float
    text: str


class TranscriptionProcessRequest(BaseModel):
    call_id: str = Field(..., description="ID da chamada em call_recordings")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")
    dialogue_text: Optional[str] = Field(default=None, description="Texto transcrito pré-existente ou fixture")
    audio_url: Optional[str] = Field(default=None, description="URL do arquivo de áudio no R2")
    duration_seconds: Optional[float] = Field(default=0.0, description="Duração total da gravação em segundos")


class TranscriptionProcessResponse(BaseModel):
    model_config = {"extra": "allow"}
    success: bool
    transcription_id: str
    call_id: str
    deal_id: Optional[str] = None
    duration_seconds: float
    speakers_count: int
    segments: List[TranscriptionSegment]


class TranscriptionItemOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    call_id: str
    deal_id: Optional[str] = None
    full_text: str
    language: str = "pt"
    model_name: str = "faster-whisper-medium"
    duration_seconds: float = 0.0
    speakers_detected: int = 2
    segments: List[TranscriptionSegment]
    created_at: str


class MeetingIntelligenceExtraction(BaseModel):
    model_config = {"extra": "allow"}
    executive_summary: str
    implant_systems_mentioned: List[str] = Field(default_factory=list)
    competitors_cited: List[str] = Field(default_factory=list)
    objections_raised: List[Dict[str, str]] = Field(default_factory=list)
    next_steps_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_deal_value: Optional[float] = None
    suggested_probability: Optional[int] = None


class CopilotExtractAndApplyRequest(BaseModel):
    deal_id: str = Field(..., description="ID do Deal vinculado")
    transcription_text: str = Field(..., description="Texto da transcrição ou nota de voz")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class CopilotExtractAndApplyResponse(BaseModel):
    model_config = {"extra": "allow"}
    success: bool
    deal_id: str
    extraction: MeetingIntelligenceExtraction
    objections_count: int
    tasks_count: int
    updated_value: Optional[float] = None


class CatalogChunkIngestRequest(BaseModel):
    source_manual: str = Field(..., description="Nome do catálogo/manual técnico")
    page_number: int = Field(..., description="Página de referência")
    implant_line: str = Field(..., description="Linha do implante/componente")
    bone_type: Optional[str] = Field(None, description="Classificação óssea (ex: Tipo I, II, III, IV)")
    content_chunk: str = Field(..., description="Texto do fragmento técnico")
    drill_sequence: List[str] = Field(default_factory=list, description="Lista ordenada de brocas/fresas")
    recommended_implant_torque_ncm: Optional[float] = Field(None, description="Torque de inserção do implante em N.cm")
    recommended_prosthetic_torque_ncm: Optional[float] = Field(None, description="Torque do parafuso protético em N.cm")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class CatalogChunkIngestResponse(BaseModel):
    model_config = {"extra": "allow"}
    status: str
    chunk_id: str
    vector_dimensions: int
    message: str


class CatalogRagQueryRequest(BaseModel):
    query: str = Field(..., description="Pergunta do operador ou cirurgião sobre fresagem/torque")
    bone_type: Optional[str] = Field(None, description="Filtro opcional de tipo ósseo")
    min_similarity: Optional[float] = Field(default=0.65, description="Limiar de similaridade de cosseno")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class CatalogRagQueryResponse(BaseModel):
    model_config = {"extra": "allow"}
    query: str
    matched: bool
    similarity_score: float
    source_manual: Optional[str] = None
    page_number: Optional[int] = None
    implant_line: Optional[str] = None
    bone_type: Optional[str] = None
    recommended_implant_torque_ncm: Optional[float] = None
    recommended_prosthetic_torque_ncm: Optional[float] = None
    drill_sequence: List[str] = Field(default_factory=list)
    content_chunk: Optional[str] = None
    answer: str


class SupersetGuestTokenRequest(BaseModel):
    user_id: str = Field(..., description="ID do usuário solicitante (para RLS automático)")
    dashboard_id: str = Field(..., description="ID ou UUID do dashboard no Superset")
    dashboard_type: Optional[str] = Field(default="industry_consignment", description="Tipo de painel: industry_consignment | clinic_chair | dentgo_sla")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class SupersetGuestTokenResponse(BaseModel):
    model_config = {"extra": "allow"}
    token: str
    dashboard_id: str
    dashboard_type: str
    rls_clause: str
    user_id: str
    account_id: str
    superset_domain: str
    expires_in_seconds: int = 3600


class AnalyticsDatasetExportRequest(BaseModel):
    dataset_name: str = Field(..., description="Nome do dataset: deals_funnel | consignment_turnover | dentgo_deliveries | anvisa_rma")
    user_id: str = Field(..., description="ID do usuário solicitante")
    format: Optional[str] = Field(default="csv", pattern="^(csv|parquet)$", description="Formato de saída: csv | parquet")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class AnalyticsDatasetExportResponse(BaseModel):
    model_config = {"extra": "allow"}
    dataset_name: str
    format: str
    r2_storage_key: str
    record_count: int
    download_url: str
    status: str
    exported_at: str


class TextToSqlExecuteRequest(BaseModel):
    natural_language_query: Optional[str] = Field(None, description="Pergunta analítica em português (ex: Total faturado por regional)")
    raw_sql: Optional[str] = Field(None, description="Consulta SQL customizada gerada ou validada")
    user_id: str = Field(..., description="ID do usuário para injeção estrita de escopo RBAC/RLS")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class TextToSqlExecuteResponse(BaseModel):
    model_config = {"extra": "allow"}
    query: str
    sql_executed: str
    is_safe: bool
    columns: List[str] = Field(default_factory=list)
    rows: List[Dict[str, Any]] = Field(default_factory=list)
    chart_labels: List[str] = Field(default_factory=list)
    chart_values: List[float] = Field(default_factory=list)
    summary: str
    execution_time_ms: float


class SokCalculationRequest(BaseModel):
    agreement_id: str = Field(..., description="ID do termo de consignacao KeyPartners")
    days_without_surgery: int = Field(..., ge=0, description="Dias decorridos sem cirurgia realizada")
    contract_limit_days: int = Field(default=30, ge=1, description="Limite contratual em dias para giro do kit")
    kit_immobilized_value: float = Field(..., ge=0.0, description="Valor do kit imobilizado em R$")
    avg_monthly_revenue: float = Field(..., gt=0.0, description="Faturamento medio mensal do parceiro em R$")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class SokCalculationResponse(BaseModel):
    model_config = {"extra": "allow"}
    agreement_id: str
    sok_score: float
    is_idle: bool
    days_without_surgery: int
    contract_limit_days: int
    kit_immobilized_value: float
    avg_monthly_revenue: float
    status: str
    recommendation: str
    dentgo_reverse_pickup_suggested: bool
    dentgo_order_id: Optional[str] = None
    calculated_at: str


class PrCalculationRequest(BaseModel):
    agreement_id: str = Field(..., description="ID do termo de consignacao KeyPartners")
    avg_daily_consumption: float = Field(..., ge=0.0, description="Consumo medio diario em unidades (C_medio_diario)")
    delivery_lead_time_days: float = Field(..., ge=0.0, description="Prazo de entrega DENTGO em dias (T_entrega_dentgo)")
    safety_stock: float = Field(default=0.0, ge=0.0, description="Estoque de seguranca em unidades (ES)")
    current_stock: Optional[int] = Field(None, ge=0, description="Saldo atual de unidades em estoque do parceiro")
    trigger_deal: Optional[bool] = Field(default=True, description="Criar Deal automatico no funil se current_stock <= PR")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class PrCalculationResponse(BaseModel):
    model_config = {"extra": "allow"}
    agreement_id: str
    pr_score: float
    current_stock: int
    replenishment_needed: bool
    deal_id: Optional[str] = None
    deal_title: Optional[str] = None
    whatsapp_sent: bool = False
    whatsapp_message_id: Optional[str] = None
    approval_link: Optional[str] = None
    recommendation: str
    calculated_at: str


class PredictiveInventoryReportResponse(BaseModel):
    model_config = {"extra": "allow"}
    agreement_id: str
    partner_name: str
    scores_history: List[Dict[str, Any]] = Field(default_factory=list)
    total_records: int
