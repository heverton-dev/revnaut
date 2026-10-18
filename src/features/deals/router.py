# -*- coding: utf-8 -*-
"""
Vertical Slice: Deals Router
Endpoints OpenAPI 3.1 para Funil e Negócios.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Header, status
from fastapi.responses import Response
from src.features.deals.schemas import (
    DealCreate, DealMove, DealUpdate, PipelineItemOut,
    PipelineMetricsOut, DealsListResponse, DealCreateResponse,
    DealMoveResponse, DealDetailOut, DealTimelineResponse,
    DealApproveCreditResponse,
    ProductCatalogItemOut, PriceTableOut,
    CalculateProposalRequest, CalculateProposalResponse,
    ApproveDiscountRequest, ApproveDiscountResponse,
)
from src.features.deals import service
from src.features.deals import catalog_pricing
from src.core.database import get_connection
from src.core.security import enforce_user_permission


router = APIRouter(tags=["Vendas & Funil"])


@router.get("/api/v1/pipelines", response_model=List[PipelineItemOut], summary="Listar Funis de Vendas Disponíveis")
def read_pipelines():
    return service.list_pipelines()


@router.get("/api/v1/metrics", response_model=PipelineMetricsOut, summary="Métricas de Pipeline e MRR")
def read_metrics():
    return service.get_metrics()


@router.get("/api/v1/deals", response_model=DealsListResponse, summary="Listar Oportunidades e Estágios com Escopo Hierárquico")
def read_deals(
    pipeline_id: Optional[int] = None,
    account_id: str = "0f14ffff",
    x_user_id: Optional[str] = Header(None)
):
    return service.get_pipeline_and_deals(pipeline_id=pipeline_id, account_id=account_id, user_id=x_user_id)


@router.post("/api/v1/deals", response_model=DealCreateResponse, status_code=status.HTTP_201_CREATED, summary="Criar Nova Oportunidade com Validação RBAC")
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
    return service.create_deal(payload, user_id=x_user_id)


@router.put("/api/v1/deals/{deal_id}/stage", response_model=DealMoveResponse, summary="Mover Oportunidade de Estágio com Validação de Crédito")
def move_deal(
    deal_id: str, 
    payload: DealMove,
    x_user_id: Optional[str] = Header(None)
):
    try:
        success = service.move_deal_stage(deal_id, payload.stage_id, user_id=x_user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Negócio não encontrado.")
        return {"deal_id": deal_id, "new_stage_id": payload.stage_id, "status": "updated"}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.put("/api/v1/deals/{deal_id}", response_model=DealDetailOut, summary="Edição Inline de Oportunidade (Valor, Título, Prazo)")
def update_deal_inline(
    deal_id: str,
    payload: DealUpdate,
    x_user_id: Optional[str] = Header(None)
):
    try:
        updated = service.update_deal(deal_id, payload.model_dump(exclude_unset=True), user_id=x_user_id)
        return updated
    except KeyError:
        raise HTTPException(status_code=404, detail="Negócio não encontrado.")


@router.get("/api/v1/deals/{deal_id}/timeline", response_model=DealTimelineResponse, summary="Histórico de Auditoria e Linha do Tempo do Negócio")
def get_deal_timeline(deal_id: str):
    return {"deal_id": deal_id, "timeline": service.get_deal_timeline(deal_id)}


@router.post("/api/v1/deals/{deal_id}/approve-credit", response_model=DealApproveCreditResponse, summary="Aprovar Limite de Crédito para Liberação de Consignação")
def approve_deal_credit(
    deal_id: str,
    x_user_id: Optional[str] = Header(None)
):
    success = service.approve_deal_credit_limit(deal_id, approver_name="Controladoria Financeira", user_id=x_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Negócio não encontrado.")
    return {"deal_id": deal_id, "credit_approved": True, "message": "Limite de crédito liberado com sucesso."}



@router.get("/api/v1/deals/export/csv", summary="Exportar Pipeline Comercial Ativo em CSV")
def export_deals_csv(
    pipeline_id: Optional[int] = None,
    account_id: str = "0f14ffff",
    x_user_id: Optional[str] = Header(None)
):
    csv_content = service.export_deals_csv(pipeline_id=pipeline_id, account_id=account_id, user_id=x_user_id)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=pipeline_revnaut_dental.csv"}
    )


@router.get("/api/v1/deals/catalog/products", response_model=List[ProductCatalogItemOut], summary="Listar catálogo técnico odontológico")
def get_catalog_products(account_id: str = "0f14ffff"):
    return catalog_pricing.list_catalog_products(account_id=account_id)


@router.get("/api/v1/deals/catalog/price-tables", response_model=List[PriceTableOut], summary="Listar tabelas de preço odontológicas")
def get_price_tables(account_id: str = "0f14ffff"):
    return catalog_pricing.list_price_tables(account_id=account_id)


@router.post("/api/v1/deals/catalog/calculate-proposal", response_model=CalculateProposalResponse, summary="Calcular proposta e validar alçada de desconto")
def calculate_proposal(payload: CalculateProposalRequest):
    return catalog_pricing.calculate_proposal_pricing(
        deal_id=payload.deal_id,
        table_key=payload.table_key,
        items=[item.model_dump() for item in payload.items],
        requested_discount_pct=payload.requested_discount_pct,
        user_id=payload.user_id,
        user_role=payload.user_role,
        account_id=payload.account_id or "0f14ffff"
    )


@router.post("/api/v1/deals/catalog/approve-discount", response_model=ApproveDiscountResponse, summary="Aprovação de solicitação de desconto por gestor")
def approve_discount(payload: ApproveDiscountRequest):
    try:
        return catalog_pricing.approve_discount_request(
            request_id=payload.request_id,
            approver_user_id=payload.approver_user_id,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


