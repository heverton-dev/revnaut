# -*- coding: utf-8 -*-
"""
Test Suite: Motor Matematico de Score de Ociosidade de Kit (SOK) e Ponto de Reposicao (PR)
Valida a exatidao dos calculos preditivos, disparo de coleta reversa DENTGO e criacao de Deals de Recompra Ativa.
"""

import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers

from src.main import app
from src.core.database import get_connection, init_db
from src.features.intelligence import predictive_inventory
from src.features.intelligence.schemas import (
    SokCalculationRequest,
    PrCalculationRequest
)


client = TestClient(app, headers=bearer_headers())


@pytest.fixture(autouse=True)
def setup_predictive_test_environment():
    """Garante tabelas inicializadas e seeds necessarias para o teste."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Seed account padrao
        cur.execute("""
            INSERT OR IGNORE INTO accounts (id, name, plan)
            VALUES ('0f14ffff', 'Odonto Prime Test Tenant', 'Enterprise Scale')
        """)

        # Seed pipeline e stage para integridade relacional de Deals
        cur.execute("""
            INSERT OR IGNORE INTO pipelines (id, account_id, name)
            VALUES (1, '0f14ffff', 'Funil Comercial Consignado')
        """)
        cur.execute("""
            INSERT OR IGNORE INTO stages (id, pipeline_id, name, color, step_order, probability)
            VALUES (101, 1, 'Recompra Ativa Consignado', '#3B82F6', 1, 80)
        """)

        # Seed de acordo consignado KeyPartners
        cur.execute("""
            INSERT OR REPLACE INTO kp_partner_agreements (
                id, account_id, partner_name, partner_cro_uf, tier, credit_limit, used_credit, min_monthly_revenue, max_turnover_days
            ) VALUES (
                'agr-pred-01', '0f14ffff', 'Clinica OdontoAlpha Implantes', 'CRO-SP 12345', 'GOLD', 100000.0, 35000.0, 5000.0, 30
            )
        """)
        conn.commit()
    finally:
        conn.close()


def test_sok_exact_math_idle_warning_dentgo_reverse():
    """
    TDD Obrigatorio:
    Clinica com 60 dias sem cirurgia (limite 30 dias) e kit de R$ 20.000 com faturamento medio de R$ 5.000:
    SOK = (60/30)*0.6 + (20000/5000)*0.4 = 2.0*0.6 + 4.0*0.4 = 1.2 + 1.6 = 2.8 >= 1.0.
    Deve sinalizar IDLE_WARNING e gerar sugestao de coleta reversa no DENTGO.
    """
    req = SokCalculationRequest(
        agreement_id="agr-pred-01",
        days_without_surgery=60,
        contract_limit_days=30,
        kit_immobilized_value=20000.0,
        avg_monthly_revenue=5000.0,
        account_id="0f14ffff"
    )

    result = predictive_inventory.calculate_kit_idle_score_sok(req)

    assert result["sok_score"] == 2.8
    assert result["is_idle"] is True
    assert result["status"] == "IDLE_WARNING"
    assert result["dentgo_reverse_pickup_suggested"] is True
    assert result["dentgo_order_id"] is not None
    assert "coleta reversa no DENTGO" in result["recommendation"]

    # Valida persistencia no banco de dados SQLite
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT sok_score, is_idle, recommendation, deal_id
            FROM kp_predictive_inventory_scores
            WHERE agreement_id = 'agr-pred-01' AND is_idle = 1
            ORDER BY created_at DESC LIMIT 1
        """)
        row = cur.fetchone()
        assert row is not None
        assert row["sok_score"] == 2.8
        assert row["is_idle"] == 1
    finally:
        conn.close()


def test_sok_regular_flow_below_threshold():
    """Valida kit em fluxo normal quando SOK < 1.0."""
    req = SokCalculationRequest(
        agreement_id="agr-pred-01",
        days_without_surgery=10,
        contract_limit_days=30,
        kit_immobilized_value=5000.0,
        avg_monthly_revenue=20000.0,
        account_id="0f14ffff"
    )

    result = predictive_inventory.calculate_kit_idle_score_sok(req)

    # (10/30)*0.6 = 0.2; (5000/20000)*0.4 = 0.1 => SOK = 0.3
    assert result["sok_score"] == 0.3
    assert result["is_idle"] is False
    assert result["status"] == "REGULAR_FLOW"
    assert result["dentgo_reverse_pickup_suggested"] is False


