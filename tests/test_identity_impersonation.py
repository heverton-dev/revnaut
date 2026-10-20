# -*- coding: utf-8 -*-
"""
Identidade das requisições: token Bearer de sessão obrigatório e X-User-Id apenas como
impersonação por superadmin (seletor de usuário). Prova que headers livres não autenticam.
"""

from __future__ import annotations

import hashlib
import hmac
import time

import pytest
from fastapi.testclient import TestClient

from src.core.config import SECRET_KEY, SESSION_TTL_SECONDS
from src.core.database import get_connection, init_db
from src.features.auth.service import create_session_token
from src.main import app
from tests.auth_helpers import SUPERADMIN_ID, bearer_headers

client = TestClient(app)

IDENTITY_ROUTES = [
    ("GET", "/api/v1/auth/me"),
    ("GET", "/api/v1/deals"),
    ("GET", "/api/v1/contacts"),
    ("GET", "/api/v1/intelligence/clinical-graph"),
]


def _expired_token(user_id: str) -> str:
    issued = int(time.time()) - SESSION_TTL_SECONDS - 60
    sig = hmac.new(SECRET_KEY.encode("utf-8"), f"{user_id}:{issued}".encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{user_id}.{issued}.{sig}"


@pytest.mark.parametrize("method,path", IDENTITY_ROUTES)
@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"X-User-Id": SUPERADMIN_ID},
        {"Authorization": f"Bearer {SUPERADMIN_ID}.1700000000.assinatura-forjada"},
        {"Authorization": f"Bearer {_expired_token(SUPERADMIN_ID)}", "X-User-Id": SUPERADMIN_ID},
    ],
    ids=["sem-credencial", "so-x-user-id", "token-forjado", "token-expirado"],
)
def test_identity_routes_require_valid_session(method, path, headers):
    assert client.request(method, path, headers=headers).status_code == 401


def test_non_superadmin_cannot_impersonate_via_header():
    res = client.get("/api/v1/auth/me", headers={**bearer_headers("usr-field-ricardo"), "X-User-Id": SUPERADMIN_ID})
    assert res.status_code == 200
    assert res.json()["id"] == "usr-field-ricardo"
    assert res.json()["is_superadmin"] is False


def test_superadmin_impersonates_existing_active_user():
    res = client.get("/api/v1/auth/me", headers={**bearer_headers(), "X-User-Id": "usr-field-ricardo"})
    assert res.status_code == 200 and res.json()["id"] == "usr-field-ricardo"


def test_superadmin_impersonation_of_unknown_or_inactive_user_keeps_own_identity():
    init_db()
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO users (id, account_id, name, email, role, is_superadmin, is_active) "
            "VALUES ('usr-inativo-imp', '0f14ffff', 'Inativo', 'inativo.imp@teste.revnault.com', 'Consultor Externo (Campo)', 0, 0)"
        )
        conn.commit()
    finally:
        conn.close()
    for target in ("usr-que-nao-existe", "usr-inativo-imp"):
        res = client.get("/api/v1/auth/me", headers={**bearer_headers(), "X-User-Id": target})
        assert res.status_code == 200 and res.json()["id"] == SUPERADMIN_ID


def test_inactive_user_session_is_rejected():
    init_db()
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO users (id, account_id, name, email, role, is_superadmin, is_active) "
            "VALUES ('usr-inativo-sess', '0f14ffff', 'Inativo Sessão', 'inativo.sess@teste.revnault.com', 'Gerente Comercial', 0, 0)"
        )
        conn.commit()
    finally:
        conn.close()
    res = client.get("/api/v1/deals", headers={"Authorization": f"Bearer {create_session_token('usr-inativo-sess')}"})
    assert res.status_code == 401
