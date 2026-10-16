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
    specialty: Optional[str] = Field(default="Implantodontia", description="Especialidade odontológica")
    work_model: Optional[str] = Field(default="Clínica Própria", description="Modelo de atuação clínica")
    monthly_implants_volume: Optional[str] = Field(default="20-50/mês", description="Volume de implantes/mês")
    customer_type: Optional[str] = Field(default="Cirurgião", description="Cirurgião | Clínica/PJ | Aluno | Professor/KOL | Distribuidor")

