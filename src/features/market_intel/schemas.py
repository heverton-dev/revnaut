# -*- coding: utf-8 -*-
"""Contratos Pydantic V2 da Inteligência de Mercado, Radar de Concorrência e Campanhas Táticas."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

SourceType = Literal["scientific_journal", "regulatory_anvisa", "congress_ciosp", "news"]
BuTarget = Literal["Implantodontia", "Prótese Digital", "Biomateriais"]
OpportunityType = Literal["PRICE_COUNTER_ATTACK", "CLINICAL_UPGRADE", "EVENT_SURGE"]
OpportunityStatus = Literal["PENDING", "CAMPAIGN_TRIGGERED", "DISMISSED"]
CampaignChannel = Literal["WHATSAPP", "EMAIL"]
DispatchStatus = Literal["DRAFT", "SCHEDULED", "EXECUTED"]
PageType = Literal["pricing_table", "catalog", "blog_post", "social_ad"]


class StructuredPayload(BaseModel):
    topics: List[str] = Field(default_factory=list)
    detected_trends: List[str] = Field(default_factory=list)
    target_specialties: List[str] = Field(default_factory=list)


class MarketSignalOut(BaseModel):
    id: str
    account_id: str
    title: str
    source_url: str
    source_type: SourceType
    raw_content: str
    structured_payload: StructuredPayload
    geographic_scope: str
    created_at: str


class MarketSignalPage(BaseModel):
    items: List[MarketSignalOut]
    total: int
    limit: int
    offset: int
    visible_scopes: List[str]


class RecommendedProduct(BaseModel):
    sku: str
    name: str
    category: str
    base_price: float


class MarketOpportunityOut(BaseModel):
    id: str
    account_id: str
    signal_id: Optional[str] = None
    competitor_snapshot_id: Optional[str] = None
    source_title: Optional[str] = None
    bu_target: BuTarget
    recommended_product_ids: List[str]
    recommended_products: List[RecommendedProduct] = Field(default_factory=list)
    opportunity_type: OpportunityType
    suggested_action: str
    region_code: str
    status: OpportunityStatus
    created_at: str


class OpportunityMatchRequest(BaseModel):
    signal_id: Optional[str] = None
    competitor_snapshot_id: Optional[str] = None
    region_code: Optional[str] = None

    @model_validator(mode="after")
    def _exactly_one_source(self) -> "OpportunityMatchRequest":
        if bool(self.signal_id) == bool(self.competitor_snapshot_id):
            raise ValueError("Informe exatamente um entre signal_id e competitor_snapshot_id.")
        return self


class OpportunityMatchResponse(BaseModel):
    id: str
    bu_target: BuTarget
    recommended_product_ids: List[str]
    opportunity_type: OpportunityType
    suggested_action: str
    region_code: str
    status: OpportunityStatus
    created: bool


class AudienceFilter(BaseModel):
    region: str
    specialty: Optional[str] = None
    purchase_window: int = 90


class CampaignDraftRequest(BaseModel):
    opportunity_id: str
    target_region: Optional[str] = None
    channel: CampaignChannel = "WHATSAPP"
    specialty: Optional[str] = None
    purchase_window: int = Field(90, ge=1, le=365)
    message_template: Optional[str] = Field(None, max_length=4000)


class ComplianceReport(BaseModel):
    is_compliant: bool
    violations: List[str]
    warnings: List[str]
    has_responsible_cro: bool
    detected_cro: Optional[str] = None


class TargetedCampaignOut(BaseModel):
    id: str
    account_id: str
    opportunity_id: str
    target_audience_filter: AudienceFilter
    message_template: str
    channel: CampaignChannel
    dispatch_status: DispatchStatus
    scheduled_for: Optional[str] = None
    sent_count: int
    skipped_cooldown_15d_count: int
    created_by_user_id: Optional[str] = None
    approved_by_user_id: Optional[str] = None
    executed_at: Optional[str] = None
    created_at: str
    opportunity_type: Optional[OpportunityType] = None
    bu_target: Optional[BuTarget] = None
    opportunity_status: Optional[OpportunityStatus] = None
    compliance: Optional[ComplianceReport] = None


class CampaignDispatchResult(BaseModel):
    campaign_id: str
    dispatch_status: DispatchStatus
    eligible_count: int
    sent_count: int
    skipped_cooldown_15d_count: int
    failed_count: int
    approved_by_user_id: Optional[str] = None
    executed_at: str


class CompetitorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    domain: str = Field(..., min_length=4, max_length=255)
    social_handles: Dict[str, str] = Field(default_factory=dict)
    crawl_frequency_hours: int = Field(72, ge=24, le=720)


class PassiveQueuePolicy(BaseModel):
    dead_window_utc: str
    jitter_seconds_min: float
    jitter_seconds_max: float
    dedup: str
    ad_hoc_scraping_allowed: bool


class CompetitorOut(BaseModel):
    id: str
    account_id: str
    name: str
    domain: str
    social_handles: Dict[str, Any]
    active: bool
    crawl_frequency_hours: int
    last_scraped_at: Optional[str] = None
    next_scheduled_crawl_at: str
    snapshots_count: int
    created_at: str


class CompetitorListResponse(BaseModel):
    items: List[CompetitorOut]
    passive_queue: PassiveQueuePolicy
    can_manage_competitors: bool


class DetectedOffer(BaseModel):
    product: str
    price: float
    discount: str


class CompetitorSnapshotOut(BaseModel):
    id: str
    competitor_id: str
    page_type: PageType
    extracted_title: str
    content_hash: str
    detected_offers: List[DetectedOffer]
    tactical_summary: str
    created_at: str


class TacticalInsight(BaseModel):
    competitor_id: str
    competitor_name: str
    snapshot_id: str
    competitor_product: str
    competitor_price: float
    competitor_discount: str
    matched_sku: Optional[str] = None
    matched_product_name: Optional[str] = None
    our_base_price: Optional[float] = None
    price_gap_pct: Optional[float] = None
    counter_attack: str


class TacticalInsightsResponse(BaseModel):
    generated_at: str
    value_pillars: List[str]
    insights: List[TacticalInsight]
