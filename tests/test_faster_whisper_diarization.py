# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-12: Pipeline STT de Alta Performance com faster-whisper e Diarização pyannote.audio
"""

import json
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection
from src.features.intelligence.transcription_worker import process_call_audio


@pytest.fixture
def client():
    return TestClient(app)


def test_transcription_worker_diarizes_commercial_dialogue():
    # 1. Setup da gravação de chamada no banco
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM call_transcriptions WHERE call_id = 'call-test-rec-12'")
            cur.execute("DELETE FROM semantic_embeddings WHERE entity_id LIKE 'transc-call-test-rec-12%'")
            cur.execute("""
                INSERT OR REPLACE INTO call_recordings (
                    id, account_id, room_name, deal_id, caller_identity,
                    receiver_identity, call_type, status, duration_seconds, r2_audio_key
                ) VALUES (
                    'call-test-rec-12', '0f14ffff', 'deal-d-1', 'd-1', 'consultant_lucas',
                    '+5511999998888', 'voip_sip', 'completed', 45, 'recordings/deal-d-1/audio.ogg'
                )
            """)
        conn.commit()
    finally:
        conn.close()

    # Fixture de diálogo simulando áudio gravado entre consultor e cirurgião
    sample_dialogue = (
        "[00:00 - 00:08] SPEAKER_CONSULTANT: Bom dia Dr. Roberto! Como estão as cirurgias de implante essa semana?\n"
        "[00:09 - 00:22] SPEAKER_SURGEON: Olá Lucas, tudo ótimo. Estou precisando repor 15 implantes Cone Morse 3.75x11 e 5 de 4.3x13.\n"
        "[00:23 - 00:35] SPEAKER_CONSULTANT: Perfeito Doutor. Temos em estoque pronta entrega com chave de inserção inclusa.\n"
        "[00:36 - 00:44] SPEAKER_SURGEON: Maravilha, me envie a proposta com faturamento para 30 dias por gentileza."
    )

    # 2. Executa processamento pelo worker
    result = process_call_audio(
        call_id="call-test-rec-12",
        account_id="0f14ffff",
        dialogue_text=sample_dialogue,
        duration_seconds=44.0
    )

    assert result["success"] is True
    assert result["transcription_id"] is not None
    assert result["deal_id"] == "d-1"
    assert len(result["segments"]) == 4

    # Valida diarização dos participantes
    speakers = {seg["speaker"] for seg in result["segments"]}
    assert "SPEAKER_CONSULTANT" in speakers
    assert "SPEAKER_SURGEON" in speakers
    assert result["segments"][1]["speaker"] == "SPEAKER_SURGEON"
    assert "Cone Morse" in result["segments"][1]["text"]

    # 3. Valida persistência em call_transcriptions
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, deal_id, full_text, segments_json FROM call_transcriptions WHERE id = ?", (result["transcription_id"],))
        row = cur.fetchone()
        assert row is not None
        assert row["deal_id"] == "d-1"
        assert "Cone Morse" in row["full_text"]
        stored_segments = json.loads(row["segments_json"])
        assert len(stored_segments) == 4

        # 4. Valida indexação semântica em semantic_embeddings
        cur.execute(
            "SELECT COUNT(*) FROM semantic_embeddings WHERE entity_id = ? AND entity_type = 'call_transcript'",
            (result["transcription_id"],)
        )
        emb_count = cur.fetchone()[0]
        assert emb_count >= 1
    finally:
        conn.close()


def test_transcription_api_endpoints(client):
    # Setup call recording
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO call_recordings (
                    id, account_id, room_name, deal_id, caller_identity,
                    call_type, status, duration_seconds
                ) VALUES (
                    'call-api-stt-1', '0f14ffff', 'deal-d-1', 'd-1', 'consultant_ana',
                    'webrtc', 'completed', 30
                )
            """)
        conn.commit()
    finally:
        conn.close()

    # 1. Dispara transcrição via endpoint
    req_payload = {
        "call_id": "call-api-stt-1",
        "account_id": "0f14ffff",
        "dialogue_text": "[00:00 - 00:10] SPEAKER_CONSULTANT: Alô Dr. Marcos.\n[00:11 - 00:25] SPEAKER_SURGEON: Gostaria de testar o kit cirúrgico guiado.",
        "duration_seconds": 25.0
    }
    res = client.post("/api/v1/intelligence/transcriptions/process", json=req_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["transcription_id"] is not None
    transc_id = data["transcription_id"]

    # 2. Busca transcrição específica por ID
    res_get = client.get(f"/api/v1/intelligence/transcriptions/{transc_id}")
    assert res_get.status_code == 200
    get_data = res_get.json()
    assert get_data["id"] == transc_id
    assert len(get_data["segments"]) == 2

    # 3. Busca transcrições vinculadas ao Deal
    res_deal = client.get("/api/v1/intelligence/transcriptions/deal/d-1")
    assert res_deal.status_code == 200
    deal_list = res_deal.json()
    assert isinstance(deal_list, list)
    assert any(t["id"] == transc_id for t in deal_list)
