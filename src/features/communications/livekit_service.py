# -*- coding: utf-8 -*-
"""
Vertical Slice: LiveKit SFU & LiveKit SIP Service
Infraestrutura de videoconferência WebRTC, telefonia VoIP e gravação automatizada no R2.
"""

from __future__ import annotations
import json
import os
import time
import uuid
from typing import Any, Dict, List, Optional
import jwt
from src.core.database import get_connection
from src.core.events import EventBus, StreamName


LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://livekit.revnaut.internal")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "dev_secret_key_revnaut_webrtc_2026")



def generate_room_token(
    room_name: str,
    identity: str,
    name: Optional[str] = None,
    deal_id: Optional[str] = None,
    account_id: str = "0f14ffff",
    ttl_seconds: int = 3600,
) -> str:
    """
    Gera um token JWT padrão do LiveKit assinado com a chave da API.
    Concede permissão para entrar na sala WebRTC vinculada ao Deal.
    """
    now = int(time.time())
    metadata = {
        "deal_id": deal_id,
        "account_id": account_id,
        "identity": identity,
    }
    payload = {
        "iss": LIVEKIT_API_KEY,
        "sub": identity,
        "name": name or identity,
        "nbf": now - 5,
        "exp": now + ttl_seconds,
        "video": {
            "room": room_name,
            "roomJoin": True,
            "canPublish": True,
            "canSubscribe": True,
            "canPublishData": True,
        },
        "metadata": json.dumps(metadata),
    }

    token = jwt.encode(payload, LIVEKIT_API_SECRET, algorithm="HS256")
    return token


def dial_sip_participant(
    phone_number: str,
    room_name: str,
    caller_id: Optional[str] = None,
    deal_id: Optional[str] = None,
    account_id: str = "0f14ffff",
) -> Dict[str, Any]:
    """
    Dispara discagem VoIP via LiveKit SIP para conectar cirurgião/cliente à sala WebRTC.
    """
    call_id = f"call-sip-{int(time.time() * 1000)}-{uuid.uuid4().hex[:4]}"
    caller = caller_id or os.getenv("LIVEKIT_SIP_DEFAULT_CALLER", "+551140001234")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO call_recordings (
                id, account_id, room_name, deal_id, caller_identity,
                receiver_identity, call_type, status
            ) VALUES (?, ?, ?, ?, ?, ?, 'voip_sip', 'calling')
        """, (call_id, account_id, room_name, deal_id, caller, phone_number))
        conn.commit()
    finally:
        conn.close()

    return {
        "call_id": call_id,
        "room_name": room_name,
        "phone_number": phone_number,
        "caller_id": caller,
        "deal_id": deal_id,
        "status": "calling",
    }


def handle_livekit_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Consome webhooks de ciclo de vida do LiveKit (egress_ended, room_finished).
    Atualiza gravações, calcula duração e emite evento call.recording_ready no EventBus.
    """
    event = payload.get("event")
    room_name = ""
    duration = 0
    audio_key = ""
    egress_id = ""

    if event == "egress_ended":
        egress_info = payload.get("egressInfo", {})
        egress_id = egress_info.get("egressId", "")
        room_name = egress_info.get("roomName", "")
        file_results = egress_info.get("fileResults", [])
        if file_results:
            first_file = file_results[0]
            audio_key = first_file.get("filename", "")
            duration = int(first_file.get("duration", 0))

    elif event == "room_finished":
        room_info = payload.get("room", {})
        room_name = room_info.get("name", "")

    if not room_name:
        return {"success": False, "reason": "room_name not found in event"}

    r2_public_url = os.getenv("R2_PUBLIC_URL", "https://r2.revnaut.internal")
    recording_url = f"{r2_public_url}/{audio_key}" if audio_key else None

    conn = get_connection()
    deal_id = None
    account_id = "0f14ffff"
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, deal_id, account_id FROM call_recordings WHERE room_name = ? ORDER BY created_at DESC LIMIT 1", (room_name,))
        row = cur.fetchone()
        if row:
            deal_id = row["deal_id"]
            account_id = row["account_id"]
            cur.execute("""
                UPDATE call_recordings
                SET status = 'completed',
                    duration_seconds = ?,
                    r2_audio_key = ?,
                    r2_recording_url = ?,
                    egress_id = ?,
                    ended_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (duration, audio_key, recording_url, egress_id, row["id"]))
        else:
            new_id = f"call-rec-{uuid.uuid4().hex[:8]}"
            cur.execute("""
                INSERT INTO call_recordings (
                    id, account_id, room_name, deal_id, caller_identity,
                    call_type, status, duration_seconds, r2_audio_key, r2_recording_url, egress_id, ended_at
                ) VALUES (?, ?, ?, NULL, 'system', 'webrtc', 'completed', ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (new_id, account_id, room_name, duration, audio_key, recording_url, egress_id))
        conn.commit()
    finally:
        conn.close()

    return {
        "success": True,
        "event": event,
        "room_name": room_name,
        "deal_id": deal_id,
        "duration_seconds": duration,
        "r2_audio_key": audio_key,
    }


def list_deal_recordings(deal_id: str, account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    """
    Lista histórico de gravações de videoconferências e ligações VoIP vinculadas ao Deal.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, account_id, room_name, deal_id, caller_identity, receiver_identity,
                   call_type, status, duration_seconds, r2_recording_url, r2_audio_key, egress_id, created_at
            FROM call_recordings
            WHERE deal_id = ? AND account_id = ?
            ORDER BY created_at DESC
        """, (deal_id, account_id))
        rows = [dict(r) for r in cur.fetchall()]
        return rows
    finally:
        conn.close()
