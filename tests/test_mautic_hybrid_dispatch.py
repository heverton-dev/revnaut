# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-08: Arquitetura Híbrida Mautic Visual + Despachante Determinístico
"""

import os
import hmac
import hashlib
import json
import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection
from src.features.campaigns.mautic_bridge import (
    resolve_consultant_for_contact,
    render_template_variables,
    process_mautic_campaign_action,
)

TEST_SIGNING_KEY = os.environ["OMNICHANNEL_WEBHOOK_SECRET"]


def _generate_hmac(payload_dict: dict, signing_key: str = TEST_SIGNING_KEY) -> str:
    body_bytes = json.dumps(payload_dict).encode("utf-8")
    return hmac.new(signing_key.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()


@pytest.fixture
def client():
    return TestClient(app, headers=bearer_headers())


def test_resolve_consultant_routing():
    # Insere consultor de teste e contato atribuído
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO users (id, account_id, name, email, role)
                VALUES ('u_field_rep_sp1', '0f14ffff', 'Carlos Eduardo Consultor', 'carlos.sp@revnault.com', 'Consultor')
            """)
            cur.execute("""
                INSERT OR REPLACE INTO contacts (id, account_id, name, email, phone, cro, field_owner_id, specialty)
                VALUES (9901, '0f14ffff', 'Dr. Henrique Valente', 'henrique.valente@dent.com', '+5511999991111', 'CRO-SP 88112', 'u_field_rep_sp1', 'Implantodontia')
            """)
        conn.commit()
    finally:
        conn.close()

    # Resolver dono da carteira
    consultant = resolve_consultant_for_contact(9901)
    assert consultant is not None
    assert consultant["id"] == "u_field_rep_sp1"
    assert consultant["name"] == "Carlos Eduardo Consultor"
    assert "carlos" in consultant["instance_name"].lower() or "sp1" in consultant["instance_name"].lower()


def test_render_template_variables():
    template = "Olá {{contact.name}}, aqui é o {{consultant.name}}! Seu CRO {{contact.cro}} já foi homologado."
    contact = {"name": "Dr. Henrique Valente", "cro": "CRO-SP 88112"}
    consultant = {"name": "Carlos Eduardo Consultor"}

    rendered = render_template_variables(template, contact, consultant)
    assert "Olá Dr. Henrique Valente" in rendered
    assert "Carlos Eduardo Consultor" in rendered
    assert "CRO-SP 88112" in rendered
    assert "{{" not in rendered


def test_mautic_campaign_action_webhook_endpoint(client):
    # Simula payload de ação de campanha visual do Mautic (disparo de WhatsApp direcionado)
    payload = {
        "event": "mautic.campaign_action",
        "action": "send_whatsapp",
        "campaign_id": 401,
        "campaign_name": "Nutrição Especialista Cone Morse 2026",
        "contact": {
            "id": 9901,
            "email": "henrique.valente@dent.com",
            "name": "Dr. Henrique Valente",
            "phone": "+5511999991111",
            "cro": "CRO-SP 88112"
        },
        "message_template": "Olá {{contact.name}}, seu kit experimental com torque guiado está disponível! Fale comigo, {{consultant.name}}."
    }

    raw_signature = _generate_hmac(payload)
    body_bytes = json.dumps(payload).encode("utf-8")

    # 1. Requisição sem assinatura deve ser bloqueada (Lei #13)
    res_unauth = client.post(
        "/api/v1/webhooks/mautic/campaign-action",
        content=body_bytes,
        headers={"Content-Type": "application/json"}
    )
    assert res_unauth.status_code == 401

    # 2. Requisição com HMAC válido
    res_auth = client.post(
        "/api/v1/webhooks/mautic/campaign-action",
        content=body_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Mautic-Signature": f"sha256={raw_signature}"
        }
    )
    assert res_auth.status_code == 200
    data = res_auth.json()
    assert data["success"] is True
    assert data["action"] == "send_whatsapp"
    assert data["contact_id"] == 9901
    assert data["consultant_id"] == "u_field_rep_sp1"
    assert "carlos" in data["dispatched_instance"].lower() or "sp1" in data["dispatched_instance"].lower()
    assert "Dr. Henrique Valente" in data["rendered_message"]

