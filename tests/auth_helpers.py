# -*- coding: utf-8 -*-
"""
Credenciais reais de sessão para testes de API.

As rotas exigem token Bearer de sessão assinado (HMAC). O superadmin pode agir como outro
usuário enviando X-User-Id (impersonação do seletor de usuário); por isso clientes autenticados
como superadmin preservam a semântica "agir como o usuário X" dos testes de escopo e RBAC.
"""

from __future__ import annotations

from typing import Dict

from src.features.auth.service import create_session_token

SUPERADMIN_ID = "usr-superadmin-god"


def bearer_headers(user_id: str = SUPERADMIN_ID) -> Dict[str, str]:
    return {"Authorization": f"Bearer {create_session_token(user_id)}"}
