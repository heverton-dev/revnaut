# -*- coding: utf-8 -*-
"""
Vertical Slice: Campaigns Router (FastAPI)
"""

from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from src.features.campaigns.schemas import (
    CampaignCreate,
    CampaignOut,
    CampaignMetricsOut,
    LandingPageCreate,
    LandingPageUpdate,
    LandingPageOut,
    LandingPagePublishResponse,
    LandingPageSubmissionCreate,
    LandingPageSubmissionResponse,
    LandingPageTemplateOut,
    ListmonkBroadcastRequest,
    ListmonkBroadcastResponse,
)
from src.features.campaigns import service
from src.features.campaigns import landing_pages
from src.features.campaigns.listmonk_adapter import ListmonkClient


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


@router.get("/landing-pages/templates", response_model=List[LandingPageTemplateOut], summary="Listar templates verticais de Landing Pages odontológicas")
def get_landing_page_templates():
    return landing_pages.get_prebuilt_templates()


@router.post("/landing-pages", response_model=LandingPageOut, status_code=status.HTTP_201_CREATED, summary="Criar nova Landing Page")
def create_lp(data: LandingPageCreate):
    return landing_pages.create_landing_page(data)


@router.get("/landing-pages", response_model=List[LandingPageOut], summary="Listar Landing Pages do tenant")
def list_lps():
    return landing_pages.list_landing_pages()


@router.get("/landing-pages/{page_id}", response_model=LandingPageOut, summary="Obter detalhes da Landing Page")
def get_lp(page_id: str):
    lp = landing_pages.get_landing_page(page_id)
    if not lp:
        raise HTTPException(status_code=404, detail="Landing page não encontrada.")
    return lp


@router.put("/landing-pages/{page_id}", response_model=LandingPageOut, summary="Atualizar Landing Page (HTML/CSS/GrapesJS)")
def update_lp(page_id: str, data: LandingPageUpdate):
    lp = landing_pages.update_landing_page(page_id, data)
    if not lp:
        raise HTTPException(status_code=404, detail="Landing page não encontrada.")
    return lp


@router.put("/landing-pages/{page_id}/publish", response_model=LandingPagePublishResponse, summary="Compilar e publicar Landing Page no Cloudflare R2")
def publish_lp(page_id: str):
    try:
        return landing_pages.publish_landing_page(page_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/public/lp/{slug}/submit", response_model=LandingPageSubmissionResponse, status_code=status.HTTP_201_CREATED, summary="Submissão pública de formulário de Landing Page")
def submit_lp_lead(slug: str, data: LandingPageSubmissionCreate):
    try:
        return landing_pages.submit_public_lead(slug, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/broadcast-listmonk", response_model=ListmonkBroadcastResponse, summary="Enfileirar disparo em massa de e-mails via Listmonk Engine")
def broadcast_listmonk_endpoint(payload: ListmonkBroadcastRequest):
    client = ListmonkClient()
    result = client.dispatch_broadcast(
        title=payload.title,
        subject=payload.subject,
        body_html=payload.body_html,
        target_uf=payload.target_uf,
        target_specialty=payload.target_specialty,
        list_id=payload.listmonk_list_id or 1,
    )
    return ListmonkBroadcastResponse(**result)


