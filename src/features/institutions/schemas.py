# -*- coding: utf-8 -*-
"""
Vertical Slice: Institutions Schemas (Instituições de Ensino & Cursos de Especialização Odontológica)
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class InstitutionCreate(BaseModel):
    name: str = Field(..., min_length=2, description="Nome da instituição (Ex: Faculdade São Leopoldo Mandic)")
    institution_type: str = Field(default="Faculdade / Pós-Graduação")
    city: str = Field(..., min_length=2)
    state: str = Field(..., min_length=2, max_length=2)
    coordinator_name: str = Field(..., min_length=2)
    active_students_count: int = Field(default=0, ge=0)
    accreditation_status: str = Field(default="credenciada", pattern="^(credenciada|em_negociacao|prospect)$")


class InstitutionOut(BaseModel):
    id: str
    account_id: str
    name: str
    institution_type: str
    city: str
    state: str
    coordinator_name: str
    active_students_count: int
    accreditation_status: str
    created_at: str
