# -*- coding: utf-8 -*-
"""
Vertical Slice: KeyPartners Router
Endpoints REST OpenAPI 3.1 para Consignação Cirúrgica, Gestão de Kits e Razão de Custódia.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, status
from src.features.keypartners.schemas import (
    PartnerAgreementCreate, PartnerAgreementOut,
    ConsignmentKitCreate, ConsignmentKitOut,
    CustodyDispatchRequest, CustodyDispatchResponse,
    CustodySummaryResponse,
    SurgicalOrderCreate, SurgicalOrderApproveRequest,
    SurgicalPostopReportRequest, SurgicalPostopReportResponse,
    SurgicalOrderOut
)
from src.features.keypartners import service
from src.features.keypartners import surgical_cycle

router = APIRouter(prefix="/api/v1/keypartners", tags=["KeyPartners • Consignação Cirúrgica"])


@router.post("/agreements", response_model=PartnerAgreementOut, status_code=status.HTTP_201_CREATED, summary="Criar novo acordo de consignação e parceria")
def create_agreement(payload: PartnerAgreementCreate):
    return service.create_partner_agreement(
        partner_name=payload.partner_name,
        partner_cro_uf=payload.partner_cro_uf,
        tier=payload.tier,
        credit_limit=payload.credit_limit,
        min_monthly_revenue=payload.min_monthly_revenue,
        max_turnover_days=payload.max_turnover_days,
        account_id=payload.account_id or "0f14ffff"
    )


@router.get("/agreements", response_model=List[PartnerAgreementOut], summary="Listar acordos de parceria do tenant")
def list_agreements(account_id: str = "0f14ffff"):
    return service.list_partner_agreements(account_id=account_id)


@router.post("/kits", response_model=ConsignmentKitOut, status_code=status.HTTP_201_CREATED, summary="Cadastrar novo kit cirúrgico/protético seriadocom QR Code")
def register_kit(payload: ConsignmentKitCreate):
    return service.register_consignment_kit(
        serial_number=payload.serial_number,
        name=payload.name,
        composition_json=payload.composition_json,
        account_id=payload.account_id or "0f14ffff"
    )


@router.post("/agreements/{agreement_id}/dispatch", response_model=CustodyDispatchResponse, summary="Efetuar remessa de custódia com auditoria de limite e validade ANVISA")
def dispatch_custody(agreement_id: str, payload: CustodyDispatchRequest):
    try:
        items_dict = [it.model_dump() for it in payload.items]
        return service.dispatch_consignment_custody(
            agreement_id=agreement_id,
            items=items_dict,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/agreements/{agreement_id}/custody-summary", response_model=CustodySummaryResponse, summary="Obter extrato e saldo de itens em posse da clínica parceira")
def get_custody_summary(agreement_id: str, account_id: str = "0f14ffff"):
    try:
        return service.get_partner_custody_summary(
            agreement_id=agreement_id,
            account_id=account_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/surgical-orders", response_model=SurgicalOrderOut, status_code=status.HTTP_201_CREATED, summary="Solicitar remessa para cirurgia agendada (SOLICITADO_FIELD)")
def create_surgical_order(payload: SurgicalOrderCreate):
    try:
        items_dict = [it.model_dump() for it in payload.items]
        return surgical_cycle.create_surgical_request(
            agreement_id=payload.agreement_id,
            patient_identifier=payload.patient_identifier,
            surgery_date=payload.surgery_date,
            items=items_dict,
            field_consultant_id=payload.field_consultant_id,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/surgical-orders/{order_id}/approve", response_model=SurgicalOrderOut, summary="Analista interno aprova a remessa cirúrgica")
def approve_surgical_order(order_id: str, payload: SurgicalOrderApproveRequest):
    try:
        return surgical_cycle.approve_surgical_request(
            order_id=order_id,
            inside_analyst_id=payload.inside_analyst_id or "usr-inside-01",
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/surgical-orders/{order_id}/dispatch", response_model=SurgicalOrderOut, summary="Efetuar despacho da maleta e termo de custódia")
def dispatch_surgical_order(order_id: str, account_id: str = "0f14ffff"):
    try:
        return surgical_cycle.dispatch_surgical_order(order_id=order_id, account_id=account_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/surgical-orders/{order_id}/postop-report", response_model=SurgicalPostopReportResponse, summary="Reporte pós-operatório e faturamento automático CFOP 5.113")
def report_postop(order_id: str, payload: SurgicalPostopReportRequest):
    try:
        consumed_dict = [it.model_dump() for it in payload.consumed_items]
        return surgical_cycle.report_surgical_postop(
            order_id=order_id,
            consumed_items=consumed_dict,
            seal_photo_r2_key=payload.seal_photo_r2_key,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/surgical-orders/{order_id}", response_model=SurgicalOrderOut, summary="Consultar detalhes da ordem cirúrgica")
def get_surgical_order(order_id: str, account_id: str = "0f14ffff"):
    try:
        return surgical_cycle.get_surgical_order(order_id=order_id, account_id=account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
