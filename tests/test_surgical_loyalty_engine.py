# -*- coding: utf-8 -*-
"""
Test Suite: Programa de Fidelidade "Moeda Cirúrgica" (KeyPartners Loyalty Engine)
Valida acúmulo de pontos por implante, progressão de tier (SILVER -> GOLD -> BLACK_KOL) e resgate de vouchers.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.core.database import get_connection, init_db
from src.features.keypartners import loyalty_engine


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_loyalty_test_environment():
    """Garante tabelas inicializadas e limpa tabelas de loyalty para testes isolados."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO accounts (id, name, plan)
            VALUES ('0f14ffff', 'Odonto Prime Test Tenant', 'Enterprise Scale')
        """)
        cur.execute("DELETE FROM kp_loyalty_transactions")
        cur.execute("DELETE FROM kp_loyalty_wallets")
        conn.commit()
    finally:
        conn.close()


def test_loyalty_credit_progression_silver_to_gold_and_redemption():
    """
    TDD Obrigatório:
    Faturar 30 implantes para um cirurgião:
    - Valida progressão de tier de SILVER para GOLD (>= 25 implantes)
    - Acumula 3.000 pontos (100 pontos por implante)
    - Executa resgate de 1 voucher de frete express no DENTGO (500 pontos)
    - Valida saldo remanescente de 2.500 pontos e geração do código de voucher
    """
    partner_id = "dr-carlos-implantes"
    partner_name = "Dr. Carlos Eduardo Silveira"

    # 1. Faturamento de 30 implantes
    credit_res = loyalty_engine.credit_loyalty_points(
        partner_id=partner_id,
        partner_name=partner_name,
        implants_count=30,
        event_origin="deal.won",
        reference_id="deal-impl-101",
        account_id="0f14ffff"
    )

    assert credit_res["points_earned"] == 3000
    assert credit_res["points_balance"] == 3000
    assert credit_res["implants_billed_total"] == 30
    assert credit_res["previous_tier"] == "SILVER"
    assert credit_res["current_tier"] == "GOLD"
    assert credit_res["tier_promoted"] is True

    # 2. Resgate de 1 voucher de frete express no DENTGO (500 pontos)
    redeem_res = loyalty_engine.redeem_loyalty_reward(
        partner_id=partner_id,
        reward_type_or_id="DENTGO_EXPRESS_VOUCHER",
        account_id="0f14ffff"
    )

    assert redeem_res["points_debited"] == 500
    assert redeem_res["points_balance_remaining"] == 2500
    assert "MOEDA-EXPRESS-" in redeem_res["voucher_code"]
    assert redeem_res["reward_type"] == "DENTGO_EXPRESS_VOUCHER"

    # 3. Consulta de carteira e extrato
    wallet = loyalty_engine.get_partner_loyalty_wallet(partner_id=partner_id, account_id="0f14ffff")
    assert wallet["points_balance"] == 2500
    assert wallet["current_tier"] == "GOLD"
    assert wallet["implants_billed_total"] == 30
    assert len(wallet["transactions"]) == 2  # 1 CREDIT, 1 DEBIT


def test_loyalty_insufficient_balance_raises_error():
    """Valida bloqueio determinístico de resgate caso o parceiro não possua saldo suficiente."""
    partner_id = "dr-iniciante"
    partner_name = "Dr. Gabriel Santos"

    # Credita apenas 2 implantes = 200 pontos
    loyalty_engine.credit_loyalty_points(
        partner_id=partner_id,
        partner_name=partner_name,
        implants_count=2,
        account_id="0f14ffff"
    )

    # Tenta resgatar voucher de 500 pontos
    with pytest.raises(ValueError) as excinfo:
        loyalty_engine.redeem_loyalty_reward(
            partner_id=partner_id,
            reward_type_or_id="DENTGO_EXPRESS_VOUCHER",
            account_id="0f14ffff"
        )

    assert "Saldo insuficiente" in str(excinfo.value)


def test_loyalty_progression_to_black_kol():
    """Valida progressão ao tier máximo BLACK_KOL quando atinge >= 100 implantes faturados."""
    partner_id = "dr-kol-speaker"
    partner_name = "Prof. Dr. Alexandre Magno (Speaker)"

    # Fatura 120 implantes
    res = loyalty_engine.credit_loyalty_points(
        partner_id=partner_id,
        partner_name=partner_name,
        implants_count=120,
        account_id="0f14ffff"
    )

    assert res["implants_billed_total"] == 120
    assert res["current_tier"] == "BLACK_KOL"
    assert res["points_balance"] == 12000


def test_api_loyalty_endpoints():
    """Valida as rotas HTTP FastAPI do motor de fidelidade."""
    # 1. POST /api/v1/keypartners/loyalty/credit
    credit_payload = {
        "partner_id": "dr-api-test",
        "partner_name": "Dra. Renata Figueiredo",
        "implants_count": 30,
        "event_origin": "deal.won"
    }
    res_cred = client.post("/api/v1/keypartners/loyalty/credit", json=credit_payload)
    assert res_cred.status_code == 200
    data_cred = res_cred.json()
    assert data_cred["points_balance"] == 3000
    assert data_cred["current_tier"] == "GOLD"

    # 2. POST /api/v1/keypartners/loyalty/redeem
    redeem_payload = {
        "partner_id": "dr-api-test",
        "reward_type_or_id": "DENTGO_EXPRESS_VOUCHER"
    }
    res_red = client.post("/api/v1/keypartners/loyalty/redeem", json=redeem_payload)
    assert res_red.status_code == 200
    data_red = res_red.json()
    assert data_red["points_balance_remaining"] == 2500
    assert "MOEDA-EXPRESS-" in data_red["voucher_code"]

    # 3. GET /api/v1/keypartners/loyalty/wallet/{partner_id}
    res_wal = client.get("/api/v1/keypartners/loyalty/wallet/dr-api-test")
    assert res_wal.status_code == 200
    data_wal = res_wal.json()
    assert data_wal["points_balance"] == 2500
    assert data_wal["current_tier"] == "GOLD"

    # 4. GET /api/v1/keypartners/loyalty/rewards
    res_cat = client.get("/api/v1/keypartners/loyalty/rewards")
    assert res_cat.status_code == 200
    rewards_list = res_cat.json()
    assert len(rewards_list) >= 4
