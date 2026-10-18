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


class PostOpCareStartRequest(BaseModel):
    patient_name: str = Field(..., min_length=2, description="Nome do paciente operado")
    patient_phone: str = Field(..., description="Telefone WhatsApp do paciente (+55...)")
    surgeon_name: str = Field(..., min_length=2, description="Nome do cirurgião-dentista")
    surgeon_phone: str = Field(..., description="WhatsApp do cirurgião para alertas de emergência (+55...)")
    procedure_name: str = Field(..., description="Procedimento cirúrgico realizado (ex: Implante Unitário, Protocolo)")
    surgery_date: str = Field(..., description="Data da realização da cirurgia (YYYY-MM-DD)")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class PostOpMilestoneItem(BaseModel):
    model_config = {"extra": "allow"}
    code: str
    target_date: str
    title: str
    status: str = "SCHEDULED"
    template_message: str
    feedback_received: Optional[str] = None
    evaluated_alert: Optional[bool] = None


class PostOpCareScheduleOut(BaseModel):
    model_config = {"extra": "allow"}
    id: str
    account_id: str
    patient_name: str
    patient_phone: str
    surgeon_name: str
    surgeon_phone: str
    procedure_name: str
    surgery_date: str
    status: str
    milestones: list[PostOpMilestoneItem] = Field(default_factory=list)
    alert_ticket_id: Optional[str] = None
    last_interaction_notes: Optional[str] = None
    created_at: str


class PostOpFeedbackRequest(BaseModel):
    feedback_text: str = Field(..., description="Texto ou transcrição do áudio enviado pelo paciente")
    milestone_code: str = Field(default="24h", description="Marco da régua: 24h | 48h | 72h | 7d")
    account_id: Optional[str] = Field(default="0f14ffff", description="ID da conta tenant")


class PostOpFeedbackResponse(BaseModel):
    model_config = {"extra": "allow"}
    schedule_id: str
    milestone_code: str
    is_critical: bool
    detected_triggers: list[str] = Field(default_factory=list)
    alert_ticket_id: Optional[str] = None
    patient_response_message: str
    surgeon_alert_sent: bool
    updated_status: str

