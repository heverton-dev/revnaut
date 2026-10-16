# -*- coding: utf-8 -*-
"""
Vertical Slice: Campaigns Schemas (RevOps Marketing & Atribuição de Mídia)
"""

from __future__ import annotations
from typing import Optional
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
