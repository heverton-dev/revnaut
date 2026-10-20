# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-11: Infraestrutura de Salas WebRTC e Telefonia VoIP com LiveKit SFU & LiveKit SIP
"""

import json
import jwt
import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection
from src.features.communications import livekit_service


@pytest.fixture
def client():
    return TestClient(app, headers=bearer_headers())


def test_livekit_generate_room_token():
    token = livekit_service.generate_room_token(
        room_name="deal-room-9901",
        identity="consultant_roberto",
        name="Dr. Roberto Consultor",
        deal_id="d-1",
        account_id="0f14ffff"
    )
    assert token is not None
    assert len(token) > 20

    # Decodifica token sem verificar secret para testar claims
    decoded = jwt.decode(token, options={"verify_signature": False})
    assert decoded["sub"] == "consultant_roberto"
    assert decoded["name"] == "Dr. Roberto Consultor"
    assert decoded["video"]["room"] == "deal-room-9901"
    assert decoded["video"]["roomJoin"] is True
    metadata = json.loads(decoded["metadata"])
    assert metadata["deal_id"] == "d-1"
    assert metadata["account_id"] == "0f14ffff"


def test_livekit_dial_sip_participant():
    res = livekit_service.dial_sip_participant(
        phone_number="+5511988887777",
        room_name="deal-room-9901",
        caller_id="+551140001234",
        deal_id="d-1",
        account_id="0f14ffff"
    )
    assert res["status"] in ["calling", "initiated"]
    assert res["room_name"] == "deal-room-9901"
    assert res["phone_number"] == "+5511988887777"
    assert res["call_id"] is not None

    # Valida persistência da chamada no SQLite
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, deal_id, call_type, status FROM call_recordings WHERE id = ?", (res["call_id"],))
        call_row = cur.fetchone()
        assert call_row is not None
        assert call_row["deal_id"] == "d-1"
        assert call_row["call_type"] == "voip_sip"
    finally:
        conn.close()


def test_livekit_webhook_egress_ended():
    # Cria registro inicial de chamada
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO call_recordings (
                    id, account_id, room_name, deal_id, caller_identity, call_type, status
                ) VALUES (
                    'call-test-99', '0f14ffff', 'deal-room-9901', 'd-1', 'consultant_roberto', 'webrtc', 'in_progress'
                )
            """)
        conn.commit()
    finally:
        conn.close()


    # Payload simulado do webhook LiveKit egress_ended
    webhook_payload = {
        "event": "egress_ended",
        "egressInfo": {
            "egressId": "EG_test_12345",
            "roomName": "deal-room-9901",
            "status": "EGRESS_COMPLETE",
            "fileResults": [
                {
                    "filename": "recordings/deal-room-9901/composite.ogg",
                    "duration": 185
                }
            ]
        }
    }

    result = livekit_service.handle_livekit_webhook(webhook_payload)
    assert result["success"] is True
    assert result["room_name"] == "deal-room-9901"

    # Valida que o registro no banco foi atualizado com a URL da gravação e status completed
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT status, duration_seconds, r2_audio_key, egress_id FROM call_recordings WHERE room_name = 'deal-room-9901'")
        rec_row = cur.fetchone()
        assert rec_row is not None
        assert rec_row["status"] == "completed"
        assert rec_row["duration_seconds"] == 185
        assert rec_row["egress_id"] == "EG_test_12345"
        assert "composite.ogg" in rec_row["r2_audio_key"]
    finally:
        conn.close()


def test_livekit_endpoints_api(client):
    # 1. Obter token de sala
    token_req = {
        "room_name": "deal-room-api-1",
        "identity": "sdr_amanda",
        "name": "Amanda SDR",
        "deal_id": "d-1",
        "account_id": "0f14ffff"
    }
    res_tok = client.post("/api/v1/communications/rooms/token", json=token_req)
    assert res_tok.status_code == 200
    tok_data = res_tok.json()
    assert "token" in tok_data
    assert tok_data["room_name"] == "deal-room-api-1"
    assert "livekit_url" in tok_data

    # 2. Discagem VoIP SIP
    dial_req = {
        "phone_number": "+5511999998888",
        "room_name": "deal-room-api-1",
        "deal_id": "d-1",
        "account_id": "0f14ffff"
    }
    res_dial = client.post("/api/v1/communications/voip/dial", json=dial_req)
    assert res_dial.status_code == 200
    dial_data = res_dial.json()
    assert dial_data["status"] in ["calling", "initiated"]
    assert dial_data["call_id"] is not None

    # 3. Listar gravações do Deal
    res_rec = client.get("/api/v1/communications/deals/d-1/recordings")
    assert res_rec.status_code == 200
    rec_list = res_rec.json()
    assert isinstance(rec_list, list)
