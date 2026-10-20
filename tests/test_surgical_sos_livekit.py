# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-25: Vídeo Suporte Cirúrgico Crítico em 1 Clique ("SOS Mesa Cirúrgica" via LiveKit)
"""

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection, init_db
from src.features.tickets import surgical_sos
from src.features.dentgo import service as dentgo_service


@pytest.fixture
def client():
    return TestClient(app, headers=bearer_headers())


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
        cur.execute("DELETE FROM tickets WHERE priority = 'P0_SURGICAL_TABLE' OR category = 'SOS Mesa Cirúrgica'")
        conn.commit()
    finally:
        conn.close()


def test_trigger_surgical_sos_livekit_room_and_p0_ticket():
    # Cirurgião aciona socorro técnico urgente durante cirurgia
    res = surgical_sos.trigger_surgical_sos(
        customer_name="Dr. Alexandre Neves",
        customer_phone="+5511999991234",
        cro_uf="CRO-SP-88771",
        procedure_details="Dúvida de fresagem para osso tipo IV com perda de travamento",
        account_id="0f14ffff"
    )

    assert res["ticket_id"].startswith("t-")
    assert res["priority"] == "P0_SURGICAL_TABLE"
    assert "https://meet.revops.local/room/sos-" in res["livekit_room_url"]
    assert res["cro_uf"] == "CRO-SP-88771"
    assert res["status"] == "aberto"

    # Confere persistência no banco
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tickets WHERE id = ?", (res["ticket_id"],))
        row = cur.fetchone()
        assert row is not None
        assert row["priority"] == "P0_SURGICAL_TABLE"
        assert row["livekit_room_url"] == res["livekit_room_url"]
        assert row["cro_uf"] == "CRO-SP-88771"
    finally:
        conn.close()


def test_dispatch_dentgo_item_from_sos_call():
    # 1. Setup Hub com implante de emergência
    hub = dentgo_service.create_hub(
        name="Hub DENTGO Jardins SOS",
        cnpj="55.666.777/0001-88",
        latitude=-23.5650,
        longitude=-46.6650,
        account_id="0f14ffff"
    )
    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")
    dentgo_service.add_hub_inventory(
        hub_id=hub["id"],
        product_id="prod-cm-sos",
        product_name="Implante Titânio CM 4.3x8.5 Curto",
        anvisa_reg="ANVISA-80123450001",
        batch_number="LOTE-SOS-01",
        quantity_available=15,
        unit_price=850.0,
        sterilization_expiry_date=valid_expiry,
        account_id="0f14ffff"
    )

    # 2. Abre chamado SOS Cirúrgico
    sos_res = surgical_sos.trigger_surgical_sos(
        customer_name="Dr. Carlos Trauma",
        customer_phone="+5511988882222",
        cro_uf="CRO-SP-99221",
        procedure_details="Necessita implante curto de urgência por proximidade de canal mandibular",
        account_id="0f14ffff"
    )

    # 3. Assessor técnico despacha componente direto via DENTGO dentro da chamada
    dispatch_res = surgical_sos.dispatch_emergency_dentgo_item(
        ticket_id=sos_res["ticket_id"],
        product_id="prod-cm-sos",
        quantity=1,
        delivery_address="Hospital Santa Catarina, Sala 4 - Av. Paulista, 200",
        delivery_lat=-23.5660,
        delivery_lng=-46.6660,
        account_id="0f14ffff"
    )

    assert dispatch_res["ticket_id"] == sos_res["ticket_id"]
    assert dispatch_res["status"] == "DISPATCHED_EXPRESS"
    assert dispatch_res["dentgo_order_id"].startswith("dord-")
    assert dispatch_res["estimated_eta_minutes"] > 0

    # Valida vinculação no ticket
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT dentgo_order_id FROM tickets WHERE id = ?", (sos_res["ticket_id"],))
        row = cur.fetchone()
        assert row["dentgo_order_id"] == dispatch_res["dentgo_order_id"]
    finally:
        conn.close()


def test_surgical_sos_api_endpoints(client):
    # 1. POST /api/v1/tickets/surgical-sos
    payload = {
        "customer_name": "Dra. Renata API",
        "customer_phone": "+5511977773333",
        "cro_uf": "CRO-SP-11223",
        "procedure_details": "Fratura de broca durante osteotomia"
    }
    res = client.post("/api/v1/tickets/surgical-sos", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["priority"] == "P0_SURGICAL_TABLE"
    assert "https://meet.revops.local/room/sos-" in data["livekit_room_url"]

    ticket_id = data["ticket_id"]

    # 2. GET /api/v1/tickets/surgical-sos/{ticket_id}
    res_get = client.get(f"/api/v1/tickets/surgical-sos/{ticket_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == ticket_id
    assert res_get.json()["priority"] == "P0_SURGICAL_TABLE"
