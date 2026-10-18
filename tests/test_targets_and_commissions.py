# -*- coding: utf-8 -*-
"""
Test Suite: Metas Comerciais, Sugestão Algorítmica e Comissionamento Multinível (Lei #5, Lei #13)
Valida:
1. Sugestão algorítmica de metas com evolução progressiva (+15% sobre histórico de vendas).
2. Criação de metas cascateadas e cálculo de atingimento em tempo real a partir de deals ganhos.
3. Regras de comissionamento por papel corporativo e extrato consolidado.
4. Presets odontológicos de Lead Scoring e customização de tiers (Tier A / B / C).
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_targets_fixture():
    """Configura ambiente limpo e determinístico para testes de metas e comissões."""
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = OFF;")
    with conn:
        acc = "0f14ffff"
        # Garante role de consultor e gerente regional
        conn.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES ('role-cons-odonto', ?, 'Consultor Implantes', 'self', 0)", (acc,))
        conn.execute("INSERT OR IGNORE INTO roles (id, account_id, name, default_data_scope, is_admin) VALUES ('role-greg-odonto', ?, 'Gerente Regional SP', 'team', 0)", (acc,))
        
        # Garante time
        conn.execute("INSERT OR IGNORE INTO business_units (id, account_id, name, code) VALUES ('bu-cir-test', ?, 'Divisão Cirúrgica', 'CIR')", (acc,))
        conn.execute("INSERT OR IGNORE INTO teams (id, account_id, business_unit_id, name) VALUES ('team-capital-test', ?, 'bu-cir-test', 'Equipe Capital')", (acc,))

        # Usuários
        conn.execute(
            "INSERT OR REPLACE INTO users (id, account_id, team_id, role_id, name, email, role, is_superadmin) "
            "VALUES ('u-vendedor-1', ?, 'team-capital-test', 'role-cons-odonto', 'Dr. Vendedor Campo', 'vend1@empresa.com', 'Consultor', 0)", (acc,)
        )
        conn.execute(
            "INSERT OR REPLACE INTO users (id, account_id, team_id, role_id, name, email, role, is_superadmin) "
            "VALUES ('u-gestor-1', ?, 'team-capital-test', 'role-greg-odonto', 'Gestor Regional Marcelo', 'gest1@empresa.com', 'Gerente Regional', 0)", (acc,)
        )

        # Deals ganhos (stage_id = 105)
        for tbl in ["deal_audit_logs", "deal_objections", "deal_discount_requests", "deal_contracts", "call_transcriptions", "call_recordings"]:
            conn.execute(f"DELETE FROM {tbl} WHERE deal_id IN ('d-won-1', 'd-won-2')")
        conn.execute("DELETE FROM deals WHERE id IN ('d-won-1', 'd-won-2')")
        conn.execute(
            "INSERT INTO deals (id, account_id, pipeline_id, stage_id, title, value, company, contact_name, priority, owner_id, team_id) "
            "VALUES ('d-won-1', ?, 1, 105, 'Venda 100 Implantes Cone Morse', 80000.0, 'Clínica Odonto Center', 'Dr. André', 'alta', 'u-vendedor-1', 'team-capital-test')",
            (acc,)
        )
        conn.execute(
            "INSERT INTO deals (id, account_id, pipeline_id, stage_id, title, value, company, contact_name, priority, owner_id, team_id) "
            "VALUES ('d-won-2', ?, 1, 105, 'Kit Cirúrgico Completo Grand Morse', 40000.0, 'Hospital Buco Sul', 'Dra. Denise', 'alta', 'u-vendedor-1', 'team-capital-test')",
            (acc,)
        )

        # Limpar metas anteriores de teste
        conn.execute("DELETE FROM sales_targets WHERE account_id = ? AND period = '2026-TEST'", (acc,))
    conn.close()


def test_algorithmic_target_suggestion():
    """Valida o motor algorítmico de sugestão de metas com base histórica e fator de crescimento."""
    res = client.get(
        "/api/v1/hierarchy/targets/suggestion?entity_type=user&entity_id=u-vendedor-1&period=2026-TEST&growth_rate_pct=15.0"
    )
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["entity_type"] == "user"
    assert data["entity_id"] == "u-vendedor-1"
    # Base histórica: 80.000 + 40.000 = 120.000
    assert data["historical_base"] == 120000.0
    assert data["growth_rate_pct"] == 15.0
    # Sugerida: 120.000 * 1.15 = 138.000
    assert data["suggested_target"] == 138000.0
    assert "+15.0%" in data["explanation"]


def test_create_target_and_real_time_achievement():
    """Valida cadastro de meta e apuração de atingimento em tempo real dos deals ganhos."""
    payload = {
        "period": "2026-TEST",
        "user_id": "u-vendedor-1",
        "target_amount": 100000.0,
        "calculation_basis": "algoritmica_sugerida",
        "growth_rate_pct": 15.0
    }
    create_res = client.post("/api/v1/hierarchy/targets", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()

    assert created["target_amount"] == 100000.0
    assert created["entity_name"] == "Dr. Vendedor Campo"
    assert created["achieved_amount"] == 120000.0  # 80k + 40k dos deals ganhos
    assert created["achievement_rate_pct"] == 120.0  # 120% da meta atingida!


def test_commission_rules_and_statement_with_supermeta_accelerator():
    """Valida regra de comissão com acelerador de supermeta (> 100% ativa taxa diferenciada)."""
    # 1. Configurar regra: 5.0% base, acelerador em 100% da meta pula para 7.5%
    rule_payload = {
        "role_id": "role-cons-odonto",
        "base_percentage": 5.0,
        "accelerator_threshold_pct": 100.0,
        "accelerator_percentage": 7.5
    }
    rule_res = client.post("/api/v1/hierarchy/commissions/rules", json=rule_payload)
    assert rule_res.status_code == 201
    rule_data = rule_res.json()
    assert rule_data["base_percentage"] == 5.0
    assert rule_data["accelerator_percentage"] == 7.5

    # 2. Cadastrar meta de 100.000 para o vendedor
    client.post("/api/v1/hierarchy/targets", json={
        "period": "2026-TEST",
        "user_id": "u-vendedor-1",
        "target_amount": 100000.0
    })

    # 3. Gerar extrato de comissão
    statement_res = client.get("/api/v1/hierarchy/commissions/statement?user_id=u-vendedor-1&period=2026-TEST")
    assert statement_res.status_code == 200
    st = statement_res.json()

    assert st["user_name"] == "Dr. Vendedor Campo"
    assert st["achieved_amount"] == 120000.0
    assert st["achievement_rate_pct"] == 120.0
    assert st["is_accelerated"] is True  # Acelerador ativado!
    # Comissão calculada a 7.5% de 120.000 = 9.000,00
    assert st["total_commission"] == 9000.0
    assert len(st["items"]) == 2
    assert st["items"][0]["commission_rate_pct"] == 7.5


def test_scoring_presets_and_custom_tiers_recalculation():
    """Valida aplicação de presets de Lead Scoring e cálculo com tiers customizados."""
    # 1. Listar presets disponíveis
    presets_res = client.get("/api/v1/scoring/presets")
    assert presets_res.status_code == 200
    presets = presets_res.json()
    assert len(presets) == 4
    keys = [p["preset_key"] for p in presets]
    assert "implantes_cirurgia_premium" in keys
    assert "ensino_academico" in keys

    # 2. Aplicar preset "implantes_cirurgia_premium"
    apply_res = client.post("/api/v1/scoring/presets/apply", json={"preset_key": "implantes_cirurgia_premium"})
    assert apply_res.status_code == 200
    assert apply_res.json()["success"] is True

    # 3. Recalcular scores com Tiers customizados pela empresa (Tier A >= 75, Tier B >= 45)
    recalc_res = client.post("/api/v1/scoring/recalculate", json={"tier_a_min": 75, "tier_b_min": 45})
    assert recalc_res.status_code == 200
    recalc_data = recalc_res.json()

    assert recalc_data["recalculated_count"] > 0
    assert "ranked_leads" in recalc_data
    # Contatos odontológicos com CRO e > 50/mês devem receber alta pontuação
    top_lead = recalc_data["ranked_leads"][0]
    assert top_lead["score"] >= 50
    assert top_lead["tier"] in ("Tier A", "Tier B")


def test_frontend_targets_and_scoring_presets_elements():
    """Valida presença dos novos elementos de interface no frontend servido em /."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    # 1. Aba Metas & Comissões na view hierarchy
    assert 'id="btn-tab-hierarchy-targets"' in html
    assert 'id="tab-content-hierarchy-targets"' in html
    assert 'id="targets-table"' in html
    assert 'id="target-suggestion-user"' in html
    assert 'id="target-modal"' in html
    # 2. Presets e Tiers Customizáveis em Scoring ICP
    assert 'id="scoring-tier-a-min"' in html
    assert 'id="scoring-tier-b-min"' in html
    assert "Implantes Premium" in html
    assert "Acadêmico & Mandic" in html


