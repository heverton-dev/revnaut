# -*- coding: utf-8 -*-
"""
Router FastAPI para Automações e Gatilhos de Receita.
"""

from fastapi import APIRouter, HTTPException, status
from src.features.automations.schemas import HotLeadEvaluationResponse
from src.features.automations.revenue_triggers import evaluate_hot_lead_and_overflow

router = APIRouter(prefix="/api/v1/automations", tags=["Automações & Gatilhos de Receita"])


@router.post("/evaluate-hot-lead/{contact_id}", response_model=HotLeadEvaluationResponse, status_code=status.HTTP_200_OK, summary="Avaliar e Transbordar Lead Hot (Tier A)")
def evaluate_hot_lead(contact_id: int, account_id: str = "0f14ffff"):
    res = evaluate_hot_lead_and_overflow(contact_id, account_id=account_id)
    if res.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Contato não encontrado.")
    return res
