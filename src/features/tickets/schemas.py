# -*- coding: utf-8 -*-
"""
Vertical Slice: Tickets Schemas
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=2)
    customer_name: str = Field(..., min_length=2)
    priority: str = Field(default="media", pattern="^(alta|media|baixa)$")
    category: str = Field(default="Suporte Técnico")
    status: str = Field(default="aberto", pattern="^(aberto|em_andamento|resolvido)$")


class TicketStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(aberto|em_andamento|resolvido)$")


class TicketOut(BaseModel):
    id: str
    account_id: str
    title: str
    customer_name: str
    priority: str
    status: str
    category: str
    created_at: str
