# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-19: Incorporação do Domínio Core DENTGO: Hubs Logísticos, Estoque Regional e Catálogo de Urgência
"""

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
def clean_dentgo_tables():
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


def test_dentgo_haversine_and_hub_routing_with_inventory():
    init_db()

    # 1. Cadastra Hub A: Centro SP (lat -23.5505, lng -46.6333) SEM estoque
    hub_a = dentgo_service.create_hub(
        name="Hub DENTGO Express Sé Centro",
        cnpj="11.222.333/0001-44",
        latitude=-23.5505,
        longitude=-46.6333,
        coverage_radius_km=30.0,
        account_id="0f14ffff"
    )

    # 2. Cadastra Hub B: Jardins SP (lat -23.5650, lng -46.6650) COM estoque de 15 unidades válidas
    hub_b = dentgo_service.create_hub(
        name="Hub DENTGO Jardins Cirúrgico",
        cnpj="22.333.444/0001-55",
        latitude=-23.5650,
        longitude=-46.6650,
        coverage_radius_km=30.0,
        account_id="0f14ffff"
    )

    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=120)).strftime("%Y-%m-%d")
    dentgo_service.add_hub_inventory(
        hub_id=hub_b["id"],
        product_id="prod-cm-4311",
        product_name="Implante Titânio Cone Morse 4.3x11.5",
        anvisa_reg="ANVISA-80123450001",
        batch_number="LOTE-URG-881",
        quantity_available=15,
        unit_price=850.0,
        sterilization_expiry_date=valid_expiry,
        account_id="0f14ffff"
    )

    # 3. Busca de emergência a partir de Clínica em Pinheiros (lat -23.5615, lng -46.6900)
    # Distância para Hub B ~2.6 km; Hub A ~5.9 km
    search_results = dentgo_service.search_emergency_supply(
        delivery_lat=-23.5615,
        delivery_lng=-46.6900,
        product_id="prod-cm-4311",
        required_qty=2,
        account_id="0f14ffff"
    )

    assert len(search_results) == 1
    best_hub = search_results[0]
    assert best_hub["hub_id"] == hub_b["id"]
    assert best_hub["distance_km"] < 5.0
    assert best_hub["estimated_eta_minutes"] <= 45
    assert best_hub["quantity_available"] >= 2
    assert best_hub["unit_price"] == 850.0


def test_dentgo_blocks_implant_checkout_without_verified_cro():
    init_db()

    # Tentativa de checkout com CRO inválido
    with pytest.raises(ValueError, match="Checkout bloqueado: Exige validação ativa de CRO para aquisição de dispositivos implantáveis"):
        dentgo_service.create_express_order(
            customer_cro_uf="CRO-INVALIDO-99",
            delivery_address="Rua dos Pinheiros, 1000 - SP",
            delivery_lat=-23.5615,
            delivery_lng=-46.6900,
            items=[{
                "product_id": "prod-cm-4311",
                "quantity": 2
            }],
            account_id="0f14ffff"
        )


def test_dentgo_express_checkout_success():
    init_db()

    # Cria Hub com estoque
    hub = dentgo_service.create_hub(
        name="Hub Moema Dental Express",
        cnpj="33.444.555/0001-66",
        latitude=-23.6000,
        longitude=-46.6600,
        coverage_radius_km=25.0,
        account_id="0f14ffff"
    )

    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")
    dentgo_service.add_hub_inventory(
        hub_id=hub["id"],
        product_id="prod-gm-urgente",
        product_name="Implante Grand Morse 3.5x10",
        anvisa_reg="ANVISA-80123450002",
        batch_number="LOTE-MOEMA-1",
        quantity_available=10,
        unit_price=900.0,
        sterilization_expiry_date=valid_expiry,
        account_id="0f14ffff"
    )

    # Checkout com CRO ativo e válido
    order = dentgo_service.create_express_order(
        customer_cro_uf="CRO-SP-109283",
        delivery_address="Av. Ibirapuera, 2500 - SP",
        delivery_lat=-23.6050,
        delivery_lng=-46.6620,
        items=[{
            "product_id": "prod-gm-urgente",
            "quantity": 3
        }],
        account_id="0f14ffff"
    )

    assert order["status"] == "ORDER_PLACED"
    assert order["hub_id"] == hub["id"]
    assert order["cro_verified"] == 1
    assert order["subtotal"] == 2700.0
    assert order["total_amount"] > 2700.0  # subtotal + urgency_fee
    assert order["estimated_eta_minutes"] <= 45

    # Valida baixa de estoque no Hub: 10 - 3 = 7
    inv = dentgo_service.get_hub_product_inventory(hub["id"], "prod-gm-urgente", account_id="0f14ffff")
    assert inv["quantity_available"] == 7


def test_dentgo_api_endpoints(client):
    # 1. POST /api/v1/dentgo/hubs
    hub_payload = {
        "name": "Hub API Paulista",
        "cnpj": "99.888.777/0001-11",
        "latitude": -23.5600,
        "longitude": -46.6500,
        "coverage_radius_km": 35.0
    }
    res_hub = client.post("/api/v1/dentgo/hubs", json=hub_payload)
    assert res_hub.status_code == 201
    hub_data = res_hub.json()
    hub_id = hub_data["id"]

    # 2. GET /api/v1/dentgo/hubs
    res_hubs = client.get("/api/v1/dentgo/hubs")
    assert res_hubs.status_code == 200
    assert any(h["id"] == hub_id for h in res_hubs.json())

    # 3. POST /api/v1/dentgo/hubs/{id}/inventory
    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=100)).strftime("%Y-%m-%d")
    inv_payload = {
        "product_id": "prod-api-implant",
        "product_name": "Implante API Teste",
        "anvisa_reg": "ANVISA-991122",
        "batch_number": "LOTE-API-01",
        "quantity_available": 20,
        "unit_price": 750.0,
        "sterilization_expiry_date": valid_expiry
    }
    res_inv = client.post(f"/api/v1/dentgo/hubs/{hub_id}/inventory", json=inv_payload)
    assert res_inv.status_code == 201

    # 4. POST /api/v1/dentgo/hubs/search-emergency
    search_payload = {
        "delivery_lat": -23.5620,
        "delivery_lng": -46.6520,
        "product_id": "prod-api-implant",
        "required_qty": 4
    }
    res_search = client.post("/api/v1/dentgo/hubs/search-emergency", json=search_payload)
    assert res_search.status_code == 200
    results = res_search.json()
    assert len(results) >= 1
    assert results[0]["hub_id"] == hub_id

    # 5. POST /api/v1/dentgo/orders/checkout
    checkout_payload = {
        "customer_cro_uf": "CRO-SP-123456",
        "delivery_address": "Alameda Santos, 1200 - SP",
        "delivery_lat": -23.5630,
        "delivery_lng": -46.6530,
        "items": [
            {
                "product_id": "prod-api-implant",
                "quantity": 2
            }
        ]
    }
    res_ord = client.post("/api/v1/dentgo/orders/checkout", json=checkout_payload)
    assert res_ord.status_code == 201
    ord_data = res_ord.json()
    assert ord_data["status"] == "ORDER_PLACED"
    order_id = ord_data["id"]

    # 6. GET /api/v1/dentgo/orders/{id}
    res_get = client.get(f"/api/v1/dentgo/orders/{order_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == order_id
