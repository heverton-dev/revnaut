# -*- coding: utf-8 -*-
"""
Schemas Pydantic para Hierarquia Organizacional, RBAC e Presets Odontológicos.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class HierarchyAuditLogOut(BaseModel):
    id: str
    user_name: str
    previous_role: str
    new_role: str
    previous_region: str
    new_region: str
    effective_date: str
    promoted_by: str
    justification: str
    audit_hash: str


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


class RolePermissionsUpdate(BaseModel):
    permissions: List[str] = Field(..., description="Lista de códigos no formato 'recurso:acao'")


class PermissionCatalogItem(BaseModel):
    resource: str
    resource_label: str
    actions: List[Dict[str, str]]


class SalesTargetCreate(BaseModel):
    period: str = Field(..., description="Período da meta, ex: '2026-Q4', '2026-10'")
    business_unit_id: Optional[str] = None
    team_id: Optional[str] = None
    user_id: Optional[str] = None
    target_amount: float = Field(..., gt=0, description="Valor monetário da meta em R$")
    calculation_basis: str = Field(default="manual", description="'manual', 'algoritmica_sugerida', 'cascateada'")
    growth_rate_pct: float = Field(default=15.0, description="Taxa de crescimento (%)")


class SalesTargetOut(BaseModel):
    id: str
    account_id: str
    period: str
    business_unit_id: Optional[str] = None
    team_id: Optional[str] = None
    user_id: Optional[str] = None
    entity_name: Optional[str] = None
    target_amount: float
    achieved_amount: float = 0.0
    achievement_rate_pct: float = 0.0
    calculation_basis: str = "manual"
    growth_rate_pct: float = 15.0
    created_at: str


class AlgorithmicTargetSuggestion(BaseModel):
    entity_type: str
    entity_id: str
    entity_name: str
    period: str
    historical_base: float
    growth_rate_pct: float
    suggested_target: float
    explanation: str


class CommissionRuleCreate(BaseModel):
    role_id: str
    base_percentage: float = Field(..., ge=0.0, le=50.0, description="Percentual base de comissão direta ou override")
    accelerator_threshold_pct: float = Field(default=100.0, ge=50.0, description="% da meta para ativar o acelerador")
    accelerator_percentage: float = Field(default=7.5, ge=0.0, le=50.0, description="Percentual acelerado pós-supermeta")


class CommissionRuleOut(BaseModel):
    id: str
    account_id: str
    role_id: str
    role_name: Optional[str] = None
    base_percentage: float
    accelerator_threshold_pct: float
    accelerator_percentage: float
    is_active: int
    created_at: str


class CommissionPayoutItem(BaseModel):
    deal_id: str
    deal_title: str
    deal_value: float
    commission_rate_pct: float
    commission_amount: float
    payout_type: str


class CommissionStatementOut(BaseModel):
    user_id: str
    user_name: str
    role_id: str
    role_name: str
    period: str
    target_amount: float
    achieved_amount: float
    achievement_rate_pct: float
    is_accelerated: bool
    total_commission: float
    items: List[CommissionPayoutItem]


class PresetApplyResponse(BaseModel):
    success: bool
    preset: str
    business_units_count: int
    teams_count: int
    roles_count: int


class PermissionCatalogResponse(BaseModel):
    resources: List[Dict[str, Any]]


class RolePermissionsResponse(BaseModel):
    model_config = {"extra": "allow"}
    role_id: Optional[str] = None
    role_name: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    success: bool = True



