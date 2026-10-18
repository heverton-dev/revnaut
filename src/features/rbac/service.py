# -*- coding: utf-8 -*-
"""
Vertical Slice: RBAC Service
Engine de Resolução de Escopo (Row-Level Security) e Data Scoping Hierárquico.
"""

from __future__ import annotations
from typing import Optional, Tuple, List, Any
from src.core.database import get_connection
from src.features.hierarchy.schemas import UserContext, DataScopeEnum
from src.core.security import resolve_data_scope_clause, get_user_context, get_scoped_user_ids


def build_scope_filter_sql(
    user_ctx: Optional[UserContext], 
    table_alias: str = "",
    conn = None
) -> Tuple[str, List[Any]]:
    """
    Constrói a cláusula WHERE determinística para isolamento de dados por escopo hierárquico.
    Suporta: self, team, subtree (via CTE recursiva), business_unit, tenant_global.
    """
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True
    try:
        account_id = user_ctx.account_id if user_ctx else "0f14ffff"
        return resolve_data_scope_clause(conn, user_ctx, account_id, table_alias)
    finally:
        if should_close:
            conn.close()


__all__ = ["build_scope_filter_sql", "get_user_context", "get_scoped_user_ids"]
