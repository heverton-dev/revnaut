# -*- coding: utf-8 -*-
"""
Vertical Slice: Tasks Service (SQLite WAL)
"""

from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional
from src.core.database import get_connection
from src.features.tasks.schemas import TaskCreate, TaskToggle


def list_tasks(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, account_id, title, due_date, assignee, priority, completed, created_at "
        "FROM tasks WHERE account_id = ? ORDER BY completed ASC, id ASC",
        (account_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_task(data: TaskCreate, account_id: str = "0f14ffff") -> Dict[str, Any]:
    task_id = f"task-{uuid.uuid4().hex[:6]}"
    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT INTO tasks (id, account_id, title, due_date, assignee, priority, completed) "
            "VALUES (?, ?, ?, ?, ?, ?, 0)",
            (task_id, account_id, data.title, data.due_date, data.assignee, data.priority)
        )
        cur = conn.cursor()
        cur.execute("SELECT id, account_id, title, due_date, assignee, priority, completed, created_at FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
    conn.close()
    return dict(row)


def toggle_task(task_id: str, data: TaskToggle) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("UPDATE tasks SET completed = ? WHERE id = ?", (1 if data.completed else 0, task_id))
        if cur.rowcount == 0:
            conn.close()
            return None
        cur.execute("SELECT id, account_id, title, due_date, assignee, priority, completed, created_at FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
