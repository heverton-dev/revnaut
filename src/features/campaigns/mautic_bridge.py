# -*- coding: utf-8 -*-
"""
Vertical Slice: Mautic Hybrid Bridge & Deterministic Campaign Dispatcher
Roteia ações de campanha do Mautic diretamente para a instância Evolution do consultor responsável.
"""

from __future__ import annotations
import asyncio
import os
import time
import uuid
from typing import Any, Dict, Optional
from src.core.database import get_connection
from src.core.events import EventBus, StreamName, default_event_bus


def resolve_consultant_for_contact(contact_id: int) -> Dict[str, Any]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, email, field_owner_id, inside_owner_id, owner_id 
            FROM contacts 
            WHERE id = ?
        """, (contact_id,))
        contact_row = cur.fetchone()
        if not contact_row:
            return {
                "id": "u_corp_fallback",
                "name": "Consultor Especialista Corporativo",
                "email": "atendimento@revnaut.com",
                "instance_name": "revnaut_default_corporate",
            }

        # Prioridade: Field Rep -> Inside Rep -> Owner -> Fallback
        owner_id = (
            contact_row["field_owner_id"] or
            contact_row["inside_owner_id"] or
            contact_row["owner_id"]
        )

        if not owner_id:
            return {
                "id": "u_corp_fallback",
                "name": "Consultor Especialista Corporativo",
                "email": "atendimento@revnaut.com",
                "instance_name": "revnaut_default_corporate",
            }

        cur.execute("SELECT id, name, email, role FROM users WHERE id = ?", (owner_id,))
        user_row = cur.fetchone()
        if not user_row:
            return {
                "id": owner_id,
                "name": "Consultor Designado",
                "email": "consultor@revnaut.com",
                "instance_name": f"instance_{owner_id}",
            }

        return {
            "id": user_row["id"],
            "name": user_row["name"],
            "email": user_row["email"],
            "role": user_row["role"],
            "instance_name": f"evolution_instance_{user_row['id']}",
        }
    finally:
        conn.close()


def render_template_variables(
    template: str,
    contact: Dict[str, Any],
    consultant: Dict[str, Any]
) -> str:
    rendered = template
    replacements = {
        "{{contact.name}}": str(contact.get("name") or ""),
        "{{contact.cro}}": str(contact.get("cro") or ""),
        "{{contact.specialty}}": str(contact.get("specialty") or ""),
        "{{contact.phone}}": str(contact.get("phone") or ""),
        "{{contact.email}}": str(contact.get("email") or ""),
        "{{consultant.name}}": str(consultant.get("name") or ""),
        "{{consultant.id}}": str(consultant.get("id") or ""),
        "{{consultant.email}}": str(consultant.get("email") or ""),
    }

    for placeholder, val in replacements.items():
        rendered = rendered.replace(placeholder, val)

    return rendered


def process_mautic_campaign_action(payload: Dict[str, Any], account_id: str = "0f14ffff") -> Dict[str, Any]:
    action = payload.get("action", "send_whatsapp")
    contact_data = dict(payload.get("contact") or {})
    contact_id = contact_data.get("id")
    eff_account_id = payload.get("account_id") or account_id

    if not contact_id:
        email = contact_data.get("email")
        if email:
            conn = get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, name, phone, cro, specialty FROM contacts WHERE email = ?", (email,))
                row = cur.fetchone()
                if row:
                    contact_id = row["id"]
                    contact_data.setdefault("name", row["name"])
                    contact_data.setdefault("phone", row["phone"])
                    contact_data.setdefault("cro", row["cro"])
                    contact_data.setdefault("specialty", row["specialty"])
            finally:
                conn.close()

    consultant = resolve_consultant_for_contact(contact_id) if contact_id else {
        "id": "u_corp_fallback",
        "name": "Consultor Corporativo",
        "email": "atendimento@revnaut.com",
        "instance_name": "revnaut_default_corporate",
    }

    raw_template = payload.get("message_template") or "Olá {{contact.name}}, seu consultor {{consultant.name}} está à disposição."
    rendered_message = render_template_variables(raw_template, contact_data, consultant)
    phone = contact_data.get("phone") or "+5511999990000"

    # Registra despacho na instância do consultor em omnichannel_messages
    msg_id = f"omni-mautic-{uuid.uuid4().hex[:10]}"
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
                INSERT INTO omnichannel_messages (
                    id, account_id, instance_name, remote_jid, sender_phone,
                    message_type, content, from_me
                ) VALUES (?, ?, ?, ?, ?, 'text', ?, 1)
            """, (
                msg_id,
                eff_account_id,
                consultant["instance_name"],
                f"{phone.lstrip('+')}@s.whatsapp.net",
                phone,
                rendered_message,
            ))
    finally:
        conn.close()

    # Publica evento de disparo no barramento global Redis Streams (stream:marketing)
    event_id = default_event_bus.publish_sync(
        StreamName.MARKETING,
        "campaign.whatsapp.dispatch",
        {
            "message_id": msg_id,
            "campaign_id": payload.get("campaign_id"),
            "campaign_name": payload.get("campaign_name"),
            "contact_id": contact_id,
            "contact_phone": phone,
            "consultant_id": consultant["id"],
            "instance_name": consultant["instance_name"],
            "message": rendered_message,
        },
        tenant_id=eff_account_id,
    )

    return {
        "success": True,
        "action": action,
        "campaign_id": payload.get("campaign_id"),
        "contact_id": contact_id,
        "consultant_id": consultant["id"],
        "dispatched_instance": consultant["instance_name"],
        "rendered_message": rendered_message,
        "message_id": msg_id,
        "event_id": event_id,
        "timestamp": time.time(),
    }

