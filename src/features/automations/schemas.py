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


class AutomationFlowOut(BaseModel):
    id: str
    account_id: str
    name: str
    category: str
    trigger_event: str
    action_description: str
    is_active: bool
    execution_count: int
    last_run_at: Optional[str] = None


class AutomationFlowToggleResponse(BaseModel):
    id: str
    is_active: bool
    message: str


class AutomationTestResponse(BaseModel):
    flow_id: str
    status: str
    summary: str
    execution_count: int
    executed_at: str


class AutomationLogOut(BaseModel):
    id: int
    flow_id: str
    result_summary: str
    status: str
    executed_at: str
