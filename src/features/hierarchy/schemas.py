# -*- coding: utf-8 -*-
"""
Schemas Pydantic para Hierarquia Organizacional, RBAC e Presets Odontológicos.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DataScopeEnum(str, Enum):
    SELF = "self"                     # Vê apenas registros de sua autoria (owner_id == user.id)
    TEAM = "team"                     # Vê registros do time direto
    SUBTREE = "subtree"               # Vê registros do próprio time e descendentes recursivos
    BUSINESS_UNIT = "business_unit"   # Vê registros de toda a Divisão/BU
    TENANT_GLOBAL = "tenant_global"   # Vê todos os registros da empresa (Admin/C-Level)


class BusinessUnitCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    code: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None


class BusinessUnitOut(BaseModel):
    id: str
    account_id: str
    name: str
    code: str
    description: Optional[str] = None
    created_at: str


class TeamCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    business_unit_id: str
    parent_id: Optional[str] = None
    leader_id: Optional[str] = None


class TeamUpdateParent(BaseModel):
    parent_id: Optional[str] = None


class TeamOut(BaseModel):
    id: str
    account_id: str
    business_unit_id: str
    parent_id: Optional[str] = None
    name: str
    leader_id: Optional[str] = None
    created_at: str


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    default_data_scope: DataScopeEnum = DataScopeEnum.SELF
    is_admin: int = 0
    permissions: List[str] = Field(default_factory=list)


class RoleOut(BaseModel):
    id: str
    account_id: str
    name: str
    description: Optional[str] = None
    default_data_scope: str
    is_admin: int
    permissions: List[str] = Field(default_factory=list)
    created_at: str


class PresetApplyRequest(BaseModel):
    preset_name: str = Field(
        ...,
        description="Preset desejado: 'fabrica_enxuta', 'nacional_expansao', 'multidivisao_produtos', 'multinacional_enterprise'"
    )


class UserContext(BaseModel):
    user_id: str
    account_id: str
    role_id: str
    team_id: Optional[str] = None
    business_unit_id: Optional[str] = None
    data_scope: DataScopeEnum
    permissions: List[str] = Field(default_factory=list)
    is_superadmin: bool = False

