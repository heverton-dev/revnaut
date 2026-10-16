# -*- coding: utf-8 -*-
"""
Vertical Slice: Campaigns Router (FastAPI)
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from src.features.campaigns.schemas import CampaignCreate, CampaignOut, CampaignMetricsOut
from src.features.campaigns import service

router = APIRouter(prefix="/api/v1/campaigns", tags=["Campanhas & Mídia"])


@router.get("", response_model=List[CampaignOut], summary="Listar campanhas de marketing com ROAS e CAC")
def get_campaigns(status: Optional[str] = None):
    return service.list_campaigns(status=status)


@router.get("/metrics", response_model=CampaignMetricsOut, summary="Obter métricas agregadas de campanhas")
def get_metrics():
    return service.get_campaign_metrics()


@router.post("", response_model=CampaignOut, status_code=status.HTTP_201_CREATED, summary="Criar nova campanha de mídia")
def create_campaign(data: CampaignCreate):
    return service.create_campaign(data)
