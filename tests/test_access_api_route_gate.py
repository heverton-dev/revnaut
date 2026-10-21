# -*- coding: utf-8 -*-
"""Fase 6 — 403 em APIs de domínio fora do grant do cargo."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.features.auth.service import set_user_password
from src.main import app
from tests.auth_helpers import bearer_headers

client = TestClient(app, headers=bearer_headers())

SUPERADMIN_TEST_PASSWORD = "Teste-Superadmin-RevNault-2026!"
LOGISTICS_TEST_PASSWORD = "Logistica-Teste-RevNault-2026!"


@pytest.fixture(autouse=True)
def _passwords():
    conn_ctx = __import__("src.core.database", fromlist=["get_connection"]).get_connection()
    try:
        uid = conn_ctx.execute(
            "SELECT id FROM users WHERE email = 'hevertoneduardoperes@gmail.com'"
        ).fetchone()[0]
    finally:
        conn_ctx.close()
    set_user_password(uid, SUPERADMIN_TEST_PASSWORD)
    set_user_password("usr-log-marcos", LOGISTICS_TEST_PASSWORD)
    yield


def _login(email: str, password: str) -> dict:
    res = client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_logistics_cannot_list_deals():
    headers = _login("marcos.logistica@salesrocketbrasil.com.br", LOGISTICS_TEST_PASSWORD)
    res = client.get("/api/v1/deals", headers=headers)
    assert res.status_code == 403
    assert "não está liberado" in res.json()["detail"]


def test_logistics_can_list_dentgo():
    headers = _login("marcos.logistica@salesrocketbrasil.com.br", LOGISTICS_TEST_PASSWORD)
    res = client.get("/api/v1/dentgo/orders", headers=headers)
    # 200 ou 404 de recurso — nunca 403 de grant
    assert res.status_code != 403, res.text


def test_superadmin_can_list_deals():
    headers = _login("hevertoneduardoperes@gmail.com", SUPERADMIN_TEST_PASSWORD)
    res = client.get("/api/v1/deals", headers=headers)
    assert res.status_code != 403, res.text


def test_logistics_can_hit_exempt_auth():
    headers = _login("marcos.logistica@salesrocketbrasil.com.br", LOGISTICS_TEST_PASSWORD)
    res = client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 200


def test_required_routes_helper():
    from src.features.access.service import required_routes_for_path

    assert required_routes_for_path("/api/v1/deals") == ("deals",)
    assert required_routes_for_path("/api/v1/hierarchy/teams") == ("rbac", "settings")
    assert required_routes_for_path("/api/v1/auth/login") is None
    assert required_routes_for_path("/api/v1/webhooks/evolution") is None
    assert required_routes_for_path("/api/v1/access/me") is None
    # backlog fase 9+ — novos prefixes
    assert required_routes_for_path("/api/v1/automations/flows") == (
        "scheduling",
        "support",
        "marketing",
    )
    assert required_routes_for_path("/api/v1/integrations/totvs/orders") == (
        "settings",
        "deals",
        "dentgo",
    )
    assert required_routes_for_path("/api/v1/documenso/lifecycle") == ("contracts",)
