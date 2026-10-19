# -*- coding: utf-8 -*-
"""Rota POST /api/v1/dentgo/orders/express: checkout multi-item com voucher MOEDA-EXPRESS-* / DENTGO-EXPRESS-*."""

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection, init_db
from src.features.dentgo import service as dentgo_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def seeded_hub():
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM dentgo_financial_splits")
        cur.execute("DELETE FROM dentgo_orders")
        cur.execute("DELETE FROM dentgo_hub_inventory")
        cur.execute("DELETE FROM dentgo_hubs")
        conn.commit()
    finally:
        conn.close()

    hub = dentgo_service.create_hub(
        name="Hub Express Vila Mariana",
        cnpj="55.666.777/0001-88",
        latitude=-23.5880,
        longitude=-46.6350,
        coverage_radius_km=25.0,
        account_id="0f14ffff",
    )
    expiry = (datetime.now(timezone.utc) + timedelta(days=120)).strftime("%Y-%m-%d")
    for pid, batch, price in (("prod-exp-a", "LOTE-EXP-A", 500.0), ("prod-exp-b", "LOTE-EXP-B", 120.0)):
        dentgo_service.add_hub_inventory(
            hub_id=hub["id"],
            product_id=pid,
            product_name=f"Item {pid}",
            anvisa_reg="ANVISA-80123450009",
            batch_number=batch,
            quantity_available=10,
            unit_price=price,
            sterilization_expiry_date=expiry,
            account_id="0f14ffff",
        )
    return hub


def _payload(voucher=None):
    return {
        "customer_cro_uf": "CRO-SP-109283",
        "delivery_address": "Rua Domingos de Morais, 1000 - SP",
        "delivery_lat": -23.5900,
        "delivery_lng": -46.6380,
        "items": [
            {"product_id": "prod-exp-a", "quantity": 2},
            {"product_id": "prod-exp-b", "quantity": 3},
        ],
        "voucher_code": voucher,
        "account_id": "0f14ffff",
    }


def test_express_multi_item_without_voucher_charges_urgency(client):
    res = client.post("/api/v1/dentgo/orders/express", json=_payload())
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["subtotal"] == 1360.0
    assert body["urgency_fee"] > 0
    assert body["total_amount"] == round(1360.0 + body["urgency_fee"], 2)


@pytest.mark.parametrize("voucher", ["MOEDA-EXPRESS-2026", "dentgo-express-vip01"])
def test_express_valid_voucher_waives_urgency_fee(client, voucher):
    res = client.post("/api/v1/dentgo/orders/express", json=_payload(voucher))
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["urgency_fee"] == 0.0
    assert body["total_amount"] == 1360.0


@pytest.mark.parametrize("voucher", ["CUPOM10", "MOEDA-EXPRESS-", "DENTGO-EXPRESS-ab_c"])
def test_express_rejects_invalid_voucher_format(client, voucher):
    res = client.post("/api/v1/dentgo/orders/express", json=_payload(voucher))
    assert res.status_code == 400
    assert "MOEDA-EXPRESS" in res.json()["detail"]
    inv = dentgo_service.get_hub_product_inventory(
        dentgo_service.list_hubs(account_id="0f14ffff")[0]["id"], "prod-exp-a", account_id="0f14ffff"
    )
    assert inv["quantity_available"] == 10
