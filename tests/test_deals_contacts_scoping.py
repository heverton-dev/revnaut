# -*- coding: utf-8 -*-
"""
Testes TDD - Data Scoping em Deals e Contatos (Row-Level Security)
Valida a restrição matemática de isolamento hierárquico nas rotas:
- GET /api/v1/deals
- GET /api/v1/contacts
"""

from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection

client = TestClient(app)


def setup_deals_contacts_scoping_fixture():
    """Insere fixture com deals e contatos distribuídos em diferentes equipes e consultores."""
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        acc = "0f14ffff"

        # 1. Deals de teste atribuídos a donos e equipes
        cur.execute("INSERT OR REPLACE INTO deals (id, account_id, pipeline_id, stage_id, title, value, company, contact_name, priority, owner_id, team_id) VALUES "
                    "('d-scope-cap-1', ?, 1, 101, 'Venda Kits Neodent Cap 1', 60000.0, 'Clínica Sorriso SP', 'Dr. Roberto', 'alta', 'u_cons_capital_1', 'tm_reg_capital')", (acc,))
        cur.execute("INSERT OR REPLACE INTO deals (id, account_id, pipeline_id, stage_id, title, value, company, contact_name, priority, owner_id, team_id) VALUES "
                    "('d-scope-cap-2', ?, 1, 101, 'Venda BLX Straumann Cap 2', 45000.0, 'Clínica Jardins', 'Dra. Camila', 'media', 'u_cons_capital_2', 'tm_reg_capital')", (acc,))
        cur.execute("INSERT OR REPLACE INTO deals (id, account_id, pipeline_id, stage_id, title, value, company, contact_name, priority, owner_id, team_id) VALUES "
                    "('d-scope-int-1', ?, 1, 101, 'Venda Implantes Campinas', 80000.0, 'Centro Odonto Campinas', 'Dr. Fabio', 'alta', 'u_cons_interior_1', 'tm_reg_interior')", (acc,))

        # 2. Contatos de teste atribuídos
        cur.execute("INSERT OR REPLACE INTO contacts (id, account_id, name, email, phone, company, score, cro, cro_uf, specialty, owner_id, team_id) VALUES "
                    "(101, ?, 'Dr. Cirurgião Capital 1', 'cir1@capital.com', '+55 11 91111', 'Clínica Sorriso SP', 85, 'SP-10101', 'SP', 'Implantodontia', 'u_cons_capital_1', 'tm_reg_capital')", (acc,))
        cur.execute("INSERT OR REPLACE INTO contacts (id, account_id, name, email, phone, company, score, cro, cro_uf, specialty, owner_id, team_id) VALUES "
                    "(102, ?, 'Dra. Cirurgiã Capital 2', 'cir2@capital.com', '+55 11 92222', 'Clínica Jardins', 90, 'SP-10202', 'SP', 'Prótese Dentária', 'u_cons_capital_2', 'tm_reg_capital')", (acc,))
        cur.execute("INSERT OR REPLACE INTO contacts (id, account_id, name, email, phone, company, score, cro, cro_uf, specialty, owner_id, team_id) VALUES "
                    "(103, ?, 'Dr. Cirurgião Interior 1', 'cir1@interior.com', '+55 19 93333', 'Centro Odonto Campinas', 78, 'SP-10303', 'SP', 'Periodontia', 'u_cons_interior_1', 'tm_reg_interior')", (acc,))
    conn.close()


def test_deals_consultor_sees_only_own_deals():
    """Valida escopo 'self': Consultor Capital 1 vê apenas o deal d-scope-cap-1."""
    setup_deals_contacts_scoping_fixture()
    headers = {"X-User-Id": "u_cons_capital_1"}
    res = client.get("/api/v1/deals", headers=headers)
    assert res.status_code == 200
    deals = res.json()["deals"]
    deal_ids = [d["id"] for d in deals]
    assert "d-scope-cap-1" in deal_ids
    assert "d-scope-cap-2" not in deal_ids
    assert "d-scope-int-1" not in deal_ids


def test_deals_regional_manager_sees_team_deals():
    """Valida escopo 'team': Gestor Regional vê deals do Consultor 1 e 2, mas não do Interior."""
    setup_deals_contacts_scoping_fixture()
    headers = {"X-User-Id": "u_greg_capital"}
    res = client.get("/api/v1/deals", headers=headers)
    assert res.status_code == 200
    deals = res.json()["deals"]
    deal_ids = [d["id"] for d in deals]
    assert "d-scope-cap-1" in deal_ids
    assert "d-scope-cap-2" in deal_ids
    assert "d-scope-int-1" not in deal_ids


def test_deals_district_manager_sees_subtree_deals():
    """Valida escopo 'subtree': Gestor Distrital SP vê Capital 1, Capital 2 e Interior 1."""
    setup_deals_contacts_scoping_fixture()
    headers = {"X-User-Id": "u_gdist_sp"}
    res = client.get("/api/v1/deals", headers=headers)
    assert res.status_code == 200
    deals = res.json()["deals"]
    deal_ids = [d["id"] for d in deals]
    assert "d-scope-cap-1" in deal_ids
    assert "d-scope-cap-2" in deal_ids
    assert "d-scope-int-1" in deal_ids


def test_contacts_scoping_isolation():
    """Valida escopo 'self' e 'team' na rota /api/v1/contacts."""
    setup_deals_contacts_scoping_fixture()

    # 1. Consultor Capital 1 vê apenas contato 101
    res_cons = client.get("/api/v1/contacts", headers={"X-User-Id": "u_cons_capital_1"})
    assert res_cons.status_code == 200
    cons_contacts = res_cons.json()
    cons_ids = [c["id"] for c in cons_contacts]
    assert 101 in cons_ids
    assert 102 not in cons_ids
    assert 103 not in cons_ids

    # 2. Gestor Regional Capital vê contatos 101 e 102, mas não 103
    res_mgr = client.get("/api/v1/contacts", headers={"X-User-Id": "u_greg_capital"})
    assert res_mgr.status_code == 200
    mgr_contacts = res_mgr.json()
    mgr_ids = [c["id"] for c in mgr_contacts]
    assert 101 in mgr_ids
    assert 102 in mgr_ids
    assert 103 not in mgr_ids
