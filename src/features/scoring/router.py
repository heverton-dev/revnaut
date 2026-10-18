# -*- coding: utf-8 -*-
"""
Vertical Slice: Scoring Router (FastAPI)
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Body
from src.features.scoring.schemas import (
    ScoringRuleCreate,
    ScoringRuleUpdate,
    ScoringRuleOut,
    RecalculateRequest,
    RecalculateResponse,
    ScoringPresetOut,
    ScoringPresetApply,
    ScoringPresetApplyResponse,
    DeleteRuleResponse,
    EvaluateHandoffRequest,
    EvaluateHandoffResponse,
)
from src.features.scoring import service

router = APIRouter(prefix="/api/v1/scoring", tags=["Lead Scoring & ICP"])


@router.get("/presets", response_model=List[ScoringPresetOut], summary="Listar Presets Plug & Play de Lead Scoring Odontológico")
def get_presets():
    return service.list_presets()


@router.post("/presets/apply", response_model=ScoringPresetApplyResponse, summary="Aplicar Preset Plug & Play de Lead Scoring")
def apply_preset(data: ScoringPresetApply):
    try:
        return service.apply_preset(data.preset_key, overwrite_existing=data.overwrite_existing)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rules", response_model=List[ScoringRuleOut], summary="Listar regras e critérios de pontuação ICP")
def get_rules():
    return service.list_rules()


@router.post("/rules", response_model=ScoringRuleOut, status_code=status.HTTP_201_CREATED, summary="Criar nova regra de pontuação")
def create_rule(data: ScoringRuleCreate):
    return service.create_rule(data)


@router.put("/rules/{rule_id}", response_model=ScoringRuleOut, summary="Atualizar pesos ou status de regra ICP")
def update_rule(rule_id: str, data: ScoringRuleUpdate):
    rule = service.update_rule(rule_id, data)
    if not rule:
        raise HTTPException(status_code=404, detail="Regra de pontuação não encontrada")
    return rule


@router.delete("/rules/{rule_id}", response_model=DeleteRuleResponse, summary="Remover regra de pontuação")
def delete_rule(rule_id: str):
    ok = service.delete_rule(rule_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Regra de pontuação não encontrada")
    return {"status": "deleted", "rule_id": rule_id}



@router.post("/recalculate", response_model=RecalculateResponse, summary="Recalcular scores de toda a base com tiers configuráveis")
def recalculate_scores(payload: Optional[RecalculateRequest] = Body(default=None)):
    tier_a = payload.tier_a_min if payload else 80
    tier_b = payload.tier_b_min if payload else 50
    return service.recalculate_all_scores(tier_a_min=tier_a, tier_b_min=tier_b)


@router.post("/evaluate-handoff", response_model=EvaluateHandoffResponse, summary="Avaliar lead scoring odontológico e executar handoff automático")
def evaluate_handoff(payload: EvaluateHandoffRequest):
    try:
        res = service.calculate_contact_score_and_handoff(
            contact_id=payload.contact_id,
            account_id=payload.account_id or "0f14ffff",
            additional_interactions=payload.interactions,
        )
        return {
            "success": True,
            "contact_id": payload.contact_id,
            "score": res["score"],
            "tier": res["tier"],
            "deal_created": res["deal_created"],
            "deal_id": res["deal_id"],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

