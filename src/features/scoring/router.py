# -*- coding: utf-8 -*-
"""
Vertical Slice: Scoring Router (FastAPI)
"""

from __future__ import annotations
from typing import List
from fastapi import APIRouter, HTTPException, status
from src.features.scoring.schemas import ScoringRuleCreate, ScoringRuleUpdate, ScoringRuleOut, RecalculateResponse
from src.features.scoring import service

router = APIRouter(prefix="/api/v1/scoring", tags=["Lead Scoring & ICP"])


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


@router.delete("/rules/{rule_id}", summary="Remover regra de pontuação")
def delete_rule(rule_id: str):
    ok = service.delete_rule(rule_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Regra de pontuação não encontrada")
    return {"status": "deleted", "rule_id": rule_id}


@router.post("/recalculate", response_model=RecalculateResponse, summary="Recalcular scores de toda a base de contatos")
def recalculate_scores():
    return service.recalculate_all_scores()
