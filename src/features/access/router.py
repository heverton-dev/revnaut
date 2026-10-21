# -*- coding: utf-8 -*-
"""API de permissão granular de navegação (fase 2 + 4)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.features.access.schemas import (
    AccessAssignUserIn,
    AccessAssignUserOut,
    AccessCreateRoleIn,
    AccessCreateRoleOut,
    AccessMatrixOut,
    AccessMeOut,
    AccessRoleUserOut,
    AccessSaveGrantsIn,
    AccessSaveGrantsOut,
    AccessUnassignUserOut,
)
from src.features.access.service import (
    assign_user_to_role,
    can_manage_role,
    create_operational_role,
    get_access_me,
    list_access_matrix,
    list_role_users,
    save_role_grants,
    unassign_user_from_role,
)
from src.features.auth.router import get_current_user
from src.features.auth.schemas import UserProfileOut

router = APIRouter(prefix="/api/v1/access", tags=["Access · Permissões Granulares"])


def _user_dict(user: UserProfileOut) -> dict:
    return {
        "id": user.id,
        "account_id": user.account_id,
        "role": user.role,
        "role_id": user.role_id,
        "is_superadmin": user.is_superadmin,
    }


@router.get(
    "/me",
    response_model=AccessMeOut,
    summary="Grants de navegação do usuário efetivo (routes + facilities + landing)",
)
def access_me(user: UserProfileOut = Depends(get_current_user)) -> AccessMeOut:
    return get_access_me(_user_dict(user))


@router.get(
    "/matrix",
    response_model=AccessMatrixOut,
    summary="Matriz de cargos × rotas × facilities (leitura)",
)
def access_matrix(user: UserProfileOut = Depends(get_current_user)) -> AccessMatrixOut:
    return list_access_matrix(_user_dict(user), user.account_id)


@router.put(
    "/roles/{role_id}/grants",
    response_model=AccessSaveGrantsOut,
    summary="Substitui grants de um cargo (Super Admin ou Admin de Acesso)",
)
def replace_grants(
    role_id: str,
    payload: AccessSaveGrantsIn,
    user: UserProfileOut = Depends(get_current_user),
) -> AccessSaveGrantsOut:
    try:
        result = save_role_grants(
            _user_dict(user),
            user.account_id,
            role_id,
            [r.model_dump() for r in payload.routes],
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return AccessSaveGrantsOut(**result)


@router.post(
    "/roles",
    response_model=AccessCreateRoleOut,
    status_code=status.HTTP_201_CREATED,
    summary="Cria cargo operacional com grants iniciais (Super Admin ou Admin de Acesso)",
)
def create_role(
    payload: AccessCreateRoleIn,
    user: UserProfileOut = Depends(get_current_user),
) -> AccessCreateRoleOut:
    try:
        result = create_operational_role(
            _user_dict(user),
            user.account_id,
            payload.name.strip(),
            payload.description,
            payload.default_data_scope,
            [r.model_dump() for r in payload.routes],
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return AccessCreateRoleOut(**result)


@router.get(
    "/roles/{role_id}/users",
    response_model=list[AccessRoleUserOut],
    summary="Usuários vinculados a um cargo",
)
def role_users(
    role_id: str,
    user: UserProfileOut = Depends(get_current_user),
) -> list[AccessRoleUserOut]:
    actor = _user_dict(user)
    try:
        rows = list_role_users(actor, user.account_id, role_id)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return [AccessRoleUserOut(**r) for r in rows]


@router.put(
    "/roles/{role_id}/users/{target_user_id}",
    response_model=AccessAssignUserOut,
    summary="Atribui usuário existente ao cargo (Super Admin ou Admin de Acesso)",
)
def assign_user(
    role_id: str,
    target_user_id: str,
    payload: AccessAssignUserIn | None = None,
    user: UserProfileOut = Depends(get_current_user),
) -> AccessAssignUserOut:
    sync = True if payload is None else payload.sync_role_label
    if payload is not None and payload.user_id and payload.user_id != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id do corpo não confere com o path.",
        )
    try:
        result = assign_user_to_role(
            _user_dict(user),
            user.account_id,
            role_id,
            target_user_id,
            sync_role_label=sync,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return AccessAssignUserOut(**result)


@router.delete(
    "/roles/{role_id}/users/{target_user_id}",
    response_model=AccessUnassignUserOut,
    summary="Desvincula usuário do cargo (role_id → NULL)",
)
def unassign_user(
    role_id: str,
    target_user_id: str,
    user: UserProfileOut = Depends(get_current_user),
) -> AccessUnassignUserOut:
    try:
        result = unassign_user_from_role(
            _user_dict(user),
            user.account_id,
            role_id,
            target_user_id,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        msg = str(exc)
        if "não está vinculado" in msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
    return AccessUnassignUserOut(**result)
