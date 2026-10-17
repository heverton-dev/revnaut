# -*- coding: utf-8 -*-
"""
Router FastAPI para Conector TOTVS Protheus.
"""

from typing import List, Optional
from fastapi import APIRouter, Header, status, Query
from src.features.integrations.totvs.schemas import (
    TotvsCustomerSA1,
    TotvsOrderSC5,
    TotvsSyncResponse,
    OutboxItemOut
)
from src.features.integrations.totvs import service

router = APIRouter(prefix="/api/v1/integrations/totvs", tags=["Integrações • TOTVS Protheus"])


@router.post("/customers/sync", response_model=TotvsSyncResponse, status_code=status.HTTP_200_OK, summary="Sincronizar Cliente SA1 com Protheus")
def sync_customer(
    payload: TotvsCustomerSA1,
    account_id: str = "0f14ffff",
    idempotency_key: Optional[str] = Header(None)
):
    return service.sync_sa1_customer(payload, account_id=account_id, idempotency_key=idempotency_key)


@router.post("/orders", response_model=TotvsSyncResponse, status_code=status.HTTP_201_CREATED, summary="Emitir Pedido de Venda SC5/SC6 no Protheus")
def create_order(
    payload: TotvsOrderSC5,
    account_id: str = "0f14ffff"
):
    return service.create_sc5_order(payload, account_id=account_id)


@router.get("/outbox", response_model=List[OutboxItemOut], summary="Listar Fila de Integrações Outbox")
def list_outbox(
    account_id: str = "0f14ffff",
    status_filter: Optional[str] = Query(None, description="Filtro por status: pending, sent, failed")
):
    return service.list_outbox_items(account_id=account_id, status_filter=status_filter)
