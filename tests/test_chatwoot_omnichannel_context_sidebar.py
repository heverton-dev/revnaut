# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-24: Integração Profunda Chatwoot Omnichannel + Sidebar Contextual 360° (KeyPartners + DENTGO)
"""

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection, init_db
from src.features.integrations.omnichannel import chatwoot_bridge
from src.features.keypartners import service as kp_service
from src.features.dentgo import service as dentgo_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_test_data():
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
        cur.execute("DELETE FROM kp_kol_contracts")
        cur.execute("DELETE FROM kp_partner_agreements")
        cur.execute("DELETE FROM contacts WHERE phone = ? OR cro_uf = ?", ("+5511988887777", "CRO-SP-54321"))
        conn.commit()
    finally:
        conn.close()


def test_get_omnichannel_360_context_full_stack():
    # 1. Cria Contato Cirurgião com telefone e CRO
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO contacts (
                account_id, name, email, phone, cro_uf, specialty, score
            ) VALUES ('0f14ffff', 'Dra. Camila Cirurgiã', 'camila@clinica.com.br', '+5511988887777', 'CRO-SP-54321', 'Implantodontia', 85)
        """)
        conn.commit()
    finally:
        conn.close()

    # 2. Cria Acordo KeyPartners para a Dra. Camila
    agr = kp_service.create_partner_agreement(
        partner_name="Clínica Dra. Camila",
        partner_cro_uf="CRO-SP-54321",
        tier="BLACK_KOL",
        credit_limit=50000.0,
        account_id="0f14ffff"
    )

    # 3. Registra e aloca Kit Consignado na Clínica dela
    kit = kp_service.register_consignment_kit(
        serial_number="KIT-CAMILA-01",
        name="Kit Cirúrgico Guiado Avançado",
        composition_json='{"drills": 8}',
        account_id="0f14ffff"
    )
    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=120)).strftime("%Y-%m-%d")
    kp_service.dispatch_consignment_custody(
        agreement_id=agr["id"],
        items=[{
            "product_id": "prod-kit-camila",
            "product_name": "Kit Cirúrgico Guiado Avançado",
            "anvisa_reg": "ANVISA-80123450001",
            "batch_number": "LOTE-CAM-01",
            "serial_number": "KIT-CAMILA-01",
            "quantity": 1,
            "unit_value": 4500.0,
            "sterilization_expiry_date": valid_expiry
        }],
        account_id="0f14ffff"
    )

    # 4. Cria Pedido DENTGO Ativo em Trânsito para o CRO dela
    hub = dentgo_service.create_hub(
        name="Hub DENTGO Jardins",
        cnpj="44.555.666/0001-77",
        latitude=-23.5600,
        longitude=-46.6600,
        account_id="0f14ffff"
    )
    dentgo_service.add_hub_inventory(
        hub_id=hub["id"],
        product_id="prod-cm-urg",
        product_name="Implante CM 3.8x10",
        anvisa_reg="ANVISA-80123450001",
        batch_number="LOTE-URG-1",
        quantity_available=10,
        unit_price=800.0,
        sterilization_expiry_date=valid_expiry,
        account_id="0f14ffff"
    )
    dentgo_order = dentgo_service.create_express_order(
        customer_cro_uf="CRO-SP-54321",
        delivery_address="Rua Haddock Lobo, 800 - Jardins, SP",
        delivery_lat=-23.5610,
        delivery_lng=-46.6610,
        items=[{"product_id": "prod-cm-urg", "quantity": 1}],
        account_id="0f14ffff"
    )

    # 5. Executa a agregação 360° pelo telefone do WhatsApp
    ctx = chatwoot_bridge.get_omnichannel_360_context(
        contact_identifier="+5511988887777",
        account_id="0f14ffff"
    )

    # Asserções dos 4 Pilares
    # Pilar 1: Contato e CRO
    assert ctx["contact"] is not None
    assert ctx["contact"]["name"] == "Dra. Camila Cirurgiã"
    assert ctx["cro_uf"] == "CRO-SP-54321"
    assert ctx["contact"]["score"] == 85

    # Pilar 2: KeyPartners Acordo & Crédito
    assert ctx["agreement"] is not None
    assert ctx["agreement"]["tier"] == "BLACK_KOL"
    assert ctx["agreement"]["credit_limit"] == 50000.0
    assert ctx["agreement"]["used_credit"] == 4500.0
    assert ctx["agreement"]["available_credit"] == 45500.0

    # Pilar 3: Kits Consignados em Campo
    assert len(ctx["consignments_in_field"]) >= 1
    assert ctx["consignments_in_field"][0]["serial_number"] == "KIT-CAMILA-01"

    # Pilar 4: Entregas Expressas DENTGO em Andamento
    assert len(ctx["active_dentgo_orders"]) >= 1
    assert ctx["active_dentgo_orders"][0]["id"] == dentgo_order["id"]


def test_sync_contact_to_chatwoot():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO contacts (
                account_id, name, email, phone, cro_uf, specialty, score
            ) VALUES ('0f14ffff', 'Dr. Roberto Sync', 'roberto@dent.com', '+5511977776666', 'CRO-SP-99112', 'Periodontia', 70)
        """)
        conn.commit()
        contact_id = cur.lastrowid
    finally:
        conn.close()

    res = chatwoot_bridge.sync_contact_to_chatwoot(contact_id=contact_id, account_id="0f14ffff")
    assert res["status"] == "SYNCED"
    assert res["contact_id"] == contact_id
    assert res["chatwoot_contact_id"] > 0


def test_omnichannel_context_api_endpoint(client):
    # Setup de contato
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO contacts (
                account_id, name, email, phone, cro_uf, specialty, score
            ) VALUES ('0f14ffff', 'Dr. API Contexto', 'api@dent.com', '+5511988887777', 'CRO-SP-54321', 'Cirurgia', 90)
        """)
        conn.commit()
    finally:
        conn.close()

    # GET /api/v1/omnichannel/context/5511988887777
    res = client.get("/api/v1/omnichannel/context/5511988887777")
    assert res.status_code == 200
    data = res.json()
    assert data["cro_uf"] == "CRO-SP-54321"
    assert data["contact"]["name"] == "Dr. API Contexto"
    assert "consignments_in_field" in data
    assert "active_dentgo_orders" in data
