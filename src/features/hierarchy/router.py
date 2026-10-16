# -*- coding: utf-8 -*-
"""
Router FastAPI para Gestão de Hierarquia Organizacional, RBAC e Presets.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, status

from src.features.hierarchy.schemas import (
    BusinessUnitCreate, BusinessUnitOut, TeamCreate, TeamUpdateParent,
    TeamOut, RoleCreate, RoleOut, PresetApplyRequest
)
from src.features.hierarchy import service

router = APIRouter(prefix="/api/v1/hierarchy", tags=["Hierarquia Organizacional & RBAC"])


@router.post("/presets/apply", summary="Aplica Preset Organizacional Odontológico")
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
