# -*- coding: utf-8 -*-
"""
Motor Central de Segurança, RBAC e Data Scoping Hierárquico.
Resolve cláusulas SQL determinísticas baseadas no contexto e organograma do usuário.
"""

from __future__ import annotations
import base64
import os
from typing import Optional, Dict, Any, Tuple, List
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from fastapi import Header, HTTPException
from src.core.config import SECRET_KEY, VAULT_SECRET_KEY
from src.core.database import get_connection
from src.features.hierarchy.schemas import DataScopeEnum, UserContext


_VAULT_SALT = b"revnault-vault-salt-2026"


def _derive_aes_key(secret: str) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=_VAULT_SALT, iterations=100000)
    return kdf.derive(secret.encode())


def _get_aes_key() -> bytes:
    return _derive_aes_key(VAULT_SECRET_KEY)


def _decrypt_with(key: bytes, ciphertext: str) -> str:
    raw = base64.b64decode(ciphertext.encode("utf-8"))
    nonce, ct = raw[:12], raw[12:]
    return AESGCM(key).decrypt(nonce, ct, None).decode("utf-8")


def encrypt_secret(plaintext: str) -> str:
    """Criptografa segredo com AES-256-GCM (chave derivada de VAULT_SECRET_KEY) e retorna base64."""
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ct).decode("utf-8")


def decrypt_secret(ciphertext: str) -> str:
    """Descriptografa com a chave atual do cofre; aceita a chave legada (SECRET_KEY) até a rotação."""
    try:
        return _decrypt_with(_get_aes_key(), ciphertext)
    except Exception:
        if VAULT_SECRET_KEY == SECRET_KEY:
            raise
        return _decrypt_with(_derive_aes_key(SECRET_KEY), ciphertext)


# (tabela, coluna cifrada) com dados do cofre em repouso
VAULT_ENCRYPTED_COLUMNS = (
    ("tenant_credentials", "encrypted_payload"),
    ("webhook_subscriptions", "signing_secret_encrypted"),
)


def rotate_vault_encryption(conn) -> Dict[str, int]:
    """
    Re-cifra (idempotente) valores gravados com a chave legada usando VAULT_SECRET_KEY.
    Valores que já abrem com a chave atual não são tocados; valores ilegíveis são preservados.
    """
    stats = {"rotated": 0, "current": 0, "unreadable": 0}
    if VAULT_SECRET_KEY == SECRET_KEY:
        return stats
    current_key = _get_aes_key()
    legacy_key = _derive_aes_key(SECRET_KEY)
    existing_tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for table, column in VAULT_ENCRYPTED_COLUMNS:
        if table not in existing_tables:
            continue
        cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
        if column not in cols:
            continue
        rows = conn.execute(f"SELECT rowid, {column} FROM {table} WHERE {column} IS NOT NULL AND {column} != ''").fetchall()
        for rowid, value in rows:
            try:
                _decrypt_with(current_key, value)
                stats["current"] += 1
                continue
            except Exception:
                pass
            try:
                plaintext = _decrypt_with(legacy_key, value)
            except Exception:
                stats["unreadable"] += 1
                continue
            conn.execute(f"UPDATE {table} SET {column} = ? WHERE rowid = ?", (encrypt_secret(plaintext), rowid))
            stats["rotated"] += 1
    conn.commit()
    return stats


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
    """Bloqueia com HTTP 401/403 caso o usuário não esteja autenticado ou não possua a permissão necessária."""
    if user_id is None:
        return
    if not str(user_id).strip():
        raise HTTPException(
            status_code=401,
            detail="Não autenticado: cabeçalho X-User-ID é obrigatório.",
        )
    user_ctx = get_user_context(conn, user_id, account_id)
    if not check_user_permission(user_ctx, required_permission):
        raise HTTPException(
            status_code=403, 
            detail=f"Acesso negado: a função do usuário não possui a permissão '{required_permission}'."
        )


