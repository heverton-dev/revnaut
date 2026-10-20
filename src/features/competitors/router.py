# -*- coding: utf-8 -*-
"""Vertical Slice: Competitor Radar Router (FastAPI) - /api/v1/competitors (TICKET-MKTINTEL-06)."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.features.competitors import service
from src.features.competitors.service import CompetitorConflict
from src.features.market_intel.rbac import MarketIntelPrincipal, get_market_intel_principal
from src.features.market_intel.router import raise_http_for
from src.features.market_intel.schemas import (
    CompetitorCreate,
    CompetitorListResponse,
    CompetitorOut,
    CompetitorSnapshotOut,
    TacticalInsightsResponse,
)

router = APIRouter(prefix="/api/v1/competitors", tags=["Radar de Concorrência"])


@router.get("", response_model=CompetitorListResponse, summary="Listar concorrentes monitorados e política da fila passiva")
def get_competitors(principal: MarketIntelPrincipal = Depends(get_market_intel_principal)):
    return service.list_competitors(principal)


@router.post(
    "",
    response_model=CompetitorOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar concorrente na fila passiva noturna (somente Diretoria/Admin, sem raspagem síncrona)",
)
def post_competitor(payload: CompetitorCreate, principal: MarketIntelPrincipal = Depends(get_market_intel_principal)):
    try:
        return service.create_competitor(
            principal,
            name=payload.name,
            domain=payload.domain,
            social_handles=payload.social_handles,
            crawl_frequency_hours=payload.crawl_frequency_hours,
        )
    except CompetitorConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except Exception as exc:
        raise_http_for(exc)


@router.get("/tactical-insights", response_model=TacticalInsightsResponse, summary="Relatório comparativo de contra-ataque B2B")
def get_tactical_insights(principal: MarketIntelPrincipal = Depends(get_market_intel_principal)):
    return service.build_tactical_insights(principal)


@router.get("/{competitor_id}/snapshots", response_model=List[CompetitorSnapshotOut], summary="Timeline de snapshots do concorrente")
def get_competitor_snapshots(competitor_id: str, principal: MarketIntelPrincipal = Depends(get_market_intel_principal)):
    try:
        return service.list_snapshots(principal, competitor_id)
    except Exception as exc:
        raise_http_for(exc)
