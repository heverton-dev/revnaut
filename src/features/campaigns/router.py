# -*- coding: utf-8 -*-
"""
Vertical Slice: Campaigns Router (FastAPI)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
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
    ReferralLinkGenerateRequest,
    ReferralLinkResponse,
    ReferralRegisterRequest,
    ReferralRegisterResponse,
    ReferralQualifyRequest,
    ReferralQualifyResponse,
    ReferralDashboardResponse,
)
from src.features.campaigns import service
from src.features.campaigns import landing_pages
from src.features.campaigns import referral_mgm
from src.features.campaigns.listmonk_adapter import ListmonkClient, process_listmonk_webhook_event
from src.features.market_intel import campaign_dispatcher
from src.features.market_intel.rbac import MarketIntelPrincipal, get_market_intel_principal
from src.features.market_intel.router import raise_http_for
from src.features.market_intel.schemas import CampaignDispatchResult


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
def publish_lp(page_id: str, block_on_cfo_violation: bool = False):
    try:
        return landing_pages.publish_landing_page(page_id, block_on_cfo_violation=block_on_cfo_violation)
    except ValueError as e:
        msg = str(e)
        if "bloqueada por violação" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=404, detail=msg)


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


@router.post("/webhooks/listmonk", response_model=dict, summary="Webhook Listmonk para eventos de bounce, open e click")
def listmonk_campaign_webhook(payload: dict):
    try:
        return process_listmonk_webhook_event(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/referral/generate-link", response_model=ReferralLinkResponse, summary="Gerar link unico de indicacao B2B para o parceiro")
def generate_mgm_link(payload: ReferralLinkGenerateRequest):
    try:
        return referral_mgm.generate_referral_link(
            referrer_id=payload.referrer_id,
            referrer_name=payload.referrer_name,
            referrer_cro_uf=payload.referrer_cro_uf,
            account_id=payload.account_id or "0f14ffff"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/referral/register", response_model=ReferralRegisterResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar colega indicado via link MGM com score acelerado")
def register_mgm_lead(payload: ReferralRegisterRequest):
    try:
        return referral_mgm.register_referral_lead(
            referral_code=payload.referral_code,
            referred_name=payload.referred_name,
            referred_cro_uf=payload.referred_cro_uf,
            referred_phone=payload.referred_phone,
            referred_email=payload.referred_email,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/referral/qualify", response_model=ReferralQualifyResponse, summary="Qualificar indicacao e bonificar ambos no primeiro deal faturado")
def qualify_mgm_deal(payload: ReferralQualifyRequest):
    try:
        return referral_mgm.qualify_referral_deal_won(
            deal_id=payload.deal_id,
            referred_cro_uf=payload.referred_cro_uf,
            account_id=payload.account_id or "0f14ffff"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/referral/dashboard/{referrer_id}", response_model=ReferralDashboardResponse, summary="Obter metricas e lista de colegas indicados pelo parceiro")
def get_mgm_dashboard(referrer_id: str, account_id: str = "0f14ffff"):
    try:
        return referral_mgm.get_referral_dashboard(referrer_id=referrer_id, account_id=account_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





# TICKET-MKTINTEL-08: Aprovação e disparo de campanha tática com trava anti-spam de 15 dias (RBAC Seção 5)
@router.post(
    "/{campaign_id}/dispatch",
    response_model=CampaignDispatchResult,
    summary="Aprovar e disparar campanha tática (somente Diretoria/Gerente Regional) com trava de 15 dias",
)
def dispatch_targeted_campaign(campaign_id: str, principal: MarketIntelPrincipal = Depends(get_market_intel_principal)):
    try:
        return campaign_dispatcher.dispatch_campaign(principal, campaign_id)
    except Exception as exc:
        raise_http_for(exc)
