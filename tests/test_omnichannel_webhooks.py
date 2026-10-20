# -*- coding: utf-8 -*-
"""
Testes TDD - TICKET-07: Gateway Unificado Omnichannel (Evolution API + Chatwoot + Mautic)
Simula payloads reais com validação de assinatura HMAC SHA-256 e atualização de score/timeline.
"""

import os
import hmac
import hashlib
import json
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection

client = TestClient(app, headers=bearer_headers())
TEST_SIGNING_KEY = os.environ["OMNICHANNEL_WEBHOOK_SECRET"]


def _generate_hmac(payload_dict: dict, signing_key: str = TEST_SIGNING_KEY) -> str:
    body_bytes = json.dumps(payload_dict).encode("utf-8")
    return hmac.new(signing_key.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()


def test_hmac_gate_blocks_invalid_signature():
    """Lei #13: Prova que requisições com assinatura HMAC forjada ou ausente são bloqueadas com HTTP 401."""
    payload = {"event": "messages.upsert", "data": {}}
    
    # Sem assinatura
    res1 = client.post("/api/v1/webhooks/evolution", json=payload)
    assert res1.status_code == 401
    assert "Assinatura HMAC inválida" in res1.json()["detail"]

    # Com assinatura falsa
    res2 = client.post(
        "/api/v1/webhooks/evolution",
        json=payload,
        headers={"X-Evolution-Signature": "sha256=assinatura_falsa_12345"}
    )
    assert res2.status_code == 401


def test_evolution_api_webhook_updates_surgeon_score_and_timeline():
    """Simula resposta inbound de cirurgião via WhatsApp na Evolution API v2."""
    # Garante um contato de teste com telefone conhecido
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT id, phone FROM contacts WHERE phone IS NOT NULL LIMIT 1")
        row = cur.fetchone()
        contact_id = row["id"]
        phone_raw = row["phone"]
        cur.execute("UPDATE contacts SET score = 60 WHERE id = ?", (contact_id,))
        score_before = 60
    conn.close()


    phone_clean = "".join(filter(str.isdigit, phone_raw))

    payload = {
        "event": "messages.upsert",
        "instance": "revnault-evolution-prod",
        "data": {
            "key": {
                "remoteJid": f"{phone_clean}@s.whatsapp.net",
                "fromMe": False,
                "id": "EVO_MSG_12345"
            },
            "message": {
                "conversation": "Olá, gostaríamos de agendar a cirurgia demonstrativa com o kit de implantes cone morse."
            }
        }
    }

    body_bytes = json.dumps(payload).encode("utf-8")
    sig = _generate_hmac(payload)

    res = client.post(
        "/api/v1/webhooks/evolution",
        content=body_bytes,
        headers={"Content-Type": "application/json", "X-Evolution-Signature": f"sha256={sig}"}
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["success"] is True
    assert data["contact_id"] == contact_id
    assert data["score_updated"] is not None
    assert data["score_updated"] > score_before

    # Verifica persistência na timeline
    res_timeline = client.get(f"/api/v1/contacts/{contact_id}/timeline")
    assert res_timeline.status_code == 200
    timeline = res_timeline.json()["timeline"]
    actions = [item["action"] for item in timeline]
    assert "WHATSAPP_RESPONSE" in actions


def test_chatwoot_webhook_updates_interaction():
    """Simula interação de atendimento recebida no Chatwoot."""
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT id, email, score FROM contacts WHERE email IS NOT NULL LIMIT 1")
        row = cur.fetchone()
        contact_id = row["id"]
        email = row["email"]
    conn.close()

    payload = {
        "event": "message_created",
        "sender": {
            "type": "contact",
            "email": email,
            "name": "Dr. Cirurgião Teste"
        },
        "content": "Confirmando recebimento das brocas cirúrgicas."
    }

    body_bytes = json.dumps(payload).encode("utf-8")
    sig = _generate_hmac(payload)

    res = client.post(
        "/api/v1/webhooks/chatwoot",
        content=body_bytes,
        headers={"Content-Type": "application/json", "X-Chatwoot-Signature": sig}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["contact_id"] == contact_id


def test_mautic_webhook_updates_lead_score():
    """Simula evento lead.changepoints disparado pelo Mautic 5."""
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT id, email FROM contacts WHERE email IS NOT NULL LIMIT 1")
        row = cur.fetchone()
        contact_id = row["id"]
        email = row["email"]
    conn.close()

    payload = {
        "event": "lead.changepoints",
        "lead": {
            "id": 999,
            "email": email,
            "points": 95
        }
    }

    body_bytes = json.dumps(payload).encode("utf-8")
    sig = _generate_hmac(payload)

    res = client.post(
        "/api/v1/webhooks/mautic",
        content=body_bytes,
        headers={"Content-Type": "application/json", "X-Mautic-Signature": sig}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["contact_id"] == contact_id
    assert data["score_updated"] == 95

    # Valida atualização do score no banco
    res_prof = client.get(f"/api/v1/contacts/{contact_id}/profile")
    assert res_prof.status_code == 200
    assert res_prof.json()["score"] == 95
