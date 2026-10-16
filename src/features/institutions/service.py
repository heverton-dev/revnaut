# -*- coding: utf-8 -*-
"""
Vertical Slice: Institutions Service (SQLite WAL)
"""

from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional
from src.core.database import get_connection
from src.features.institutions.schemas import InstitutionCreate


def list_institutions(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, account_id, name, institution_type, city, state, coordinator_name, "
        "active_students_count, accreditation_status, created_at "
        "FROM institutions WHERE account_id = ? ORDER BY active_students_count DESC, created_at ASC",
        (account_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_institution(data: InstitutionCreate, account_id: str = "0f14ffff") -> Dict[str, Any]:
    inst_id = f"inst-{uuid.uuid4().hex[:6]}"
    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT INTO institutions (id, account_id, name, institution_type, city, state, "
            "coordinator_name, active_students_count, accreditation_status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                inst_id,
                account_id,
                data.name,
                data.institution_type,
                data.city,
                data.state.upper(),
                data.coordinator_name,
                data.active_students_count,
                data.accreditation_status
            )
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM institutions WHERE id = ?", (inst_id,))
        row = cur.fetchone()
    conn.close()
    return dict(row)
