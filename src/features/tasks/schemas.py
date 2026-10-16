# -*- coding: utf-8 -*-
"""
Vertical Slice: Tasks Schemas
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=2)
    due_date: str = Field(default="Hoje")
    assignee: str = Field(default="Thiago Hortolan")
    priority: str = Field(default="media", pattern="^(alta|media|baixa)$")


class TaskToggle(BaseModel):
    completed: bool


class TaskOut(BaseModel):
    id: str
    account_id: str
    title: str
    due_date: str
    assignee: str
    priority: str
    completed: int
    created_at: str
