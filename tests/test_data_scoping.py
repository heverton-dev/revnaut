# -*- coding: utf-8 -*-
"""
Testes TDD - TICKET-03: Motor Central de Data Scoping no Backend
Valida a restrição matemática em nível de linha (Row-Level Security)
entre Consultores, Gestores Regionais, Distritais e Super Admin.
"""

from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection

client = TestClient(app)


def setup_scoping_fixture():
    """Configura fixture hierárquica completa para testes de isolamento."""
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

        # 5. Caixas Consignadas atribuídas
        cur.execute("INSERT OR REPLACE INTO consignments (id, account_id, contact_id, clinic_name, box_code, total_items, consumed_items, owner_id, team_id) VALUES "
                    "('box-scope-cap-1', ?, 1, 'Clínica Capital A', 'BOX-CAP-1', 50, 0, 'u_cons_capital_1', 'tm_reg_capital')", (acc,))
        cur.execute("INSERT OR REPLACE INTO consignments (id, account_id, contact_id, clinic_name, box_code, total_items, consumed_items, owner_id, team_id) VALUES "
                    "('box-scope-cap-2', ?, 2, 'Clínica Capital B', 'BOX-CAP-2', 50, 0, 'u_cons_capital_2', 'tm_reg_capital')", (acc,))
        cur.execute("INSERT OR REPLACE INTO consignments (id, account_id, contact_id, clinic_name, box_code, total_items, consumed_items, owner_id, team_id) VALUES "
                    "('box-scope-int-1', ?, 3, 'Clínica Interior A', 'BOX-INT-1', 50, 0, 'u_cons_interior_1', 'tm_reg_interior')", (acc,))
    conn.close()


def test_consultor_sees_only_own_consignments():
    """Valida escopo 'self': Consultor Capital 1 vê apenas sua caixa 'BOX-CAP-1'."""
    setup_scoping_fixture()
    headers = {"X-User-Id": "u_cons_capital_1"}
    res = client.get("/api/v1/consignments", headers=headers)
    assert res.status_code == 200
    boxes = res.json()
    box_codes = [b["box_code"] for b in boxes]
    assert "BOX-CAP-1" in box_codes
    assert "BOX-CAP-2" not in box_codes
    assert "BOX-INT-1" not in box_codes


def test_regional_manager_sees_all_team_consignments():
    """Valida escopo 'team': Gestor Regional Capital vê caixas do Consultor 1 e 2, mas não do Interior."""
    setup_scoping_fixture()
    headers = {"X-User-Id": "u_greg_capital"}
    res = client.get("/api/v1/consignments", headers=headers)
    assert res.status_code == 200
    boxes = res.json()
    box_codes = [b["box_code"] for b in boxes]
    assert "BOX-CAP-1" in box_codes
    assert "BOX-CAP-2" in box_codes
    assert "BOX-INT-1" not in box_codes


def test_district_manager_sees_recursive_subtree_consignments():
    """Valida escopo 'subtree': Gestor Distrital vê caixas de Capital E Interior recursivamente."""
    setup_scoping_fixture()
    headers = {"X-User-Id": "u_gdist_sp"}
    res = client.get("/api/v1/consignments", headers=headers)
    assert res.status_code == 200
    boxes = res.json()
    box_codes = [b["box_code"] for b in boxes]
    assert "BOX-CAP-1" in box_codes
    assert "BOX-CAP-2" in box_codes
    assert "BOX-INT-1" in box_codes


def test_superadmin_god_sees_everything():
    """Valida que o Super Admin (User God) tem bypass irrestrito de escopo."""
    setup_scoping_fixture()
    headers = {"X-User-Id": "usr-superadmin-god"}
    res = client.get("/api/v1/consignments", headers=headers)
    assert res.status_code == 200
    boxes = res.json()
    box_codes = [b["box_code"] for b in boxes]
    assert "BOX-CAP-1" in box_codes
    assert "BOX-CAP-2" in box_codes
    assert "BOX-INT-1" in box_codes
