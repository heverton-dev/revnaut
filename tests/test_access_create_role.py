# -*- coding: utf-8 -*-
"""Fase 7 — criação de cargos operacionais via API de access."""

from __future__ import annotations

import uuid

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
    from src.core.database import get_connection

    conn = get_connection()
    try:
        uid = conn.execute(
            "SELECT id FROM users WHERE email = 'hevertoneduardoperes@gmail.com'"
        ).fetchone()[0]
    finally:
        conn.close()
    set_user_password(uid, SUPERADMIN_TEST_PASSWORD)
    set_user_password("usr-log-marcos", LOGISTICS_TEST_PASSWORD)
    yield


def _login(email: str, password: str) -> dict:
    res = client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_superadmin_can_create_role_with_grants():
    headers = _login("hevertoneduardoperes@gmail.com", SUPERADMIN_TEST_PASSWORD)
    name = f"Especialista Teste {uuid.uuid4().hex[:6]}"
    res = client.post(
        "/api/v1/access/roles",
        headers=headers,
        json={
            "name": name,
            "description": "Cargo de teste fase 7",
            "default_data_scope": "team",
            "routes": [
                {
                    "route_id": "deals",
                    "menu_priority": 1,
                    "allow_submenus": False,
                    "facilities": [],
                },
                {
                    "route_id": "contacts",
                    "menu_priority": 2,
                    "allow_submenus": True,
                    "facilities": ["crm_surgeons", "institutions_links"],
                },
            ],
        },
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["created"] is True
    assert body["route_count"] >= 2
    role_id = body["role_id"]

    # Matriz mostra o cargo editável
    matrix = client.get("/api/v1/access/matrix", headers=headers).json()
    role = next(r for r in matrix["roles"] if r["role_id"] == role_id)
    assert role["editable"] is True
    assert [g["route_id"] for g in role["grants"]] == ["deals", "contacts"]
    contacts = next(g for g in role["grants"] if g["route_id"] == "contacts")
    fac_ids = [f["facility_id"] for f in contacts["facilities"]]
    assert "crm_surgeons" in fac_ids

    # /access/me para usuário recém-criado não existe — só grants no role
    # Limpeza: remove role de teste
    from src.core.database import get_connection

    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM role_facility_grants WHERE role_id = ?", (role_id,))
        conn.execute("DELETE FROM role_route_grants WHERE role_id = ?", (role_id,))
        conn.execute("DELETE FROM access_audit_log WHERE target_role_id = ?", (role_id,))
        conn.execute("DELETE FROM access_admin_scopes WHERE editable_role_id = ?", (role_id,))
        conn.execute("DELETE FROM roles WHERE id = ?", (role_id,))
    conn.close()


def test_logistics_cannot_create_role():
    headers = _login("marcos.logistica@salesrocketbrasil.com.br", LOGISTICS_TEST_PASSWORD)
    res = client.post(
        "/api/v1/access/roles",
        headers=headers,
        json={"name": "Hack Cargo", "routes": []},
    )
    assert res.status_code == 403


def test_duplicate_role_name_conflict():
    headers = _login("hevertoneduardoperes@gmail.com", SUPERADMIN_TEST_PASSWORD)
    name = f"Cargo Duplicado {uuid.uuid4().hex[:6]}"
    first = client.post(
        "/api/v1/access/roles",
        headers=headers,
        json={"name": name, "routes": []},
    )
    assert first.status_code == 201, first.text
    role_id = first.json()["role_id"]

    res = client.post(
        "/api/v1/access/roles",
        headers=headers,
        json={"name": name, "routes": []},
    )
    assert res.status_code == 409

    from src.core.database import get_connection

    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM roles WHERE id = ?", (role_id,))
    conn.close()
