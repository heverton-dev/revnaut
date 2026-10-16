# -*- coding: utf-8 -*-
"""
Vertical Slice: Consignments Router (FastAPI)
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, status
from src.features.consignments.schemas import ConsignmentOut, ConsignmentConsumptionCreate, ConsignmentConsumptionOut
from src.features.consignments import service

router = APIRouter(prefix="/api/v1/consignments", tags=["Estoque Consignado & Caixas Cirúrgicas"])


@router.get("", response_model=List[ConsignmentOut], summary="Listar caixas cirúrgicas consignadas com isolamento hierárquico")
def get_consignments(account_id: str = "0f14ffff", x_user_id: Optional[str] = Header(None)):
    return service.list_consignments(account_id=account_id, user_id=x_user_id)



@router.get("/{consignment_id}", response_model=ConsignmentOut, summary="Obter detalhes e inventário de uma caixa consignada")
def get_consignment(consignment_id: str):
    box = service.get_consignment(consignment_id)
    if not box:
        raise HTTPException(status_code=404, detail="Caixa consignada não encontrada")
    return box


from src.core.database import get_connection
from src.core.security import enforce_user_permission


@router.post("/{consignment_id}/consume", response_model=ConsignmentConsumptionOut, summary="Registrar baixa cirúrgica e disparar reposição automática")
def consume_item(
    consignment_id: str, 
    data: ConsignmentConsumptionCreate,
    account_id: str = "0f14ffff",
    x_user_id: Optional[str] = Header(None)
):
    conn = get_connection()
    try:
        enforce_user_permission(conn, x_user_id, account_id, "consignments:consume")
    finally:
        conn.close()

    try:
        return service.log_consumption(consignment_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

