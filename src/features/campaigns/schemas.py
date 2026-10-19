# -*- coding: utf-8 -*-
"""
Vertical Slice: Campaigns Schemas (RevOps Marketing & Atribuição de Mídia)
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=2, description="Nome identificador da campanha")
    channel: str = Field(default="Google Ads Search (GCLID)", description="Canal ou rede de tráfego")
    utm_source: str = Field(default="google", min_length=1)
    utm_medium: str = Field(default="cpc", min_length=1)
    utm_campaign: str = Field(default="revops-camp", min_length=1)
    budget: float = Field(default=0.0, ge=0.0, description="Orçamento alocado em BRL")
    spend: float = Field(default=0.0, ge=0.0, description="Valor investido/consumido em BRL")
    revenue: float = Field(default=0.0, ge=0.0, description="Receita atribuída diretamente")
    leads_count: int = Field(default=0, ge=0)
    deals_count: int = Field(default=0, ge=0)
    status: str = Field(default="ativa", pattern="^(ativa|pausada|concluida)$")


class CampaignOut(BaseModel):
    id: str
    account_id: str
    name: str
    channel: str
    utm_source: str
    utm_medium: str
    utm_campaign: str
    budget: float
    spend: float
    revenue: float
    leads_count: int
    deals_count: int
    roas: float
    cac: float
    conversion_rate: float
    status: str
    created_at: str


class CampaignMetricsOut(BaseModel):
    total_budget: float
    total_spend: float
    total_revenue: float
    avg_roas: float
    avg_cac: float
    total_leads: int
    total_deals: int
    active_campaigns_count: int


class LandingPageTemplateOut(BaseModel):
    template_type: str
    name: str
    description: str
    category: str
    html: str
    css: str


class LandingPageCreate(BaseModel):
    title: str = Field(..., min_length=2)
    slug: str = Field(..., min_length=2)
    template_type: Optional[str] = "imersao_fluxo_digital"
    gjs_html: Optional[str] = None
    gjs_css: Optional[str] = None
    gjs_components_json: Optional[str] = None
    cfo_responsible_cro: Optional[str] = None
    cfo_responsible_name: Optional[str] = None


class LandingPageUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    template_type: Optional[str] = None
    gjs_html: Optional[str] = None
    gjs_css: Optional[str] = None
    gjs_components_json: Optional[str] = None
    cfo_responsible_cro: Optional[str] = None
    cfo_responsible_name: Optional[str] = None


class LandingPageOut(BaseModel):
    id: str
    tenant_id: str
    slug: str
    title: str
    template_type: str
    gjs_html: Optional[str] = None
    gjs_css: Optional[str] = None
    gjs_components_json: Optional[str] = None
    cfo_responsible_cro: Optional[str] = None
    cfo_responsible_name: Optional[str] = None
    published_r2_url: Optional[str] = None
    is_published: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class LandingPagePublishResponse(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    slug: str
    is_published: bool = True
    published_r2_url: str
    published_url: Optional[str] = None
    r2_url: Optional[str] = None
    cfo_compliance_status: str
    message: str


class LandingPageSubmissionCreate(BaseModel):
    name: str = Field(..., min_length=2)
    email: str = Field(..., min_length=3)
    phone: Optional[str] = None
    cro: Optional[str] = None
    cro_uf: Optional[str] = None
    specialty: Optional[str] = "Implantodontia"
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None


class LandingPageSubmissionResponse(BaseModel):
    success: bool = True
    lead_id: int
    landing_page_slug: str
    cro_verified: bool = False
    message: str


class ListmonkBroadcastRequest(BaseModel):
    title: str = Field(..., min_length=2)
    subject: str = Field(..., min_length=2)
    body_html: str = Field(..., min_length=5)
    target_uf: Optional[str] = None
    target_specialty: Optional[str] = None
    listmonk_list_id: Optional[int] = 1


class ListmonkBroadcastResponse(BaseModel):
    success: bool = True
    status: str
    queued_count: int
    listmonk_campaign_id: Optional[int] = None
    message: str


class ReferralLinkGenerateRequest(BaseModel):
    referrer_id: str = Field(..., description="ID do cirurgiao promotor ou parceiro")
    referrer_name: str = Field(..., description="Nome do parceiro que indica")
    referrer_cro_uf: str = Field(..., description="CRO/UF do indicador (ex: CRO-SP 11111)")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class ReferralLinkResponse(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    referrer_id: str
    referrer_name: str
    referrer_cro_uf: str
    referral_code: str
    referral_url: str
    created_at: str


class ReferralRegisterRequest(BaseModel):
    referral_code: str = Field(..., description="Codigo do link de indicacao MGM")
    referred_name: str = Field(..., description="Nome do cirurgiao indicado")
    referred_cro_uf: str = Field(..., description="CRO/UF do indicado")
    referred_phone: Optional[str] = Field(default=None, description="Telefone WhatsApp do indicado")
    referred_email: Optional[str] = Field(default=None, description="Email do indicado")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class ReferralRegisterResponse(BaseModel):
    model_config = {"extra": "allow"}
    conversion_id: str
    referral_code: str
    referrer_id: str
    referrer_name: str
    referred_contact_id: str
    referred_name: str
    referred_cro_uf: str
    lead_score_boost: int
    status: str
    message: str


class ReferralQualifyRequest(BaseModel):
    deal_id: str = Field(..., description="ID do primeiro deal fechado pelo indicado")
    referred_cro_uf: Optional[str] = Field(default=None, description="CRO/UF do indicado se conhecido")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID do tenant")


class ReferralQualifyResponse(BaseModel):
    model_config = {"extra": "allow"}
    status: str
    conversion_id: str
    deal_id: Optional[str] = None
    referrer_id: Optional[str] = None
    referred_contact_id: Optional[str] = None
    referrer_bonus_amount: float
    referred_bonus_amount: float
    qualified_at: Optional[str] = None
    message: str


class ReferralDashboardResponse(BaseModel):
    model_config = {"extra": "allow"}
    referrer_id: str
    referral_code: Optional[str] = None
    referral_url: Optional[str] = None
    total_referrals: int
    qualified_referrals: int
    total_bonus_earned: float
    conversions: List[Dict[str, Any]] = Field(default_factory=list)



