# -*- coding: utf-8 -*-
"""
Vertical Slice: Surgical SOS LiveKit & Immediate DENTGO Dispatch
Atendimento emergencial de mesa cirúrgica em menos de 10 segundos com sala WebRTC LiveKit e despacho 1-clique.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from src.core.database import get_connection, init_db
from src.core.events import StreamName, default_event_bus
from src.features.communications import livekit_service
from src.features.dentgo import service as dentgo_service


def trigger_surgical_sos(
    customer_name: str,
    customer_phone: str,
    cro_uf: str,
    procedure_details: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Abre ticket crítico P0_SURGICAL_TABLE, gera sala instantânea WebRTC LiveKit com JWT real,
    dispara link WhatsApp em omnichannel_messages e publica cx.surgical_sos_triggered.
    """
    init_db()
    ticket_id = f"t-{uuid.uuid4().hex[:6]}"
    room_id = f"sos-{uuid.uuid4().hex[:6]}"
    lk_token_data = livekit_service.generate_room_token(
        room_name=room_id,
        participant_identity=cro_uf or customer_phone or f"surgeon-{ticket_id}",
        participant_name=customer_name,
    )
    lk_token = lk_token_data["token"] if isinstance(lk_token_data, dict) else str(lk_token_data)
    livekit_room_url = f"https://meet.revnault.local/room/{room_id}?token={lk_token}"
    title = f"SOS Mesa Cirúrgica - {customer_name} ({cro_uf})"

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tickets (
                id, account_id, title, customer_name, priority, status, category,
                livekit_room_url, customer_phone, cro_uf, clinical_notes
            ) VALUES (?, ?, ?, ?, 'P0_SURGICAL_TABLE', 'aberto', 'SOS Mesa Cirúrgica', ?, ?, ?, ?)
        """, (
            ticket_id, account_id, title, customer_name,
            livekit_room_url, customer_phone, cro_uf, procedure_details
        ))

        msg_id = f"msg-sos-{uuid.uuid4().hex[:8]}"
        clean_phone = "".join(ch for ch in (customer_phone or "") if ch.isdigit()) or "5511999999999"
        sos_msg_text = (
            f"[SOS MESA CIRÚRGICA P0] Dr(a). {customer_name}, sala de vídeo emergencial aberta: {livekit_room_url}"
        )
        cur.execute("""
            INSERT INTO omnichannel_messages (
                id, account_id, instance_name, remote_jid, sender_phone,
                message_type, content, media_r2_key, from_me, sos_call_link
            ) VALUES (?, ?, 'sos_surgical_desk', ?, ?, 'SOS_EMERGENCY_LINK', ?, NULL, 1, ?)
        """, (
            msg_id, account_id, f"{clean_phone}@s.whatsapp.net", customer_phone, sos_msg_text, livekit_room_url
        ))

        conn.commit()

        cur.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        row = cur.fetchone()
        row_dict = dict(row)
    finally:
        conn.close()

    res_payload = {
        "ticket_id": ticket_id,
        "title": title,
        "priority": "P0_SURGICAL_TABLE",
        "livekit_room_url": livekit_room_url,
        "livekit_token": lk_token,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "cro_uf": cro_uf,
        "status": "aberto",
        "whatsapp_message_id": msg_id,
        "created_at": row_dict.get("created_at") or datetime.now(timezone.utc).isoformat()
    }
    default_event_bus.publish_sync(
        stream=StreamName.CX,
        event_type="cx.surgical_sos_triggered",
        account_id=account_id,
        payload=res_payload,
    )
    return res_payload


def dispatch_emergency_dentgo_item(
    ticket_id: str,
    product_id: str,
    quantity: int,
    delivery_address: str,
    delivery_lat: float,
    delivery_lng: float,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Despacha componente cirúrgico em caráter de urgência extrema via DENTGO acoplado ao ticket SOS.
    """
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tickets WHERE id = ? AND account_id = ?", (ticket_id, account_id))
        ticket_row = cur.fetchone()
        if not ticket_row:
            raise ValueError(f"Ticket SOS {ticket_id} não encontrado")

        ticket = dict(ticket_row)
        cro_uf = ticket.get("cro_uf") or "CRO-SP-00000"

        # Cria pedido DENTGO express com validação sanitária
        order = dentgo_service.create_express_order(
            customer_cro_uf=cro_uf,
            delivery_address=delivery_address,
            delivery_lat=delivery_lat,
            delivery_lng=delivery_lng,
            items=[{"product_id": product_id, "quantity": quantity}],
            account_id=account_id
        )

        cur.execute(
            "UPDATE tickets SET dentgo_order_id = ? WHERE id = ?",
            (order["id"], ticket_id)
        )
        conn.commit()

        return {
            "ticket_id": ticket_id,
            "dentgo_order_id": order["id"],
            "status": "DISPATCHED_EXPRESS",
            "estimated_eta_minutes": int(order["estimated_eta_minutes"]),
            "hub_id": order["hub_id"],
            "total_amount": float(order["total_amount"])
        }
    finally:
        conn.close()


def get_surgical_sos_ticket(ticket_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Retorna detalhes do ticket crítico SOS."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tickets WHERE id = ? AND account_id = ?", (ticket_id, account_id))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Ticket {ticket_id} não encontrado")
        return dict(row)
    finally:
        conn.close()
