# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-23: Orquestrador de Sharding da Evolution API v2 e Espelhamento em Tempo Real
"""

import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection, init_db
from src.features.integrations.omnichannel import evolution_cluster
from src.features.integrations.omnichannel import evolution_webhook_router


@pytest.fixture
def client():
    return TestClient(app, headers=bearer_headers())


@pytest.fixture(autouse=True)
def clean_omnichannel_tables():
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM omnichannel_messages")
        cur.execute("DELETE FROM whatsapp_instances")
        conn.commit()
    finally:
        conn.close()


def test_evolution_cluster_sharding_distribution():
    # 1. Configura 3 shards
    shards = [
        "http://evolution-shard-1:8080",
        "http://evolution-shard-2:8080",
        "http://evolution-shard-3:8080"
    ]

    # 2. Provisiona 3 instâncias de consultores e verifica distribuição balanceada
    inst1 = evolution_cluster.provision_whatsapp_instance(
        instance_name="consultor_joao_sp",
        consultant_user_id="usr-joao",
        phone_number="+5511988881111",
        account_id="0f14ffff",
        shard_nodes=shards
    )
    inst2 = evolution_cluster.provision_whatsapp_instance(
        instance_name="consultor_maria_rj",
        consultant_user_id="usr-maria",
        phone_number="+5521977772222",
        account_id="0f14ffff",
        shard_nodes=shards
    )
    inst3 = evolution_cluster.provision_whatsapp_instance(
        instance_name="consultor_carlos_mg",
        consultant_user_id="usr-carlos",
        phone_number="+5531966663333",
        account_id="0f14ffff",
        shard_nodes=shards
    )

    allocated_shards = {inst1["shard_node_url"], inst2["shard_node_url"], inst3["shard_node_url"]}
    # Cada uma das 3 instâncias deve ter ido para um shard diferente (balanceamento de carga)
    assert len(allocated_shards) == 3
    assert inst1["status"] in ("CONNECTING", "DISCONNECTED", "CONNECTED")

    # 3. Provisiona a 4ª instância — deve reutilizar o primeiro com menor contagem
    inst4 = evolution_cluster.provision_whatsapp_instance(
        instance_name="consultor_ana_pr",
        consultant_user_id="usr-ana",
        phone_number="+5541955554444",
        account_id="0f14ffff",
        shard_nodes=shards
    )
    assert inst4["shard_node_url"] in shards


def test_call_offer_webhook_triggers_sos_livekit_video_room():
    # Simula webhook de tentativa de chamada de voz no WhatsApp recebida durante ato operatório
    call_payload = {
        "event": "CALL_OFFER",
        "instance": "consultor_joao_sp",
        "data": {
            "id": "call-surge-991",
            "from": "5511999998888@s.whatsapp.net",
            "timestamp": 1729200000,
            "isVideo": False,
            "isGroup": False
        }
    }

    result = evolution_webhook_router.handle_evolution_event(
        payload=call_payload,
        account_id="0f14ffff"
    )

    assert result["event"] == "CALL_OFFER"
    assert result["action"] == "SOS_VIDEO_LINK_SENT"
    assert "https://meet.revops.local/room/sos-" in result["sos_call_link"]
    assert "urgência cirúrgica" in result["response_message"]
    assert result["phone"] == "5511999998888"

    # Verifica persistência no histórico de mensagens omnichannel
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM omnichannel_messages WHERE remote_jid = ?", ("5511999998888@s.whatsapp.net",))
        row = cur.fetchone()
        assert row is not None
        assert row["message_type"] == "CALL_OFFER"
        assert row["sos_call_link"] == result["sos_call_link"]
    finally:
        conn.close()


def test_messages_upsert_with_media_archive():
    # Simula mensagem com imagem de exame ou radiografia enviada pelo cirurgião
    msg_payload = {
        "event": "messages.upsert",
        "instance": "consultor_joao_sp",
        "data": {
            "key": {
                "remoteJid": "5511999998888@s.whatsapp.net",
                "fromMe": False,
                "id": "msg-tomografia-001"
            },
            "messageType": "imageMessage",
            "message": {
                "imageMessage": {
                    "caption": "Tomografia do dente 36 antes de abrir o retalho",
                    "mimetype": "image/jpeg",
                    "url": "https://mmg.whatsapp.net/d/f/xxx.enc"
                }
            }
        }
    }

    result = evolution_webhook_router.handle_evolution_event(
        payload=msg_payload,
        account_id="0f14ffff"
    )

    assert result["event"] in ("messages.upsert", "MESSAGES_UPSERT")
    assert result["status"] == "STORED"
    assert "whatsapp_media/0f14ffff/consultor_joao_sp" in result["media_r2_key"]


def test_evolution_cluster_api_endpoints(client):
    # 1. POST /api/v1/omnichannel/whatsapp/instances
    payload = {
        "instance_name": "consultor_api_test",
        "consultant_user_id": "usr-api-10",
        "phone_number": "+5511944445555"
    }
    res = client.post("/api/v1/omnichannel/whatsapp/instances", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["instance_name"] == "consultor_api_test"
    assert "http://evolution-shard-" in data["shard_node_url"]

    # 2. GET /api/v1/omnichannel/whatsapp/instances/{instance_name}
    res_get = client.get("/api/v1/omnichannel/whatsapp/instances/consultor_api_test")
    assert res_get.status_code == 200
    assert res_get.json()["instance_name"] == "consultor_api_test"

    # 3. GET /api/v1/omnichannel/whatsapp/instances
    res_list = client.get("/api/v1/omnichannel/whatsapp/instances")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 4. POST /api/v1/omnichannel/webhook/evolution com CALL_OFFER
    call_payload = {
        "event": "CALL_OFFER",
        "instance": "consultor_api_test",
        "data": {
            "id": "call-api-11",
            "from": "5511988887777@s.whatsapp.net"
        }
    }
    res_webhook = client.post("/api/v1/omnichannel/webhook/evolution", json=call_payload)
    assert res_webhook.status_code == 200
    w_data = res_webhook.json()
    assert w_data["success"] is True
    assert "sos_call_link" in w_data
