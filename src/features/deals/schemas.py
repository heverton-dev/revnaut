# -*- coding: utf-8 -*-
"""
Vertical Slice: Deals & Pipeline
Schemas tipados OpenAPI 3.1
"""

from pydantic import BaseModel, Field


class DealCreate(BaseModel):
    title: str = Field(..., description="Título da oportunidade comercial")
    value: float = Field(..., gt=0, description="Valor do negócio em Reais")
    company: str = Field(..., description="Nome da empresa")
    contact_name: str = Field(..., description="Nome do contato decisor")
    pipeline_id: int | None = Field(default=None, description="ID do funil/pipeline de vendas")
    stage_id: int = Field(default=101, description="ID do estágio inicial no funil")
    priority: str = Field(default="media", pattern="^(baixa|media|alta)$")


class DealMove(BaseModel):
    stage_id: int = Field(..., description="Novo ID de estágio no funil")


class DealUpdate(BaseModel):
    title: str | None = Field(default=None, description="Título da oportunidade comercial")
    value: float | None = Field(default=None, gt=0, description="Novo valor do negócio em Reais")
    priority: str | None = Field(default=None, pattern="^(baixa|media|alta)$")
    expected_close_date: str | None = Field(default=None, description="Data estimada de fechamento (AAAA-MM-DD)")
    comment: str | None = Field(default=None, description="Comentário para auditoria")


class PipelineItemOut(BaseModel):
    id: int
    name: str


class PipelineMetricsOut(BaseModel):
    mrr: float
    pipelineTotal: float
    closedWonMRR: float = 0.0
    totalDeals: int = 0
    conversionRate: float = 0.0


class DealsListResponse(BaseModel):
    stages: list[dict]
    deals: list[dict]


class DealCreateResponse(BaseModel):
    model_config = {"extra": "allow"}
    status: str
    id: str
    title: str | None = None
    value: float | None = None
    company: str | None = None
    contact_name: str | None = None
    pipeline_id: int | None = None
    stage_id: int | None = None
    priority: str | None = None
    owner_id: str | None = None
    team_id: str | None = None



class DealMoveResponse(BaseModel):
    status: str
    deal_id: str
    new_stage_id: int


class DealDetailOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str | None = None
    value: float | None = None
    priority: str | None = None
    expected_close_date: str | None = None


class DealTimelineResponse(BaseModel):
    deal_id: str
    timeline: list[dict]


class DealApproveCreditResponse(BaseModel):
    deal_id: str
    credit_approved: bool = True
    message: str
    credit_limit: float | None = None



