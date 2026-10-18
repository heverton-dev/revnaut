# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-21: Sinergia Automática KeyPartners <-> DENTGO (Reposição On-Demand e Resgate de Ociosos)
"""

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection, init_db
from src.features.keypartners import service as kp_service
from src.features.keypartners import surgical_cycle
from src.features.dentgo import service as dentgo_service
from src.features.dentgo import keypartners_synergy


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_tables():
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM dentgo_financial_splits")
        cur.execute("DELETE FROM dentgo_orders")
        cur.execute("DELETE FROM dentgo_hub_inventory")
        cur.execute("DELETE FROM dentgo_hubs")
        cur.execute("DELETE FROM kp_surgical_orders")
        cur.execute("DELETE FROM kp_custody_ledger")
        cur.execute("DELETE FROM kp_consignment_kits")
        cur.execute("DELETE FROM kp_partner_agreements")
        conn.commit()
    finally:
        conn.close()


def test_automatic_replenishment_after_postop():
    # 1. Setup Hub DENTGO com estoque
    hub = dentgo_service.create_hub(
        name="Hub DENTGO Jardins Reposição",
        cnpj="66.777.888/0001-99",
        latitude=-23.5650,
        longitude=-46.6650,
        account_id="0f14ffff"
    )

    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")
    dentgo_service.add_hub_inventory(
        hub_id=hub["id"],
        product_id="prod-cm-syn",
        product_name="Implante Titânio CM 4.3x11.5",
        anvisa_reg="ANVISA-80123450001",
        batch_number="LOTE-REP-01",
        quantity_available=20,
        unit_price=800.0,
        sterilization_expiry_date=valid_expiry,
        account_id="0f14ffff"
    )

    # 2. Setup Acordo KeyPartners e Ordem cirúrgica
    agr = kp_service.create_partner_agreement(
        partner_name="Clínica Implante & Arte",
        partner_cro_uf="CRO-SP-88221",
        tier="GOLD",
        credit_limit=25000.0,
        account_id="0f14ffff"
    )

    order = surgical_cycle.create_surgical_request(
        agreement_id=agr["id"],
        patient_identifier="Paciente Sinergia Test",
        surgery_date="2026-11-15",
        items=[{
            "product_id": "prod-cm-syn",
            "product_name": "Implante Titânio CM 4.3x11.5",
            "anvisa_reg": "ANVISA-80123450001",
            "batch_number": "LOTE-REP-01",
            "quantity": 5,
            "unit_value": 800.0,
            "sterilization_expiry_date": valid_expiry
        }],
        account_id="0f14ffff"
    )
    surgical_cycle.approve_surgical_request(order["id"], account_id="0f14ffff")
    surgical_cycle.dispatch_surgical_order(order["id"], account_id="0f14ffff")

    # 3. Reporte pós-operatório de 2 implantes consumidos
    postop_res = surgical_cycle.report_surgical_postop(
        order_id=order["id"],
        consumed_items=[{
            "product_id": "prod-cm-syn",
            "product_name": "Implante Titânio CM 4.3x11.5",
            "anvisa_reg": "ANVISA-80123450001",
            "batch_number": "LOTE-REP-01",
            "quantity": 2,
            "unit_value": 800.0
        }],
        seal_photo_r2_key="seals/syn_01/lacre.jpg",
        account_id="0f14ffff"
    )

    # 4. Disparo automático da reposição no DENTGO
    replenish_res = keypartners_synergy.trigger_automatic_replenishment_on_postop(
        postop_event=postop_res,
        delivery_lat=-23.5660,
        delivery_lng=-46.6660,
        delivery_address="Rua Oscar Freire, 1000 - SP",
        account_id="0f14ffff"
    )

    assert replenish_res["status"] == "REPLENISHMENT_ORDER_CREATED"
    assert replenish_res["agreement_id"] == agr["id"]
    assert replenish_res["hub_id"] == hub["id"]
    assert replenish_res["items_count"] == 2
    assert replenish_res["replenishment_order_id"].startswith("dord-")


def test_reverse_pickup_of_idle_consignment_kit():
    # 1. Cria Clínica A (onde o kit está ocioso) e Clínica B (destino do kit)
    agr_a = kp_service.create_partner_agreement(
        partner_name="Clínica Origem A (Kit Ocioso)",
        partner_cro_uf="CRO-SP-11111",
        tier="SILVER",
        credit_limit=15000.0,
        account_id="0f14ffff"
    )
    agr_b = kp_service.create_partner_agreement(
        partner_name="Clínica Destino B (Demanda Urgente)",
        partner_cro_uf="CRO-SP-22222",
        tier="GOLD",
        credit_limit=20000.0,
        account_id="0f14ffff"
    )

    # 2. Registra kit e aloca inicialmente na Clínica A
    kit = kp_service.register_consignment_kit(
        serial_number="KIT-REV-2026-X8",
        name="Kit Cirúrgico Guiado Universal",
        composition_json='{"drills": 6}',
        account_id="0f14ffff"
    )

    # Simula remessa do kit para a Clínica A
    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=180)).strftime("%Y-%m-%d")
    kp_service.dispatch_consignment_custody(
        agreement_id=agr_a["id"],
        items=[{
            "product_id": "prod-kit-guided",
            "product_name": "Kit Cirúrgico Guiado Universal",
            "anvisa_reg": "ANVISA-80123450001",
            "batch_number": "LOTE-KIT-X8",
            "serial_number": "KIT-REV-2026-X8",
            "quantity": 1,
            "unit_value": 3000.0,
            "sterilization_expiry_date": valid_expiry
        }],
        account_id="0f14ffff"
    )

    # 3. Dispara a Coleta Reversa do kit ocioso com destino à Clínica B
    pickup_res = keypartners_synergy.trigger_dentgo_reverse_pickup(
        kit_serial="KIT-REV-2026-X8",
        target_agreement_id=agr_b["id"],
        pickup_address="Av. Brasil, 500 - Clínica A",
        destination_address="Av. Rebouças, 1200 - Clínica B",
        account_id="0f14ffff"
    )

    assert pickup_res["success"] is True
    assert pickup_res["status"] == "REVERSE_PICKUP_DISPATCHED"
    assert pickup_res["origin_agreement_id"] == agr_a["id"]
    assert pickup_res["target_agreement_id"] == agr_b["id"]
    assert pickup_res["pickup_order_id"].startswith("dord-rev-")

    # 4. Valida transferência de custódia no razão imutável (kp_custody_ledger)
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Na Clínica A deve haver DEVOLUCAO_INTACTA
        cur.execute("SELECT movement_type FROM kp_custody_ledger WHERE agreement_id = ? ORDER BY created_at DESC", (agr_a["id"],))
        rows_a = [r["movement_type"] for r in cur.fetchall()]
        assert "DEVOLUCAO_INTACTA" in rows_a

        # Na Clínica B deve haver REMESSA
        cur.execute("SELECT movement_type FROM kp_custody_ledger WHERE agreement_id = ? ORDER BY created_at DESC", (agr_b["id"],))
        rows_b = [r["movement_type"] for r in cur.fetchall()]
        assert "REMESSA" in rows_b

        # O kit agora deve estar com current_agreement_id da Clínica B
        cur.execute("SELECT current_agreement_id, status FROM kp_consignment_kits WHERE serial_number = ?", ("KIT-REV-2026-X8",))
        kit_row = cur.fetchone()
        assert kit_row["current_agreement_id"] == agr_b["id"]
        assert kit_row["status"] == "IN_FIELD"
    finally:
        conn.close()


def test_dentgo_synergy_api_endpoint(client):
    # Setup
    agr_a = kp_service.create_partner_agreement(
        partner_name="Clínica API A",
        partner_cro_uf="CRO-SP-33333",
        account_id="0f14ffff"
    )
    agr_b = kp_service.create_partner_agreement(
        partner_name="Clínica API B",
        partner_cro_uf="CRO-SP-44444",
        account_id="0f14ffff"
    )
    kit = kp_service.register_consignment_kit(
        serial_number="KIT-API-REV-01",
        name="Kit Prótese Cone Morse",
        account_id="0f14ffff"
    )
    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=120)).strftime("%Y-%m-%d")
    kp_service.dispatch_consignment_custody(
        agreement_id=agr_a["id"],
        items=[{
            "product_id": "prod-kit-api",
            "product_name": "Kit Prótese Cone Morse",
            "anvisa_reg": "ANVISA-80123450001",
            "batch_number": "LOTE-K1",
            "serial_number": "KIT-API-REV-01",
            "quantity": 1,
            "unit_value": 2500.0,
            "sterilization_expiry_date": valid_expiry
        }],
        account_id="0f14ffff"
    )

    # Chamada ao endpoint REST POST /api/v1/keypartners/consignments/KIT-API-REV-01/trigger-dentgo-pickup
    payload = {
        "target_agreement_id": agr_b["id"],
        "pickup_address": "Rua das Flores, 100",
        "destination_address": "Rua dos Pinheiros, 200"
    }
    res = client.post("/api/v1/keypartners/consignments/KIT-API-REV-01/trigger-dentgo-pickup", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["status"] == "REVERSE_PICKUP_DISPATCHED"
    assert data["target_agreement_id"] == agr_b["id"]
