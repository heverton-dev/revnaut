# -*- coding: utf-8 -*-
"""
Schemas OpenAPI 3.1 & Pydantic para Automações e Gatilhos de Receita.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class HotLeadEvaluationResponse(BaseModel):
    is_hot_lead: bool
    contact_id: int
    closer_id: Optional[str] = None
    closer_name: Optional[str] = None
    team_id: Optional[str] = None
    deal_id: Optional[str] = None
    task_id: Optional[str] = None
    sla_minutes: int = 15
    status: str
    message: str
