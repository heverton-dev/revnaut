# -*- coding: utf-8 -*-
"""
Vertical Slice: Scoring Schemas (Lead Scoring & Qualificação ICP)
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class ScoringRuleCreate(BaseModel):
    name: str = Field(..., min_length=2, description="Nome do critério ou regra")
    category: str = Field(default="Firmográfico", description="Firmográfico | Demográfico | Comportamental")
    condition_key: str = Field(..., description="Chave de correspondência: tag, company, interaction, source")
    condition_val: str = Field(..., description="Valor(es) procurado(s) separados por vírgula")
    points: int = Field(default=10, ge=1, le=100, description="Pontos atribuídos")
    impact_description: str = Field(default="Ação comercial automática")
    is_active: int = Field(default=1, ge=0, le=1)


class ScoringRuleUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    condition_key: Optional[str] = None
    condition_val: Optional[str] = None
    points: Optional[int] = Field(default=None, ge=1, le=100)
    impact_description: Optional[str] = None
    is_active: Optional[int] = Field(default=None, ge=0, le=1)


class ScoringRuleOut(BaseModel):
    id: str
    account_id: str
    name: str
    category: str
    condition_key: str
    condition_val: str
    points: int
    impact_description: str
    is_active: int
    created_at: str


class LeadRankItem(BaseModel):
    id: int
    name: str
    company: str
    email: str
    score: int
    tier: str
    tags: List[str]


class RecalculateResponse(BaseModel):
    recalculated_count: int
    tier_a_count: int
    tier_b_count: int
    tier_c_count: int
    avg_score: float
    ranked_leads: List[LeadRankItem]
