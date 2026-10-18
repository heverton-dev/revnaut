# -*- coding: utf-8 -*-
"""
Router FastAPI para Conector TOTVS Protheus & Hub Fiscal ERP (Windmill).
"""

from typing import List, Optional
from fastapi import APIRouter, Header, HTTPException, status, Query
from src.features.integrations.totvs.schemas import (
    TotvsCustomerSA1,
    TotvsOrderSC5,
    TotvsSyncResponse,
    OutboxItemOut,
    ErpRemittanceRequest,
    ErpSettlementRequest,
    ErpFiscalInvoiceOut,
    ErpSettlementResponse,
)
from src.features.integrations.totvs import service
from src.features.integrations.erp_hub import windmill_client

router = APIRouter(tags=["Integrações • TOTVS Protheus & ERP Hub"])


@router.post("/api/v1/integrations/totvs/customers/sync", response_model=TotvsSyncResponse, status_code=status.HTTP_200_OK, summary="Sincronizar Cliente SA1 com Protheus")
def sync_customer(
    payload: TotvsCustomerSA1,
    account_id: str = "0f14ffff",
    idempotency_key: Optional[str] = Header(None)
):
    return service.sync_sa1_customer(payload, account_id=account_id, idempotency_key=idempotency_key)


@router.post("/api/v1/integrations/totvs/orders", response_model=TotvsSyncResponse, status_code=status.HTTP_201_CREATED, summary="Emitir Pedido de Venda SC5/SC6 no Protheus")
def create_order(
    payload: TotvsOrderSC5,
    account_id: str = "0f14ffff"
):
    return service.create_sc5_order(payload, account_id=account_id)


@router.get("/api/v1/integrations/totvs/outbox", response_model=List[OutboxItemOut], summary="Listar Fila de Integrações Outbox")
def list_outbox(
    account_id: str = "0f14ffff",
    status_filter: Optional[str] = Query(None, description="Filtro por status: pending, sent, failed")
):
    return service.list_outbox_items(account_id=account_id, status_filter=status_filter)


@router.post(
    "/api/v1/integrations/erp/remittance/emit",
    response_model=ErpFiscalInvoiceOut,
    status_code=status.HTTP_201_CREATED,
    summary="Emitir NF-e de Remessa em Consignação (CFOP 5.917 / 6.917)"
)
def emit_remittance_invoice(payload: ErpRemittanceRequest):
    orchestrator = windmill_client.WindmillERPOrchestrator()
    return orchestrator.dispatch_consignment_remittance(
        remittance_data=payload.model_dump(),
        erp_type=payload.erp_type,
        account_id=payload.account_id or "0f14ffff"
    )


@router.post(
    "/api/v1/integrations/erp/settlement/emit",
    response_model=ErpSettlementResponse,
    status_code=status.HTTP_200_OK,
    summary="Liquidação Pós-Cirúrgica: Retorno Simbólico (1.918) e Faturamento de Venda (5.113)"
)
def emit_settlement_invoices(payload: ErpSettlementRequest):
    orchestrator = windmill_client.WindmillERPOrchestrator()
    return orchestrator.dispatch_consignment_settlement(
        settlement_data=payload.model_dump(),
        erp_type=payload.erp_type,
        account_id=payload.account_id or "0f14ffff"
    )


@router.get(
    "/api/v1/integrations/erp/invoices",
    response_model=List[ErpFiscalInvoiceOut],
    summary="Listar NF-es de Consignação emitidas"
)
def list_erp_invoices(
    flow_type: Optional[str] = None,
    erp_type: Optional[str] = None,
    account_id: str = "0f14ffff"
):
    return windmill_client.list_fiscal_invoices(
        flow_type=flow_type,
        erp_type=erp_type,
        account_id=account_id
    )


@router.get(
    "/api/v1/integrations/erp/invoices/{invoice_id}",
    response_model=ErpFiscalInvoiceOut,
    summary="Consultar detalhes de uma NF-e específica"
)
def get_erp_invoice(invoice_id: str, account_id: str = "0f14ffff"):
    inv = windmill_client.get_fiscal_invoice(invoice_id=invoice_id, account_id=account_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Nota fiscal não encontrada.")
    return inv
