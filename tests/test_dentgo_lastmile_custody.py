# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-20: Máquina de Despacho Last-Mile, Custódia por Lacre Térmico e Comprovante no R2
"""

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection, init_db
from src.features.dentgo import service as dentgo_service
from src.features.dentgo import logistics_dispatch


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


def test_full_dispatch_flow_and_pin_verification():
    # 1. Setup Hub e Ordem inicial
    hub = dentgo_service.create_hub(
        name="Hub DENTGO Jardins",
        cnpj="44.555.666/0001-77",
        latitude=-23.5650,
        longitude=-46.6650,
        account_id="0f14ffff"
    )

    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")
    dentgo_service.add_hub_inventory(
        hub_id=hub["id"],
        product_id="prod-cm-urgent-99",
        product_name="Implante CM 4.3x11.5",
        anvisa_reg="ANVISA-80123450001",
        batch_number="LOTE-EXP-01",
        quantity_available=10,
        unit_price=800.0,
        sterilization_expiry_date=valid_expiry,
        account_id="0f14ffff"
    )

    order = dentgo_service.create_express_order(
        customer_cro_uf="CRO-SP-109283",
        delivery_address="Alameda Gabriel Monteiro da Silva, 500",
        delivery_lat=-23.5700,
        delivery_lng=-46.6750,
        items=[{"product_id": "prod-cm-urgent-99", "quantity": 1}],
        account_id="0f14ffff"
    )
    assert order["status"] == "ORDER_PLACED"
    order_id = order["id"]

    # 2. Bipagem no CD: ORDER_PLACED -> PICKING_BIPADO
    picked = logistics_dispatch.bip_picking(order_id, scanned_barcode="789123450001", account_id="0f14ffff")
    assert picked["status"] == "PICKING_BIPADO"

    # 3. Lacre térmico e geração de PIN: PICKING_BIPADO -> SEALED_READY
    sealed = logistics_dispatch.seal_package(order_id, seal_code="LACRE-TERM-2026-991", account_id="0f14ffff")
    assert sealed["status"] == "SEALED_READY"
    assert sealed["seal_code"] == "LACRE-TERM-2026-991"
    pin = sealed["delivery_pin"]
    assert len(pin) == 4
    assert pin.isdigit()

    # 4. Atribuição de entregador: SEALED_READY -> COURIER_ASSIGNED
    assigned = logistics_dispatch.assign_courier(order_id, courier_id="courier-express-07", account_id="0f14ffff")
    assert assigned["status"] == "COURIER_ASSIGNED"
    assert assigned["courier_id"] == "courier-express-07"

    # 5. Início do trânsito: COURIER_ASSIGNED -> IN_TRANSIT_LIVE
    in_transit = logistics_dispatch.start_transit(order_id, account_id="0f14ffff")
    assert in_transit["status"] == "IN_TRANSIT_LIVE"

    # 6. Tentativa de entrega com PIN incorreto
    with pytest.raises(ValueError, match="PIN de entrega incorreto. Validação sanitária de custódia falhou."):
        logistics_dispatch.verify_and_complete_delivery(
            order_id=order_id,
            entered_pin="0000",
            proof_photo_r2_key="pod/dord-test/foto.jpg",
            recipient_name="Dra. Patricia",
            account_id="0f14ffff"
        )

    # 7. Finalização com PIN correto e comprovante no Cloudflare R2
    delivered = logistics_dispatch.verify_and_complete_delivery(
        order_id=order_id,
        entered_pin=pin,
        proof_photo_r2_key="pod/dord-test/foto_lacre_recebido.jpg",
        recipient_name="Dra. Patricia Neves",
        account_id="0f14ffff"
    )
    assert delivered["status"] == "DELIVERED_VERIFIED"
    assert delivered["proof_of_delivery_r2_key"] == "pod/dord-test/foto_lacre_recebido.jpg"
    assert delivered["recipient_signature_name"] == "Dra. Patricia Neves"
    assert delivered["delivered_at"] is not None


def test_dentgo_dispatch_api_endpoints(client):
    # Setup de ordem
    hub = dentgo_service.create_hub(
        name="Hub API Express",
        cnpj="55.666.777/0001-88",
        latitude=-23.5600,
        longitude=-46.6500,
        account_id="0f14ffff"
    )
    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")
    dentgo_service.add_hub_inventory(
        hub_id=hub["id"],
        product_id="prod-api-gm",
        product_name="Implante GM API",
        anvisa_reg="ANVISA-889900",
        batch_number="LOTE-A1",
        quantity_available=5,
        unit_price=1000.0,
        sterilization_expiry_date=valid_expiry,
        account_id="0f14ffff"
    )
    order = dentgo_service.create_express_order(
        customer_cro_uf="CRO-SP-123456",
        delivery_address="Rua Augusta, 1500 - SP",
        delivery_lat=-23.5610,
        delivery_lng=-46.6510,
        items=[{"product_id": "prod-api-gm", "quantity": 1}],
        account_id="0f14ffff"
    )
    order_id = order["id"]

    # 1. POST /api/v1/dentgo/orders/{id}/picking
    res_pick = client.post(f"/api/v1/dentgo/orders/{order_id}/picking", json={"scanned_barcode": "789001"})
    assert res_pick.status_code == 200
    assert res_pick.json()["status"] == "PICKING_BIPADO"

    # 2. POST /api/v1/dentgo/orders/{id}/seal
    res_seal = client.post(f"/api/v1/dentgo/orders/{order_id}/seal", json={"seal_code": "LACRE-API-01"})
    assert res_seal.status_code == 200
    seal_data = res_seal.json()
    assert seal_data["status"] == "SEALED_READY"
    pin = seal_data["delivery_pin"]

    # 3. POST /api/v1/dentgo/orders/{id}/assign-courier
    res_assign = client.post(f"/api/v1/dentgo/orders/{order_id}/assign-courier", json={"courier_id": "courier-api-99"})
    assert res_assign.status_code == 200
    assert res_assign.json()["status"] == "COURIER_ASSIGNED"

    # 4. POST /api/v1/dentgo/orders/{id}/start-transit
    res_trans = client.post(f"/api/v1/dentgo/orders/{order_id}/start-transit")
    assert res_trans.status_code == 200
    assert res_trans.json()["status"] == "IN_TRANSIT_LIVE"

    # 5. POST /api/v1/dentgo/orders/{id}/verify-delivery (PIN errado -> 400)
    bad_payload = {
        "entered_pin": "9999",
        "proof_photo_r2_key": "pod/err/foto.png",
        "recipient_name": "Recepção"
    }
    res_bad = client.post(f"/api/v1/dentgo/orders/{order_id}/verify-delivery", json=bad_payload)
    assert res_bad.status_code == 400

    # 6. POST /api/v1/dentgo/orders/{id}/verify-delivery (PIN correto -> 200)
    good_payload = {
        "entered_pin": pin,
        "proof_photo_r2_key": "pod/ok/foto_final.png",
        "recipient_name": "Dra. Renata"
    }
    res_good = client.post(f"/api/v1/dentgo/orders/{order_id}/verify-delivery", json=good_payload)
    assert res_good.status_code == 200
    assert res_good.json()["status"] == "DELIVERED_VERIFIED"
