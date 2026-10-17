# -*- coding: utf-8 -*-
"""
Router FastAPI para Gestão de Hierarquia Organizacional, RBAC e Presets.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, status

from src.features.hierarchy.schemas import (
    BusinessUnitCreate, BusinessUnitOut, TeamCreate, TeamUpdateParent,
    TeamOut, RoleCreate, RoleOut, PresetApplyRequest, RolePermissionsUpdate,
    SalesTargetCreate, SalesTargetOut, AlgorithmicTargetSuggestion,
    CommissionRuleCreate, CommissionRuleOut, CommissionStatementOut,
    PresetApplyResponse, PermissionCatalogItem, RolePermissionsResponse
)
from src.features.hierarchy import service

router = APIRouter(prefix="/api/v1/hierarchy", tags=["Hierarquia Organizacional & RBAC"])


@router.post("/presets/apply", response_model=PresetApplyResponse, summary="Aplica Preset Organizacional Odontológico")
def apply_preset(payload: PresetApplyRequest, account_id: str = "0f14ffff"):
    try:
        return service.apply_hierarchy_preset(account_id, payload.preset_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



@router.get("/business-units", response_model=List[BusinessUnitOut], summary="Lista Business Units")
def list_business_units(account_id: str = "0f14ffff"):
    return service.list_business_units(account_id)


@router.post("/business-units", response_model=BusinessUnitOut, status_code=status.HTTP_201_CREATED, summary="Cria Business Unit")
def create_business_unit(payload: BusinessUnitCreate, account_id: str = "0f14ffff"):
    return service.create_business_unit(payload, account_id)


@router.get("/teams", response_model=List[TeamOut], summary="Lista Equipes Organizacionais")
def list_teams(account_id: str = "0f14ffff"):
    return service.list_teams(account_id)


@router.get("/tree", response_model=List[TeamOut], summary="Árvore Hierárquica de Equipes (Alias)")
def get_hierarchy_tree(account_id: str = "0f14ffff"):
    return service.list_teams(account_id)


@router.post("/teams", response_model=TeamOut, status_code=status.HTTP_201_CREATED, summary="Cria Equipe")
def create_team(payload: TeamCreate, account_id: str = "0f14ffff"):
    try:
        return service.create_team(payload, account_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.put("/teams/{team_id}/parent", response_model=TeamOut, summary="Atualiza Pai da Equipe com Validação Anti-Loop")
def update_team_parent(team_id: str, payload: TeamUpdateParent, account_id: str = "0f14ffff"):
    try:
        return service.update_team_parent(team_id, payload.parent_id, account_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get("/roles", response_model=List[RoleOut], summary="Lista Cargos e Perfis de Acesso")
def list_roles(account_id: str = "0f14ffff"):
    return service.list_roles(account_id)


@router.post("/roles", response_model=RoleOut, status_code=status.HTTP_201_CREATED, summary="Cria Perfil de Acesso Customizado")
def create_role(payload: RoleCreate, account_id: str = "0f14ffff"):
    return service.create_role(payload, account_id)


@router.get("/catalog", response_model=List[PermissionCatalogItem], summary="Catálogo de Permissões Granulares por Recurso")
def get_permission_catalog():
    return service.get_permission_catalog()


@router.get("/roles/{role_id}/permissions", response_model=RolePermissionsResponse, summary="Obter Permissões Ativas de uma Função")
def get_role_permissions(role_id: str, account_id: str = "0f14ffff"):
    role = service.get_role_permissions(role_id, account_id)
    if not role:
        raise HTTPException(status_code=404, detail="Função não encontrada.")
    return role


@router.put("/roles/{role_id}/permissions", response_model=RolePermissionsResponse, summary="Atualizar Matriz de Permissões da Função")
def update_role_permissions(
    role_id: str, 
    payload: RolePermissionsUpdate, 
    account_id: str = "0f14ffff"
):
    try:
        return service.update_role_permissions(role_id, payload.permissions, account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))



# --- Metas Comerciais & Comissionamento Multinível ---

@router.get("/targets", response_model=List[SalesTargetOut], summary="Listar Metas Comerciais com Atingimento em Tempo Real")
def list_targets(
    period: Optional[str] = None,
    account_id: str = "0f14ffff"
):
    return service.list_targets(account_id=account_id, period=period)


@router.post("/targets", response_model=SalesTargetOut, status_code=status.HTTP_201_CREATED, summary="Criar Meta Comercial (Cascateada ou Manual)")
def create_target(
    payload: SalesTargetCreate,
    account_id: str = "0f14ffff"
):
    try:
        return service.create_target(payload, account_id=account_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/targets/suggestion", response_model=AlgorithmicTargetSuggestion, summary="Calcular Sugestão Algorítmica de Meta com Crescimento Progressivo")
def get_target_suggestion(
    entity_type: str = Query(..., description="'user', 'team' ou 'bu'"),
    entity_id: str = Query(..., description="ID da entidade"),
    period: str = "2026-Q4",
    growth_rate_pct: float = 15.0,
    account_id: str = "0f14ffff"
):
    return service.get_target_suggestion(
        entity_type=entity_type,
        entity_id=entity_id,
        period=period,
        growth_rate_pct=growth_rate_pct,
        account_id=account_id
    )


@router.get("/commissions/rules", response_model=List[CommissionRuleOut], summary="Listar Regras de Comissionamento por Cargo")
def list_commission_rules(account_id: str = "0f14ffff"):
    return service.list_commission_rules(account_id=account_id)


@router.post("/commissions/rules", response_model=CommissionRuleOut, status_code=status.HTTP_201_CREATED, summary="Criar ou Atualizar Regra de Comissionamento")
def create_commission_rule(
    payload: CommissionRuleCreate,
    account_id: str = "0f14ffff"
):
    try:
        return service.create_commission_rule(payload, account_id=account_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/commissions/statement", response_model=CommissionStatementOut, summary="Extrato Consolidado de Comissões do Vendedor/Gestor")
def get_commission_statement(
    user_id: str = Query(..., description="ID do usuário"),
    period: str = "2026-Q4",
    account_id: str = "0f14ffff"
):
    try:
        return service.get_commission_statement(user_id=user_id, period=period, account_id=account_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

