# -*- coding: utf-8 -*-
"""
Test Suite: Loop Viral de Indicação B2B (Member-Get-Member Cirúrgico entre Colegas de Pós/CRO)
Valida links rastreáveis, bloqueio de auto-indicação, aceleração de lead (+40 pts) e bonificação mútua (R$ 600).
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.core.database import get_connection, init_db
from src.features.campaigns import referral_mgm
from src.features.keypartners import loyalty_engine


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_referral_test_env():
    """Garante tabelas inicializadas e limpa tabelas de referral e loyalty."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO accounts (id, name, plan)
            VALUES ('0f14ffff', 'Odonto Prime Test Tenant', 'Enterprise Scale')
        """)
        cur.execute("DELETE FROM referral_conversions")
        cur.execute("DELETE FROM referral_links")
        cur.execute("DELETE FROM kp_loyalty_transactions")
        cur.execute("DELETE FROM kp_loyalty_wallets")
        cur.execute("""
            DELETE FROM contacts
            WHERE cro_uf IN (
                'CRO-SP 11111', 'CRO-SP 22222', 'CRO-RJ 33333',
                'CRO-MG 44444', 'CRO-MG 55551', 'CRO-MG 55552',
                'CRO-RS 77777', 'CRO-RS 88888'
            )
        """)
        conn.commit()
    finally:
        conn.close()


def test_referral_mgm_full_loop_marcos_and_lucas():
    """
    TDD Obrigatório:
    1. Gerar código MGM para o Dr. Marcos (CRO-SP 11111)
    2. Cadastrar Dr. Lucas (CRO-SP 22222) usando o código
    3. Fechar o primeiro Deal do Dr. Lucas
    4. Validar crédito automático de R$ 600 em bonificação (Moedas Cirúrgicas) para ambos
    """
    # 1. Gerar link e código MGM para o Dr. Marcos
    link_info = referral_mgm.generate_referral_link(
        referrer_id="dr-marcos-11111",
        referrer_name="Dr. Marcos Vinicius",
        referrer_cro_uf="CRO-SP 11111",
        account_id="0f14ffff"
    )

    assert "MGM-CRO-SP-11111" in link_info["referral_code"]
    assert "https://revnault.app.br/r/" in link_info["referral_url"]

    # 2. Cadastrar Dr. Lucas usando o código
    cand_info = referral_mgm.register_referral_lead(
        referral_code=link_info["referral_code"],
        referred_name="Dr. Lucas Silveira",
        referred_cro_uf="CRO-SP 22222",
        referred_phone="+5511988882222",
        referred_email="dr.lucas@clinica.com.br",
        account_id="0f14ffff"
    )

    assert cand_info["status"] == "LEAD_CAPTURED"
    assert cand_info["lead_score_boost"] == 40
    assert cand_info["referred_name"] == "Dr. Lucas Silveira"
    assert cand_info["referrer_id"] == "dr-marcos-11111"

    # Verifica se o contato foi criado no CRM com a tag de indicação
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM contacts WHERE cro_uf = 'CRO-SP 22222' AND account_id = '0f14ffff'")
        contact = cur.fetchone()
        assert contact is not None
        assert "origem_indicacao_kol" in contact["tags"]
    finally:
        conn.close()

    # 3. Fechar o primeiro Deal do Dr. Lucas e qualificar a indicação
    qualify_res = referral_mgm.qualify_referral_deal_won(
        deal_id="deal-lucas-first-won",
        referred_cro_uf="CRO-SP 22222",
        account_id="0f14ffff"
    )

    assert qualify_res["status"] == "BONUS_CREDITED"
    assert qualify_res["referrer_bonus_amount"] == 600.0
    assert qualify_res["referred_bonus_amount"] == 600.0

    # 4. Validar crédito de Moedas Cirúrgicas nas carteiras de ambos
    wallet_marcos = loyalty_engine.get_partner_loyalty_wallet("dr-marcos-11111", account_id="0f14ffff")
    assert wallet_marcos["points_balance"] == 600

    wallet_lucas = loyalty_engine.get_partner_loyalty_wallet(str(cand_info["referred_contact_id"]), account_id="0f14ffff")
    assert wallet_lucas["points_balance"] == 600


def test_referral_self_referral_prevention():
    """Valida bloqueio imediato contra tentativa de auto-indicação com o mesmo CRO/UF."""
    link_info = referral_mgm.generate_referral_link(
        referrer_id="dr-fraude-01",
        referrer_name="Dr. Joao da Silva",
        referrer_cro_uf="CRO-RJ 33333",
        account_id="0f14ffff"
    )

    with pytest.raises(ValueError) as excinfo:
        referral_mgm.register_referral_lead(
            referral_code=link_info["referral_code"],
            referred_name="Dr. Joao Outro",
            referred_cro_uf="CRO-RJ 33333",  # Mesmo CRO
            account_id="0f14ffff"
        )

    assert "Auto-indicação proibida" in str(excinfo.value)


def test_referral_dashboard_metrics():
    """Valida resumo de métricas do dashboard do indicador."""
    link_info = referral_mgm.generate_referral_link(
        referrer_id="dr-promoter-01",
        referrer_name="Dra. Camila Nogueira",
        referrer_cro_uf="CRO-MG 44444",
        account_id="0f14ffff"
    )

    # Cadastra 2 indicados
    referral_mgm.register_referral_lead(
        referral_code=link_info["referral_code"],
        referred_name="Colega 1",
        referred_cro_uf="CRO-MG 55551",
        account_id="0f14ffff"
    )
    referral_mgm.register_referral_lead(
        referral_code=link_info["referral_code"],
        referred_name="Colega 2",
        referred_cro_uf="CRO-MG 55552",
        account_id="0f14ffff"
    )

    # Qualifica 1 indicação
    referral_mgm.qualify_referral_deal_won(
        deal_id="deal-col-1",
        referred_cro_uf="CRO-MG 55551",
        account_id="0f14ffff"
    )

    dash = referral_mgm.get_referral_dashboard(referrer_id="dr-promoter-01", account_id="0f14ffff")
    assert dash["total_referrals"] == 2
    assert dash["qualified_referrals"] == 1
    assert dash["total_bonus_earned"] == 600.0


def test_api_referral_mgm_endpoints():
    """Valida as rotas HTTP FastAPI do motor MGM."""
    # 1. POST /api/v1/campaigns/referral/generate-link
    res_link = client.post("/api/v1/campaigns/referral/generate-link", json={
        "referrer_id": "dr-api-ref",
        "referrer_name": "Dr. Fernando Teles",
        "referrer_cro_uf": "CRO-RS 77777"
    })
    assert res_link.status_code == 200
    link_data = res_link.json()
    assert "MGM-CRO-RS-77777" in link_data["referral_code"]

    # 2. POST /api/v1/campaigns/referral/register
    res_reg = client.post("/api/v1/campaigns/referral/register", json={
        "referral_code": link_data["referral_code"],
        "referred_name": "Dra. Patricia Lima",
        "referred_cro_uf": "CRO-RS 88888",
        "referred_phone": "+5551977776666"
    })
    assert res_reg.status_code == 201
    reg_data = res_reg.json()
    assert reg_data["status"] == "LEAD_CAPTURED"

    # 3. POST /api/v1/campaigns/referral/qualify
    res_qual = client.post("/api/v1/campaigns/referral/qualify", json={
        "deal_id": "deal-patricia-api",
        "referred_cro_uf": "CRO-RS 88888"
    })
    assert res_qual.status_code == 200
    qual_data = res_qual.json()
    assert qual_data["status"] == "BONUS_CREDITED"
    assert qual_data["referrer_bonus_amount"] == 600.0

    # 4. GET /api/v1/campaigns/referral/dashboard/{referrer_id}
    res_dash = client.get("/api/v1/campaigns/referral/dashboard/dr-api-ref")
    assert res_dash.status_code == 200
    dash_data = res_dash.json()
    assert dash_data["qualified_referrals"] == 1
    assert dash_data["total_bonus_earned"] == 600.0
