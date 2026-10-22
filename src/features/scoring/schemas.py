# -*- coding: utf-8 -*-
"""
Vertical Slice: Scoring Schemas (Lead Scoring & Qualificação ICP)
"""

from __future__ import annotations
from typing import Dict, List, Optional
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
    model_config = {"extra": "allow"}
    id: int
    name: str
    company: Optional[str] = None
    email: Optional[str] = None
    score: int
    tier: str
    tags: List[str] = Field(default_factory=list)
    cro: Optional[str] = None
    specialty: Optional[str] = None
    monthly_implants_volume: Optional[str] = None


class RecalculateRequest(BaseModel):
    tier_a_min: int = Field(default=80, ge=1, le=100, description="Nota mínima para Tier A")
    tier_b_min: int = Field(default=50, ge=1, le=100, description="Nota mínima para Tier B")
    weights: Optional[Dict[str, float]] = Field(default=None, description="Pesos dimensionais (volume, specialty, geography, institution)")


class RecalculateResponse(BaseModel):
    recalculated_count: int
    tier_a_count: int
    tier_b_count: int
    tier_c_count: int
    avg_score: float
    ranked_leads: List[LeadRankItem]


class ScoringPresetRuleItem(BaseModel):
    name: str
    category: str
    condition_key: str
    condition_val: str
    points: int
    impact_description: str


class ScoringPresetOut(BaseModel):
    preset_key: str
    name: str
    description: str
    target_segment: str
    rules: List[ScoringPresetRuleItem]


class ScoringPresetApply(BaseModel):
    preset_key: str = Field(..., description="Chave do preset: 'implantes_cirurgia_premium', 'ensino_academico', 'distribuidores_atacado', 'clinicas_multidisciplinares'")
    overwrite_existing: bool = Field(default=True, description="Se True, substitui as regras anteriores")


class ScoringPresetApplyResponse(BaseModel):
    success: bool
    preset_key: str
    name: str
    rules_applied: int


class DeleteRuleResponse(BaseModel):
    status: str
    rule_id: str


class EvaluateHandoffRequest(BaseModel):
    contact_id: int = Field(..., description="ID do contato a ser avaliado")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant/account")
    interactions: Optional[List[str]] = Field(default_factory=list, description="Lista de interações ou eventos de engajamento")


class EvaluateHandoffResponse(BaseModel):
    success: bool
    contact_id: int
    score: int
    tier: str
    deal_created: bool
    deal_id: Optional[str] = None


