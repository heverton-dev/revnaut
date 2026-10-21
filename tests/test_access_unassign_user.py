# -*- coding: utf-8 -*-
"""Fase 9 — desvincular usuário do cargo."""

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


def _restore_marcos_logistics() -> None:
    from src.core.database import get_connection

    conn = get_connection()
    with conn:
        conn.execute(
            "UPDATE users SET role_id = 'role-logistics', "
            "role = 'Logística e Estoque (Expedição)', is_superadmin = 0 "
            "WHERE id = 'usr-log-marcos'"
        )
    conn.close()


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


def test_unassign_user_from_cargo_roundtrip():
    headers = _login("hevertoneduardoperes@gmail.com", SUPERADMIN_TEST_PASSWORD)
    name = f"Desvincula {uuid.uuid4().hex[:6]}"
    create = client.post(
        "/api/v1/access/roles",
        headers=headers,
        json={"name": name, "routes": [{"route_id": "dentgo", "menu_priority": 1}]},
    )
    assert create.status_code == 201, create.text
    role_id = create.json()["role_id"]

    try:
        put = client.put(
            f"/api/v1/access/roles/{role_id}/users/usr-log-marcos",
            headers=headers,
            json={"user_id": "usr-log-marcos"},
        )
        assert put.status_code == 200, put.text

        delete = client.delete(
            f"/api/v1/access/roles/{role_id}/users/usr-log-marcos",
            headers=headers,
        )
        assert delete.status_code == 200, delete.text
        body = delete.json()
        assert body["unassigned"] is True
        assert body["role_name"] == "Sem cargo"

        members = client.get(
            f"/api/v1/access/roles/{role_id}/users", headers=headers
        ).json()
        assert not any(u["user_id"] == "usr-log-marcos" for u in members)

        # /access/me sem role_id → fallback least-privilege (não vazio)
        marcos = _login(
            "marcos.logistica@salesrocketbrasil.com.br", LOGISTICS_TEST_PASSWORD
        )
        # senha ainda é a de teste; role label mudou mas login é por email
        me = client.get("/api/v1/access/me", headers=marcos)
        assert me.status_code == 200
        assert me.json()["role_id"] in (None, "")
        assert me.json()["routes"], "menu não pode ficar vazio"

        _restore_marcos_logistics()
    except AssertionError:
        _restore_marcos_logistics()
        raise
    finally:
        _cleanup_role(role_id)
        _restore_marcos_logistics()


def test_unassign_wrong_membership_409():
    headers = _login("hevertoneduardoperes@gmail.com", SUPERADMIN_TEST_PASSWORD)
    # marcos não está em role-field
    res = client.delete(
        "/api/v1/access/roles/role-field/users/usr-log-marcos",
        headers=headers,
    )
    assert res.status_code == 409
    # restaura caso alguma corrida tenha alterado
    _restore_marcos_logistics()


def test_logistics_cannot_unassign():
    headers = _login("marcos.logistica@salesrocketbrasil.com.br", LOGISTICS_TEST_PASSWORD)
    res = client.delete(
        "/api/v1/access/roles/role-field/users/usr-inside-camila",
        headers=headers,
    )
    assert res.status_code == 403


def test_superadmin_cannot_unassign_self_from_directoria():
    headers = _login("hevertoneduardoperes@gmail.com", SUPERADMIN_TEST_PASSWORD)
    res = client.delete(
        "/api/v1/access/roles/role-ceo/users/usr-superadmin-god",
        headers=headers,
    )
    assert res.status_code == 403
