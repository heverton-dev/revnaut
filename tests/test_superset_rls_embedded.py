# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-29: Integração do Apache Superset Embedded com Guest Tokens JWT e Row-Level Security (RLS)
"""

import jwt
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.config import SUPERSET_SECRET_KEY
from src.core.database import get_connection, init_db
from src.features.intelligence import superset_embedded


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_users_and_scopes():
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        # 1. Usuário Consultor Regional PR (Escopo Self)
        cur.execute("""
            INSERT OR REPLACE INTO users (
                id, account_id, name, email, role, custom_data_scope, is_active, is_superadmin
            ) VALUES (
                'usr-consultant-pr', '0f14ffff', 'Marcos Consultor PR', 'marcos.pr@revnaut.com',
                'Consultor Comercial', 'self', 1, 0
            )
        """)

        # 2. Usuário Diretor Nacional (Escopo Tenant Global)
        cur.execute("""
            INSERT OR REPLACE INTO users (
                id, account_id, name, email, role, custom_data_scope, is_active, is_superadmin
            ) VALUES (
                'usr-director-br', '0f14ffff', 'Carlos Diretor Nacional', 'carlos.dir@revnaut.com',
                'Diretor Geral', 'tenant_global', 1, 0
            )
        """)

        # 3. Time Regional e Gestor de Time (Escopo Team)
        cur.execute("""
            INSERT OR IGNORE INTO business_units (id, account_id, name, code)
            VALUES ('bu-bi-01', '0f14ffff', 'Divisão Cirúrgica', 'BU_CIRURGIA_DIRETA')
        """)
        cur.execute("""
            INSERT OR REPLACE INTO teams (id, account_id, name, business_unit_id, parent_id)
            VALUES ('team-pr-sul', '0f14ffff', 'Regional Paraná e Sul', 'bu-bi-01', NULL)
        """)

        cur.execute("""
            INSERT OR REPLACE INTO users (
                id, account_id, name, email, role, team_id, custom_data_scope, is_active, is_superadmin
            ) VALUES (
                'usr-manager-pr', '0f14ffff', 'Fernanda Gerente Sul', 'fernanda.mgr@revnaut.com',
                'Gerente Regional', 'team-pr-sul', 'team', 1, 0
            )
        """)

        # Seed de Deals para exportação analítica
        cur.execute("""
            INSERT OR REPLACE INTO deals (
                id, account_id, title, value, stage_id, pipeline_id, owner_id, company, contact_name
            ) VALUES (
                'deal-bi-01', '0f14ffff', 'Consignação Clínica Curitiba', 15000.0, 101, 1, 'usr-consultant-pr',
                'Clínica Curitiba Odonto', 'Dr. Curitiba'
            )
        """)


        conn.commit()
    finally:
        conn.close()


def test_generate_guest_token_for_regional_consultant_rls():
    res = superset_embedded.generate_superset_guest_token(
        user_id="usr-consultant-pr",
        dashboard_id="dash-ind-consignment",
        dashboard_type="industry_consignment",
        account_id="0f14ffff"
    )

    assert "token" in res
    assert res["dashboard_id"] == "dash-ind-consignment"
    assert res["expires_in_seconds"] == 3600

    # Decodificar e auditar o payload JWT e a cláusula RLS injetada
    payload = jwt.decode(res["token"], SUPERSET_SECRET_KEY, algorithms=["HS256"])
    assert payload["resources"][0]["id"] == "dash-ind-consignment"
    assert payload["user"]["username"] == "guest_usr-consultant-pr"

    rls_clause = payload["rls"][0]["clause"]
    assert "account_id = '0f14ffff'" in rls_clause
    assert "owner_id = 'usr-consultant-pr'" in rls_clause


def test_generate_guest_token_for_national_director_full_rls():
    res = superset_embedded.generate_superset_guest_token(
        user_id="usr-director-br",
        dashboard_id="dash-national-overview",
        dashboard_type="industry_consignment",
        account_id="0f14ffff"
    )

    payload = jwt.decode(res["token"], SUPERSET_SECRET_KEY, algorithms=["HS256"])
    rls_clause = payload["rls"][0]["clause"]

    # Diretor Nacional não deve estar restrito a um consultor individual
    assert rls_clause == "account_id = '0f14ffff'"
    assert "owner_id" not in rls_clause


def test_generate_guest_token_for_superadmin_god():
    res = superset_embedded.generate_superset_guest_token(
        user_id="usr-superadmin-god",
        dashboard_id="dash-master-admin",
        dashboard_type="industry_consignment",
        account_id="0f14ffff"
    )

    payload = jwt.decode(res["token"], SUPERSET_SECRET_KEY, algorithms=["HS256"])
    rls_clause = payload["rls"][0]["clause"]
    assert rls_clause == "1=1"


def test_generate_guest_token_for_regional_manager_team_rls():
    res = superset_embedded.generate_superset_guest_token(
        user_id="usr-manager-pr",
        dashboard_id="dash-regional-pr",
        dashboard_type="industry_consignment",
        account_id="0f14ffff"
    )

    payload = jwt.decode(res["token"], SUPERSET_SECRET_KEY, algorithms=["HS256"])
    rls_clause = payload["rls"][0]["clause"]
    assert "team_id = 'team-pr-sul'" in rls_clause


def test_export_analytics_dataset():
    res = superset_embedded.export_analytics_dataset(
        dataset_name="deals_funnel",
        user_id="usr-director-br",
        format="csv",
        account_id="0f14ffff"
    )

    assert res["status"] == "COMPLETED"
    assert res["format"] == "csv"
    assert res["r2_storage_key"].startswith("datasets/0f14ffff/deals_funnel_")
    assert res["record_count"] >= 1
    assert "deals_funnel" in res["download_url"]


def test_superset_bi_api_endpoints(client):
    # 1. POST /api/v1/intelligence/bi/guest-token
    payload_token = {
        "user_id": "usr-consultant-pr",
        "dashboard_id": "dash-api-test",
        "dashboard_type": "industry_consignment"
    }
    res_t = client.post(
        "/api/v1/intelligence/bi/guest-token",
        json=payload_token,
        headers={"X-User-Id": "usr-superadmin-god"},
    )
    assert res_t.status_code == 200
    t_data = res_t.json()
    assert "token" in t_data
    assert t_data["dashboard_id"] == "dash-api-test"
    assert "owner_id = 'usr-consultant-pr'" in t_data["rls_clause"]

    # 2. POST /api/v1/intelligence/bi/export-dataset
    payload_export = {
        "dataset_name": "deals_funnel",
        "user_id": "usr-consultant-pr",
        "format": "csv"
    }
    res_e = client.post("/api/v1/intelligence/bi/export-dataset", json=payload_export)
    assert res_e.status_code == 200
    e_data = res_e.json()
    assert e_data["status"] == "COMPLETED"
    assert e_data["format"] == "csv"
    assert e_data["record_count"] >= 1
