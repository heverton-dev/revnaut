# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-17: Fluxo Operacional de Remessa, Conferência de Lacre e Baixa Pós-Cirúrgica (Inside + Field)
"""

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection, init_db
from src.features.keypartners import service as kp_service
from src.features.keypartners import surgical_cycle


@pytest.fixture
def client():
    return TestClient(app, headers=bearer_headers())


def test_full_surgical_cycle_and_postop_reconciliation():
    init_db()

    # 1. Setup Acordo com limite de R$ 30.000
    agr = kp_service.create_partner_agreement(
        partner_name="Hospital Odontológico Paulista",
        partner_cro_uf="CRO-SP-10203",
        tier="GOLD",
        credit_limit=30000.0,
        account_id="0f14ffff"
    )

    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=150)).strftime("%Y-%m-%d")
    requested_items = [
        {
            "product_id": "prod-cm-43",
            "product_name": "Implante Cone Morse 4.3x10",
            "anvisa_reg": "ANVISA-80123450001",
            "batch_number": "LOTE-IMP-A1",
            "quantity": 10,
            "unit_value": 1000.0,
            "sterilization_expiry_date": valid_expiry,
        }
    ]

    # 2. Consultor de Campo solicita remessa cirúrgica
    order = surgical_cycle.create_surgical_request(
        agreement_id=agr["id"],
        patient_identifier="Paciente Carlos Mendes",
        surgery_date="2026-11-10",
        field_consultant_id="usr-field-01",
        items=requested_items,
        account_id="0f14ffff"
    )
    assert order["status"] == "SOLICITADO_FIELD"
    assert order["agreement_id"] == agr["id"]

    # 3. Analista Interno aprova a solicitação
    approved_order = surgical_cycle.approve_surgical_request(
        order_id=order["id"],
        inside_analyst_id="usr-inside-02",
        account_id="0f14ffff"
    )
    assert approved_order["status"] == "APROVADO_INSIDE"

    # 4. Despacho logístico com Termo de Custódia
    dispatched_order = surgical_cycle.dispatch_surgical_order(
        order_id=order["id"],
        account_id="0f14ffff"
    )
    assert dispatched_order["status"] == "EM_POSSE_CLINICA"

    # Valida que os 10 implantes entraram na custódia (R$ 10.000)
    summary_before = kp_service.get_partner_custody_summary(agr["id"], account_id="0f14ffff")
    assert summary_before["total_custodied_value"] == 10000.0
    assert summary_before["total_items_count"] == 10

    # 5. Reporte Pós-Operatório:
    # 3 implantes foram instalados no paciente (R$ 3.000 faturáveis)
    # 7 implantes permanecem intactos na clínica / custódia
    consumed_items = [
        {
            "product_id": "prod-cm-43",
            "product_name": "Implante Cone Morse 4.3x10",
            "anvisa_reg": "ANVISA-80123450001",
            "batch_number": "LOTE-IMP-A1",
            "quantity": 3,
            "unit_value": 1000.0,
            "patient_notes": "Instalados na região 14, 15 e 16 com torque 45 N.cm",
        }
    ]

    postop_res = surgical_cycle.report_surgical_postop(
        order_id=order["id"],
        consumed_items=consumed_items,
        seal_photo_r2_key="seals/surg-01/photo_lacre_intacto.jpg",
        account_id="0f14ffff"
    )

    assert postop_res["status"] == "FATURADO_E_REPOSTO"
    assert postop_res["billed_amount"] == 3000.0
    assert postop_res["cfop"] == "5.113"
    assert postop_res["consumed_units"] == 3
    assert postop_res["retained_units"] == 7
    assert postop_res["billing_order_id"].startswith("ped-cfop-")

    # 6. Saldo em custódia deve refletir 7 itens intactos e R$ 7.000 em custódia ativa
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT used_credit FROM kp_partner_agreements WHERE id = ?", (agr["id"],))
        used_credit = cur.fetchone()["used_credit"]
        assert used_credit == 7000.0

        cur.execute("SELECT movement_type, quantity, total_value FROM kp_custody_ledger WHERE agreement_id = ?", (agr["id"],))
        movements = [dict(r) for r in cur.fetchall()]
        assert len(movements) == 2
        m_types = [m["movement_type"] for m in movements]
        assert "REMESSA" in m_types
        assert "CONSUMO_CIRURGICO" in m_types
    finally:
        conn.close()


def test_keypartners_surgical_api_endpoints(client):
    # Setup inicial
    agr = kp_service.create_partner_agreement(
        partner_name="Clínica API Cirurgia",
        partner_cro_uf="CRO-DF-77889",
        tier="BLACK_KOL",
        credit_limit=40000.0,
        account_id="0f14ffff"
    )

    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")

    # 1. POST /api/v1/keypartners/surgical-orders
    req_body = {
        "agreement_id": agr["id"],
        "patient_identifier": "Paciente Dra. Renata",
        "surgery_date": "2026-11-20",
        "field_consultant_id": "usr-field-renata",
        "items": [
            {
                "product_id": "prod-gm-35",
                "product_name": "Implante Grand Morse 3.5x13",
                "anvisa_reg": "ANVISA-80123450001",
                "batch_number": "LOTE-GM-99",
                "quantity": 5,
                "unit_value": 1500.0,
                "sterilization_expiry_date": valid_expiry
            }
        ]
    }
    res_create = client.post("/api/v1/keypartners/surgical-orders", json=req_body)
    assert res_create.status_code == 201
    order_data = res_create.json()
    order_id = order_data["id"]
    assert order_data["status"] == "SOLICITADO_FIELD"

    # 2. POST /api/v1/keypartners/surgical-orders/{id}/approve
    res_appr = client.post(f"/api/v1/keypartners/surgical-orders/{order_id}/approve", json={"inside_analyst_id": "usr-inside-ana"})
    assert res_appr.status_code == 200
    assert res_appr.json()["status"] == "APROVADO_INSIDE"

    # 3. POST /api/v1/keypartners/surgical-orders/{id}/dispatch
    res_disp = client.post(f"/api/v1/keypartners/surgical-orders/{order_id}/dispatch")
    assert res_disp.status_code == 200
    assert res_disp.json()["status"] == "EM_POSSE_CLINICA"

    # 4. POST /api/v1/keypartners/surgical-orders/{id}/postop-report
    postop_body = {
        "consumed_items": [
            {
                "product_id": "prod-gm-35",
                "product_name": "Implante Grand Morse 3.5x13",
                "anvisa_reg": "ANVISA-80123450001",
                "batch_number": "LOTE-GM-99",
                "quantity": 2,
                "unit_value": 1500.0,
                "patient_notes": "Enxerto ósseo + 2 implantes"
            }
        ],
        "seal_photo_r2_key": "seals/order_test/lacre_conferido.png"
    }
    res_postop = client.post(f"/api/v1/keypartners/surgical-orders/{order_id}/postop-report", json=postop_body)
    assert res_postop.status_code == 200
    postop_data = res_postop.json()
    assert postop_data["status"] == "FATURADO_E_REPOSTO"
    assert postop_data["billed_amount"] == 3000.0

    # 5. GET /api/v1/keypartners/surgical-orders/{id}
    res_get = client.get(f"/api/v1/keypartners/surgical-orders/{order_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == order_id
    assert res_get.json()["status"] == "FATURADO_E_REPOSTO"
