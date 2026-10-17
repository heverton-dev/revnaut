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
