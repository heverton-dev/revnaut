# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-27: Módulo de Cosmovigilância, Tecnovigilância ANVISA e Garantia de Osseointegração (RMA)
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection, init_db
from src.features.tickets import anvisa_technovigilance


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_rma_data():
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM anvisa_rma_claims")
        cur.execute("DELETE FROM anvisa_batch_quarantines")
        cur.execute("DELETE FROM dentgo_financial_splits")
        cur.execute("DELETE FROM dentgo_orders")
        cur.execute("DELETE FROM dentgo_hub_inventory WHERE batch_number IN ('LOTE-1122', 'LOTE-9988', 'LOTE-API-77')")
        cur.execute("DELETE FROM dentgo_hubs WHERE id = 'hub-curitiba'")
        cur.execute("DELETE FROM kp_custody_ledger WHERE batch_number IN ('LOTE-1122', 'LOTE-9988', 'LOTE-API-77')")
        cur.execute("DELETE FROM kp_consignment_kits WHERE serial_number IN ('KIT-ANVISA-01')")
        cur.execute("DELETE FROM kp_partner_agreements WHERE id IN ('agr-test-01', 'agr-test-02', 'agr-api-01')")
        cur.execute("DELETE FROM tickets WHERE category = 'Tecnovigilância ANVISA - RMA'")
        conn.commit()
    finally:
        conn.close()


def test_rma_claim_custody_validation_fails_for_unknown_batch():
    # Tenta registrar queixa para um lote inexistente na fábrica ou consignação
    with pytest.raises(ValueError, match="não localizado no histórico de custódia"):
        anvisa_technovigilance.submit_anvisa_rma_claim(
            surgeon_cro_uf="CRO-SP 12345",
            product_id="IMP-CM-3513",
            product_name="Implante Cone Morse 3.5x13",
            batch_number="LOTE-FANTASMA-999",
            fdi_tooth_region="21",
            insertion_torque_ncm=35.0,
            surgery_date="2026-08-01",
            explant_date="2026-09-15",
            failure_reason="loss_of_osseointegration",
            radiograph_r2_key="r2://clinica-sp/rma/raiox-21.jpg",
            enforce_custody_check=True
        )


