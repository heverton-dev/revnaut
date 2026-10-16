# -*- coding: utf-8 -*-
"""
Vertical Slice: Consignments Service (SQLite WAL)
Motor de Gestão de Estoque Consignado, Baixa Cirúrgica e Reposição Automática.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from src.core.database import get_connection
from src.features.consignments.schemas import ConsignmentConsumptionCreate


from src.core.security import get_user_context, resolve_data_scope_clause


def list_consignments(account_id: str = "0f14ffff", user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        user_ctx = get_user_context(conn, user_id, account_id) if user_id else None
        clause, params = resolve_data_scope_clause(conn, user_ctx, account_id)

        cur = conn.cursor()
        query = (
            "SELECT id, account_id, contact_id, clinic_name, box_code, total_items, consumed_items, "
            "last_audit_date, status, created_at, owner_id, team_id "
            f"FROM consignments WHERE {clause} ORDER BY created_at DESC"
        )
        cur.execute(query, tuple(params))
        boxes = [dict(r) for r in cur.fetchall()]

        for b in boxes:
            cur.execute(
                "SELECT id, consignment_id, product_sku, product_name, batch_number, "
                "quantity_allocated, quantity_consumed, unit_price "
                "FROM consignment_items WHERE consignment_id = ?",
                (b["id"],)
            )
            b["items"] = [dict(i) for i in cur.fetchall()]

        return boxes
    finally:
        conn.close()



def get_consignment(consignment_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, account_id, contact_id, clinic_name, box_code, total_items, consumed_items, "
        "last_audit_date, status, created_at "
        "FROM consignments WHERE id = ?",
        (consignment_id,)
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    data = dict(row)
    cur.execute(
        "SELECT id, consignment_id, product_sku, product_name, batch_number, "
        "quantity_allocated, quantity_consumed, unit_price "
        "FROM consignment_items WHERE consignment_id = ?",
        (consignment_id,)
    )
    data["items"] = [dict(i) for i in cur.fetchall()]
    conn.close()
    return data


def log_consumption(consignment_id: str, data: ConsignmentConsumptionCreate) -> Dict[str, Any]:
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, quantity_allocated, quantity_consumed, unit_price FROM consignment_items "
                "WHERE consignment_id = ? AND product_sku = ?",
                (consignment_id, data.product_sku)
            )
            item = cur.fetchone()
            if not item:
                raise ValueError(f"SKU '{data.product_sku}' não encontrado na caixa consignada '{consignment_id}'.")

            allocated = int(item["quantity_allocated"])
            consumed = int(item["quantity_consumed"])
            unit_price = float(item["unit_price"])

            available = allocated - consumed
            if data.quantity > available:
                raise ValueError(f"Quantidade solicitada ({data.quantity}) excede o saldo físico na caixa ({available} un).")

            new_item_consumed = consumed + data.quantity
            cur.execute(
                "UPDATE consignment_items SET quantity_consumed = ? WHERE id = ?",
                (new_item_consumed, item["id"])
            )

            cur.execute(
                "UPDATE consignments SET consumed_items = consumed_items + ? WHERE id = ?",
                (data.quantity, consignment_id)
            )

        remaining = allocated - new_item_consumed
        total_billed = round(data.quantity * unit_price, 2)

        return {
            "status": "consumed",
            "consignment_id": consignment_id,
            "product_sku": data.product_sku,
            "quantity_consumed": data.quantity,
            "remaining_quantity": remaining,
            "total_billed": total_billed,
            "replacement_order_triggered": True
        }
    finally:
        conn.close()
