# -*- coding: utf-8 -*-
"""Fase 8 — atribuir usuário existente a cargo."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from src.features.auth.service import set_user_password, hash_password
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


def _create_role(headers: dict, name: str) -> str:
    res = client.post(
        "/api/v1/access/roles",
        headers=headers,
        json={"name": name, "routes": [{"route_id": "deals", "menu_priority": 1}]},
    )
    assert res.status_code == 201, res.text
    return res.json()["role_id"]


def _cleanup_role(role_id: str) -> None:
    from src.core.database import get_connection

    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM role_facility_grants WHERE role_id = ?", (role_id,))
        conn.execute("DELETE FROM role_route_grants WHERE role_id = ?", (role_id,))
        conn.execute("DELETE FROM access_admin_scopes WHERE editable_role_id = ?", (role_id,))
        conn.execute("DELETE FROM access_audit_log WHERE target_role_id = ?", (role_id,))
        conn.execute("DELETE FROM roles WHERE id = ?", (role_id,))
    conn.close()


def test_assign_user_to_role_roundtrip():
    headers = _login("hevertoneduardoperes@gmail.com", SUPERADMIN_TEST_PASSWORD)
    role_id = _create_role(headers, f"Cargo Atrib {uuid.uuid4().hex[:6]}")

    try:
        res = client.put(
            f"/api/v1/access/roles/{role_id}/users/usr-log-marcos",
            headers=headers,
            json={"user_id": "usr-log-marcos", "sync_role_label": True},
        )
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["assigned"] is True
        assert body["role_id"] == role_id

        members = client.get(
            f"/api/v1/access/roles/{role_id}/users", headers=headers
        )
        assert members.status_code == 200
        users = members.json()
        assert any(u["user_id"] == "usr-log-marcos" for u in users)

        # /access/me de marcos reflete o novo cargo
        marcos = _login(
            "marcos.logistica@salesrocketbrasil.com.br", LOGISTICS_TEST_PASSWORD
        )
        me = client.get("/api/v1/access/me", headers=marcos)
        assert me.status_code == 200
        assert me.json()["role_id"] == role_id
        route_ids = [r["route_id"] for r in me.json()["routes"]]
        assert route_ids == ["deals"]

        # Restaura marcos para logística
        from src.core.database import get_connection

        conn = get_connection()
        with conn:
            conn.execute(
                "UPDATE users SET role_id = 'role-logistics', "
                "role = 'Logística e Estoque (Expedição)', is_superadmin = 0 "
                "WHERE id = 'usr-log-marcos'"
            )
        conn.close()
    finally:
        _cleanup_role(role_id)


def test_logistics_cannot_assign_users():
    headers = _login("marcos.logistica@salesrocketbrasil.com.br", LOGISTICS_TEST_PASSWORD)
    res = client.put(
        "/api/v1/access/roles/role-field/users/usr-inside-camila",
        headers=headers,
        json={"user_id": "usr-inside-camila"},
    )
    assert res.status_code == 403


def test_list_members_of_protected_role_blocked_for_non_admin():
    headers = _login("marcos.logistica@salesrocketbrasil.com.br", LOGISTICS_TEST_PASSWORD)
    res = client.get("/api/v1/access/roles/role-ceo/users", headers=headers)
    assert res.status_code == 403
