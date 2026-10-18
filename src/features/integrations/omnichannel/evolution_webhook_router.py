# -*- coding: utf-8 -*-
"""
Vertical Slice: Evolution API Webhook Router
Tratamento de eventos em tempo real: CALL_OFFER (Sala de Vídeo SOS LiveKit) e MESSAGES_UPSERT (Arquivamento R2).
"""

from __future__ import annotations
import uuid
from typing import Any, Dict, Optional
from src.core.database import get_connection, init_db


def handle_evolution_event(payload: Dict[str, Any], account_id: str = "0f14ffff") -> Dict[str, Any]:
    """
    Roteador de eventos da Evolution API v2:
    - CALL_OFFER: Intercepta chamada de voz e envia link imediato de sala WebRTC LiveKit.
    - MESSAGES_UPSERT: Persiste mensagens de texto e arquivos de exames/radiografias particionados no Cloudflare R2.
    """
    init_db()
    raw_event = payload.get("event", "")
    event_upper = raw_event.upper()
    instance_name = payload.get("instance") or "default_instance"
    data = payload.get("data") or {}

    conn = get_connection()
    try:
        cur = conn.cursor()

        # 1. Tratamento de tentativa de chamada de voz (CALL_OFFER)
        if "CALL_OFFER" in event_upper or "CALL.OFFER" in event_upper:
            remote_jid = data.get("from") or data.get("remoteJid") or ""
            phone = remote_jid.split("@")[0] if "@" in remote_jid else remote_jid
            call_id = data.get("id") or uuid.uuid4().hex[:6]
            sos_call_link = f"https://meet.revops.local/room/sos-{call_id}"
            response_msg = (
                f"Olá! Identificamos sua chamada de urgência cirúrgica. "
                f"Para suporte audiovisual imediato com nosso especialista e gravação do caso com IA, "
                f"acesse nossa sala segura: {sos_call_link}"
            )

            msg_id = f"msg-{uuid.uuid4().hex[:8]}"
            cur.execute("""
                INSERT INTO omnichannel_messages (
                    id, account_id, instance_name, remote_jid, sender_phone,
                    message_type, content, media_r2_key, from_me, sos_call_link
                ) VALUES (?, ?, ?, ?, ?, 'CALL_OFFER', ?, NULL, 0, ?)
            """, (
                msg_id, account_id, instance_name, remote_jid,
                phone, response_msg, sos_call_link
            ))
            conn.commit()

            return {
                "event": "CALL_OFFER",
                "action": "SOS_VIDEO_LINK_SENT",
                "sos_call_link": sos_call_link,
                "remote_jid": remote_jid,
                "phone": phone,
                "response_message": response_msg,
                "success": True
            }

        # 2. Tratamento de mensagens e mídias recebidas (MESSAGES_UPSERT)
        if "MESSAGES" in event_upper:
            key = data.get("key") or {}
            remote_jid = key.get("remoteJid") or data.get("remoteJid") or ""
            phone = remote_jid.split("@")[0] if "@" in remote_jid else remote_jid
            from_me = 1 if key.get("fromMe", False) else 0

            msg_type = data.get("messageType", "conversation")
            msg_obj = data.get("message") or {}

            media_r2_key: Optional[str] = None
            if msg_type in ("imageMessage", "audioMessage", "documentMessage", "videoMessage"):
                media_id = key.get("id") or uuid.uuid4().hex[:8]
                media_r2_key = f"whatsapp_media/{account_id}/{instance_name}/{media_id}.bin"
                content = msg_obj.get(msg_type, {}).get("caption", "Arquivo de mídia cirúrgica recebido")
            else:
                content = msg_obj.get("conversation") or msg_obj.get("extendedTextMessage", {}).get("text") or "Mensagem de texto recebida"

            msg_id = f"msg-{uuid.uuid4().hex[:8]}"
            cur.execute("""
                INSERT INTO omnichannel_messages (
                    id, account_id, instance_name, remote_jid, sender_phone,
                    message_type, content, media_r2_key, from_me, sos_call_link
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """, (
                msg_id, account_id, instance_name, remote_jid,
                phone, msg_type, content, media_r2_key, from_me
            ))
            conn.commit()

            return {
                "event": raw_event,
                "status": "STORED",
                "message_id": msg_id,
                "remote_jid": remote_jid,
                "phone": phone,
                "media_r2_key": media_r2_key,
                "success": True
            }

        # Eventos gerais / fallbacks
        return {
            "event": raw_event,
            "status": "PROCESSED",
            "success": True
        }
    finally:
        conn.close()
