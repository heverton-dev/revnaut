# -*- coding: utf-8 -*-
"""
Vertical Slice: Omnichannel Integrations Service
Processamento de Webhooks Evolution API v2, Chatwoot e Mautic 5.
"""

from __future__ import annotations
import hmac
import hashlib
import json
import os
import re
from typing import Optional, Dict, Any, Tuple
from src.core.database import get_connection



def verify_hmac_signature(raw_body: bytes, signature_header: Optional[str], secret: Optional[str] = None) -> bool:
    """Valida assinatura HMAC SHA-256 do payload (segredo em OMNICHANNEL_WEBHOOK_SECRET; sem segredo, rejeita)."""
    if secret is None:
        from src.core import config
        secret = os.getenv("OMNICHANNEL_WEBHOOK_SECRET", config.OMNICHANNEL_WEBHOOK_SECRET)
    if not signature_header or not secret:
        return False

    clean_sig = signature_header.strip()
    if clean_sig.startswith("sha256="):
        clean_sig = clean_sig.split("sha256=", 1)[1]

    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(clean_sig.lower(), expected.lower())


def _normalize_phone(phone: str) -> str:
    """Extrai apenas dígitos do telefone para comparação uniforme."""
    return re.sub(r"\D", "", phone or "")


def process_evolution_webhook(payload: dict) -> Dict[str, Any]:
    """Processa evento da Evolution API v2 (ex: resposta inbound no WhatsApp)."""
    event = payload.get("event", "messages.upsert")
    data = payload.get("data", {})
    
    # Extrai telefone e mensagem
    key = data.get("key", {})
    from_me = key.get("fromMe", False)
    remote_jid = key.get("remoteJid", "")
    phone_digits = remote_jid.split("@")[0] if "@" in remote_jid else remote_jid
    
    msg_obj = data.get("message", {})
    text_content = msg_obj.get("conversation") or msg_obj.get("extendedTextMessage", {}).get("text") or "Mensagem recebida"

    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            # Localiza contato pelo final do telefone (últimos 8-9 dígitos)
            cur.execute("SELECT id, name, phone, score FROM contacts")
            contacts = cur.fetchall()
            matched_contact = None
            clean_inbound = _normalize_phone(phone_digits)

            for c in contacts:
                c_phone = _normalize_phone(c["phone"])
                if c_phone and (c_phone.endswith(clean_inbound[-8:]) or clean_inbound.endswith(c_phone[-8:])):
                    matched_contact = c
                    break

            contact_id = matched_contact["id"] if matched_contact else None
            new_score = None

            if matched_contact and not from_me:
                # Incrementa lead score por engajamento ativo (+15 pontos)
                current_score = matched_contact["score"] or 50
                new_score = min(100, current_score + 15)
                cur.execute("UPDATE contacts SET score = ? WHERE id = ?", (new_score, contact_id))

                # Registra na timeline unificada
                cur.execute("""
                    INSERT INTO contact_audit_logs (contact_id, author_name, action, new_value, comment)
                    VALUES (?, 'Evolution API (WhatsApp)', 'WHATSAPP_RESPONSE', ?, ?)
                """, (contact_id, f"Score: {new_score}", f"Cirurgião respondeu: '{text_content[:100]}'"))

            return {
                "success": True,
                "event": event,
                "channel": "evolution_whatsapp",
                "contact_id": contact_id,
                "score_updated": new_score,
                "message": f"Mensagem de {phone_digits} processada com sucesso"
            }
    finally:
        conn.close()


def process_chatwoot_webhook(payload: dict) -> Dict[str, Any]:
    """Processa webhook do Chatwoot (ex: message_created do contato)."""
    event = payload.get("event", "message_created")
    sender = payload.get("sender", {})
    sender_type = sender.get("type", "contact")
    sender_email = sender.get("email")
    sender_phone = sender.get("phone_number")
    content = payload.get("content", "Mensagem Chatwoot")

    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            matched_contact = None
            if sender_email:
                cur.execute("SELECT id, name, score FROM contacts WHERE email = ?", (sender_email,))
                matched_contact = cur.fetchone()

            if not matched_contact and sender_phone:
                cur.execute("SELECT id, name, phone, score FROM contacts")
                clean_phone = _normalize_phone(sender_phone)
                for c in cur.fetchall():
                    c_phone = _normalize_phone(c["phone"])
                    if c_phone and (c_phone.endswith(clean_phone[-8:]) or clean_phone.endswith(c_phone[-8:])):
                        matched_contact = c
                        break

            contact_id = matched_contact["id"] if matched_contact else None
            new_score = None

            if matched_contact and sender_type == "contact":
                current_score = matched_contact["score"] or 50
                new_score = min(100, current_score + 10)
                cur.execute("UPDATE contacts SET score = ? WHERE id = ?", (new_score, contact_id))

                cur.execute("""
                    INSERT INTO contact_audit_logs (contact_id, author_name, action, new_value, comment)
                    VALUES (?, 'Chatwoot Omnichannel', 'CHATWOOT_INBOX_INTERACTION', ?, ?)
                """, (contact_id, f"Score: {new_score}", f"Interação via Chatwoot: '{content[:100]}'"))

            return {
                "success": True,
                "event": event,
                "channel": "chatwoot",
                "contact_id": contact_id,
                "score_updated": new_score,
                "message": f"Evento Chatwoot {event} processado com sucesso"
            }
    finally:
        conn.close()


def process_mautic_webhook(payload: dict) -> Dict[str, Any]:
    """Processa webhook do Mautic 5 (ex: lead.changepoints)."""
    event = payload.get("event", "lead.changepoints")
    lead = payload.get("lead", {})
    points = payload.get("points") or lead.get("points")
    fields = lead.get("fields", {}).get("core", {})
    email = lead.get("email") or fields.get("email", {}).get("value")

    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            matched_contact = None
            if email:
                cur.execute("SELECT id, name, score FROM contacts WHERE email = ?", (email,))
                matched_contact = cur.fetchone()

            contact_id = matched_contact["id"] if matched_contact else None
            new_score = None

            if matched_contact and points is not None:
                new_score = int(points)
                cur.execute("UPDATE contacts SET score = ? WHERE id = ?", (new_score, contact_id))

                cur.execute("""
                    INSERT INTO contact_audit_logs (contact_id, author_name, action, new_value, comment)
                    VALUES (?, 'Mautic Marketing Automation', 'MAUTIC_SCORE_UPDATE', ?, ?)
                """, (contact_id, f"Score: {new_score}", f"Pontuação de marketing sincronizada: {new_score} pts"))

            return {
                "success": True,
                "event": event,
                "channel": "mautic",
                "contact_id": contact_id,
                "score_updated": new_score,
                "message": f"Lead scoring do Mautic sincronizado para {email or 'lead'}"
            }
    finally:
        conn.close()
