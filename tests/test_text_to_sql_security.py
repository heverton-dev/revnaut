# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-30: Agente Analítico Conversacional Text-to-SQL (Web & WhatsApp da Diretoria)
Proteção 100% determinística contra mutações, SQL Injection e injeção de RLS baseada em RBAC.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection, init_db
from src.features.intelligence import text_to_sql_agent


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_text_to_sql_data():
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO business_units (id, account_id, name, code)
            VALUES ('bu-sql-01', '0f14ffff', 'Divisão Implantes', 'BU_IMPLANTES')
        """)
        cur.execute("""
            INSERT OR REPLACE INTO teams (id, account_id, name, business_unit_id, parent_id)
            VALUES ('team-sql-pr', '0f14ffff', 'Regional Curitiba', 'bu-sql-01', NULL)
        """)
        cur.execute("""
            INSERT OR REPLACE INTO users (
                id, account_id, name, email, role, team_id, custom_data_scope, is_active, is_superadmin
            ) VALUES (
                'usr-sql-consultant', '0f14ffff', 'Marcos Consultor', 'marcos@revnaut.com',
                'Consultor Comercial', 'team-sql-pr', 'self', 1, 0
            )
        """)
        cur.execute("""
            INSERT OR REPLACE INTO users (
                id, account_id, name, email, role, custom_data_scope, is_active, is_superadmin
            ) VALUES (
                'usr-sql-director', '0f14ffff', 'Carlos Diretor', 'carlos@revnaut.com',
                'Diretor Geral', 'tenant_global', 1, 0
            )
        """)
        cur.execute("""
            INSERT OR REPLACE INTO deals (
                id, account_id, title, value, stage_id, pipeline_id, owner_id, team_id, company, contact_name
            ) VALUES (
                'deal-sql-01', '0f14ffff', 'Kit Cone Morse Especial', 30000.0, 101, 1,
                'usr-sql-consultant', 'team-sql-pr', 'Clínica Odonto Sul', 'Dr. Odonto'
            )
        """)
        conn.commit()
    finally:
        conn.close()


def test_legitimate_nl_query_revenue():
    res = text_to_sql_agent.execute_analytical_query(
        natural_language_query="Qual o total faturado em deals?",
        user_id="usr-sql-director",
        account_id="0f14ffff"
    )

    assert res["is_safe"] is True
    assert "total_faturamento" in res["columns"]
    assert len(res["rows"]) == 1
    assert res["rows"][0]["total_faturamento"] >= 30000.0
    assert res["execution_time_ms"] < 3000.0


def test_legitimate_nl_query_regional_ranking():
    res = text_to_sql_agent.execute_analytical_query(
        natural_language_query="Qual o faturamento por regional?",
        user_id="usr-sql-director",
        account_id="0f14ffff"
    )

    assert res["is_safe"] is True
    assert "regional" in res["columns"]
    assert "faturamento" in res["columns"]
    assert len(res["rows"]) >= 1
    assert "Regional Curitiba" in res["chart_labels"]


def test_security_blocks_destructive_drop_table():
    malicious_query = "SELECT * FROM users; DROP TABLE deals;"
    with pytest.raises(ValueError, match="Múltiplas instruções SQL ou comandos concatenados"):
        text_to_sql_agent.execute_analytical_query(
            raw_sql=malicious_query,
            user_id="usr-sql-director",
            account_id="0f14ffff"
        )


def test_security_blocks_destructive_delete():
    malicious_query = "DELETE FROM deals WHERE 1=1"
    with pytest.raises(ValueError, match="Apenas consultas de leitura analítica"):
        text_to_sql_agent.execute_analytical_query(
            raw_sql=malicious_query,
            user_id="usr-sql-director",
            account_id="0f14ffff"
        )


def test_security_blocks_mutation_update_and_insert():
    with pytest.raises(ValueError, match="Apenas consultas de leitura analítica"):
        text_to_sql_agent.execute_analytical_query(
            raw_sql="UPDATE users SET is_superadmin = 1 WHERE id = 'usr-hacker'",
            user_id="usr-sql-director"
        )

    with pytest.raises(ValueError, match="Apenas consultas de leitura analítica"):
        text_to_sql_agent.execute_analytical_query(
            raw_sql="INSERT INTO users (id, name) VALUES ('bad', 'hacker')",
            user_id="usr-sql-director"
        )


def test_security_blocks_password_hash_extraction():
    with pytest.raises(ValueError, match="coluna confidencial bloqueada"):
        text_to_sql_agent.execute_analytical_query(
            raw_sql="SELECT id, email, password_hash FROM users",
            user_id="usr-sql-director"
        )


def test_rls_scoping_applied_to_consultant():
    res = text_to_sql_agent.execute_analytical_query(
        raw_sql="SELECT id, title, value FROM deals",
        user_id="usr-sql-consultant",
        account_id="0f14ffff"
    )

    assert res["is_safe"] is True
    # Validar que a cláusula RLS de proprietário foi injetada no SQL executado
    assert "owner_id = 'usr-sql-consultant'" in res["sql_executed"]


def test_text_to_sql_api_endpoints(client):
    # 1. Consulta Legítima
    payload_valid = {
        "natural_language_query": "Qual o faturamento total da empresa?",
        "user_id": "usr-sql-director"
    }
    res_v = client.post("/api/v1/intelligence/bi/text-to-sql", json=payload_valid)
    assert res_v.status_code == 200
    v_data = res_v.json()
    assert v_data["is_safe"] is True
    assert len(v_data["rows"]) >= 1

    # 2. Tentativa Maliciosa (Bloqueio 400)
    payload_malicious = {
        "raw_sql": "SELECT * FROM deals; DROP TABLE contacts;",
        "user_id": "usr-sql-director"
    }
    res_m = client.post("/api/v1/intelligence/bi/text-to-sql", json=payload_malicious)
    assert res_m.status_code == 400
    assert "Múltiplas instruções SQL ou comandos concatenados" in res_m.json()["detail"]
