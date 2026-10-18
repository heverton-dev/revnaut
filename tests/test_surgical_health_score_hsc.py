# -*- coding: utf-8 -*-
"""
Test Suite: Motor Determinístico de Health Score Cirúrgico (HSC) e Prevenção Ativa de Churn
Valida cálculo matemático ponderado do HSC, disparos de resgate (HSC < 40) e promoção MGM (HSC > 75).
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.core.database import get_connection, init_db
from src.features.intelligence import health_score_hsc
from src.features.intelligence.schemas import HealthScoreCalculateRequest


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_hsc_test_env():
    """Garante tabelas inicializadas e limpeza do ambiente de teste."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO accounts (id, name, plan)
            VALUES ('0f14ffff', 'Odonto Prime Test Tenant', 'Enterprise Scale')
        """)
        cur.execute("DELETE FROM kp_surgical_health_scores WHERE account_id = '0f14ffff'")
        conn.commit()
    finally:
        conn.close()


def test_hsc_critical_churn_risk_rescue_task_and_dentgo_voucher():
    """
    TDD Obrigatório:
    Simular cirurgião cujo intervalo entre cirurgias subiu de 7 para 35 dias e abriu 2 queixas técnicas (HSC = 28):
    F_cirurgica = 20.0, G_consignado = 30.0, S_atendimento = 25.0, E_canal = 60.0
    HSC = 0.4*(20) + 0.3*(30) + 0.2*(25) + 0.1*(60) = 8 + 9 + 5 + 6 = 28.0 (< 40).
    Deve gerar:
    - classification = 'CRITICAL_RISK'
    - tarefa urgente de resgate presencial em tasks
    - voucher de Frete Express Grátis no DENTGO
    - mensagem de engajamento no WhatsApp
    """
    req = HealthScoreCalculateRequest(
        partner_id="part-cir-99",
        partner_name="Dr. Renato Vasconcelos",
        f_cirurgica=20.0,
        g_consignado=30.0,
        s_atendimento=25.0,
        e_canal=60.0,
        baseline_interval_days=7.0,
        current_interval_days=35.0,
        rma_claims_count=2,
        account_id="0f14ffff"
    )

    result = health_score_hsc.calculate_surgical_health_score(req)

    assert result["hsc_score"] == 28.0
    assert result["classification"] == "CRITICAL_RISK"
    assert result["rescue_task_id"] is not None
    assert result["dentgo_voucher_code"] is not None
    assert "DENTGO-EXPRESS" in result["dentgo_voucher_code"]
    assert result["upsell_eligible"] is False
    assert result["mgm_eligible"] is False

    # Valida inserção da tarefa presencial urgente no banco SQLite
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (result["rescue_task_id"],))
        task_row = cur.fetchone()
        assert task_row is not None
        assert "Visita presencial urgente de resgate" in task_row["title"]
        assert task_row["priority"] == "alta"

        # Valida disparo da mensagem WhatsApp com o voucher
        cur.execute("""
            SELECT * FROM omnichannel_messages
            WHERE account_id = '0f14ffff' AND content LIKE ?
            ORDER BY created_at DESC LIMIT 1
        """, (f"%{result['dentgo_voucher_code']}%",))
        wa_row = cur.fetchone()
        assert wa_row is not None
        assert "Frete Express Gratis no DENTGO" in wa_row["content"]
    finally:
        conn.close()


def test_hsc_promoter_account_upsell_and_mgm_eligible():
    """
    Valida conta promotora quando HSC > 75:
    F_cirurgica = 90.0, G_consignado = 85.0, S_atendimento = 95.0, E_canal = 80.0
    HSC = 0.4*(90) + 0.3*(85) + 0.2*(95) + 0.1*(80) = 36 + 25.5 + 19 + 8 = 88.5 (> 75).
    Deve habilitar upsell de fluxo digital e programa de indicação MGM.
    """
    req = HealthScoreCalculateRequest(
        partner_id="part-cir-promoter",
        partner_name="Dra. Juliana Brandao",
        f_cirurgica=90.0,
        g_consignado=85.0,
        s_atendimento=95.0,
        e_canal=80.0,
        account_id="0f14ffff"
    )

    result = health_score_hsc.calculate_surgical_health_score(req)

    assert result["hsc_score"] == 88.5
    assert result["classification"] == "PROMOTER"
    assert result["upsell_eligible"] is True
    assert result["mgm_eligible"] is True
    assert result["rescue_task_id"] is None
    assert result["dentgo_voucher_code"] is None
    assert "Conta Promotora" in result["recommendation"]


def test_hsc_stable_account_standard_flow():
    """Valida conta estável com HSC entre 40 e 75."""
    req = HealthScoreCalculateRequest(
        partner_id="part-cir-stable",
        partner_name="Dr. Claudio Paiva",
        f_cirurgica=60.0,
        g_consignado=60.0,
        s_atendimento=60.0,
        e_canal=60.0,
        account_id="0f14ffff"
    )

    result = health_score_hsc.calculate_surgical_health_score(req)

    assert result["hsc_score"] == 60.0
    assert result["classification"] == "STABLE"
    assert result["upsell_eligible"] is False
    assert result["mgm_eligible"] is False
    assert result["rescue_task_id"] is None


def test_api_health_score_endpoints():
    """Valida endpoints HTTP FastAPI de cálculo e histórico de HSC."""
    # 1. POST /api/v1/intelligence/health-score/calculate
    payload = {
        "partner_id": "part-api-test",
        "partner_name": "Clinica Sorriso Real",
        "f_cirurgica": 20.0,
        "g_consignado": 30.0,
        "s_atendimento": 25.0,
        "e_canal": 60.0
    }
    res = client.post("/api/v1/intelligence/health-score/calculate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["hsc_score"] == 28.0
    assert data["classification"] == "CRITICAL_RISK"
    assert data["rescue_task_id"] is not None

    # 2. GET /api/v1/intelligence/health-score/history/{partner_id}
    res_hist = client.get("/api/v1/intelligence/health-score/history/part-api-test")
    assert res_hist.status_code == 200
    hist_data = res_hist.json()
    assert hist_data["partner_id"] == "part-api-test"
    assert hist_data["total_records"] >= 1
