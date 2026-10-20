# -*- coding: utf-8 -*-
"""CALL_OFFER recebido pelo webhook assinado /api/v1/webhooks/evolution abre sala SOS LiveKit."""

import os
import hashlib
import hmac
import json
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app

client = TestClient(app, headers=bearer_headers())
SIGNING_KEY = os.environ["OMNICHANNEL_WEBHOOK_SECRET"]

CALL_PAYLOAD = {
    "event": "CALL_OFFER",
    "instance": "consultor_sp_assinado",
    "data": {"id": "call-signed-01", "from": "5511977776666@s.whatsapp.net", "isVideo": True},
}


def _signed_post(payload: dict, key: str = SIGNING_KEY):
    body = json.dumps(payload).encode("utf-8")
    sig = hmac.new(key.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return client.post(
        "/api/v1/webhooks/evolution",
        content=body,
        headers={"Content-Type": "application/json", "X-Evolution-Signature": f"sha256={sig}"},
    )


def test_signed_call_offer_opens_sos_livekit_room():
    res = _signed_post(CALL_PAYLOAD)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["event"] == "CALL_OFFER"
    assert body["action"] == "SOS_VIDEO_LINK_SENT"
    assert body["phone"] == "5511977776666"
    assert "/room/sos-call-signed-01" in body["sos_call_link"]


def test_call_offer_without_valid_signature_is_blocked():
    assert client.post("/api/v1/webhooks/evolution", json=CALL_PAYLOAD).status_code == 401
    assert _signed_post(CALL_PAYLOAD, key="chave-forjada").status_code == 401
