# -*- coding: utf-8 -*-
"""
Testes TDD - TICKET-06: Conector Plug & Play TOTVS Protheus (SA1 / SC5 / SC6)
Valida a sincronização de clientes, emissão de pedidos e garantia de idempotência via SQLite WAL outbox.
"""

import uuid
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection

client = TestClient(app, headers=bearer_headers())


def test_sync_customer_sa1():
    """Valida sincronização bidirecional de cliente SA1 com metadados odontológicos (CRO/UF)."""
    cnpj = f"{uuid.uuid4().int % 100000000000000:014d}"
    payload = {
        "A1_NOME": "Clínica Implantar Odontologia Ltda",
        "A1_CGC": cnpj,
        "A1_X_CRO": "SP-77889",
        "A1_LC": 125000.0,
        "A1_MUN": "Campinas",
        "A1_EST": "SP"
    }

    res = client.post("/api/v1/integrations/totvs/customers/sync", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["success"] is True
    assert data["entity"] == "SA1"
    assert data["data"]["A1_CGC"] == cnpj
    assert data["data"]["A1_X_CRO"] == "SP-77889"
    assert data["data"]["sync_status"] == "synced"


def test_create_sales_order_sc5_and_sc6():
    """Valida emissão de pedido de venda com itens e vínculo com negócio (Deal)."""
    idemp_key = f"order_idemp_{uuid.uuid4().hex[:8]}"
    payload = {
        "C5_CLIENTE": "CLI001",
        "C5_LOJACLI": "01",
        "C5_CONDPAG": "030",
        "C5_TOTAL": 48500.0,
        "deal_id": "d-1",
        "idempotency_key": idemp_key,
        "items": [
            {
                "C6_ITEM": "01",
                "C6_PRODUTO": "IMP-CONE-MORSE-35",
                "C6_QTD": 20.0,
                "C6_PRCVEN": 1800.0,
                "C6_VALOR": 36000.0
            },
            {
                "C6_ITEM": "02",
                "C6_PRODUTO": "KIT-PROTETICO-CADCAM",
                "C6_QTD": 5.0,
                "C6_PRCVEN": 2500.0,
                "C6_VALOR": 12500.0
            }
        ]
    }

    res = client.post("/api/v1/integrations/totvs/orders", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["success"] is True
    assert data["entity"] == "SC5"
    assert data["idempotency_key"] == idemp_key
    assert data["data"]["items_count"] == 2
    assert "C5_NUM" in data["data"]


def test_totvs_idempotency_guarantee():
    """Garante que requisições com a mesma idempotency_key retornem o resultado original sem duplicar pedidos."""
    idemp_key = f"order_idemp_strict_{uuid.uuid4().hex[:8]}"
    payload = {
        "C5_CLIENTE": "CLI002",
        "C5_LOJACLI": "01",
        "C5_CONDPAG": "001",
        "C5_TOTAL": 15000.0,
        "idempotency_key": idemp_key,
        "items": [
            {
                "C6_ITEM": "01",
                "C6_PRODUTO": "BIO-OSS-05G",
                "C6_QTD": 10.0,
                "C6_PRCVEN": 1500.0,
                "C6_VALOR": 15000.0
            }
        ]
    }

    # Primeira chamada: emite
    res1 = client.post("/api/v1/integrations/totvs/orders", json=payload)
    assert res1.status_code == 201
    pv_num_1 = res1.json()["data"]["C5_NUM"]

    # Segunda chamada com MESMA chave: deve retornar idempotente sem criar novo número de PV
    res2 = client.post("/api/v1/integrations/totvs/orders", json=payload)
    assert res2.status_code == 201
    assert res2.json()["status"] == "already_processed"
    pv_num_2 = res2.json()["data"]["C5_NUM"]
    assert pv_num_1 == pv_num_2, "Idempotência violada: novo número de pedido gerado!"


def test_list_outbox_queue():
    """Valida leitura e auditoria da fila local de outbox no SQLite WAL."""
    res = client.get("/api/v1/integrations/totvs/outbox")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    assert all("idempotency_key" in item for item in items)
