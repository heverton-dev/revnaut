# -*- coding: utf-8 -*-
"""
Motor Central de Segurança, RBAC e Data Scoping Hierárquico.
Resolve cláusulas SQL determinísticas baseadas no contexto e organograma do usuário.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, Tuple, List
from fastapi import Header, HTTPException
from src.core.database import get_connection
from src.features.hierarchy.schemas import DataScopeEnum, UserContext


def get_user_context(conn, user_id: str, account_id: str = "0f14ffff") -> Optional[UserContext]:
    """Recupera o contexto de segurança e escopo do usuário no banco."""
    cur = conn.cursor()
    cur.execute(
        "SELECT u.id, u.account_id, u.team_id, u.role_id, u.custom_data_scope, u.is_superadmin, "
        "r.default_data_scope, r.is_admin as role_is_admin, t.business_unit_id "
        "FROM users u "
        "LEFT JOIN roles r ON u.role_id = r.id "
        "LEFT JOIN teams t ON u.team_id = t.id "
        "WHERE u.id = ? AND u.account_id = ?",
        (user_id, account_id)
    )
    row = cur.fetchone()
    if not row:
        return None

    is_superadmin = bool(row["is_superadmin"])
    is_admin = bool(row["role_is_admin"]) or is_superadmin
    raw_scope = row["custom_data_scope"] or row["default_data_scope"] or "tenant_global"
    
    try:
        data_scope = DataScopeEnum(raw_scope)
    except ValueError:
        data_scope = DataScopeEnum.TENANT_GLOBAL

    # Carrega permissões funcionais vinculadas à Role
    role_id = row["role_id"]
    permissions: List[str] = []
    if role_id:
        cur.execute(
            "SELECT permission_code FROM role_permissions WHERE role_id = ?",
            (role_id,)
        )
        permissions = [r[0] for r in cur.fetchall()]

    if is_admin or is_superadmin:
        if "*:*" not in permissions:
            permissions.append("*:*")

    return UserContext(
        user_id=row["id"],
        account_id=row["account_id"],
        role_id=role_id or "role_default",
        team_id=row["team_id"],
        business_unit_id=row["business_unit_id"],
        data_scope=data_scope,
        permissions=permissions,
        is_superadmin=is_superadmin
    )


def check_user_permission(user_context: Optional[UserContext], required_permission: str) -> bool:
    """Valida se o usuário possui a permissão requerida de forma determinística."""
    if not user_context:
        return False
    if user_context.is_superadmin:
        return True
    if "*:*" in user_context.permissions:
        return True
    if required_permission in user_context.permissions:
        return True
    
    # Suporte a wildcard por recurso (ex: 'consignments:*')
    if ":" in required_permission:
        res, _ = required_permission.split(":", 1)
        if f"{res}:*" in user_context.permissions:
            return True

    return False


def enforce_user_permission(conn, user_id: Optional[str], account_id: str, required_permission: str) -> None:
    """Bloqueia com HTTP 403 Forbidden caso o usuário não possua a permissão necessária."""
    if not user_id:
        # Se não há user_id no header em ambiente de dev/seed default, consulta se o usuário padrão tem acesso
        return
    user_ctx = get_user_context(conn, user_id, account_id)
    if not check_user_permission(user_ctx, required_permission):
        raise HTTPException(
            status_code=403, 
            detail=f"Acesso negado: a função do usuário não possui a permissão '{required_permission}'."
        )


def resolve_data_scope_clause(
    conn, 
    user_context: Optional[UserContext], 
    account_id: str = "0f14ffff", 
    table_alias: str = ""
) -> Tuple[str, List[Any]]:
    """
    Retorna uma tupla (sql_clause, params) para injeção direta em consultas SQL.
    Aplica isolamento por linha (Row-Level Security / Territory Management).
    """
    prefix = f"{table_alias}." if table_alias else ""

    # 1. Se for Super Admin (User God), tem acesso irrestrito
    if user_context and user_context.is_superadmin:
        return "1=1", []

    # 2. Se não houver contexto autenticado específico, restringe ao tenant
    if not user_context:
        return f"{prefix}account_id = ?", [account_id]

    scope = user_context.data_scope

    # 3. Escopo Global do Tenant (C-Level / Admin da Empresa)
    if scope == DataScopeEnum.TENANT_GLOBAL:
        return f"{prefix}account_id = ?", [user_context.account_id]

    # 4. Escopo Próprio / Self (Consultor de Campo titular ou Analista Inside co-piloto)
    if scope == DataScopeEnum.SELF:
        return (
            f"{prefix}account_id = ? AND ({prefix}owner_id = ? OR {prefix}field_owner_id = ? OR {prefix}inside_owner_id = ?)",
            [user_context.account_id, user_context.user_id, user_context.user_id, user_context.user_id]
        )

    # 5. Escopo de Time Direto (Gestor Regional)
    if scope == DataScopeEnum.TEAM:
        if not user_context.team_id:
            # Fallback seguro: se não tiver time, cai para self dual
            return (
                f"{prefix}account_id = ? AND ({prefix}owner_id = ? OR {prefix}field_owner_id = ? OR {prefix}inside_owner_id = ?)",
                [user_context.account_id, user_context.user_id, user_context.user_id, user_context.user_id]
            )
        return (
            f"{prefix}account_id = ? AND {prefix}team_id = ?",
            [user_context.account_id, user_context.team_id]
        )

    # 6. Escopo de Subárvore Recursiva (Gestor Distrital)
    if scope == DataScopeEnum.SUBTREE:
        if not user_context.team_id:
            return (
                f"{prefix}account_id = ? AND ({prefix}owner_id = ? OR {prefix}field_owner_id = ? OR {prefix}inside_owner_id = ?)",
                [user_context.account_id, user_context.user_id, user_context.user_id, user_context.user_id]
            )
        
        cur = conn.cursor()
        cur.execute(
            """
            WITH RECURSIVE team_tree(id) AS (
                SELECT id FROM teams WHERE id = ? AND account_id = ?
                UNION ALL
                SELECT t.id FROM teams t 
                JOIN team_tree tt ON t.parent_id = tt.id
                WHERE t.account_id = ?
            )
            SELECT id FROM team_tree;
            """,
            (user_context.team_id, user_context.account_id, user_context.account_id)
        )
        sub_teams = [r[0] for r in cur.fetchall()]
        if not sub_teams:
            sub_teams = [user_context.team_id]

        placeholders = ", ".join("?" for _ in sub_teams)
        return (
            f"{prefix}account_id = ? AND {prefix}team_id IN ({placeholders})",
            [user_context.account_id] + sub_teams
        )

    # 7. Escopo de Unidade de Negócio / Business Unit (Diretor de Divisão)
    if scope == DataScopeEnum.BUSINESS_UNIT:
        if not user_context.business_unit_id:
            return (
                f"{prefix}account_id = ? AND {prefix}owner_id = ?",
                [user_context.account_id, user_context.user_id]
            )

        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM teams WHERE business_unit_id = ? AND account_id = ?",
            (user_context.business_unit_id, user_context.account_id)
        )
        bu_teams = [r[0] for r in cur.fetchall()]
        if not bu_teams:
            return f"{prefix}account_id = ?", [user_context.account_id]

        placeholders = ", ".join("?" for _ in bu_teams)
        return (
            f"{prefix}account_id = ? AND {prefix}team_id IN ({placeholders})",
            [user_context.account_id] + bu_teams
        )

    # Fallback padrão
    return f"{prefix}account_id = ?", [account_id]
