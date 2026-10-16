# -*- coding: utf-8 -*-
"""
Vertical Slice: Contacts Service
"""

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
from src.core.database import get_connection
from src.core.security import get_user_context, resolve_data_scope_clause
from src.features.contacts.schemas import ContactCreate


def list_contacts(
    query: Optional[str] = None, 
    account_id: str = "0f14ffff", 
    user_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        user_ctx = get_user_context(conn, user_id, account_id) if user_id else None
        scope_clause, scope_params = resolve_data_scope_clause(conn, user_ctx, account_id)

        cur = conn.cursor()
        if query:
            sql = f"""
                SELECT * FROM contacts 
                WHERE ({scope_clause}) AND (name LIKE ? OR email LIKE ? OR company LIKE ?)
                ORDER BY score DESC
            """
            params = list(scope_params) + [f"%{query}%", f"%{query}%", f"%{query}%"]
            cur.execute(sql, tuple(params))
        else:
            sql = f"SELECT * FROM contacts WHERE {scope_clause} ORDER BY score DESC"
            cur.execute(sql, tuple(scope_params))

        rows = [dict(r) for r in cur.fetchall()]
        return rows
    finally:
        conn.close()


def create_contact(payload: ContactCreate) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    tags_json = json.dumps(payload.tags)
    cur.execute("""
        INSERT INTO contacts (account_id, name, email, phone, company, tags, score, cro, cro_uf, specialty, work_model, monthly_implants_volume, customer_type)
        VALUES ('0f14ffff', ?, ?, ?, ?, ?, 60, ?, ?, ?, ?, ?, ?)
    """, (
        payload.name,
        payload.email,
        payload.phone,
        payload.company,
        tags_json,
        payload.cro,
        payload.cro_uf,
        payload.specialty,
        payload.work_model,
        payload.monthly_implants_volume,
        payload.customer_type
    ))
    cid = cur.lastrowid
    conn.commit()
    conn.close()
    return {
        "id": cid,
        "name": payload.name,
        "email": payload.email,
        "company": payload.company,
        "score": 60,
        "cro": payload.cro,
        "cro_uf": payload.cro_uf,
        "specialty": payload.specialty,
        "work_model": payload.work_model,
        "monthly_implants_volume": payload.monthly_implants_volume,
        "customer_type": payload.customer_type
    }

