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
from src.features.dentgo import service as dentgo_service


def trigger_surgical_sos(
    customer_name: str,
    customer_phone: str,
    cro_uf: str,
    procedure_details: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Abre ticket crítico P0_SURGICAL_TABLE e gera sala instantânea WebRTC LiveKit.
    """
    init_db()
    ticket_id = f"t-{uuid.uuid4().hex[:6]}"
    room_id = f"sos-{uuid.uuid4().hex[:6]}"
    livekit_room_url = f"https://meet.revops.local/room/{room_id}"
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
        conn.commit()

        cur.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        row = cur.fetchone()
        row_dict = dict(row)
        return {
            "ticket_id": ticket_id,
            "title": title,
            "priority": "P0_SURGICAL_TABLE",
            "livekit_room_url": livekit_room_url,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "cro_uf": cro_uf,
            "status": "aberto",
            "created_at": row_dict.get("created_at") or datetime.now(timezone.utc).isoformat()
        }
    finally:
        conn.close()


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
