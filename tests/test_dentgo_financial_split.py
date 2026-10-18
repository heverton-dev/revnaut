# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-22: Motor de Monetização do Marketplace: Take-Rate, Frete Cirúrgico e Split de Pagamentos
"""

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection, init_db
from src.features.dentgo import service as dentgo_service
from src.features.dentgo import financial_split
from src.features.keypartners import service as kp_service


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
        cur.execute("DELETE FROM kp_kol_contracts")
        cur.execute("DELETE FROM kp_predictive_inventory_scores")
        cur.execute("DELETE FROM kp_partner_agreements")
        conn.commit()
    finally:
        conn.close()


def test_calculate_and_record_financial_split_pix():
    # 1. Setup Hub e Pedido
    hub = dentgo_service.create_hub(
        name="Hub DENTGO Paulista Split",
        cnpj="77.888.999/0001-11",
        latitude=-23.5600,
        longitude=-46.6600,
        account_id="0f14ffff"
    )

    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")
    dentgo_service.add_hub_inventory(
        hub_id=hub["id"],
        product_id="prod-cm-split",
        product_name="Implante Titânio CM 4.3x11.5",
        anvisa_reg="ANVISA-80123450001",
        batch_number="LOTE-SPLIT-01",
        quantity_available=10,
        unit_price=1000.0,
        sterilization_expiry_date=valid_expiry,
        account_id="0f14ffff"
    )

    order = dentgo_service.create_express_order(
        customer_cro_uf="CRO-SP-99881",
        delivery_address="Alameda Santos, 500 - SP",
        delivery_lat=-23.5610,
        delivery_lng=-46.6610,
        items=[{"product_id": "prod-cm-split", "quantity": 2}], # 2 * 1000 = 2000 subtotal
        account_id="0f14ffff"
    )

    # 2. Executa o Split Financeiro com Take-Rate de 5.0% e PIX
    split_res = financial_split.process_order_financial_split(
        order_id=order["id"],
        platform_take_rate_pct=5.0,
        payment_method="PIX_INSTANT",
        account_id="0f14ffff"
    )

    assert split_res["order_id"] == order["id"]
    assert split_res["items_amount"] == 2000.0
    assert split_res["platform_take_rate_pct"] == 5.0
    assert split_res["platform_fee_amount"] == 100.0  # 5% de 2000.0
    assert split_res["seller_net_payout"] == 1900.0  # 2000.0 - 100.0
    assert split_res["delivery_fee_total"] == order["urgency_fee"]
    assert split_res["courier_net_payout"] == order["urgency_fee"]
    assert split_res["settlement_status"] == "SETTLED"

    # Conciliação centavo a centavo estrita
    reconciled_sum = round(split_res["seller_net_payout"] + split_res["courier_net_payout"] + split_res["platform_fee_amount"], 2)
    assert reconciled_sum == split_res["gross_amount"]


def test_corporate_credit_keypartners_split():
    # 1. Setup Acordo KeyPartners com crédito de R$ 10.000
    agr = kp_service.create_partner_agreement(
        partner_name="Clínica Convênio Corporativo",
        partner_cro_uf="CRO-SP-55443",
        tier="GOLD",
        credit_limit=10000.0,
        account_id="0f14ffff"
    )

    # 2. Setup Hub e Pedido
    hub = dentgo_service.create_hub(
        name="Hub DENTGO Moema",
        cnpj="88.999.000/0001-22",
        latitude=-23.6000,
        longitude=-46.6700,
        account_id="0f14ffff"
    )
    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")
    dentgo_service.add_hub_inventory(
        hub_id=hub["id"],
        product_id="prod-kit-moema",
        product_name="Kit Instrumental Cirúrgico",
        anvisa_reg="ANVISA-80123450001",
        batch_number="LOTE-MOEMA-1",
        quantity_available=5,
        unit_price=1500.0,
        sterilization_expiry_date=valid_expiry,
        account_id="0f14ffff"
    )

    order = dentgo_service.create_express_order(
        customer_cro_uf="CRO-SP-55443",
        delivery_address="Av. Ibirapuera, 1000 - SP",
        delivery_lat=-23.6010,
        delivery_lng=-46.6710,
        items=[{"product_id": "prod-kit-moema", "quantity": 1}],
        account_id="0f14ffff"
    )

    # 3. Fatura no crédito corporativo KeyPartners
    split_res = financial_split.process_order_financial_split(
        order_id=order["id"],
        platform_take_rate_pct=6.0,
        payment_method="CORPORATE_CREDIT",
        agreement_id=agr["id"],
        account_id="0f14ffff"
    )

    assert split_res["settlement_status"] == "INVOICED_CORPORATE"
    assert split_res["agreement_id"] == agr["id"]

    # 4. Verifica que o used_credit do parceiro foi debitado
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT used_credit FROM kp_partner_agreements WHERE id = ?", (agr["id"],))
        agr_row = cur.fetchone()
        assert agr_row["used_credit"] == split_res["gross_amount"]
    finally:
        conn.close()


def test_corporate_credit_exceeded_raises_error():
    # Setup Acordo com limite baixo
    agr = kp_service.create_partner_agreement(
        partner_name="Clínica Limite Baixo",
        partner_cro_uf="CRO-SP-77777",
        tier="SILVER",
        credit_limit=500.0,
        account_id="0f14ffff"
    )
    hub = dentgo_service.create_hub(
        name="Hub DENTGO Sul",
        cnpj="99.000.111/0001-33",
        latitude=-23.6500,
        longitude=-46.7000,
        account_id="0f14ffff"
    )
    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")
    dentgo_service.add_hub_inventory(
        hub_id=hub["id"],
        product_id="prod-high-value",
        product_name="Motor Cirúrgico Digital",
        anvisa_reg="ANVISA-80123450001",
        batch_number="LOTE-EXP-01",
        quantity_available=2,
        unit_price=2000.0,
        sterilization_expiry_date=valid_expiry,
        account_id="0f14ffff"
    )

    order = dentgo_service.create_express_order(
        customer_cro_uf="CRO-SP-77777",
        delivery_address="Av. Santo Amaro, 200 - SP",
        delivery_lat=-23.6510,
        delivery_lng=-46.7010,
        items=[{"product_id": "prod-high-value", "quantity": 1}],
        account_id="0f14ffff"
    )

    with pytest.raises(ValueError, match="Limite de crédito corporativo excedido"):
        financial_split.process_order_financial_split(
            order_id=order["id"],
            platform_take_rate_pct=5.0,
            payment_method="CORPORATE_CREDIT",
            agreement_id=agr["id"],
            account_id="0f14ffff"
        )


def test_dentgo_financial_split_api(client):
    # Setup
    hub = dentgo_service.create_hub(
        name="Hub API Split",
        cnpj="11.222.333/0001-44",
        latitude=-23.5500,
        longitude=-46.6500,
        account_id="0f14ffff"
    )
    valid_expiry = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")
    dentgo_service.add_hub_inventory(
        hub_id=hub["id"],
        product_id="prod-api-split",
        product_name="Biomaterial Enxerto Ósseo",
        anvisa_reg="ANVISA-80123450001",
        batch_number="LOTE-BIO-01",
        quantity_available=10,
        unit_price=500.0,
        sterilization_expiry_date=valid_expiry,
        account_id="0f14ffff"
    )
    order = dentgo_service.create_express_order(
        customer_cro_uf="CRO-SP-12345",
        delivery_address="Rua Augusta, 1500 - SP",
        delivery_lat=-23.5510,
        delivery_lng=-46.6510,
        items=[{"product_id": "prod-api-split", "quantity": 1}],
        account_id="0f14ffff"
    )

    # POST /api/v1/dentgo/orders/{order_id}/split
    payload = {
        "platform_take_rate_pct": 5.0,
        "payment_method": "PIX_INSTANT"
    }
    res = client.post(f"/api/v1/dentgo/orders/{order['id']}/split", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["order_id"] == order["id"]
    assert data["platform_fee_amount"] == 25.0  # 5% de 500.0
    assert data["seller_net_payout"] == 475.0
    assert data["settlement_status"] == "SETTLED"

    # GET /api/v1/dentgo/orders/{order_id}/split
    res_get = client.get(f"/api/v1/dentgo/orders/{order['id']}/split")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == data["id"]

    # GET /api/v1/dentgo/splits
    res_list = client.get("/api/v1/dentgo/splits")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1
