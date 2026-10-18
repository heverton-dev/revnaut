# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-09: Motor de Disparo em Massa com Listmonk Engine
Valida cliente Listmonk v2, serialização de atributos odontológicos e endpoint de broadcast.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.features.campaigns.listmonk_adapter import ListmonkClient


@pytest.fixture
def client():
    return TestClient(app)


def test_listmonk_subscriber_payload_serialization():
    lm = ListmonkClient(base_url="http://mock-listmonk:9000")
    
    # Valida estrutura do payload de assinante odontológico
    payload = lm.build_subscriber_payload(
        email="dr.roberto@implantologia.com.br",
        name="Dr. Roberto Alencar",
        cro="CRO-SP 99881",
        cro_uf="SP",
        specialty="Implantodontia",
        implant_brand="Cone Morse Precision",
        list_ids=[1, 2]
    )

    assert payload["email"] == "dr.roberto@implantologia.com.br"
    assert payload["name"] == "Dr. Roberto Alencar"
    assert payload["lists"] == [1, 2]
    assert payload["attribs"]["cro"] == "CRO-SP 99881"
    assert payload["attribs"]["cro_uf"] == "SP"
    assert payload["attribs"]["specialty"] == "Implantodontia"
    assert payload["attribs"]["implant_brand"] == "Cone Morse Precision"


def test_listmonk_campaign_creation_payload():
    lm = ListmonkClient(base_url="http://mock-listmonk:9000")


    campaign_payload = lm.build_campaign_payload(
        name="Boletim Científico Cone Morse Q1 2026",
        subject="Novas Evidências Clínicas em Carga Imediata",
        body="<h1>Prezado Colega Cirurgião</h1><p>Confira os estudos recentes...</p>",
        list_ids=[1]
    )

    assert campaign_payload["name"] == "Boletim Científico Cone Morse Q1 2026"
    assert campaign_payload["subject"] == "Novas Evidências Clínicas em Carga Imediata"
    assert campaign_payload["type"] == "regular"
    assert campaign_payload["content_type"] == "html"
    assert campaign_payload["lists"] == [1]


def test_listmonk_broadcast_endpoint(client):
    broadcast_request = {
        "title": "Aviso Urgente de Lote de Implantes",
        "subject": "Atualização Regulatória ANVISA - Lote C-2026",
        "body_html": "<p>Prezados doutores, informamos a liberação do lote de anilhas cirúrgicas.</p>",
        "target_uf": "SP",
        "target_specialty": "Implantodontia",
        "listmonk_list_id": 1
    }

    res = client.post("/api/v1/campaigns/broadcast-listmonk", json=broadcast_request)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["status"] in ("queued", "running", "dispatched")
    assert data["queued_count"] >= 0
    assert data["listmonk_campaign_id"] is not None
