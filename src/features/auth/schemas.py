# -*- coding: utf-8 -*-
"""
Schemas tipados para autenticação e gestão de sessão de usuários.
"""

from __future__ import annotations
from typing import Optional, Any
from pydantic import BaseModel, model_validator


class VaultAuditLogOut(BaseModel):
    id: str
    timestamp: str
    actor: str
    action: str
    service_name: str
    ip_address: str
    status: str
    auth_mechanism: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserProfileOut(BaseModel):
    id: str
    account_id: str
    name: str
    email: str
    role: str
    is_superadmin: bool
    team_id: Optional[str] = None
    role_id: Optional[str] = None
    phone: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileOut


class LogoutResponse(BaseModel):
    success: bool = True
    message: str = "Sessão encerrada com sucesso"


class UserListItem(BaseModel):
    id: str
    account_id: str
    name: str
    email: str
    role: str
    is_superadmin: bool
    is_active: bool
    team_id: Optional[str] = None
    team_name: Optional[str] = None
    bu_id: Optional[str] = None
    bu_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[str] = None
    created_at: Optional[str] = None


class CreateCollaboratorRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "Consultor Comercial"
    team_id: Optional[str] = None
    role_id: Optional[str] = None
    phone: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    new_password: str


class UpdateUserStatusRequest(BaseModel):
    is_active: bool


class UserStatusResponse(BaseModel):
    id: str
    is_active: bool
    success: bool = True


class ResetPasswordResponse(BaseModel):
    id: str
    success: bool = True
    message: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ForgotPasswordResponse(BaseModel):
    success: bool = True
    message: str
    reset_token: Optional[str] = None


class ResetPasswordWithTokenRequest(BaseModel):
    token: str
    new_password: str


class ResetPasswordWithTokenResponse(BaseModel):
    success: bool = True
    message: str


class TenantCredentialCreate(BaseModel):
    service_name: str
    credential_type: str
    secret_payload: Optional[str] = None
    secret_value: Optional[str] = None
    metadata: Optional[dict] = None

    @model_validator(mode="before")
    @classmethod
    def _fill_payload(cls, values: Any) -> Any:
        if isinstance(values, dict):
            p = values.get("secret_payload")
            v = values.get("secret_value")
            if not p and v:
                values["secret_payload"] = v
            elif not v and p:
                values["secret_value"] = p
        return values


class TenantCredentialResponse(BaseModel):
    id: str
    account_id: str
    service_name: str
    credential_type: str
    masked_value: str
    metadata: Optional[dict] = None
    created_at: Optional[str] = None


class CredentialDeleteResponse(BaseModel):
    success: bool = True
    message: str



