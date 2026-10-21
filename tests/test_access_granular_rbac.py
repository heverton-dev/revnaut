# -*- coding: utf-8 -*-
"""
Fase 5 — Permissionamento granular de navegação (banco + API).
Gate: /access/me, matriz, 403 de auto-elevação e seed de catálogo.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.core.database import get_connection, init_db
from src.features.auth.service import set_user_password
from src.main import app
from tests.auth_helpers import bearer_headers

client = TestClient(app, headers=bearer_headers())

SUPERADMIN_TEST_PASSWORD = "Teste-Superadmin-RevNault-2026!"
LOGISTICS_TEST_PASSWORD = "Logistica-Teste-RevNault-2026!"


@pytest.fixture(autouse=True)
def _passwords():
    conn = get_connection()
    try:
        uid = conn.execute(
            "SELECT id FROM users WHERE email = 'hevertoneduardoperes@gmail.com'"
        ).fetchone()[0]
        marcos = conn.execute(
            "SELECT id FROM users WHERE id = 'usr-log-marcos'"
        ).fetchone()
    finally:
        conn.close()
    set_user_password(uid, SUPERADMIN_TEST_PASSWORD)
    if marcos:
        set_user_password("usr-log-marcos", LOGISTICS_TEST_PASSWORD)
    # Garante catálogo/grants mesmo se init_db parcial
    init_db()
    yield


def _login(email: str, password: str) -> dict:
    res = client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    assert res.status_code == 200, res.text
    data = res.json()
    return {
        "Authorization": f"Bearer {data['access_token']}",
    }


def _superadmin_headers() -> dict:
    return _login("hevertoneduardoperes@gmail.com", SUPERADMIN_TEST_PASSWORD)


def _logistics_headers() -> dict:
    return _login("marcos.logistica@salesrocketbrasil.com.br", LOGISTICS_TEST_PASSWORD)


def test_seed_catalog_has_routes_and_grants():
    conn = get_connection()
    try:
        routes = conn.execute("SELECT COUNT(*) FROM access_catalog_routes").fetchone()[0]
        facilities = conn.execute(
            "SELECT COUNT(*) FROM access_catalog_facilities"
        ).fetchone()[0]
        grants = conn.execute("SELECT COUNT(*) FROM role_route_grants").fetchone()[0]
        role = conn.execute(
            "SELECT 1 FROM roles WHERE id = 'role-access-admin'"
        ).fetchone()
        scopes = conn.execute(
            "SELECT COUNT(*) FROM access_admin_scopes WHERE admin_role_id = 'role-access-admin'"
        ).fetchone()[0]
    finally:
        conn.close()

    assert routes >= 18, "catálogo de rotas incompleto"
    assert facilities >= 30, "catálogo de facilities incompleto"
    assert grants >= 40, "grants default ausentes"
    assert role is not None, "role-access-admin não semeado"
    assert scopes >= 5, "escopos do Admin de Acesso ausentes"


def test_access_me_logistics_from_db():
    headers = _logistics_headers()
    res = client.get("/api/v1/access/me", headers=headers)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["source"] == "db"
    assert body["role_id"] == "role-logistics"
    assert body["landing_route"] == "dentgo"
    route_ids = [r["route_id"] for r in body["routes"]]
    assert route_ids == ["dentgo", "keypartners", "support", "settings"]
    # facilities de dentgo presentes
    dentgo = next(r for r in body["routes"] if r["route_id"] == "dentgo")
    fac_ids = [f["facility_id"] for f in dentgo["facilities"]]
    assert "orders" in fac_ids and "hubs" in fac_ids


def test_access_me_superadmin_full_catalog():
    headers = _superadmin_headers()
    res = client.get("/api/v1/access/me", headers=headers)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["is_superadmin"] is True
    assert body["can_manage_access"] is True
    assert len(body["routes"]) >= 18


def test_access_matrix_requires_auth():
    anon = TestClient(app)
    res = anon.get("/api/v1/access/matrix")
    assert res.status_code == 401


def test_access_matrix_superadmin_editable():
    headers = _superadmin_headers()
    res = client.get("/api/v1/access/matrix", headers=headers)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["viewer_is_superadmin"] is True
    assert body["catalog"], "catálogo vazio"
    operational = [
        r
        for r in body["roles"]
        if r["role_id"]
        in (
            "role-field",
            "role-inside",
            "role-logistics",
            "role-clinical",
            "role-manager",
        )
    ]
    assert operational, "cargos operacionais ausentes"
    assert all(r["editable"] for r in operational), (
        "superadmin deve editar cargos operacionais"
    )
    # Superadmin PODE editar protegidos (role-ceo / access-admin) — design fase 1
    by_id = {r["role_id"]: r for r in body["roles"]}
    if "role-ceo" in by_id:
        assert by_id["role-ceo"]["editable"] is True


def test_logistics_cannot_put_grants():
    headers = _logistics_headers()
    res = client.put(
        "/api/v1/access/roles/role-field/grants",
        headers=headers,
        json={"routes": [{"route_id": "dashboard", "menu_priority": 1}]},
    )
    assert res.status_code == 403


def test_superadmin_can_put_grants_roundtrip():
    headers = _superadmin_headers()
    # Lê estado atual
    before = client.get("/api/v1/access/matrix", headers=headers).json()
    role = next(r for r in before["roles"] if r["role_id"] == "role-clinical")
    original = [
        {
            "route_id": g["route_id"],
            "menu_priority": g["menu_priority"],
            "allow_submenus": g["allow_submenus"],
            "facilities": [f["facility_id"] for f in g["facilities"]],
        }
        for g in role["grants"]
    ]
    assert original, "role-clinical deve ter grants seed"

    # Round-trip idêntico
    res = client.put(
        "/api/v1/access/roles/role-clinical/grants",
        headers=headers,
        json={"routes": original},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["updated"] is True
    assert data["route_count"] == len(original)

    after = client.get("/api/v1/access/matrix", headers=headers).json()
    role2 = next(r for r in after["roles"] if r["role_id"] == "role-clinical")
    assert [g["route_id"] for g in role2["grants"]] == [
        g["route_id"] for g in original
    ]


def test_access_admin_cannot_edit_role_ceo():
    # Garante usuário Admin de Acesso no seed de teste
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM users WHERE id = 'usr-access-admin' OR role_id = 'role-access-admin' LIMIT 1"
        ).fetchone()
        if not row:
            from src.features.auth.service import hash_password

            conn.execute(
                "INSERT OR REPLACE INTO users "
                "(id, account_id, name, email, role, is_superadmin, password_hash, is_active, role_id, created_at) "
                "VALUES ('usr-access-admin', '0f14ffff', 'Acesso Admin', "
                "'acesso.admin@revnaultdental.com', 'Admin de Acesso (Permissões)', 0, ?, 1, "
                "'role-access-admin', datetime('now'))",
                (hash_password("AdminAcesso-Teste-2026!"),),
            )
            conn.commit()
        else:
            uid = row[0]
            from src.features.auth.service import hash_password

            conn.execute(
                "UPDATE users SET password_hash = ?, role_id = 'role-access-admin', is_superadmin = 0 WHERE id = ?",
                (hash_password("AdminAcesso-Teste-2026!"), uid),
            )
            conn.commit()
    finally:
        conn.close()

    headers = _login("acesso.admin@revnaultdental.com", "AdminAcesso-Teste-2026!")
    # Pode ler matriz
    res = client.get("/api/v1/access/matrix", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["viewer_is_superadmin"] is False
    assert "role-access-admin" in body["editable_role_ids"] or any(
        r["editable"] for r in body["roles"]
    )

    # NÃO pode editar role-ceo
    res = client.put(
        "/api/v1/access/roles/role-ceo/grants",
        headers=headers,
        json={"routes": [{"route_id": "deals", "menu_priority": 1}]},
    )
    assert res.status_code == 403

    # NÃO pode editar outro admin de acesso
    res = client.put(
        "/api/v1/access/roles/role-access-admin/grants",
        headers=headers,
        json={"routes": [{"route_id": "rbac", "menu_priority": 1}]},
    )
    assert res.status_code == 403

    # Pode editar um cargo operacional (no escopo)
    res = client.put(
        "/api/v1/access/roles/role-field/grants",
        headers=headers,
        json={
            "routes": [
                {
                    "route_id": "deals",
                    "menu_priority": 1,
                    "allow_submenus": False,
                    "facilities": [],
                }
            ]
        },
    )
    assert res.status_code == 200, res.text

    # Restaura field grants seed
    field_routes = [
        ("deals", 1, 0),
        ("dentgo", 2, 0),
        ("contacts", 3, 0),
        ("keypartners", 4, 0),
        ("video_sos", 5, 0),
        ("intelligence", 6, 0),
        ("market_intel", 7, 0),
    ]
    restored = [
        {"route_id": r, "menu_priority": p, "allow_submenus": bool(s), "facilities": []}
        for r, p, s in field_routes
    ]
    client.put(
        "/api/v1/access/roles/role-field/grants",
        headers=headers,
        json={"routes": restored},
    )


def test_access_me_unauthenticated():
    anon = TestClient(app)
    res = anon.get("/api/v1/access/me")
    assert res.status_code == 401
