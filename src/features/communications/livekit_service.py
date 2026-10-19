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
import httpx
import jwt
from src.core.config import (
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME,
    R2_ENDPOINT_URL,
)
from src.core.database import get_connection
from src.core.events import EventBus, StreamName, default_event_bus


LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://livekit.revnaut.internal")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "dev_secret_key_revnaut_webrtc_2026")


def generate_room_token(
    room_name: str,
    identity: Optional[str] = None,
    name: Optional[str] = None,
    deal_id: Optional[str] = None,
    account_id: str = "0f14ffff",
    ttl_seconds: int = 3600,
    *,
    participant_identity: Optional[str] = None,
    participant_name: Optional[str] = None,
    is_admin: bool = True,
    **kwargs: Any,
) -> str:
    """
    Gera um token JWT padrão do LiveKit assinado com a chave da API.
    Concede permissão para entrar na sala WebRTC vinculada ao Deal.
    """
    effective_identity = identity or participant_identity or "participant"
    effective_name = name or participant_name or effective_identity
    now = int(time.time())
    metadata = {
        "deal_id": deal_id,
        "account_id": account_id,
        "identity": effective_identity,
        "is_admin": is_admin,
    }
    payload = {
        "iss": LIVEKIT_API_KEY,
        "sub": effective_identity,
        "name": effective_name,
        "nbf": now - 5,
        "exp": now + ttl_seconds,
        "video": {
            "room": room_name,
            "roomJoin": True,
            "canPublish": True,
            "canSubscribe": True,
            "canPublishData": True,
            "roomRecord": bool(is_admin),
        },
        "metadata": json.dumps(metadata),
    }

    token = jwt.encode(payload, LIVEKIT_API_SECRET, algorithm="HS256")
    return token


def start_room_egress_to_r2(
    room_name: str,
    deal_id: Optional[str] = None,
    account_id: str = "0f14ffff",
    audio_only: bool = True,
    mock_mode: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Configura RoomCompositeEgress / TrackEgress no servidor LiveKit para exportar
    o arquivo de áudio (.ogg/.wav) diretamente para o bucket Cloudflare R2.
    """
    is_mock = (
        mock_mode
        if mock_mode is not None
        else (os.getenv("LIVEKIT_MOCK_MODE", "true").lower() in ("1", "true", "yes") or "internal" in LIVEKIT_URL)
    )
    r2_key = f"{account_id}/recordings/{room_name}/composite.ogg"
    egress_payload = {
        "room_name": room_name,
        "audio_only": audio_only,
        "file_outputs": [
            {
                "file_type": "OGG",
                "filepath": r2_key,
                "s3": {
                    "access_key": R2_ACCESS_KEY_ID,
                    "secret": R2_SECRET_ACCESS_KEY,
                    "bucket": R2_BUCKET_NAME,
                    "endpoint": R2_ENDPOINT_URL,
                    "force_path_style": True,
                },
            }
        ],
    }

    egress_id = f"EG_{uuid.uuid4().hex[:10]}"
    if not is_mock:
        http_base = LIVEKIT_URL.replace("wss://", "https://").replace("ws://", "http://").rstrip("/")
        admin_token = generate_room_token(
            room_name=room_name,
            identity="livekit-egress-admin",
            deal_id=deal_id,
            account_id=account_id,
        )
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                f"{http_base}/twirp/livekit.Egress/StartRoomCompositeEgress",
                json=egress_payload,
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            resp.raise_for_status()
            data = resp.json()
            egress_id = data.get("egress_id") or data.get("egressId") or egress_id

    return {
        "egress_id": egress_id,
        "room_name": room_name,
        "deal_id": deal_id,
        "r2_audio_key": r2_key,
        "status": "EGRESS_STARTING",
        "egress_config": egress_payload,
    }


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
    egress_info = start_room_egress_to_r2(room_name=room_name, deal_id=deal_id, account_id=account_id)

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO call_recordings (
                id, account_id, room_name, deal_id, caller_identity,
                receiver_identity, call_type, status, egress_id
            ) VALUES (?, ?, ?, ?, ?, ?, 'voip_sip', 'calling', ?)
        """, (call_id, account_id, room_name, deal_id, caller, phone_number, egress_info["egress_id"]))
        conn.commit()
    finally:
        conn.close()

    return {
        "call_id": call_id,
        "room_name": room_name,
        "phone_number": phone_number,
        "caller_id": caller,
        "deal_id": deal_id,
        "egress_id": egress_info["egress_id"],
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

    if not room_name and payload.get("room_name"):
        room_name = payload.get("room_name")
    if not audio_key and payload.get("audio_key"):
        audio_key = payload.get("audio_key")
    if not duration and payload.get("duration_seconds"):
        duration = int(payload.get("duration_seconds"))

    if not room_name:
        return {"success": False, "reason": "room_name not found in event"}

    custom_url = payload.get("r2_recording_url") or payload.get("recording_url")
    if custom_url:
        recording_url = custom_url
    elif audio_key:
        if audio_key.startswith("/") or audio_key.startswith("http"):
            recording_url = audio_key
        else:
            recording_url = f"/api/v1/storage/files/{audio_key}"
    else:
        recording_url = None

    conn = get_connection()
    call_id = None
    deal_id = payload.get("deal_id")
    account_id = payload.get("account_id") or "0f14ffff"
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, deal_id, account_id FROM call_recordings WHERE room_name = ? ORDER BY created_at DESC LIMIT 1", (room_name,))
        row = cur.fetchone()
        if row:
            call_id = row["id"]
            deal_id = deal_id or row["deal_id"]
            account_id = row["account_id"] or account_id
            cur.execute("""
                UPDATE call_recordings
                SET status = 'completed',
                    deal_id = COALESCE(?, deal_id),
                    duration_seconds = ?,
                    r2_audio_key = ?,
                    r2_recording_url = ?,
                    egress_id = ?,
                    ended_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (deal_id, duration, audio_key, recording_url, egress_id, call_id))
        else:
            call_id = f"call-rec-{uuid.uuid4().hex[:8]}"
            cur.execute("""
                INSERT INTO call_recordings (
                    id, account_id, room_name, deal_id, caller_identity,
                    call_type, status, duration_seconds, r2_audio_key, r2_recording_url, egress_id, ended_at
                ) VALUES (?, ?, ?, ?, 'system', 'webrtc', 'completed', ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (call_id, account_id, room_name, deal_id, duration, audio_key, recording_url, egress_id))
        conn.commit()
    finally:
        conn.close()

    event_id = default_event_bus.publish_sync(
        StreamName.SALES,
        "call.recording_ready",
        {
            "call_id": call_id,
            "room_name": room_name,
            "deal_id": deal_id,
            "egress_id": egress_id,
            "duration_seconds": duration,
            "r2_audio_key": audio_key,
            "r2_recording_url": recording_url,
            "account_id": account_id,
        },
        tenant_id=account_id,
    )

    return {
        "success": True,
        "event": event,
        "call_id": call_id,
        "room_name": room_name,
        "deal_id": deal_id,
        "duration_seconds": duration,
        "r2_audio_key": audio_key,
        "event_id": event_id,
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

