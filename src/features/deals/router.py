# -*- coding: utf-8 -*-
"""
Vertical Slice: Deals Router
Endpoints OpenAPI 3.1 para Funil e Negócios.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Header, status
from src.features.deals.schemas import DealCreate, DealMove
from src.features.deals import service

router = APIRouter(tags=["Vendas & Funil"])


@router.get("/api/v1/pipelines", summary="Listar Funis de Vendas Disponíveis")
def read_pipelines():
    return service.list_pipelines()


@router.get("/api/v1/metrics", summary="Métricas de Pipeline e MRR")
def read_metrics():
    return service.get_metrics()


@router.get("/api/v1/deals", summary="Listar Oportunidades e Estágios com Escopo Hierárquico")
def read_deals(
    pipeline_id: Optional[int] = None,
    account_id: str = "0f14ffff",
    x_user_id: Optional[str] = Header(None)
):
    return service.get_pipeline_and_deals(pipeline_id=pipeline_id, account_id=account_id, user_id=x_user_id)


from src.core.database import get_connection
from src.core.security import enforce_user_permission


@router.post("/api/v1/deals", status_code=status.HTTP_201_CREATED, summary="Criar Nova Oportunidade com Validação RBAC")
def create_deal(
    payload: DealCreate,
    account_id: str = "0f14ffff",
    x_user_id: Optional[str] = Header(None)
):
    conn = get_connection()
    try:
        enforce_user_permission(conn, x_user_id, account_id, "deals:write")
    finally:
        conn.close()
    return service.create_deal(payload)


@router.put("/api/v1/deals/{deal_id}/stage", summary="Mover Oportunidade de Estágio")
def move_deal(deal_id: str, payload: DealMove):
    success = service.move_deal_stage(deal_id, payload.stage_id)
    if not success:
        raise HTTPException(status_code=404, detail="Negócio não encontrado.")
    return {"deal_id": deal_id, "new_stage_id": payload.stage_id, "status": "updated"}
