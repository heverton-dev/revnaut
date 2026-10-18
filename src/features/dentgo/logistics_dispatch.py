# -*- coding: utf-8 -*-
"""
Vertical Slice: DENTGO Logistics Dispatch & Last-Mile Custody
Controle de separação no CD, lacre inviolável da maleta térmica, PIN de entrega e POD no Cloudflare R2.
"""

from __future__ import annotations
import random
from typing import Any, Dict, Optional
from src.core.database import get_connection, init_db
from src.core.events import StreamName, default_event_bus


def bip_picking(
    order_id: str,
    scanned_barcode: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Bipagem do DataMatrix/código de barras na separação do CD (PICKING_BIPADO)."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM dentgo_orders WHERE id = ? AND account_id = ?", (order_id, account_id))
        order = cur.fetchone()
        if not order:
            raise ValueError(f"Pedido {order_id} não encontrado")

        cur.execute("""
            UPDATE dentgo_orders
            SET status = 'PICKING_BIPADO'
            WHERE id = ?
        """, (order_id,))
        conn.commit()

        cur.execute("SELECT * FROM dentgo_orders WHERE id = ?", (order_id,))
        return dict(cur.fetchone())
    finally:
        conn.close()


def seal_package(
    order_id: str,
    seal_code: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Fechamento e lacre da maleta térmica (SEALED_READY).
    Gera código PIN de 4 dígitos para conferência segura na clínica.
    """
    init_db()
    if not seal_code or not seal_code.strip():
        raise ValueError("Código do lacre físico é obrigatório")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM dentgo_orders WHERE id = ? AND account_id = ?", (order_id, account_id))
        order = cur.fetchone()
        if not order:
            raise ValueError(f"Pedido {order_id} não encontrado")

        # Gera PIN de 4 dígitos (ex: 4812)
        pin = f"{random.randint(1000, 9999)}"

        cur.execute("""
            UPDATE dentgo_orders
            SET status = 'SEALED_READY',
                seal_code = ?,
                delivery_pin = ?
            WHERE id = ?
        """, (seal_code.strip(), pin, order_id))
        conn.commit()

        cur.execute("SELECT * FROM dentgo_orders WHERE id = ?", (order_id,))
        return dict(cur.fetchone())
    finally:
        conn.close()


def assign_courier(
    order_id: str,
    courier_id: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Atribui courier especializado para a entrega cirúrgica (COURIER_ASSIGNED)."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM dentgo_orders WHERE id = ? AND account_id = ?", (order_id, account_id))
        order = cur.fetchone()
        if not order:
            raise ValueError(f"Pedido {order_id} não encontrado")

        cur.execute("""
            UPDATE dentgo_orders
            SET status = 'COURIER_ASSIGNED',
                courier_id = ?
            WHERE id = ?
        """, (courier_id, order_id))
        conn.commit()

        cur.execute("SELECT * FROM dentgo_orders WHERE id = ?", (order_id,))
        return dict(cur.fetchone())
    finally:
        conn.close()


def start_transit(
    order_id: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Inicia o trajeto de entrega em tempo real (IN_TRANSIT_LIVE)."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM dentgo_orders WHERE id = ? AND account_id = ?", (order_id, account_id))
        order = cur.fetchone()
        if not order:
            raise ValueError(f"Pedido {order_id} não encontrado")

        cur.execute("""
            UPDATE dentgo_orders
            SET status = 'IN_TRANSIT_LIVE'
            WHERE id = ?
        """, (order_id,))
        conn.commit()

        cur.execute("SELECT * FROM dentgo_orders WHERE id = ?", (order_id,))
        return dict(cur.fetchone())
    finally:
        conn.close()


def verify_and_complete_delivery(
    order_id: str,
    entered_pin: str,
    proof_photo_r2_key: str,
    recipient_name: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Finaliza entrega cirúrgica com verificação estrita de PIN e foto comprobatória no R2 (DELIVERED_VERIFIED).
    """
    init_db()
    if not proof_photo_r2_key or not proof_photo_r2_key.strip():
        raise ValueError("Foto de entrega (POD) obrigatória no R2")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM dentgo_orders WHERE id = ? AND account_id = ?", (order_id, account_id))
        order = cur.fetchone()
        if not order:
            raise ValueError(f"Pedido {order_id} não encontrado")

        expected_pin = order["delivery_pin"]
        if not expected_pin or entered_pin.strip() != expected_pin.strip():
            raise ValueError("PIN de entrega incorreto. Validação sanitária de custódia falhou.")

        cur.execute("""
            UPDATE dentgo_orders
            SET status = 'DELIVERED_VERIFIED',
                proof_of_delivery_r2_key = ?,
                recipient_signature_name = ?,
                delivered_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (proof_photo_r2_key.strip(), recipient_name.strip(), order_id))
        conn.commit()

        cur.execute("SELECT * FROM dentgo_orders WHERE id = ?", (order_id,))
        updated_order = dict(cur.fetchone())
    finally:
        conn.close()

    event_payload = {
        "order_id": order_id,
        "hub_id": updated_order.get("hub_id"),
        "customer_cro_uf": updated_order.get("customer_cro_uf"),
        "proof_of_delivery_r2_key": updated_order.get("proof_of_delivery_r2_key"),
        "recipient_signature_name": updated_order.get("recipient_signature_name"),
        "total_amount": updated_order.get("total_amount"),
        "status": "DELIVERED_VERIFIED",
    }
    default_event_bus.publish_sync(
        stream=StreamName.DENTGO,
        event_type="dentgo.delivered",
        account_id=account_id,
        payload=event_payload,
    )
    default_event_bus.publish_sync(
        stream=StreamName.DENTGO,
        event_type="dentgo.order_delivered",
        account_id=account_id,
        payload=event_payload,
    )
    return updated_order
