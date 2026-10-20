# -*- coding: utf-8 -*-
"""
Test Suite: Calculadora de Margem Liquida Real por Procedimento Clinico
Valida o calculo exato da margem liquida, alertas de margem critica (< 15%) e agregacao por clinica.
"""

import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers

from src.main import app
from src.core.database import get_connection, init_db
from src.features.intelligence import clinical_margin
from src.features.intelligence.schemas import ClinicalMarginCalculateRequest


client = TestClient(app, headers=bearer_headers())


@pytest.fixture(autouse=True)
def setup_clinical_margin_test_env():
    """Inicializa banco e seeds necessarias."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO accounts (id, name, plan)
            VALUES ('0f14ffff', 'Odonto Prime Test Tenant', 'Enterprise Scale')
        """)
        cur.execute("DELETE FROM clinical_procedure_margins WHERE account_id = '0f14ffff'")
        conn.commit()
    finally:
        conn.close()


def test_clinical_procedure_exact_margin_protocol_all_on_4():
    """
    TDD Obrigatorio:
    Cirurgia de protocolo cobrada a R$ 12.000 com:
    - 4 implantes + 4 minipilares: R$ 1.800
    - Protese laboratorial: R$ 2.200
    - Honorarios do implantodontista: R$ 2.500
    - 4 horas de cadeira clinica a R$ 200/h: R$ 800
    - Imposto de 10%: R$ 1.200
    Total de custos: 1800 + 2200 + 2500 + 800 + 1200 = R$ 8.500
    Margem Liquida exata: R$ 12.000 - R$ 8.500 = R$ 3.500,00 (29.17%)
    """
    req = ClinicalMarginCalculateRequest(
        procedure_name="Protocolo All-on-4 Superior",
        gross_revenue=12000.0,
        supplies_cost=1800.0,
        lab_cost=2200.0,
        surgeon_fee=2500.0,
        chair_hours=4.0,
        chair_hour_cost=200.0,
        tax_rate_percent=10.0,
        clinic_id="clinic-sp-morumbi",
        patient_identifier="PAC-PROTO-9872",
        account_id="0f14ffff"
    )

    result = clinical_margin.calculate_procedure_net_margin(req)

    assert result["gross_revenue"] == 12000.0
    assert result["supplies_cost"] == 1800.0
    assert result["lab_cost"] == 2200.0
    assert result["surgeon_fee"] == 2500.0
    assert result["total_chair_cost"] == 800.0
    assert result["tax_amount"] == 1200.0
    assert result["total_cost"] == 8500.0
    assert result["net_margin_value"] == 3500.0
    assert result["net_margin_percent"] == 29.17
    assert result["is_low_margin"] is False
    assert result["status"] == "HEALTHY_MARGIN"

    # Valida persistencia na tabela SQLite
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clinical_procedure_margins WHERE id = ?", (result["id"],))
        row = cur.fetchone()
        assert row is not None
        assert row["net_margin_value"] == 3500.0
        assert row["net_margin_percent"] == 29.17
        assert row["is_low_margin"] == 0
    finally:
        conn.close()


def test_clinical_procedure_low_margin_warning():
    """
    Valida alerta quando a margem liquida for inferior a 15.0%:
    Procedimento cobrado a R$ 6.000:
    - Insumos: R$ 1.500
    - Protese lab: R$ 2.000
    - Honorario: R$ 1.200
    - 3 horas de cadeira a R$ 200/h: R$ 600
    - Imposto 10%: R$ 600
    Total custos: 1500 + 2000 + 1200 + 600 + 600 = R$ 5.900
    Margem: 6000 - 5900 = R$ 100,00 (1.67% < 15.0%)
    Deve disparar is_low_margin = True e status LOW_MARGIN_RISK.
    """
    req = ClinicalMarginCalculateRequest(
        procedure_name="Overdenture Inferior Convenio",
        gross_revenue=6000.0,
        supplies_cost=1500.0,
        lab_cost=2000.0,
        surgeon_fee=1200.0,
        chair_hours=3.0,
        chair_hour_cost=200.0,
        tax_rate_percent=10.0,
        clinic_id="clinic-sp-morumbi",
        account_id="0f14ffff"
    )

    result = clinical_margin.calculate_procedure_net_margin(req)

    assert result["net_margin_value"] == 100.0
    assert result["net_margin_percent"] == 1.67
    assert result["is_low_margin"] is True
    assert result["status"] == "LOW_MARGIN_RISK"
    assert "Alerta de margem critica" in result["recommendation"]


def test_clinic_margin_summary_report():
    """Valida relatorio analitico consolidado da clinica."""
    # Insere 2 procedimentos para a mesma clinica
    clinical_margin.calculate_procedure_net_margin(ClinicalMarginCalculateRequest(
        procedure_name="Implante Unitario",
        gross_revenue=4000.0,
        supplies_cost=600.0,
        lab_cost=600.0,
        surgeon_fee=800.0,
        chair_hours=1.5,
        chair_hour_cost=200.0,
        tax_rate_percent=10.0,
        clinic_id="clinic-summary-test",
        account_id="0f14ffff"
    ))
    clinical_margin.calculate_procedure_net_margin(ClinicalMarginCalculateRequest(
        procedure_name="Enxerto com Membrana",
        gross_revenue=3000.0,
        supplies_cost=1500.0,
        lab_cost=0.0,
        surgeon_fee=1000.0,
        chair_hours=2.0,
        chair_hour_cost=200.0,
        tax_rate_percent=10.0,
        clinic_id="clinic-summary-test",
        account_id="0f14ffff"
    ))

    summary = clinical_margin.get_clinic_margin_summary(
        clinic_id="clinic-summary-test",
        account_id="0f14ffff"
    )

    assert summary["clinic_id"] == "clinic-summary-test"
    assert summary["total_procedures_analyzed"] == 2
    assert len(summary["items"]) == 2
    assert summary["average_margin_percent"] > 0.0


def test_api_clinical_margin_endpoints():
    """Valida endpoints HTTP FastAPI para calculo de margem e resumo da clinica."""
    # 1. POST /api/v1/intelligence/margin/calculate
    payload = {
        "procedure_name": "Protocolo All-on-4 Superior",
        "gross_revenue": 12000.0,
        "supplies_cost": 1800.0,
        "lab_cost": 2200.0,
        "surgeon_fee": 2500.0,
        "chair_hours": 4.0,
        "chair_hour_cost": 200.0,
        "tax_rate_percent": 10.0,
        "clinic_id": "clinic-api-test"
    }
    res = client.post("/api/v1/intelligence/margin/calculate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["net_margin_value"] == 3500.0
    assert data["net_margin_percent"] == 29.17
    assert data["is_low_margin"] is False

    # 2. GET /api/v1/intelligence/margin/summary/{clinic_id}
    res_summary = client.get("/api/v1/intelligence/margin/summary/clinic-api-test")
    assert res_summary.status_code == 200
    sum_data = res_summary.json()
    assert sum_data["clinic_id"] == "clinic-api-test"
    assert sum_data["total_procedures_analyzed"] >= 1
