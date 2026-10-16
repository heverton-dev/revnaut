# -*- coding: utf-8 -*-
"""
Testes TDD - Matriz de Permissões e Functional RBAC (Lei #13 - O Portão Deve Provar que Morde)
Valida a restrição granular por ação:
- GET /api/v1/hierarchy/catalog
- GET /api/v1/hierarchy/roles
- PUT /api/v1/hierarchy/roles/{id}/permissions
- Bloqueio HTTP 403 Forbidden em mutações críticas quando a Role não possui a permissão.
"""

from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection

client = TestClient(app)


def setup_rbac_matrix_fixture():
    """Configura fixture determinística de roles e permissões para teste de bloqueio."""
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        acc = "0f14ffff"

        # 1. Cria 2 roles: uma COM permissão de baixa e outra SEM
        cur.execute("INSERT OR REPLACE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES "
                    "('r_cons_habilitado', ?, 'Consultor Habilitado', 'self', 0)", (acc,))
        cur.execute("INSERT OR REPLACE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES "
                    "('r_cons_bloqueado', ?, 'Consultor Bloqueado', 'self', 0)", (acc,))

        # 2. Atribui permissões na tabela role_permissions
        cur.execute("DELETE FROM role_permissions WHERE role_id IN ('r_cons_habilitado', 'r_cons_bloqueado')")
        cur.execute("INSERT INTO role_permissions (account_id, role_id, permission_code) VALUES (?, 'r_cons_habilitado', 'consignments:read')", (acc,))
        cur.execute("INSERT INTO role_permissions (account_id, role_id, permission_code) VALUES (?, 'r_cons_habilitado', 'consignments:consume')", (acc,))
        cur.execute("INSERT INTO role_permissions (account_id, role_id, permission_code) VALUES (?, 'r_cons_habilitado', 'deals:read')", (acc,))

        cur.execute("INSERT INTO role_permissions (account_id, role_id, permission_code) VALUES (?, 'r_cons_bloqueado', 'consignments:read')", (acc,))
        # r_cons_bloqueado NÃO possui 'consignments:consume' nem 'deals:write'

        # 3. Usuários
        cur.execute("INSERT OR REPLACE INTO users (id, account_id, team_id, role_id, name, email, custom_data_scope, is_superadmin) VALUES "
                    "('u_test_habilitado', ?, 'tm_reg_capital', 'r_cons_habilitado', 'Consultor Habilitado', 'hab@empresa.com', 'self', 0)", (acc,))
        cur.execute("INSERT OR REPLACE INTO users (id, account_id, team_id, role_id, name, email, custom_data_scope, is_superadmin) VALUES "
                    "('u_test_bloqueado', ?, 'tm_reg_capital', 'r_cons_bloqueado', 'Consultor Bloqueado', 'bloq@empresa.com', 'self', 0)", (acc,))

        # 4. Garante saldo físico na caixa box-1 para o teste
        cur.execute("UPDATE consignment_items SET quantity_consumed = 0 WHERE consignment_id = 'box-1' AND product_sku = 'IMP-GM-375-10'")
    conn.close()


def test_permission_catalog_and_roles_list():
    """Valida retorno do catálogo canônico e listagem de roles com permissões."""
    setup_rbac_matrix_fixture()

    # 1. Catálogo
    res_cat = client.get("/api/v1/hierarchy/catalog")
    assert res_cat.status_code == 200
    catalog = res_cat.json()
    resources = [item["resource"] for item in catalog]
    assert "consignments" in resources
    assert "deals" in resources
    assert "contacts" in resources

    # 2. Listagem de roles
    res_roles = client.get("/api/v1/hierarchy/roles")
    assert res_roles.status_code == 200
    roles = res_roles.json()
    role_ids = [r["id"] for r in roles]
    assert "r_cons_habilitado" in role_ids
    assert "r_cons_bloqueado" in role_ids


def test_update_role_permissions_endpoint():
    """Valida atualização dinâmica da matriz de permissões de uma role."""
    setup_rbac_matrix_fixture()
    payload = {
        "permissions": ["consignments:read", "deals:read", "deals:write", "contacts:read"]
    }
    res_update = client.put("/api/v1/hierarchy/roles/r_cons_bloqueado/permissions", json=payload)
    assert res_update.status_code == 200
    data = res_update.json()
    assert data["success"] is True
    assert "deals:write" in data["permissions"]

    # Consulta para confirmar persistência
    res_get = client.get("/api/v1/hierarchy/roles/r_cons_bloqueado/permissions")
    assert res_get.status_code == 200
    assert "deals:write" in res_get.json()["permissions"]


def test_gate_morde_enforce_permission_blocks_unauthorized_user():
    """Lei #13: Prova que a API bloqueia com HTTP 403 Forbidden usuário sem a permissão requerida."""
    setup_rbac_matrix_fixture()
    consume_payload = {
        "product_sku": "IMP-GM-375-10",
        "quantity": 1,
        "patient_protocol": "PRONT-TEST-403"
    }
    # Usuário u_test_bloqueado NÃO possui 'consignments:consume'
    headers = {"X-User-Id": "u_test_bloqueado"}
    res = client.post("/api/v1/consignments/box-1/consume", json=consume_payload, headers=headers)
    assert res.status_code == 403
    assert "consignments:consume" in res.json()["detail"]


def test_enforce_permission_allows_authorized_user():
    """Valida que usuário com a permissão correta recebe HTTP 200 na mesma operação."""
    setup_rbac_matrix_fixture()
    consume_payload = {
        "product_sku": "IMP-GM-375-10",
        "quantity": 1,
        "patient_protocol": "PRONT-TEST-200"
    }
    # Usuário u_test_habilitado POSSUI 'consignments:consume'
    headers = {"X-User-Id": "u_test_habilitado"}
    res = client.post("/api/v1/consignments/box-1/consume", json=consume_payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "consumed"
