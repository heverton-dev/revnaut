# -*- coding: utf-8 -*-
"""
TDD for [TICKET-04] RBAC Dual Hierarchy (Field Sales vs Inside Sales)
Validates:
- Visibility sharing: Inside Sales analyst views deals for both Field Consultants
- Isolation: Field Consultant A cannot view Field Consultant B deals
- Commission split calculation: split_commission_field_pct + split_commission_inside_pct = 100%
- Database columns field_owner_id, inside_owner_id, split_commission_field_pct in deals
"""

import pytest
from src.core.database import get_connection, init_db
from src.core.security import get_user_context, resolve_data_scope_clause
from src.features.deals.service import calculate_split_commissions


def setup_module():
    init_db()


def test_dual_field_inside_data_scoping_visibility():
    """
    Cenário:
    - 1 Gerente Regional (team_id: 'team_sp')
    - 2 Consultores de Campo: Field A (usr_field_a), Field B (usr_field_b)
    - 1 Analista de Inside Sales: Inside SP (usr_inside_sp)
    """
    conn = get_connection()
    try:
        # Cria times e papéis se necessário
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO accounts (id, name) VALUES ('0f14ffff', 'Sales Rocket')")
        cur.execute("INSERT OR IGNORE INTO business_units (id, account_id, name, code) VALUES ('bu_sp', '0f14ffff', 'BU São Paulo', 'SP01')")
        cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope) VALUES ('role_field', '0f14ffff', 'Consultor Field', 'self')")
        cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope) VALUES ('role_inside', '0f14ffff', 'Analista Inside', 'self')")
        cur.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope) VALUES ('role_manager', '0f14ffff', 'Gerente Regional', 'team')")

        cur.execute("INSERT OR IGNORE INTO teams (id, account_id, business_unit_id, name) VALUES ('team_sp', '0f14ffff', 'bu_sp', 'Filial São Paulo')")

        # Usuários
        cur.execute("INSERT OR REPLACE INTO users (id, account_id, name, email, role_id, team_id, custom_data_scope) VALUES ('usr_field_a', '0f14ffff', 'Consultor A', 'field_a@test.com', 'role_field', 'team_sp', 'self')")
        cur.execute("INSERT OR REPLACE INTO users (id, account_id, name, email, role_id, team_id, custom_data_scope) VALUES ('usr_field_b', '0f14ffff', 'Consultor B', 'field_b@test.com', 'role_field', 'team_sp', 'self')")
        cur.execute("INSERT OR REPLACE INTO users (id, account_id, name, email, role_id, team_id, custom_data_scope) VALUES ('usr_inside_sp', '0f14ffff', 'Analista Inside SP', 'inside@test.com', 'role_inside', 'team_sp', 'self')")
        cur.execute("INSERT OR REPLACE INTO users (id, account_id, name, email, role_id, team_id, custom_data_scope) VALUES ('usr_mgr_sp', '0f14ffff', 'Gerente SP', 'mgr@test.com', 'role_manager', 'team_sp', 'team')")

        # Cria deals com atribuição dual:
        # Deal 1: Field A titular, Inside SP co-piloto
        # Deal 2: Field B titular, Inside SP co-piloto
        cur.execute("""
            INSERT OR REPLACE INTO deals (
                id, account_id, pipeline_id, stage_id, title, value, company, contact_name,
                owner_id, field_owner_id, inside_owner_id, team_id
            ) VALUES
            ('deal_dual_1', '0f14ffff', 1, 101, 'Cirurgia Mandibular', 25000.0, 'Clínica A', 'Dr. Alpha', 'usr_field_a', 'usr_field_a', 'usr_inside_sp', 'team_sp'),
            ('deal_dual_2', '0f14ffff', 1, 101, 'Protocolo Superior', 40000.0, 'Clínica B', 'Dr. Beta', 'usr_field_b', 'usr_field_b', 'usr_inside_sp', 'team_sp')
        """)
        conn.commit()

        # 1. Consulta para Consultor Field A
        ctx_field_a = get_user_context(conn, "usr_field_a", "0f14ffff")
        sql_clause_a, params_a = resolve_data_scope_clause(conn, ctx_field_a, "0f14ffff")
        cur.execute(f"SELECT id FROM deals WHERE {sql_clause_a}", params_a)
        deals_a = [r["id"] for r in cur.fetchall()]
        assert "deal_dual_1" in deals_a, "Field A deve ver deal 1 onde é field_owner"
        assert "deal_dual_2" not in deals_a, "Field A NÃO deve ver deal 2 do Field B"

        # 2. Consulta para Analista Inside SP (co-piloto em ambos os deals)
        ctx_inside = get_user_context(conn, "usr_inside_sp", "0f14ffff")
        sql_clause_inside, params_inside = resolve_data_scope_clause(conn, ctx_inside, "0f14ffff")
        cur.execute(f"SELECT id FROM deals WHERE {sql_clause_inside}", params_inside)
        deals_inside = [r["id"] for r in cur.fetchall()]
        assert "deal_dual_1" in deals_inside, "Inside SP deve ver deal 1 onde é inside_owner"
        assert "deal_dual_2" in deals_inside, "Inside SP deve ver deal 2 onde é inside_owner"

        # 3. Consulta para Gerente Regional SP (escopo team)
        ctx_mgr = get_user_context(conn, "usr_mgr_sp", "0f14ffff")
        sql_clause_mgr, params_mgr = resolve_data_scope_clause(conn, ctx_mgr, "0f14ffff")
        cur.execute(f"SELECT id FROM deals WHERE {sql_clause_mgr}", params_mgr)
        deals_mgr = [r["id"] for r in cur.fetchall()]
        assert "deal_dual_1" in deals_mgr
        assert "deal_dual_2" in deals_mgr

    finally:
        conn.close()


def test_split_commission_calculation():
    """Garante cálculo de comissão bipartida (ex: 70% Field, 30% Inside)."""
    commissions = calculate_split_commissions(
        total_value=100000.0,
        base_rate_pct=5.0,  # 5% de R$ 100.000 = R$ 5.000 de comissão total
        field_pct=70.0,
        inside_pct=30.0,
    )
    assert commissions["total_commission"] == 5000.0
    assert commissions["field_commission"] == 3500.0
    assert commissions["inside_commission"] == 1500.0
    assert commissions["field_commission"] + commissions["inside_commission"] == 5000.0
