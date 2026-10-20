# -*- coding: utf-8 -*-
"""
Vertical Slice: Integração do Apache Superset Embedded com Guest Tokens JWT e Row-Level Security (RLS)
Geração determinística de tokens com cláusulas RLS baseadas no RBAC e exportação de datasets para Cloudflare R2.
"""

from __future__ import annotations
import csv
import io
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import jwt
from src.core.config import SUPERSET_SECRET_KEY, SUPERSET_DOMAIN, R2_PUBLIC_DOMAIN
from src.core.database import get_connection, init_db
from src.core.security import get_user_context, DataScopeEnum
from src.core.storage import R2StorageClient


_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")
_SCOPED_COLUMNS = ("owner_id", "field_owner_id", "inside_owner_id", "team_id", "business_unit_id")


def _safe_id(value: str, label: str) -> str:
    """Valida identificadores antes de qualquer interpolação em cláusula SQL/JWT."""
    if not isinstance(value, str) or not _SAFE_IDENTIFIER.match(value):
        raise ValueError(f"Identificador inválido para {label}.")
    return value


def build_table_rls_clause(conn, table: str, user_id: str, account_id: str) -> str:
    """
    RLS aplicável a uma tabela específica. Se o escopo do usuário exige colunas que a tabela não
    possui (ex.: consultor SELF em tabela só com account_id), nega em vez de ampliar ao tenant.
    """
    clause = build_superset_rls_clause(conn, user_id=user_id, account_id=account_id)
    if clause == "1=1" or clause == f"account_id = '{account_id}'":
        return clause
    columns = {r[1] for r in conn.execute(f"PRAGMA table_info({_safe_id(table, 'table')})")}
    if not columns:
        return clause
    missing = [c for c in _SCOPED_COLUMNS if re.search(rf"\b{c}\b", clause) and c not in columns]
    if missing:
        raise PermissionError(
            f"O escopo de dados do usuário não pode ser aplicado ao dataset '{table}'."
        )
    return clause


def build_superset_rls_clause(conn, user_id: str, account_id: str = "0f14ffff") -> str:
    """
    Constrói a cláusula SQL estrita de Row-Level Security (RLS) injetada no token JWT do Apache Superset,
    garantindo isolamento hermético dos dados conforme a árvore hierárquica do RBAC.
    """
    _safe_id(user_id, "user_id")
    _safe_id(account_id, "account_id")
    user_ctx = get_user_context(conn, user_id, account_id)
    if not user_ctx:
        return f"account_id = '{account_id}' AND owner_id = '{user_id}'"

    # 1. Super Admin (User God): acesso irrestrito
    if user_ctx.is_superadmin:
        return "1=1"

    scope = user_ctx.data_scope

    # 2. Diretor Nacional / C-Level (Tenant Global): vê toda a operação daquele tenant
    if scope == DataScopeEnum.TENANT_GLOBAL:
        return f"account_id = '{account_id}'"

    # 3. Consultor de Campo / Inside Sales (Self): restringe aos registros sob sua custódia/carteira
    if scope == DataScopeEnum.SELF:
        return (
            f"account_id = '{account_id}' AND "
            f"(owner_id = '{user_id}' OR field_owner_id = '{user_id}' OR inside_owner_id = '{user_id}')"
        )

    # 4. Gestor de Time Direto (Regional)
    if scope == DataScopeEnum.TEAM:
        if not user_ctx.team_id:
            return (
                f"account_id = '{account_id}' AND "
                f"(owner_id = '{user_id}' OR field_owner_id = '{user_id}' OR inside_owner_id = '{user_id}')"
            )
        return f"account_id = '{account_id}' AND team_id = '{_safe_id(user_ctx.team_id, 'team_id')}'"

    # 5. Gestor de Subárvore Recursiva (Distrital)
    if scope == DataScopeEnum.SUBTREE:
        if not user_ctx.team_id:
            return (
                f"account_id = '{account_id}' AND "
                f"(owner_id = '{user_id}' OR field_owner_id = '{user_id}' OR inside_owner_id = '{user_id}')"
            )
        cur = conn.cursor()
        cur.execute("""
            WITH RECURSIVE team_tree(id) AS (
                SELECT id FROM teams WHERE id = ? AND account_id = ?
                UNION ALL
                SELECT t.id FROM teams t
                JOIN team_tree tt ON t.parent_id = tt.id
                WHERE t.account_id = ?
            )
            SELECT id FROM team_tree;
        """, (user_ctx.team_id, account_id, account_id))
        sub_teams = [r[0] for r in cur.fetchall()]
        if not sub_teams:
            sub_teams = [user_ctx.team_id]
        teams_str = ", ".join(f"'{_safe_id(t, 'team_id')}'" for t in sub_teams)
        return f"account_id = '{account_id}' AND team_id IN ({teams_str})"

    # 6. Unidade de Negócio (Business Unit)
    if scope == DataScopeEnum.BUSINESS_UNIT:
        if user_ctx.business_unit_id:
            return f"account_id = '{account_id}' AND business_unit_id = '{_safe_id(user_ctx.business_unit_id, 'business_unit_id')}'"
        return f"account_id = '{account_id}' AND owner_id = '{user_id}'"

    return f"account_id = '{account_id}'"


