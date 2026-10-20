# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-23: Cluster Sharding Evolution API v2 & Espelhamento Bidirecional (CALL_OFFER, MESSAGES_UPSERT, CONTACTS_UPSERT)
"""

import base64
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection
from src.features.integrations.omnichannel import evolution_cluster, evolution_webhook_router


client = TestClient(app, headers=bearer_headers())


def test_evolution_cluster_sharding_load_balancing():
    shards = [
        "http://evolution-shard-alpha:8080",
        "http://evolution-shard-beta:8080",
    ]
    inst1 = evolution_cluster.provision_whatsapp_instance(
        instance_name="consultor-sp-shard-01",
        consultant_user_id="u-sp-01",
        phone_number="+5511977771111",
        account_id="0f14ffff",
        shard_nodes=shards,
        mock_mode=True,
    )
    inst2 = evolution_cluster.provision_whatsapp_instance(
        instance_name="consultor-sp-shard-02",
        consultant_user_id="u-sp-02",
        phone_number="+5511977772222",
        account_id="0f14ffff",
        shard_nodes=shards,
        mock_mode=True,
    )
    assert inst1["shard_node_url"] in shards
    assert inst2["shard_node_url"] in shards
    assert inst1["shard_node_url"] != inst2["shard_node_url"]


def test_evolution_call_offer_generates_real_livekit_jwt():
    payload = {
        "event": "CALL_OFFER",
        "instance": "consultor-sp-shard-01",
        "data": {
            "id": "call-urg-991",
            "from": "5511988887777@s.whatsapp.net",
        },
    }
    res = evolution_webhook_router.handle_evolution_event(payload, account_id="0f14ffff")
    assert res["success"] is True
    assert res["action"] == "SOS_VIDEO_LINK_SENT"
    assert "livekit_token" in res
    assert res["livekit_token"].count(".") == 2
    assert "token=" in res["sos_call_link"]


def test_evolution_messages_upsert_uploads_media_to_r2_and_contacts_upsert():
    raw_pdf = b"%PDF-1.4\nTomografia Computadorizada Cone Beam"
    payload_media = {
        "event": "MESSAGES_UPSERT",
        "instance": "consultor-sp-shard-01",
        "data": {
            "key": {"id": "med-9001", "remoteJid": "5511988887777@s.whatsapp.net", "fromMe": False},
            "messageType": "documentMessage",
            "base64": base64.b64encode(raw_pdf).decode("ascii"),
            "message": {"documentMessage": {"caption": "Exame DICOM Guiado"}},
        },
    }
    res_media = evolution_webhook_router.handle_evolution_event(payload_media, account_id="0f14ffff")
    assert res_media["success"] is True
    assert res_media["media_r2_key"] == "whatsapp_media/0f14ffff/consultor-sp-shard-01/med-9001.bin"
    assert res_media["media_r2_url"].endswith(res_media["media_r2_key"])

    payload_contacts = {
        "event": "CONTACTS_UPSERT",
        "instance": "consultor-sp-shard-01",
        "data": [
            {"id": "5511966665555@s.whatsapp.net", "pushName": "Dr. Henrique Buco"}
        ],
    }
    res_contacts = evolution_webhook_router.handle_evolution_event(payload_contacts, account_id="0f14ffff")
    assert res_contacts["success"] is True
    assert res_contacts["status"] == "CONTACTS_SYNCED"
    assert res_contacts["synced_count"] == 1
