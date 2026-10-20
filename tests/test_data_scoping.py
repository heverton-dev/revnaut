# -*- coding: utf-8 -*-
"""
Testes TDD - TICKET-03: Motor Central de Data Scoping no Backend
Valida a restrição matemática em nível de linha (Row-Level Security) no CRM
entre Consultores, Gestores Regionais, Distritais e Super Admin sobre as Oportunidades (Deals).
"""

from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection

client = TestClient(app, headers=bearer_headers())


def setup_scoping_fixture():
    """Configura fixture hierárquica completa para testes de isolamento de Deals."""
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        acc = "0f14ffff"

        # 1. BU
        cur.execute("INSERT OR IGNORE INTO business_units (id, account_id, name, code) VALUES ('bu_cir_test', ?, 'Cirurgia Test', 'CIR_TEST')", (acc,))

        # 2. Distrito e 2 Regionais
        cur.execute("INSERT OR IGNORE INTO teams (id, account_id, business_unit_id, parent_id, name) VALUES ('tm_dist_sp', ?, 'bu_cir_test', NULL, 'Distrito SP')", (acc,))
        cur.execute("INSERT OR IGNORE INTO teams (id, account_id, business_unit_id, parent_id, name) VALUES ('tm_reg_capital', ?, 'bu_cir_test', 'tm_dist_sp', 'Regional SP Capital')", (acc,))
        cur.execute("INSERT OR IGNORE INTO teams (id, account_id, business_unit_id, parent_id, name) VALUES ('tm_reg_interior', ?, 'bu_cir_test', 'tm_dist_sp', 'Regional SP Interior')", (acc,))

        # 3. Roles
        cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES ('r_cons', ?, 'Consultor', 'self', 0)", (acc,))
        cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES ('r_greg', ?, 'Gerente Regional', 'team', 0)", (acc,))
        cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES ('r_gdist', ?, 'Gerente Distrital', 'subtree', 0)", (acc,))

        for r_id in ('r_cons', 'r_greg', 'r_gdist'):
            for p_code in ('deals:read', 'deals:write', 'contacts:read', 'contacts:write'):
                cur.execute("INSERT OR IGNORE INTO role_permissions (account_id, role_id, permission_code) VALUES (?, ?, ?)", (acc, r_id, p_code))

        # 4. Usuários
        cur.execute("INSERT OR REPLACE INTO users (id, account_id, team_id, role_id, name, email, custom_data_scope, is_superadmin) VALUES "
                    "('u_cons_capital_1', ?, 'tm_reg_capital', 'r_cons', 'Consultor Capital 1', 'cons1@empresa.com', 'self', 0)", (acc,))
        cur.execute("INSERT OR REPLACE INTO users (id, account_id, team_id, role_id, name, email, custom_data_scope, is_superadmin) VALUES "
                    "('u_cons_capital_2', ?, 'tm_reg_capital', 'r_cons', 'Consultor Capital 2', 'cons2@empresa.com', 'self', 0)", (acc,))
        cur.execute("INSERT OR REPLACE INTO users (id, account_id, team_id, role_id, name, email, custom_data_scope, is_superadmin) VALUES "
                    "('u_greg_capital', ?, 'tm_reg_capital', 'r_greg', 'Gestor Regional Capital', 'greg@empresa.com', 'team', 0)", (acc,))
        cur.execute("INSERT OR REPLACE INTO users (id, account_id, team_id, role_id, name, email, custom_data_scope, is_superadmin) VALUES "
                    "('u_cons_interior_1', ?, 'tm_reg_interior', 'r_cons', 'Consultor Interior 1', 'int1@empresa.com', 'self', 0)", (acc,))
        cur.execute("INSERT OR REPLACE INTO users (id, account_id, team_id, role_id, name, email, custom_data_scope, is_superadmin) VALUES "
                    "('u_gdist_sp', ?, 'tm_dist_sp', 'r_gdist', 'Gestor Distrital SP', 'gdist@empresa.com', 'subtree', 0)", (acc,))

        # 5. Deals atribuídos às equipes e consultores
        cur.execute("INSERT OR REPLACE INTO deals (id, account_id, pipeline_id, stage_id, title, value, company, contact_name, priority, owner_id, team_id) VALUES "
                    "('d-scope-cap-1', ?, 1, 101, 'Contrato Implantes Capital A', 50000.0, 'Clínica Capital A', 'Dr. Alencar', 'alta', 'u_cons_capital_1', 'tm_reg_capital')", (acc,))
        cur.execute("INSERT OR REPLACE INTO deals (id, account_id, pipeline_id, stage_id, title, value, company, contact_name, priority, owner_id, team_id) VALUES "
                    "('d-scope-cap-2', ?, 1, 101, 'Contrato Implantes Capital B', 75000.0, 'Clínica Capital B', 'Dra. Beatriz', 'media', 'u_cons_capital_2', 'tm_reg_capital')", (acc,))
        cur.execute("INSERT OR REPLACE INTO deals (id, account_id, pipeline_id, stage_id, title, value, company, contact_name, priority, owner_id, team_id) VALUES "
                    "('d-scope-int-1', ?, 1, 101, 'Contrato Implantes Interior A', 30000.0, 'Clínica Interior A', 'Dr. Carlos', 'baixa', 'u_cons_interior_1', 'tm_reg_interior')", (acc,))
    conn.close()


def test_consultor_sees_only_own_deals():
    """Valida escopo 'self': Consultor Capital 1 vê apenas seu deal 'd-scope-cap-1'."""
    setup_scoping_fixture()
    headers = {"X-User-Id": "u_cons_capital_1"}
    res = client.get("/api/v1/deals", headers=headers)
    assert res.status_code == 200
    deals = res.json()["deals"]
    deal_ids = [d["id"] for d in deals]
    assert "d-scope-cap-1" in deal_ids
    assert "d-scope-cap-2" not in deal_ids
    assert "d-scope-int-1" not in deal_ids


def test_regional_manager_sees_all_team_deals():
    """Valida escopo 'team': Gestor Regional Capital vê deals do Consultor 1 e 2, mas não do Interior."""
    setup_scoping_fixture()
    headers = {"X-User-Id": "u_greg_capital"}
    res = client.get("/api/v1/deals", headers=headers)
    assert res.status_code == 200
    deals = res.json()["deals"]
    deal_ids = [d["id"] for d in deals]
    assert "d-scope-cap-1" in deal_ids
    assert "d-scope-cap-2" in deal_ids
    assert "d-scope-int-1" not in deal_ids


def test_district_manager_sees_recursive_subtree_deals():
    """Valida escopo 'subtree': Gestor Distrital vê deals de Capital E Interior recursivamente."""
    setup_scoping_fixture()
    headers = {"X-User-Id": "u_gdist_sp"}
    res = client.get("/api/v1/deals", headers=headers)
    assert res.status_code == 200
    deals = res.json()["deals"]
    deal_ids = [d["id"] for d in deals]
    assert "d-scope-cap-1" in deal_ids
    assert "d-scope-cap-2" in deal_ids
    assert "d-scope-int-1" in deal_ids


def test_superadmin_god_sees_everything():
    """Valida que o Super Admin (User God) tem bypass irrestrito de escopo."""
    setup_scoping_fixture()
    headers = {"X-User-Id": "usr-superadmin-god"}
    res = client.get("/api/v1/deals", headers=headers)
    assert res.status_code == 200
    deals = res.json()["deals"]
    deal_ids = [d["id"] for d in deals]
    assert "d-scope-cap-1" in deal_ids
    assert "d-scope-cap-2" in deal_ids
    assert "d-scope-int-1" in deal_ids
