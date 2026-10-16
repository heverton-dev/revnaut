# -*- coding: utf-8 -*-
"""
Schemas tipados para autenticação e gestão de sessão de usuários.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


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