def test_pr_replenishment_trigger_and_deal_creation():
    """
    TDD Obrigatorio:
    Calculo de PR = (C_medio_diario * T_entrega_dentgo) + ES
    C = 2.0 un/dia, Lead time DENTGO = 3 dias, Estoque de seguranca = 4 un
    PR = (2.0 * 3) + 4 = 10.0 un.
    Se estoque atual = 6 un (<= 10.0), dispara criacao de Deal de Recompra no funil (stage 101) e WhatsApp.
    """
    req = PrCalculationRequest(
        agreement_id="agr-pred-01",
        avg_daily_consumption=2.0,
        delivery_lead_time_days=3.0,
        safety_stock=4.0,
        current_stock=6,
        trigger_deal=True,
        account_id="0f14ffff"
    )

    result = predictive_inventory.calculate_replenishment_point_pr(req)

    assert result["pr_score"] == 10.0
    assert result["current_stock"] == 6
    assert result["replenishment_needed"] is True
    assert result["deal_id"] is not None
    assert result["deal_title"] == "Recompra Ativa Consignado - Clinica OdontoAlpha Implantes"
    assert result["whatsapp_sent"] is True
    assert "https://dentgo.app.br/orders/quick-approve" in result["approval_link"]

    # Verifica se o Deal foi realmente inserido no funil na pipeline 1 stage 101
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, title, pipeline_id, stage_id, priority FROM deals WHERE id = ?", (result["deal_id"],))
        deal_row = cur.fetchone()
        assert deal_row is not None
        assert deal_row["pipeline_id"] == 1
        assert deal_row["stage_id"] == 101
        assert deal_row["priority"] == "alta"

        # Verifica envio da mensagem no WhatsApp (omnichannel_messages)
        cur.execute("SELECT id, content FROM omnichannel_messages WHERE id = ?", (result["whatsapp_message_id"],))
        msg_row = cur.fetchone()
        assert msg_row is not None
        assert "ponto de reposicao" in msg_row["content"]
    finally:
        conn.close()


def test_pr_safe_stock_no_replenishment():
    """Valida que quando estoque atual > PR nenhuma oportunidade de recompra eh aberta."""
    req = PrCalculationRequest(
        agreement_id="agr-pred-01",
        avg_daily_consumption=1.5,
        delivery_lead_time_days=2.0,
        safety_stock=5.0,
        current_stock=20,
        trigger_deal=True,
        account_id="0f14ffff"
    )

    result = predictive_inventory.calculate_replenishment_point_pr(req)

    # PR = 1.5 * 2 + 5 = 8.0. Estoque atual 20 > 8.0
    assert result["pr_score"] == 8.0
    assert result["replenishment_needed"] is False
    assert result["deal_id"] is None
    assert result["whatsapp_sent"] is False


def test_api_predictive_inventory_endpoints():
    """Valida as rotas HTTP FastAPI para SOK, PR e relatorio consolidado."""
    # 1. POST /api/v1/intelligence/inventory/sok
    sok_payload = {
        "agreement_id": "agr-pred-01",
        "days_without_surgery": 60,
        "contract_limit_days": 30,
        "kit_immobilized_value": 20000.0,
        "avg_monthly_revenue": 5000.0
    }
    res_sok = client.post("/api/v1/intelligence/inventory/sok", json=sok_payload)
    assert res_sok.status_code == 200
    sok_data = res_sok.json()
    assert sok_data["sok_score"] == 2.8
    assert sok_data["is_idle"] is True

    # 2. POST /api/v1/intelligence/inventory/pr
    pr_payload = {
        "agreement_id": "agr-pred-01",
        "avg_daily_consumption": 2.5,
        "delivery_lead_time_days": 4.0,
        "safety_stock": 5.0,
        "current_stock": 8,
        "trigger_deal": True
    }
    # PR = 2.5 * 4 + 5 = 15.0. 8 <= 15.0 => replenishment_needed = True
    res_pr = client.post("/api/v1/intelligence/inventory/pr", json=pr_payload)
    assert res_pr.status_code == 200
    pr_data = res_pr.json()
    assert pr_data["pr_score"] == 15.0
    assert pr_data["replenishment_needed"] is True
    assert pr_data["deal_id"] is not None

    # 3. GET /api/v1/intelligence/inventory/report/agr-pred-01
    res_report = client.get("/api/v1/intelligence/inventory/report/agr-pred-01")
    assert res_report.status_code == 200
    report_data = res_report.json()
    assert report_data["agreement_id"] == "agr-pred-01"
    assert report_data["partner_name"] == "Clinica OdontoAlpha Implantes"
    assert report_data["total_records"] >= 2
