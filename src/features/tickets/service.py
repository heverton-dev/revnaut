# -*- coding: utf-8 -*-
"""
Vertical Slice: Tickets Service (SQLite WAL)
"""

from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional
from src.core.database import get_connection
from src.features.tickets.schemas import TicketCreate, TicketStatusUpdate


def list_tickets(account_id: str = "0f14ffff", status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    if status:
        cur.execute(
            "SELECT id, account_id, title, customer_name, priority, status, category, created_at "
            "FROM tickets WHERE account_id = ? AND status = ? ORDER BY created_at DESC",
            (account_id, status)
        )
    else:
        cur.execute(
            "SELECT id, account_id, title, customer_name, priority, status, category, created_at "
            "FROM tickets WHERE account_id = ? ORDER BY created_at DESC",
            (account_id,)
        )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_ticket(data: TicketCreate, account_id: str = "0f14ffff") -> Dict[str, Any]:
    ticket_id = f"t-{uuid.uuid4().hex[:6]}"
    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT INTO tickets (id, account_id, title, customer_name, priority, status, category) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (ticket_id, account_id, data.title, data.customer_name, data.priority, data.status, data.category)
        )
        cur = conn.cursor()
        cur.execute("SELECT id, account_id, title, customer_name, priority, status, category, created_at FROM tickets WHERE id = ?", (ticket_id,))
        row = cur.fetchone()
    conn.close()
    return dict(row)


def update_ticket_status(ticket_id: str, data: TicketStatusUpdate) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("UPDATE tickets SET status = ? WHERE id = ?", (data.status, ticket_id))
        if cur.rowcount == 0:
            conn.close()
            return None
        cur.execute("SELECT id, account_id, title, customer_name, priority, status, category, created_at FROM tickets WHERE id = ?", (ticket_id,))
        row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