def test_rma_claim_success_with_warranty_replacement():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO kp_partner_agreements (
                id, account_id, partner_name, partner_cro_uf, tier, credit_limit
            ) VALUES (
                'agr-test-01', '0f14ffff', 'Dr. Lucas Cirurgião', 'CRO-SP 54321', 'GOLD', 50000.0
            )
        """)
        # Seed de custódia KeyPartners prévia
        cur.execute("""
            INSERT INTO kp_custody_ledger (
                id, account_id, agreement_id, movement_type, product_id, product_name,
                anvisa_reg, batch_number, quantity, unit_value, total_value, sterilization_expiry_date
            ) VALUES (
                'mov-t27-01', '0f14ffff', 'agr-test-01', 'CONSIGNMENT_SEND',
                'IMP-CM-3513', 'Implante Cone Morse 3.5x13', 'ANVISA-80123456',
                'LOTE-1122', 50, 180.0, 9000.0, '2028-12-31'
            )
        """)
        conn.commit()
    finally:
        conn.close()

    # Submissão de RMA válida com comprovação radiográfica no R2
    claim = anvisa_technovigilance.submit_anvisa_rma_claim(
        surgeon_cro_uf="CRO-SP 54321",
        surgeon_name="Dr. Lucas Cirurgião",
        product_id="IMP-CM-3513",
        product_name="Implante Cone Morse 3.5x13",
        batch_number="LOTE-1122",
        fdi_tooth_region="16",
        insertion_torque_ncm=40.0,
        surgery_date="2026-07-10",
        explant_date="2026-09-20",
        failure_reason="loss_of_osseointegration",
        radiograph_r2_key="r2://revnault-imaging/rma/raiox-periapical-dente16.png",
        notes="Ausência de osseointegração com mobilidade grau III pós 60 dias."
    )

    assert claim["id"].startswith("rma-")
    assert claim["status"] == "REPLACED_UNDER_WARRANTY"
    assert claim["warranty_approved"] is True
    assert claim["replacement_order_id"].startswith("rep-rma-")
    assert claim["ticket_id"].startswith("tkt-anvisa-")
    assert claim["quarantine_triggered"] is False
    assert claim["batch_failure_rate_percent"] == 2.0  # 1 falha em 50 unidades = 2.0%


def test_quarantine_blocked_when_failure_rate_exceeds_threshold():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO kp_partner_agreements (
                id, account_id, partner_name, partner_cro_uf, tier, credit_limit
            ) VALUES (
                'agr-test-02', '0f14ffff', 'Clínica Paraná', 'CRO-PR 11111', 'GOLD', 50000.0
            )
        """)
        cur.execute("""
            INSERT OR IGNORE INTO dentgo_hubs (
                id, account_id, name, cnpj, latitude, longitude
            ) VALUES (
                'hub-curitiba', '0f14ffff', 'Hub Curitiba Centro', '44.555.666/0001-22', -25.4284, -49.2733
            )
        """)
        # 80 unidades distribuídas do LOTE-9988
        cur.execute("""
            INSERT INTO kp_custody_ledger (
                id, account_id, agreement_id, movement_type, product_id, product_name,
                anvisa_reg, batch_number, quantity, unit_value, total_value, sterilization_expiry_date
            ) VALUES (
                'mov-t27-99', '0f14ffff', 'agr-test-02', 'CONSIGNMENT_SEND',
                'IMP-HE-4110', 'Implante Hexágono Externo 4.1x10', 'ANVISA-80123456',
                'LOTE-9988', 80, 150.0, 12000.0, '2028-10-31'
            )
        """)
        # Estoque no DENTGO Hub com esse lote
        cur.execute("""
            INSERT INTO dentgo_hub_inventory (
                id, hub_id, account_id, product_id, product_name, anvisa_reg,
                batch_number, quantity_available, unit_price, sterilization_expiry_date, status
            ) VALUES (
                'inv-t27-hub-99', 'hub-curitiba', '0f14ffff', 'IMP-HE-4110',
                'Implante Hexágono Externo 4.1x10', 'ANVISA-80123456',
                'LOTE-9988', 20, 150.0, '2028-10-31', 'AVAILABLE'
            )
        """)
        # Kit em consignação KeyPartners contendo o LOTE-9988
        cur.execute("""
            INSERT INTO kp_consignment_kits (
                id, account_id, serial_number, qr_code, name, composition_json, status
            ) VALUES (
                'kit-t27-01', '0f14ffff', 'KIT-ANVISA-01', 'QR-9988',
                'Kit Cirúrgico HE Master', '{"batch_number": "LOTE-9988", "items": ["IMP-HE-4110"]}', 'CONSIGNED'
            )
        """)
        conn.commit()
    finally:
        conn.close()

    # Total distribuído = 80 (kp) + 20 (dentgo) = 100 unidades.
    # 2.5% de 100 = 2.5 unidades.
    # Reclamação 1: 1 / 100 = 1.0% (abaixo do teto de 2.5%)
    c1 = anvisa_technovigilance.submit_anvisa_rma_claim(
        surgeon_cro_uf="CRO-PR 11111",
        product_id="IMP-HE-4110",
        product_name="Implante Hexágono Externo 4.1x10",
        batch_number="LOTE-9988",
        fdi_tooth_region="46",
        insertion_torque_ncm=30.0,
        surgery_date="2026-08-01",
        explant_date="2026-09-01",
        failure_reason="loss_of_osseointegration",
        radiograph_r2_key="r2://imaging/c1.png"
    )
    assert c1["quarantine_triggered"] is False
    assert c1["batch_failure_rate_percent"] == 1.0

    # Reclamação 2: 2 / 100 = 2.0% (ainda abaixo ou igual a 2.5%)
    c2 = anvisa_technovigilance.submit_anvisa_rma_claim(
        surgeon_cro_uf="CRO-PR 22222",
        product_id="IMP-HE-4110",
        product_name="Implante Hexágono Externo 4.1x10",
        batch_number="LOTE-9988",
        fdi_tooth_region="36",
        insertion_torque_ncm=32.0,
        surgery_date="2026-08-05",
        explant_date="2026-09-05",
        failure_reason="fracture",
        radiograph_r2_key="r2://imaging/c2.png"
    )
    assert c2["quarantine_triggered"] is False
    assert c2["batch_failure_rate_percent"] == 2.0

    # Reclamação 3: 3 / 100 = 3.0% (> 2.5% -> TRIGGER DE RECALL / QUARANTINE_BLOCKED)
    c3 = anvisa_technovigilance.submit_anvisa_rma_claim(
        surgeon_cro_uf="CRO-PR 33333",
        product_id="IMP-HE-4110",
        product_name="Implante Hexágono Externo 4.1x10",
        batch_number="LOTE-9988",
        fdi_tooth_region="47",
        insertion_torque_ncm=35.0,
        surgery_date="2026-08-10",
        explant_date="2026-09-10",
        failure_reason="loss_of_osseointegration",
        radiograph_r2_key="r2://imaging/c3.png"
    )
    assert c3["quarantine_triggered"] is True
    assert c3["batch_failure_rate_percent"] == 3.0

    # Verificar que o lote entrou em quarentena sanitária
    q_info = anvisa_technovigilance.get_batch_quarantine_info("LOTE-9988")
    assert q_info is not None
    assert q_info["status"] == "QUARANTINE_BLOCKED"
    assert q_info["total_failures"] == 3
    assert q_info["failure_rate_percent"] == 3.0
    assert "ultrapassando o teto regulatório ANVISA" in q_info["reason"]

    # Verificar bloqueio no DENTGO Hub Inventory
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT status FROM dentgo_hub_inventory WHERE batch_number = 'LOTE-9988'")
        assert cur.fetchone()[0] == "QUARANTINE_BLOCKED"

        # Verificar bloqueio no kit consignado KeyPartners
        cur.execute("SELECT status FROM kp_consignment_kits WHERE serial_number = 'KIT-ANVISA-01'")
        assert cur.fetchone()[0] == "QUARANTINE_BLOCKED"
    finally:
        conn.close()


