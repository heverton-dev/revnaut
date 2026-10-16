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
