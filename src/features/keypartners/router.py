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
    CustodySummaryResponse
)
from src.features.keypartners import service

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