def generate_superset_guest_token(
    user_id: str,
    dashboard_id: str,
    dashboard_type: str = "industry_consignment",
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Gera Guest Token JWT assinado compatível com o @superset-ui/embedded-sdk,
    aplicando a cláusula RLS extraída determinísticamente da árvore de permissões.
    """
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM users WHERE id = ? AND account_id = ?", (user_id, account_id))
        user_row = cur.fetchone()
        user_name = user_row[0] if user_row else "Usuário RevNault"

        rls_clause = build_superset_rls_clause(conn, user_id=user_id, account_id=account_id)

        now = int(time.time())
        expires_in = 3600  # 1 hora de expiração

        payload = {
            "user": {
                "username": f"guest_{user_id}",
                "first_name": user_name.split()[0] if user_name else "Guest",
                "last_name": " ".join(user_name.split()[1:]) if user_name and len(user_name.split()) > 1 else "User"
            },
            "resources": [
                {
                    "type": "dashboard",
                    "id": dashboard_id
                }
            ],
            "rls": [
                {
                    "clause": rls_clause
                }
            ],
            "iat": now,
            "exp": now + expires_in
        }

        token = jwt.encode(payload, SUPERSET_SECRET_KEY, algorithm="HS256")

        return {
            "token": token,
            "dashboard_id": dashboard_id,
            "dashboard_type": dashboard_type,
            "rls_clause": rls_clause,
            "user_id": user_id,
            "account_id": account_id,
            "superset_domain": SUPERSET_DOMAIN,
            "expires_in_seconds": expires_in
        }
    finally:
        conn.close()


def export_analytics_dataset(
    dataset_name: str,
    user_id: str,
    format: str = "csv",
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Exporta datasets analíticos em CSV para o Cloudflare R2 com respeito ao RLS.
    """
    if (format or "csv").lower().strip() != "csv":
        raise ValueError("Formato de exportação não suportado: apenas csv.")
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()

        rows: List[Dict[str, Any]] = []

        dataset_tables = {
            "deals_funnel": "deals",
            "consignment_turnover": "kp_custody_ledger",
            "dentgo_deliveries": "dentgo_orders",
            "anvisa_rma": "anvisa_rma_claims",
        }
        table = dataset_tables.get(dataset_name, "deals")
        rls_clause = build_table_rls_clause(conn, table, user_id=user_id, account_id=account_id)
        limit = 100 if dataset_name not in dataset_tables else 500
        order = "" if dataset_name not in dataset_tables else " ORDER BY created_at DESC"
        cur.execute(f"SELECT * FROM {table} WHERE {rls_clause}{order} LIMIT {limit}")
        rows = [dict(r) for r in cur.fetchall()]

        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        r2_key = f"datasets/{account_id}/{dataset_name}_{timestamp_str}.csv"

        # Gera representação em texto/bytes e envia ao Cloudflare R2
        output_buffer = io.StringIO()
        if rows:
            headers = list(rows[0].keys())
            writer = csv.DictWriter(output_buffer, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        else:
            output_buffer.write("id,account_id,created_at\n")

        raw_bytes = output_buffer.getvalue().encode("utf-8")
        mime_type = "text/csv"
        storage = R2StorageClient()
        download_url = storage.upload_bytes(
            key=r2_key,
            data=raw_bytes,
            content_type=mime_type,
        )

        return {
            "dataset_name": dataset_name,
            "format": format,
            "r2_storage_key": r2_key,
            "record_count": len(rows),
            "download_url": download_url,
            "status": "COMPLETED",
            "exported_at": datetime.now(timezone.utc).isoformat()
        }
    finally:
        conn.close()
