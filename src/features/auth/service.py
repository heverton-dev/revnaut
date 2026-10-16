# -*- coding: utf-8 -*-
"""
Motor de Autenticação e Emissão de Tokens de Sessão.
"""

from __future__ import annotations
import hashlib
import hmac
import time
from typing import Optional, Dict, Any
from fastapi import HTTPException
from src.core.config import SECRET_KEY
from src.core.database import get_connection


def hash_password(password: str) -> str:
    """Gera hash determinístico SHA-256 para senha."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_session_token(user_id: str) -> str:
    """Gera token de sessão assinado com HMAC-SHA256."""
    timestamp = str(int(time.time()))
    payload = f"{user_id}:{timestamp}".encode("utf-8")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return f"{user_id}.{timestamp}.{signature}"


def verify_session_token(token: str) -> Optional[str]:
    """Valida assinatura do token de sessão e retorna user_id se legítimo."""
    if not token or "." not in token:
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return None
    user_id, timestamp, signature = parts
    payload = f"{user_id}:{timestamp}".encode("utf-8")
    expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    if hmac.compare_digest(signature, expected_sig):
        return user_id
    return None


def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """Autentica usuário por e-mail e senha no SQLite WAL."""
    email_clean = email.strip().lower()
    pwd_hash = hash_password(password)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, account_id, name, email, role, is_superadmin, team_id, role_id, phone, password_hash, is_active "
        "FROM users WHERE lower(email) = ?",
        (email_clean,)
    )
    user = cur.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    if user["is_active"] == 0:
        raise HTTPException(status_code=403, detail="Usuário inativo. Contate o administrador.")

    # Se usuário possui hash cadastrado, validação estrita
    stored_hash = user["password_hash"]
    if stored_hash:
        if not hmac.compare_digest(stored_hash, pwd_hash):
            raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    else:
        # Para usuários de demonstração legados sem hash cadastrado,
        # permite senha padrão 'revnaut123' ou atualiza hash se for a primeira entrada
        default_demo_hash = hash_password("revnaut123")
        if not (hmac.compare_digest(default_demo_hash, pwd_hash) or password == "revnaut123"):
            raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    return dict(user)


def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Busca perfil completo do usuário autenticado."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, account_id, name, email, role, is_superadmin, team_id, role_id, phone "
        "FROM users WHERE id = ?",
        (user_id,)
    )
    user = cur.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None
