# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-09: Motor de Disparo em Massa de Alta Velocidade com Listmonk Engine
Valida cliente REST Listmonk (sync_subscribers, create_campaign, send_transactional),
chamadas HTTP via httpx (mock_mode=False) e webhook de bounce/open/click.
"""

import json
import httpx
import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection
from src.features.campaigns.listmonk_adapter import ListmonkClient, process_listmonk_webhook_event


@pytest.fixture
def client():
    return TestClient(app, headers=bearer_headers())


def test_listmonk_subscriber_and_campaign_payloads():
    lm = ListmonkClient(base_url="http://mock-listmonk:9000", mock_mode=True)
    sub_payload = lm.build_subscriber_payload(
        email="dr.roberto@implantologia.com.br",
        name="Dr. Roberto Alencar",
        cro="CRO-SP 99881",
        cro_uf="SP",
        specialty="Implantodontia",
        implant_brand="Cone Morse Precision",
        list_ids=[1, 2],
    )
    assert sub_payload["email"] == "dr.roberto@implantologia.com.br"
    assert sub_payload["attribs"]["cro"] == "CRO-SP 99881"
    assert sub_payload["lists"] == [1, 2]

    camp_payload = lm.build_campaign_payload(
        name="Boletim Científico Cone Morse Q1 2026",
        subject="Novas Evidências Clínicas em Carga Imediata",
        body="<h1>Prezado Colega Cirurgião</h1><p>Confira os estudos recentes...</p>",
        list_ids=[1],
    )
    assert camp_payload["name"] == "Boletim Científico Cone Morse Q1 2026"
    assert camp_payload["content_type"] == "html"


def test_listmonk_httpx_real_calls(monkeypatch):
    captured_requests = []

    class DummyResponse:
        def __init__(self, json_data, status_code=200):
            self._json = json_data
            self.status_code = status_code

        def raise_for_status(self):
            if self.status_code >= 400:
                raise httpx.HTTPStatusError("Error", request=None, response=None)

        def json(self):
            return self._json

    class DummyHttpxClient:
        def __init__(self, *args, **kwargs):
            self.auth = kwargs.get("auth")

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def post(self, url, json=None):
            captured_requests.append(("POST", url, json))
            if url.endswith("/api/subscribers"):
                return DummyResponse({"data": {"id": 501}})
            if url.endswith("/api/campaigns"):
                return DummyResponse({"data": {"id": 701, "status": "draft"}})
            if url.endswith("/api/tx"):
                return DummyResponse({"data": True})
            return DummyResponse({"data": {}})

        def put(self, url, json=None):
            captured_requests.append(("PUT", url, json))
            return DummyResponse({"data": {"status": "running"}})

    monkeypatch.setattr(httpx, "Client", DummyHttpxClient)

    lm = ListmonkClient(
        base_url="https://listmonk.revnaut.internal",
        username="admin",
        password="secret",
        mock_mode=False,
    )
    sync_res = lm.sync_subscribers(
        [{"email": "cirurgiao@odonto.br", "name": "Dr. Teste", "cro": "CRO-SP 11223"}]
    )
    assert sync_res["synced_count"] == 1
    assert sync_res["subscriber_ids"] == [501]

    camp_res = lm.create_campaign(
        name="Campanha Teste HTTP",
        subject="Assunto Técnico",
        body="<p>Corpo</p>",
        start_immediately=True,
    )
    assert camp_res["campaign_id"] == 701
    assert camp_res["status"] == "running"

    tx_res = lm.send_transactional("cirurgiao@odonto.br", template_id=3, data={"voucher": "V1"})
    assert tx_res["success"] is True
    assert len(captured_requests) == 4


def test_listmonk_webhook_bounce_open_click(client):
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
                INSERT OR REPLACE INTO contacts (
                    id, account_id, name, email, phone, cro, cro_uf, specialty, score, tags
                ) VALUES (
                    9950, '0f14ffff', 'Dr. Celso Antunes', 'celso.antunes@implantes.br',
                    '+5511977776666', 'CRO-SP 44556', 'SP', 'Implantodontia', 50, '["Inbound"]'
                )
            """)
    finally:
        conn.close()

    # 1. Evento de Click em Catálogo (+15 pts)
    res_click = client.post(
        "/api/v1/campaigns/webhooks/listmonk",
        json={
            "event": "click",
            "email": "celso.antunes@implantes.br",
            "campaign_name": "Catálogo Cone Morse 2026",
            "url": "https://cdn.revnaut.app/catalogo.pdf",
        },
    )
    assert res_click.status_code == 200
    data_click = res_click.json()
    assert data_click["success"] is True
    assert data_click["new_score"] == 65

    # 2. Evento de Bounce (-15 pts e tag email_bounced)
    res_bounce = client.post(
        "/api/v1/webhooks/listmonk",
        json={
            "event": "bounce",
            "email": "celso.antunes@implantes.br",
            "campaign_name": "Boletim Mensal",
        },
    )
    assert res_bounce.status_code == 200
    data_bounce = res_bounce.json()
    assert data_bounce["email_bounced"] is True
    assert data_bounce["new_score"] == 50

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT score, tags FROM contacts WHERE id = 9950")
        row = cur.fetchone()
        tags = json.loads(row["tags"])
        assert "engaged_catalog_click" in tags
        assert "email_bounced" in tags
    finally:
        conn.close()
