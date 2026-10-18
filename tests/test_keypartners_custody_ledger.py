# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-16: Incorporação do Domínio Core KeyPartners: Custódia de Kits, Lotes ANVISA e Saldos
"""

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection, init_db
from src.features.keypartners import service as kp_service


@pytest.fixture
def client():
    return TestClient(app)


def test_create_partner_agreement_and_valid_dispatch():
    init_db()
    # 1. Cria acordo de parceria com limite de R$ 15.000
    agr = kp_service.create_partner_agreement(
        partner_name="Clínica Odonto Implantes BH",
        partner_cro_uf="CRO-MG-99887",
        tier="GOLD",
        credit_limit=15000.0,
        min_monthly_revenue=5000.0,
        max_turnover_days=45,
        account_id="0f14ffff"
    )
    assert agr["id"].startswith("kpa-")
    assert agr["credit_limit"] == 15000.0
    assert agr["used_credit"] == 0.0

    # 2. Registra um kit cirúrgico seriadocom QR code
    kit = kp_service.register_consignment_kit(
        serial_number="KIT-CM-2026-X1",
        name="Kit Cirúrgico Universal Cone Morse",
        composition_json='{"drills": ["2.0", "2.8", "3.2"], "ratchet": true}',
        account_id="0f14ffff"
    )
    assert kit["status"] == "IN_STOCK"
    assert "KIT-CM-2026-X1" in kit["qr_code"]

    # 3. Remessa de R$ 12.000: Kit (R$ 2.000) + 10 Implantes (R$ 10.000) com validade de 180 dias
    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=180)).strftime("%Y-%m-%d")
    items = [
        {
            "product_id": "prod-kit-1",
            "product_name": "Kit Cirúrgico Universal Cone Morse",
            "anvisa_reg": "ANVISA-80123450001",
            "batch_number": "LOTE-KIT-2026-01",
            "serial_number": "KIT-CM-2026-X1",
            "quantity": 1,
            "unit_value": 2000.0,
            "sterilization_expiry_date": valid_expiry,
        },
        {
            "product_id": "prod-cm-4311",
            "product_name": "Implante Titânio Cone Morse 4.3x11.5",
            "anvisa_reg": "ANVISA-80123450002",
            "batch_number": "LOTE-IMP-9921",
            "quantity": 10,
            "unit_value": 1000.0,
            "sterilization_expiry_date": valid_expiry,
        }
    ]

    dispatch_res = kp_service.dispatch_consignment_custody(
        agreement_id=agr["id"],
        items=items,
        account_id="0f14ffff"
    )

    assert dispatch_res["status"] == "DISPATCHED"
    assert dispatch_res["total_remittance_value"] == 12000.0
    assert dispatch_res["updated_used_credit"] == 12000.0
    assert dispatch_res["available_credit"] == 3000.0

    # 4. Verifica sumário de custódia
    summary = kp_service.get_partner_custody_summary(agr["id"], account_id="0f14ffff")
    assert summary["total_custodied_value"] == 12000.0
    assert summary["total_items_count"] == 11
    assert len(summary["ledger_entries"]) == 2


def test_dispatch_blocked_by_credit_limit():
    init_db()
    # Acordo com limite de R$ 15.000
    agr = kp_service.create_partner_agreement(
        partner_name="Instituto Maxilo Facial",
        partner_cro_uf="CRO-SP-55443",
        tier="SILVER",
        credit_limit=15000.0,
        account_id="0f14ffff"
    )

    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")

    # Primeira remessa de R$ 12.000 (Passa)
    kp_service.dispatch_consignment_custody(
        agreement_id=agr["id"],
        items=[{
            "product_id": "prod-imp-cm",
            "product_name": "Implante Cone Morse",
            "anvisa_reg": "ANVISA-80123450002",
            "batch_number": "LOTE-A1",
            "quantity": 12,
            "unit_value": 1000.0,
            "sterilization_expiry_date": valid_expiry,
        }],
        account_id="0f14ffff"
    )

    # Segunda remessa de R$ 5.000 (Deve bloquear porque 12k + 5k = 17k > 15k)
    with pytest.raises(ValueError, match="Limite de crédito consignado excedido para este parceiro"):
        kp_service.dispatch_consignment_custody(
            agreement_id=agr["id"],
            items=[{
                "product_id": "prod-imp-cm",
                "product_name": "Implante Cone Morse Extra",
                "anvisa_reg": "ANVISA-80123450002",
                "batch_number": "LOTE-A2",
                "quantity": 5,
                "unit_value": 1000.0,
                "sterilization_expiry_date": valid_expiry,
            }],
            account_id="0f14ffff"
        )


def test_dispatch_blocked_by_sanitary_expiry():
    init_db()
    agr = kp_service.create_partner_agreement(
        partner_name="Clínica Expirada",
        partner_cro_uf="CRO-RJ-11223",
        tier="SILVER",
        credit_limit=20000.0,
        account_id="0f14ffff"
    )

    # Validade em 15 dias (< 30 dias mínimos exigidos pela vigilância/KeyPartners)
    expired_soon = (datetime.now(timezone.utc) + timedelta(days=15)).strftime("%Y-%m-%d")

    with pytest.raises(ValueError, match="Lote vencido ou com validade inferior a 30 dias para consignação sanitária"):
        kp_service.dispatch_consignment_custody(
            agreement_id=agr["id"],
            items=[{
                "product_id": "prod-imp-short-life",
                "product_name": "Implante Vencendo",
                "anvisa_reg": "ANVISA-80123450002",
                "batch_number": "LOTE-OLD-01",
                "quantity": 1,
                "unit_value": 800.0,
                "sterilization_expiry_date": expired_soon,
            }],
            account_id="0f14ffff"
        )


def test_keypartners_api_endpoints(client):
    # 1. POST /api/v1/keypartners/agreements
    agr_payload = {
        "partner_name": "Centro Cirúrgico Rio",
        "partner_cro_uf": "CRO-RJ-44556",
        "tier": "BLACK_KOL",
        "credit_limit": 50000.0,
        "min_monthly_revenue": 10000.0,
        "max_turnover_days": 30
    }
    res_agr = client.post("/api/v1/keypartners/agreements", json=agr_payload)
    assert res_agr.status_code == 201
    agr_data = res_agr.json()
    agr_id = agr_data["id"]
    assert agr_data["tier"] == "BLACK_KOL"

    # 2. GET /api/v1/keypartners/agreements
    res_list = client.get("/api/v1/keypartners/agreements")
    assert res_list.status_code == 200
    agrs_list = res_list.json()
    assert any(a["id"] == agr_id for a in agrs_list)

    # 3. POST /api/v1/keypartners/kits
    kit_payload = {
        "serial_number": "KIT-API-990",
        "name": "Kit Prótese e Cirurgia Guiada",
        "composition_json": '{"keys": 4}'
    }
    res_kit = client.post("/api/v1/keypartners/kits", json=kit_payload)
    assert res_kit.status_code == 201
    assert res_kit.json()["serial_number"] == "KIT-API-990"

    # 4. POST /api/v1/keypartners/agreements/{agreement_id}/dispatch
    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=120)).strftime("%Y-%m-%d")
    dispatch_payload = {
        "items": [
            {
                "product_id": "prod-imp-api",
                "product_name": "Implante API Test",
                "anvisa_reg": "ANVISA-889900",
                "batch_number": "LOTE-API-01",
                "quantity": 5,
                "unit_value": 1200.0,
                "sterilization_expiry_date": valid_expiry
            }
        ]
    }
    res_disp = client.post(f"/api/v1/keypartners/agreements/{agr_id}/dispatch", json=dispatch_payload)
    assert res_disp.status_code == 200
    disp_data = res_disp.json()
    assert disp_data["status"] == "DISPATCHED"
    assert disp_data["total_remittance_value"] == 6000.0

    # 5. GET /api/v1/keypartners/agreements/{agreement_id}/custody-summary
    res_sum = client.get(f"/api/v1/keypartners/agreements/{agr_id}/custody-summary")
    assert res_sum.status_code == 200
    sum_data = res_sum.json()
    assert sum_data["total_custodied_value"] == 6000.0
    assert sum_data["available_credit"] == 44000.0
