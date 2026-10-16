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