def get_scoped_user_ids(conn, user_context: Optional[UserContext]) -> List[str]:
    """
    Resolve de forma determinística todos os IDs de usuários pertencentes ao escopo
    hierárquico (DAG) do usuário autenticado (SELF, TEAM, SUBTREE, BUSINESS_UNIT, TENANT_GLOBAL).
    """
    if not user_context:
        return []

    cur = conn.cursor()
    scope = user_context.data_scope

    if user_context.is_superadmin or scope == DataScopeEnum.TENANT_GLOBAL:
        cur.execute(
            "SELECT id FROM users WHERE account_id = ?",
            (user_context.account_id,),
        )
        ids = [r[0] for r in cur.fetchall()]
        if user_context.user_id not in ids:
            ids.append(user_context.user_id)
        return ids

    if scope == DataScopeEnum.SELF or not user_context.team_id:
        return [user_context.user_id]

    if scope == DataScopeEnum.TEAM:
        cur.execute(
            "SELECT id FROM users WHERE account_id = ? AND team_id = ?",
            (user_context.account_id, user_context.team_id),
        )
        ids = [r[0] for r in cur.fetchall()]
        if user_context.user_id not in ids:
            ids.append(user_context.user_id)
        return ids

    if scope == DataScopeEnum.SUBTREE:
        cur.execute(
            """
            WITH RECURSIVE team_tree(id) AS (
                SELECT id FROM teams WHERE id = ? AND account_id = ?
                UNION ALL
                SELECT t.id FROM teams t
                JOIN team_tree tt ON t.parent_id = tt.id
                WHERE t.account_id = ?
            )
            SELECT id FROM users
            WHERE account_id = ? AND team_id IN (SELECT id FROM team_tree);
            """,
            (
                user_context.team_id,
                user_context.account_id,
                user_context.account_id,
                user_context.account_id,
            ),
        )
        ids = [r[0] for r in cur.fetchall()]
        if user_context.user_id not in ids:
            ids.append(user_context.user_id)
        return ids

    if scope == DataScopeEnum.BUSINESS_UNIT and user_context.business_unit_id:
        cur.execute(
            """
            SELECT u.id FROM users u
            JOIN teams t ON u.team_id = t.id
            WHERE u.account_id = ? AND t.business_unit_id = ?
            """,
            (user_context.account_id, user_context.business_unit_id),
        )
        ids = [r[0] for r in cur.fetchall()]
        if user_context.user_id not in ids:
            ids.append(user_context.user_id)
        return ids

    return [user_context.user_id]


def resolve_data_scope_clause(
    conn, 
    user_context: Optional[UserContext], 
    account_id: str = "0f14ffff", 
    table_alias: str = ""
) -> Tuple[str, List[Any]]:
    """
    Retorna uma tupla (sql_clause, params) para injeção direta em consultas SQL.
    Aplica isolamento por linha (Row-Level Security / Territory Management Dual Field + Inside).
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

    # 5. Escopo de Time Direto (Gestor Regional — inclui registros do time e de subordinados Field/Inside)
    if scope == DataScopeEnum.TEAM:
        if not user_context.team_id:
            return (
                f"{prefix}account_id = ? AND ({prefix}owner_id = ? OR {prefix}field_owner_id = ? OR {prefix}inside_owner_id = ?)",
                [user_context.account_id, user_context.user_id, user_context.user_id, user_context.user_id]
            )
        scoped_users = get_scoped_user_ids(conn, user_context)
        u_placeholders = ", ".join("?" for _ in scoped_users)
        return (
            f"{prefix}account_id = ? AND ("
            f"{prefix}team_id = ? "
            f"OR {prefix}owner_id IN ({u_placeholders}) "
            f"OR {prefix}field_owner_id IN ({u_placeholders}) "
            f"OR {prefix}inside_owner_id IN ({u_placeholders})"
            f")",
            [user_context.account_id, user_context.team_id] + scoped_users + scoped_users + scoped_users
        )

    # 6. Escopo de Subárvore Recursiva (Gestor Distrital — inclui sub-times e subordinados Field/Inside)
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

        scoped_users = get_scoped_user_ids(conn, user_context)
        t_placeholders = ", ".join("?" for _ in sub_teams)
        u_placeholders = ", ".join("?" for _ in scoped_users)
        return (
            f"{prefix}account_id = ? AND ("
            f"{prefix}team_id IN ({t_placeholders}) "
            f"OR {prefix}owner_id IN ({u_placeholders}) "
            f"OR {prefix}field_owner_id IN ({u_placeholders}) "
            f"OR {prefix}inside_owner_id IN ({u_placeholders})"
            f")",
            [user_context.account_id] + sub_teams + scoped_users + scoped_users + scoped_users
        )

    # 7. Escopo de Unidade de Negócio / Business Unit (Diretor de Divisão)
    if scope == DataScopeEnum.BUSINESS_UNIT:
        if not user_context.business_unit_id:
            return (
                f"{prefix}account_id = ? AND ({prefix}owner_id = ? OR {prefix}field_owner_id = ? OR {prefix}inside_owner_id = ?)",
                [user_context.account_id, user_context.user_id, user_context.user_id, user_context.user_id]
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
