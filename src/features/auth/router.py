# -*- coding: utf-8 -*-
"""
Rotas da API para Autenticação e Sessão de Usuários.
"""

from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, HTTPException, Header, Depends
from src.features.auth.schemas import LoginRequest, LoginResponse, UserProfileOut, LogoutResponse
from src.features.auth.service import (
    authenticate_user,
    create_session_token,
    verify_session_token,
    get_user_profile
)

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação & Sessão"])


def get_current_user(
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None)
) -> UserProfileOut:
    """Extrai usuário autenticado via Bearer Token ou fallback X-User-Id."""
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ", 1)[1].strip()
        user_id = verify_session_token(token)

    if not user_id and x_user_id:
        user_id = x_user_id

    if not user_id:
        raise HTTPException(status_code=401, detail="Não autenticado. Forneça credenciais válidas.")

    profile = get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada.")

    return UserProfileOut(
        id=profile["id"],
        account_id=profile["account_id"],
        name=profile["name"],
        email=profile["email"],
        role=profile["role"],
        is_superadmin=bool(profile["is_superadmin"]),
        team_id=profile.get("team_id"),
        role_id=profile.get("role_id"),
        phone=profile.get("phone")
    )


@app_route := router.post("/login", response_model=LoginResponse, summary="Autenticar usuário e emitir token de sessão")
def login(payload: LoginRequest):
    user_dict = authenticate_user(payload.email, payload.password)
    token = create_session_token(user_dict["id"])

    user_out = UserProfileOut(
        id=user_dict["id"],
        account_id=user_dict["account_id"],
        name=user_dict["name"],
        email=user_dict["email"],
        role=user_dict["role"],
        is_superadmin=bool(user_dict["is_superadmin"]),
        team_id=user_dict.get("team_id"),
        role_id=user_dict.get("role_id"),
        phone=user_dict.get("phone")
    )
    return LoginResponse(access_token=token, token_type="bearer", user=user_out)


@router.get("/me", response_model=UserProfileOut, summary="Obter dados do usuário ativo da sessão")
def me(current_user: UserProfileOut = Depends(get_current_user)):
    return current_user


@router.post("/logout", response_model=LogoutResponse, summary="Encerrar sessão ativa")
def logout():
    return LogoutResponse(success=True, message="Sessão encerrada com sucesso")