def test_anvisa_rma_api_endpoints(client):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO kp_partner_agreements (
                id, account_id, partner_name, partner_cro_uf, tier, credit_limit
            ) VALUES (
                'agr-api-01', '0f14ffff', 'Dra. Beatriz Prótese', 'CRO-RJ 99999', 'GOLD', 50000.0
            )
        """)
        cur.execute("""
            INSERT INTO kp_custody_ledger (
                id, account_id, agreement_id, movement_type, product_id, product_name,
                anvisa_reg, batch_number, quantity, unit_value, total_value, sterilization_expiry_date
            ) VALUES (
                'mov-t27-api', '0f14ffff', 'agr-api-01', 'CONSIGNMENT_SEND',
                'IMP-PRO-50', 'Implante Pro 5.0', 'ANVISA-80123456',
                'LOTE-API-77', 100, 200.0, 20000.0, '2029-01-01'
            )
        """)
        conn.commit()
    finally:
        conn.close()

    payload = {
        "surgeon_cro_uf": "CRO-RJ 99999",
        "surgeon_name": "Dra. Beatriz Prótese",
        "product_id": "IMP-PRO-50",
        "product_name": "Implante Pro 5.0",
        "batch_number": "LOTE-API-77",
        "fdi_tooth_region": "22",
        "insertion_torque_ncm": 38.0,
        "surgery_date": "2026-06-01",
        "explant_date": "2026-08-01",
        "failure_reason": "loss_of_osseointegration",
        "radiograph_r2_key": "r2://imaging/dra-beatriz-22.jpg",
        "notes": "Fibrointegração constatada na reabertura cirúrgica."
    }

    # 1. POST /api/v1/tickets/anvisa-rma
    res_post = client.post("/api/v1/tickets/anvisa-rma", json=payload)
    assert res_post.status_code == 201
    data = res_post.json()
    assert data["status"] == "REPLACED_UNDER_WARRANTY"
    claim_id = data["id"]

    # 2. GET /api/v1/tickets/anvisa-rma/{claim_id}
    res_get = client.get(f"/api/v1/tickets/anvisa-rma/{claim_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == claim_id
    assert res_get.json()["batch_number"] == "LOTE-API-77"

    # 3. GET /api/v1/tickets/anvisa-rma (Lista)
    res_list = client.get("/api/v1/tickets/anvisa-rma?batch_number=LOTE-API-77")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1
