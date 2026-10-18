# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-14: Motor Dinâmico de Catálogo Odontológico, Multi-Tabela de Preços e Alçadas de Desconto
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection
from src.features.deals.catalog_pricing import (
    calculate_proposal_pricing,
    approve_discount_request,
    list_catalog_products,
    list_price_tables
)


@pytest.fixture
def client():
    return TestClient(app)


def test_catalog_and_price_tables_listing():
    products = list_catalog_products()
    assert len(products) >= 2
    assert any(p["sku"] == "IMP-CM-37511" for p in products)

    tables = list_price_tables()
    assert len(tables) >= 3
    table_keys = {t["table_key"] for t in tables}
    assert "BALCAO" in table_keys
    assert "FRANQUIA" in table_keys


def test_discount_governance_blocks_excessive_discount():
    # Setup Deal
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM deal_discount_requests WHERE deal_id = ?", ("d-1",))
            cur.execute("UPDATE deals SET approval_status = 'APPROVED' WHERE id = 'd-1'")
        conn.commit()
    finally:
        conn.close()

    # Consultor com alçada máxima de 5% tenta aplicar 15% de desconto
    items = [
        {"sku": "IMP-CM-37511", "quantity": 20}  # 20 * 450 = 9.000
    ]

    proposal = calculate_proposal_pricing(
        deal_id="d-1",
        table_key="BALCAO",
        items=items,
        requested_discount_pct=15.0,
        user_id="u_consultor_pedro",
        user_role="consultor",
        account_id="0f14ffff"
    )

    # Valida que foi bloqueado por alçada e entrou em aprovação pendente
    assert proposal["requires_approval"] is True
    assert proposal["status"] == "PENDING_DISCOUNT_APPROVAL"
    assert proposal["max_allowed_pct"] == 5.0
    assert proposal["requested_discount_pct"] == 15.0
    assert proposal["request_id"] is not None

    # Valida status do Deal no banco
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT approval_status FROM deals WHERE id = 'd-1'")
        deal_row = cur.fetchone()
        assert deal_row["approval_status"] == "PENDING_DISCOUNT_APPROVAL"

        # Valida inserção na tabela deal_discount_requests
        cur.execute("SELECT status, discount_pct FROM deal_discount_requests WHERE id = ?", (proposal["request_id"],))
        req_row = cur.fetchone()
        assert req_row is not None
        assert req_row["status"] == "PENDING_APPROVAL"
        assert req_row["discount_pct"] == 15.0
    finally:
        conn.close()

    # Gerente (gestor) aprova a solicitação de desconto
    approval_res = approve_discount_request(
        request_id=proposal["request_id"],
        approver_user_id="u_gerente_marcos",
        account_id="0f14ffff"
    )

    assert approval_res["success"] is True
    assert approval_res["status"] == "APPROVED"

    # Valida desbloqueio do Deal no banco
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT approval_status FROM deals WHERE id = 'd-1'")
        deal_updated = cur.fetchone()
        assert deal_updated["approval_status"] == "APPROVED"
    finally:
        conn.close()


def test_pricing_endpoints_api(client):
    # 1. Listar catálogo
    res_cat = client.get("/api/v1/deals/catalog/products")
    assert res_cat.status_code == 200
    prods = res_cat.json()
    assert isinstance(prods, list)
    assert len(prods) >= 1

    # 2. Listar tabelas de preço
    res_tab = client.get("/api/v1/deals/catalog/price-tables")
    assert res_tab.status_code == 200
    tabs = res_tab.json()
    assert isinstance(tabs, list)
    assert len(tabs) >= 1

    # 3. Calcular proposta dentro da alçada (3% de desconto)
    calc_req = {
        "deal_id": "d-1",
        "table_key": "BALCAO",
        "items": [{"sku": "IMP-CM-37511", "quantity": 10}],
        "requested_discount_pct": 3.0,
        "user_id": "u_consultor_1",
        "user_role": "consultor",
        "account_id": "0f14ffff"
    }
    res_calc = client.post("/api/v1/deals/catalog/calculate-proposal", json=calc_req)
    assert res_calc.status_code == 200
    calc_data = res_calc.json()
    assert calc_data["requires_approval"] is False
    assert calc_data["status"] == "APPROVED"
    assert calc_data["final_value"] > 0
