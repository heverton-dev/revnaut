# -*- coding: utf-8 -*-
"""
Vertical Slice: Contacts Schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ContactCreate(BaseModel):
    name: str = Field(..., description="Nome completo do contato")
    email: str = Field(..., description="E-mail corporativo")
    phone: Optional[str] = Field(None, description="Telefone ou WhatsApp")
    company: Optional[str] = Field(None, description="Empresa")
    tags: List[str] = Field(default_factory=list, description="Lista de etiquetas")
    cro: Optional[str] = Field(None, description="Registro no Conselho Regional de Odontologia")
    cro_uf: Optional[str] = Field(None, description="UF do conselho (Ex: SP, PR)")
    cro_verified: Optional[bool] = Field(default=False, description="Flag de verificação oficial no CRO")
    specialty: Optional[str] = Field(default="Implantodontia", description="Especialidade odontológica")
    work_model: Optional[str] = Field(default="Clínica Própria", description="Modelo de atuação clínica")
    monthly_implants_volume: Optional[str] = Field(default="20-50/mês", description="Volume de implantes/mês")
    customer_type: Optional[str] = Field(default="Cirurgião", description="Cirurgião | Clínica/PJ | Aluno | Professor/KOL | Distribuidor")
    city: Optional[str] = Field(None, description="Cidade da clínica")
    state: Optional[str] = Field(None, description="UF / Estado")


class ContactImportItem(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    cro: Optional[str] = None
    cro_uf: Optional[str] = None
    cro_verified: Optional[bool] = False
    specialty: Optional[str] = "Implantodontia"
    work_model: Optional[str] = "Clínica Própria"
    monthly_implants_volume: Optional[str] = "20-50/mês"
    customer_type: Optional[str] = "Cirurgião"
    city: Optional[str] = None
    state: Optional[str] = None
    owner_id: Optional[str] = None
    team_id: Optional[str] = None


class ContactImportRequest(BaseModel):
    strategy: str = Field(default="territorial", description="territorial | specialty | round_robin | keep_assigned")
    contacts: List[ContactImportItem] = Field(default_factory=list)
    csv_raw: Optional[str] = Field(None, description="Dados brutos em formato CSV para parsing automático")


class ContactImportResponse(BaseModel):
    success: bool = True
    total_received: int
    created_count: int
    updated_count: int
    skipped_count: int = 0
    strategy_used: str
    allocations_by_rep: dict[str, int]
    items_preview: List[dict]


class ContactOut(BaseModel):
    model_config = {"extra": "allow"}
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    score: Optional[int] = 50
    cro: Optional[str] = None
    cro_uf: Optional[str] = None
    cro_verified: Optional[bool] = False
    specialty: Optional[str] = None
    work_model: Optional[str] = None
    monthly_implants_volume: Optional[str] = None
    customer_type: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    owner_id: Optional[str] = None
    team_id: Optional[str] = None


class ContactProfileResponse(BaseModel):
    model_config = {"extra": "allow"}
    id: int
    name: str
    email: Optional[str] = None
    company: Optional[str] = None
    deals: List[dict] = []
    timeline: List[dict] = []
    score: int = 50



class ContactTimelineResponse(BaseModel):
    contact_id: int
    timeline: List[dict]


class ContactTimelineCommentResponse(BaseModel):
    model_config = {"extra": "allow"}
    status: Optional[str] = None
    id: Optional[int] = None
    message: Optional[str] = None


class CroValidateRequest(BaseModel):
    cro: str
    uf: Optional[str] = None
    category: Optional[str] = "CD"


class CroValidateResponse(BaseModel):
    is_valid: bool
    status: str
    verified: bool
    canonical_cro: Optional[str] = None
    professional_name: Optional[str] = None
    uf: Optional[str] = None
    clean_number: Optional[str] = None
    category: Optional[str] = None
    cached: Optional[bool] = False
    error: Optional[str] = None


class CfoComplianceRequest(BaseModel):
    text: str
    has_responsible_cro: Optional[bool] = False
    responsible_cro: Optional[str] = None


class CfoComplianceResponse(BaseModel):
    is_compliant: bool
    violations: List[str] = []
    warnings: List[str] = []
    has_responsible_cro: bool
    detected_cro: Optional[str] = None




