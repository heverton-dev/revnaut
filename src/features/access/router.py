# -*- coding: utf-8 -*-
"""API de permissão granular de navegação (fase 2)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from src.features.access.schemas import AccessMeOut
from src.features.access.service import get_access_me
from src.features.auth.router import get_current_user
from src.features.auth.schemas import UserProfileOut

router = APIRouter(prefix="/api/v1/access", tags=["Access · Permissões Granulares"])


@router.get(
    "/me",
    response_model=AccessMeOut,
    summary="Grants de navegação do usuário efetivo (routes + facilities + landing)",
)
def access_me(user: UserProfileOut = Depends(get_current_user)) -> AccessMeOut:
    return get_access_me(
        {
            "id": user.id,
            "account_id": user.account_id,
            "role": user.role,
            "role_id": user.role_id,
            "is_superadmin": user.is_superadmin,
        }
    )
