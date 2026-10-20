# -*- coding: utf-8 -*-
"""Vertical Slice: Market Intel Router (FastAPI) - /api/v1/market-intel (TICKET-MKTINTEL-06/07/08)."""

from __future__ import annotations

from typing import List, NoReturn, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.features.market_intel import campaign_dispatcher, service
from src.features.market_intel.campaign_dispatcher import CampaignStateError, CampaignValidationError
from src.features.market_intel.opportunity_matcher import match_and_create_opportunity
from src.features.market_intel.rbac import (
    MarketIntelForbidden,
    MarketIntelPrincipal,
    VALID_REGIONS,
    get_market_intel_principal,
)
from src.features.market_intel.schemas import (
    BuTarget,
    CampaignDispatchResult,
    CampaignDraftRequest,
    MarketOpportunityOut,
    MarketSignalPage,
    OpportunityMatchRequest,
    OpportunityMatchResponse,
    OpportunityStatus,
    SourceType,
    TargetedCampaignOut,
)

router = APIRouter(prefix="/api/v1/market-intel", tags=["Inteligência de Mercado & Radar Tático"])


def raise_http_for(exc: Exception) -> NoReturn:
    """Mapeamento único de exceções de domínio para status HTTP."""
    if isinstance(exc, MarketIntelForbidden):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, CampaignStateError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, CampaignValidationError):
        raise HTTPException(
            status_code=422,
            detail={"message": str(exc), "violations": exc.violations},
        )
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=422, detail=str(exc))
    raise exc


@router.get("/signals", response_model=MarketSignalPage, summary="Listar sinais de mercado no escopo territorial do perfil")
def get_signals(
    scope: Optional[str] = Query(None, description="GLOBAL, BR-SP, BR-PR, BR-PE, US-FL, LATAM"),
    specialty: Optional[str] = Query(None),
    source_type: Optional[SourceType] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    principal: MarketIntelPrincipal = Depends(get_market_intel_principal),
):
    try:
        return service.list_signals(principal, scope=scope, specialty=specialty, source_type=source_type, limit=limit, offset=offset)
    except Exception as exc:
        raise_http_for(exc)


@router.get("/opportunities", response_model=List[MarketOpportunityOut], summary="Cards táticos de oportunidades cruzadas por BU e praça")
def get_opportunities(
    region_code: Optional[str] = Query(None),
    bu_target: Optional[BuTarget] = Query(None),
    status_filter: Optional[OpportunityStatus] = Query(None, alias="status"),
    principal: MarketIntelPrincipal = Depends(get_market_intel_principal),
):
    try:
        return service.list_opportunities(principal, region_code=region_code, bu_target=bu_target, status=status_filter)
    except Exception as exc:
        raise_http_for(exc)


@router.post("/opportunities/match", response_model=OpportunityMatchResponse, summary="Cruzar sinal ou snapshot de concorrente com o catálogo")
def post_match_opportunity(
    payload: OpportunityMatchRequest,
    principal: MarketIntelPrincipal = Depends(get_market_intel_principal),
):
    try:
        if not principal.can_generate_draft:
            raise MarketIntelForbidden("Perfil sem permissão para gerar oportunidades (Consultor Externo / Campo).")
        region = payload.region_code.upper() if payload.region_code else None
        if region is not None:
            if region not in VALID_REGIONS:
                raise ValueError(f"Região inválida: '{region}'.")
            if not principal.can_see_scope(region):
                raise MarketIntelForbidden(f"Praça '{region}' fora do escopo territorial do perfil.")
        return match_and_create_opportunity(
            account_id=principal.account_id,
            signal_id=payload.signal_id,
            competitor_snapshot_id=payload.competitor_snapshot_id,
            region_code=region,
        )
    except Exception as exc:
        raise_http_for(exc)


@router.post(
    "/campaigns/generate-draft",
    response_model=TargetedCampaignOut,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar minuta determinística de campanha tática (validação ética CFO 196/2019)",
)
def post_generate_draft(
    payload: CampaignDraftRequest,
    principal: MarketIntelPrincipal = Depends(get_market_intel_principal),
):
    try:
        return campaign_dispatcher.generate_campaign_draft(
            principal,
            opportunity_id=payload.opportunity_id,
            target_region=payload.target_region,
            channel=payload.channel,
            specialty=payload.specialty,
            purchase_window=payload.purchase_window,
            message_template=payload.message_template,
        )
    except Exception as exc:
        raise_http_for(exc)


@router.get("/campaigns", response_model=List[TargetedCampaignOut], summary="Listar campanhas táticas com metadados da oportunidade")
def get_campaigns(
    dispatch_status: Optional[str] = Query(None, description="DRAFT, SCHEDULED ou EXECUTED"),
    principal: MarketIntelPrincipal = Depends(get_market_intel_principal),
):
    try:
        return service.list_campaigns(principal, dispatch_status=dispatch_status)
    except Exception as exc:
        raise_http_for(exc)


@router.post(
    "/campaigns/{campaign_id}/dispatch",
    response_model=CampaignDispatchResult,
    summary="Aprovar e disparar campanha com trava anti-spam determinística de 15 dias",
)
def post_dispatch_campaign(campaign_id: str, principal: MarketIntelPrincipal = Depends(get_market_intel_principal)):
    try:
        return campaign_dispatcher.dispatch_campaign(principal, campaign_id)
    except Exception as exc:
        raise_http_for(exc)
