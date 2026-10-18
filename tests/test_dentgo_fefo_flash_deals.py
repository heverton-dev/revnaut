# -*- coding: utf-8 -*-
"""
Testes TDD para TICKET-37: Liquidação Inteligente FEFO de Lotes com Validade Curta
via Flash Deals no DENTGO.
"""

from __future__ import annotations
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection, init_db
from src.features.dentgo import fefo_flash_deals

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_fefo_test_db():
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM fefo_flash_deal_reservations WHERE account_id = '0f14ffff'")
        cur.execute("DELETE FROM fefo_flash_deals WHERE account_id = '0f14ffff'")
        cur.execute("DELETE FROM dentgo_hub_inventory WHERE account_id = '0f14ffff'")
        cur.execute("DELETE FROM dentgo_hubs WHERE cnpj = '11222333000199'")
        cur.execute("DELETE FROM contacts WHERE email LIKE ?", ("%@fefo-test.com",))
        cur.execute("DELETE FROM omnichannel_messages WHERE account_id = '0f14ffff'")

        # Cria Hub Campinas (-22.9056, -47.0608)
        cur.execute("""
            INSERT INTO dentgo_hubs (
                id, account_id, name, cnpj, latitude, longitude,
                coverage_radius_km, on_duty_schedule, is_active
            ) VALUES (
                'hub-campinas-test', '0f14ffff', 'DENTGO Hub Campinas', '11222333000199',
                -22.9056, -47.0608, 50.0, '24h', 1
            )
        """)

        # Cria Cirurgiões para o teste: 2 em Campinas (um alto giro biomaterial, um geral) e 1 no Rio de Janeiro
        cur.execute("""
            INSERT INTO contacts (
                account_id, name, email, phone, company, tags, score,
                cro, cro_uf, city, state, customer_type, monthly_implants_volume
            ) VALUES
            (
                '0f14ffff', 'Dr. Rafael Campinas', 'rafael@fefo-test.com', '+5519991112233',
                'Clínica Campinas Implantes', '["biomateriais", "alto_giro_regeneracao"]', 95,
                '12345', 'SP', 'Campinas', 'SP', 'CIRURGIAO', 40
            ),
            (
                '0f14ffff', 'Dra. Beatriz Paulinia', 'beatriz@fefo-test.com', '+5519994445566',
                'Instituto Paulínia Oral', '["biomateriais", "enxerto_osseo"]', 85,
                '23456', 'SP', 'Paulínia', 'SP', 'CIRURGIAO', 25
            ),
            (
                '0f14ffff', 'Dr. Rodrigo Carioca', 'rodrigo@fefo-test.com', '+5521997778899',
                'Barra Dental Center', '["biomateriais", "alto_giro"]', 90,
                '34567', 'RJ', 'Rio de Janeiro', 'RJ', 'CIRURGIAO', 50
            )
        """)
        conn.commit()
    finally:
        conn.close()


