# -*- coding: utf-8 -*-
"""
Rotas da API para Autenticação e Sessão de Usuários.
"""

from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, HTTPException, Header, Depends
from src.features.auth.schemas import (
    LoginRequest,
    LoginResponse,
    UserProfileOut,
    LogoutResponse,
    UserListItem,
    CreateCollaboratorRequest,
    ResetPasswordRequest,
    UpdateUserStatusRequest
)
from src.features.auth.service import (
    authenticate_user,
    create_session_token,
    verify_session_token,
    get_user_profile,
    list_all_users,
    create_collaborator,
    update_user_status,
    reset_user_password
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


@router.post("/login", response_model=LoginResponse, summary="Autenticar usuário e emitir token de sessão")
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


@router.get("/users", response_model=list[UserListItem], summary="Listar todos os colaboradores da conta")
def list_users(current_user: UserProfileOut = Depends(get_current_user)):
    return list_all_users(account_id=current_user.account_id)


from src.features.auth.schemas import (
    LoginRequest,
    LoginResponse,
    UserProfileOut,
    LogoutResponse,
    UserListItem,
    CreateCollaboratorRequest,
    ResetPasswordRequest,
    UpdateUserStatusRequest,
    UserStatusResponse,
    ResetPasswordResponse
)


@router.post("/users", response_model=UserProfileOut, summary="Cadastrar novo colaborador (Super Admin exclusivo)")
def create_user(payload: CreateCollaboratorRequest, current_user: UserProfileOut = Depends(get_current_user)):
    return create_collaborator(
        data=payload,
        current_user=current_user.model_dump(),
        account_id=current_user.account_id
    )


@router.put("/users/{user_id}/status", response_model=UserStatusResponse, summary="Alterar status de ativação de colaborador")
def change_status(
    user_id: str,
    payload: UpdateUserStatusRequest,
    current_user: UserProfileOut = Depends(get_current_user)
):
    return update_user_status(
        target_user_id=user_id,
        is_active=payload.is_active,
        current_user=current_user.model_dump()
    )


@router.post("/users/{user_id}/reset-password", response_model=ResetPasswordResponse, summary="Redefinir senha de colaborador (Super Admin exclusivo)")
def reset_password(
    user_id: str,
    payload: ResetPasswordRequest,
    current_user: UserProfileOut = Depends(get_current_user)
):
    return reset_user_password(
        target_user_id=user_id,
        new_password=payload.new_password,
        current_user=current_user.model_dump()
    )


from src.features.auth.schemas import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordWithTokenRequest,
    ResetPasswordWithTokenResponse
)
from src.features.auth.service import (
    request_password_reset,
    reset_password_with_token
)


@router.post("/forgot-password", response_model=ForgotPasswordResponse, summary="Solicitar link temporário de recuperação de senha")
def forgot_password(payload: ForgotPasswordRequest):
    return request_password_reset(payload.email)


@router.post("/reset-password-with-token", response_model=ResetPasswordWithTokenResponse, summary="Redefinir senha utilizando token temporário de recuperação")
def reset_with_token(payload: ResetPasswordWithTokenRequest):
    return reset_password_with_token(token=payload.token, new_password=payload.new_password)


from src.features.auth.schemas import (
    TenantCredentialCreate,
    TenantCredentialResponse,
    CredentialDeleteResponse,
)
from src.features.auth.service import (
    store_tenant_credential,
    list_tenant_credentials,
    delete_tenant_credential,
)


@router.post("/credentials", response_model=TenantCredentialResponse, summary="Armazenar credencial com AES-256 no cofre")
def create_credential(
    payload: TenantCredentialCreate,
    x_account_id: Optional[str] = Header(None, alias="X-Account-ID"),
):
    account_id = x_account_id or "0f14ffff"
    cred_id = store_tenant_credential(
        account_id=account_id,
        service_name=payload.service_name,
        credential_type=payload.credential_type,
        secret_payload=payload.secret_payload,
        metadata=payload.metadata,
    )
    last4 = payload.secret_payload[-4:] if len(payload.secret_payload) >= 4 else "****"
    return TenantCredentialResponse(
        id=cred_id,
        account_id=account_id,
        service_name=payload.service_name,
        credential_type=payload.credential_type,
        masked_value=f"****{last4}",
        metadata=payload.metadata,
    )


@router.get("/credentials", response_model=list[TenantCredentialResponse], summary="Listar credenciais do tenant com valores mascarados")
def get_credentials(
    x_account_id: Optional[str] = Header(None, alias="X-Account-ID"),
):
    account_id = x_account_id or "0f14ffff"
    creds = list_tenant_credentials(account_id)
    return [TenantCredentialResponse(**c) for c in creds]


@router.delete("/credentials/{credential_id}", response_model=CredentialDeleteResponse, summary="Remover credencial do cofre")
def remove_credential(
    credential_id: str,
    x_account_id: Optional[str] = Header(None, alias="X-Account-ID"),
):
    account_id = x_account_id or "0f14ffff"
    success = delete_tenant_credential(account_id, credential_id)
    if not success:
        raise HTTPException(status_code=404, detail="Credencial não encontrada.")
    return CredentialDeleteResponse(success=True, message="Credencial removida com sucesso.")