def test_fefo_scan_detects_batches_in_6_to_9_months_window():
    """Valida identificação de lotes com validade residual entre 6 e 9 meses (210 dias)."""
    ref_date = "2026-05-01"
    ref_dt = datetime.strptime(ref_date, "%Y-%m-%d")

    # Lote 1: 20 membranas de colágeno vencendo em 7 meses (210 dias) -> DENTRO DO ALERTA
    exp_7m = (ref_dt + timedelta(days=210)).strftime("%Y-%m-%d")
    # Lote 2: 50 implantes vencendo em 24 meses (720 dias) -> FORA DO ALERTA
    exp_24m = (ref_dt + timedelta(days=720)).strftime("%Y-%m-%d")
    # Lote 3: 10 brocas vencendo em 2 meses (60 dias) -> FORA DO ALERTA (vencimento imediato)
    exp_2m = (ref_dt + timedelta(days=60)).strftime("%Y-%m-%d")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO dentgo_hub_inventory (
                id, hub_id, account_id, product_id, product_name, anvisa_reg,
                batch_number, quantity_available, unit_price, sterilization_expiry_date
            ) VALUES
            ('inv-membrana-20', 'hub-campinas-test', '0f14ffff', 'BIO-MEM-COL-20',
             'Membrana de Colágeno Reabsorvível 20x30mm', 'ANVISA-80123456780', 'LOTE-MEM-7M',
             20, 320.0, ?),
            ('inv-implante-50', 'hub-campinas-test', '0f14ffff', 'IMP-CM-4311',
             'Implante Cone Morse 4.3x11mm', 'ANVISA-80123456789', 'LOTE-IMP-24M',
             50, 480.0, ?),
            ('inv-broca-10', 'hub-campinas-test', '0f14ffff', 'INST-BROCA-20',
             'Broca Lança Titanium', 'ANVISA-80123456799', 'LOTE-BROCA-2M',
             10, 150.0, ?)
        """, (exp_7m, exp_24m, exp_2m))
        conn.commit()
    finally:
        conn.close()

    result = fefo_flash_deals.scan_and_generate_flash_deals(
        reference_date=ref_date,
        discount_percentage=35.0,
        account_id="0f14ffff"
    )

    assert result["scanned_batches"] >= 3
    assert result["created_deals_count"] == 1

    deals = result["created_deals"]
    assert len(deals) == 1
    deal = deals[0]

    assert deal["product_id"] == "BIO-MEM-COL-20"
    assert deal["batch_number"] == "LOTE-MEM-7M"
    assert deal["original_quantity"] == 20
    assert deal["available_quantity"] == 20
    assert deal["original_unit_price"] == 320.0
    assert deal["discount_percentage"] == 35.0
    # 320 * (1 - 0.35) = 208.0
    assert deal["flash_unit_price"] == 208.0
    assert 6.0 <= deal["months_to_expire"] <= 9.0
    assert deal["status"] == "ACTIVE"


def test_target_surgeons_segmentation_by_radius_and_consumption():
    """Valida direcionamento exclusivo aos cirurgiões num raio de 50 km de Campinas que consomem biomateriais."""
    ref_date = "2026-05-01"
    exp_7m = (datetime.strptime(ref_date, "%Y-%m-%d") + timedelta(days=210)).strftime("%Y-%m-%d")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO dentgo_hub_inventory (
                id, hub_id, account_id, product_id, product_name, anvisa_reg,
                batch_number, quantity_available, unit_price, sterilization_expiry_date
            ) VALUES
            ('inv-membrana-target', 'hub-campinas-test', '0f14ffff', 'BIO-MEM-COL-20',
             'Membrana de Colágeno Reabsorvível 20x30mm', 'ANVISA-80123456780', 'LOTE-MEM-TARGET',
             20, 320.0, ?)
        """, (exp_7m,))
        conn.commit()
    finally:
        conn.close()

    result = fefo_flash_deals.scan_and_generate_flash_deals(
        reference_date=ref_date,
        discount_percentage=35.0,
        account_id="0f14ffff"
    )

    deal = result["created_deals"][0]
    target_surgeons = deal["target_surgeons"]

    # Deve conter os 2 cirurgiões da região de Campinas (Campinas e Paulínia) e NÃO o do Rio de Janeiro
    surgeon_names = [s["name"] for s in target_surgeons]
    assert "Dr. Rafael Campinas" in surgeon_names
    assert "Dra. Beatriz Paulinia" in surgeon_names
    assert "Dr. Rodrigo Carioca" not in surgeon_names

    # Valida persistência dos disparos de WhatsApp com 1-clique no banco de mensagens omnichannel
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT content, remote_jid FROM omnichannel_messages WHERE content LIKE ?", ("%Flash Deal DENTGO%",))
        messages = cur.fetchall()
        assert len(messages) == 2
        for m in messages:
            assert "Membrana de Colágeno" in m["content"]
            assert "35%" in m["content"]
            assert "dentgo.app" in m["content"]
    finally:
        conn.close()


def test_atomic_reservation_of_flash_deal_batch():
    """Valida reserva atômica de saldo e esgotamento automático do lote."""
    ref_date = "2026-05-01"
    exp_7m = (datetime.strptime(ref_date, "%Y-%m-%d") + timedelta(days=210)).strftime("%Y-%m-%d")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO dentgo_hub_inventory (
                id, hub_id, account_id, product_id, product_name, anvisa_reg,
                batch_number, quantity_available, unit_price, sterilization_expiry_date
            ) VALUES
            ('inv-membrana-atomic', 'hub-campinas-test', '0f14ffff', 'BIO-MEM-COL-20',
             'Membrana de Colágeno Reabsorvível 20x30mm', 'ANVISA-80123456780', 'LOTE-ATOMIC-20',
             20, 320.0, ?)
        """, (exp_7m,))
        conn.commit()
    finally:
        conn.close()

    result = fefo_flash_deals.scan_and_generate_flash_deals(
        reference_date=ref_date,
        account_id="0f14ffff"
    )
    deal_id = result["created_deals"][0]["id"]

    # 1. Cirurgião reserva 5 unidades
    res1 = fefo_flash_deals.reserve_flash_deal_batch(
        deal_id=deal_id,
        surgeon_cro_uf="12345-SP",
        surgeon_name="Dr. Rafael Campinas",
        quantity=5,
        account_id="0f14ffff"
    )

    assert res1["quantity_reserved"] == 5
    assert res1["remaining_available"] == 15
    assert res1["status"] == "RESERVED"

    # Confirma baixa atômica no dentgo_hub_inventory
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT quantity_available FROM dentgo_hub_inventory WHERE id = 'inv-membrana-atomic'")
        assert cur.fetchone()["quantity_available"] == 15
    finally:
        conn.close()

    # 2. Cirurgião reserva as 15 unidades restantes -> esgota o lote
    res2 = fefo_flash_deals.reserve_flash_deal_batch(
        deal_id=deal_id,
        surgeon_cro_uf="23456-SP",
        surgeon_name="Dra. Beatriz Paulinia",
        quantity=15,
        account_id="0f14ffff"
    )
    assert res2["remaining_available"] == 0
    assert res2["deal_status"] == "EXHAUSTED"

    # 3. Tentativa de reservar mais 1 unidade deve falhar com erro estrito de estoque
    with pytest.raises(ValueError, match="Estoque insuficiente ou lote esgotado"):
        fefo_flash_deals.reserve_flash_deal_batch(
            deal_id=deal_id,
            surgeon_cro_uf="12345-SP",
            surgeon_name="Dr. Rafael Campinas",
            quantity=1,
            account_id="0f14ffff"
        )


def test_api_endpoints_fefo_flash_deals():
    """Valida endpoints REST OpenAPI 3.1 para o motor FEFO."""
    ref_date = "2026-05-01"
    exp_7m = (datetime.strptime(ref_date, "%Y-%m-%d") + timedelta(days=210)).strftime("%Y-%m-%d")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO dentgo_hub_inventory (
                id, hub_id, account_id, product_id, product_name, anvisa_reg,
                batch_number, quantity_available, unit_price, sterilization_expiry_date
            ) VALUES
            ('inv-membrana-api', 'hub-campinas-test', '0f14ffff', 'BIO-MEM-COL-20',
             'Membrana de Colágeno Reabsorvível 20x30mm', 'ANVISA-80123456780', 'LOTE-MEM-API',
             20, 320.0, ?)
        """, (exp_7m,))
        conn.commit()
    finally:
        conn.close()

    # 1. Disparar varredura FEFO via API
    resp_scan = client.post(
        "/api/v1/dentgo/fefo/scan",
        json={
            "reference_date": ref_date,
            "discount_percentage": 40.0,
            "account_id": "0f14ffff"
        }
    )
    assert resp_scan.status_code == 200
    scan_data = resp_scan.json()
    assert scan_data["created_deals_count"] >= 1
    deal = scan_data["created_deals"][0]
    deal_id = deal["id"]

    # 2. Listar Flash Deals ativos via API
    resp_list = client.get("/api/v1/dentgo/fefo/deals?status=ACTIVE")
    assert resp_list.status_code == 200
    deals_list = resp_list.json()
    assert len(deals_list) >= 1
    assert any(d["id"] == deal_id for d in deals_list)

    # 3. Reservar via API (1 clique checkout)
    resp_res = client.post(
        f"/api/v1/dentgo/fefo/deals/{deal_id}/reserve",
        json={
            "surgeon_name": "Dr. Rafael Campinas",
            "surgeon_cro_uf": "12345-SP",
            "quantity": 10,
            "account_id": "0f14ffff"
        }
    )
    assert resp_res.status_code == 201
    res_data = resp_res.json()
    assert res_data["quantity_reserved"] == 10
    assert res_data["remaining_available"] == 10
    assert res_data["status"] == "RESERVED"
