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


_failed_login_attempts: Dict[str, list[float]] = {}
RATE_LIMIT_WINDOW_SECONDS = 900  # 15 minutos
MAX_FAILED_ATTEMPTS = 5


def _check_rate_limit(email_clean: str):
    now = time.time()
    attempts = _failed_login_attempts.get(email_clean, [])
    # Limpa tentativas mais velhas que 15 min
    valid_attempts = [t for t in attempts if now - t < RATE_LIMIT_WINDOW_SECONDS]
    _failed_login_attempts[email_clean] = valid_attempts
    if len(valid_attempts) >= MAX_FAILED_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Muitas tentativas de login incorretas. Conta bloqueada temporariamente por 15 minutos (Proteção contra força bruta)."
        )


def _record_failed_attempt(email_clean: str):
    now = time.time()
    if email_clean not in _failed_login_attempts:
        _failed_login_attempts[email_clean] = []
    _failed_login_attempts[email_clean].append(now)


def _clear_failed_attempts(email_clean: str):
    if email_clean in _failed_login_attempts:
        _failed_login_attempts.pop(email_clean, None)


def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """Autentica usuário por e-mail e senha no SQLite WAL com rate limiting contra força bruta."""
    email_clean = email.strip().lower()
    _check_rate_limit(email_clean)

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
        _record_failed_attempt(email_clean)
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    if user["is_active"] == 0:
        raise HTTPException(status_code=403, detail="Usuário inativo. Contate o administrador.")

    # Se usuário possui hash cadastrado, validação estrita
    stored_hash = user["password_hash"]
    if stored_hash:
        if not hmac.compare_digest(stored_hash, pwd_hash):
            _record_failed_attempt(email_clean)
            raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    else:
        # Para usuários de demonstração legados sem hash cadastrado,
        # permite senha padrão 'revnaut123' ou atualiza hash se for a primeira entrada
        default_demo_hash = hash_password("revnaut123")
        if not (hmac.compare_digest(default_demo_hash, pwd_hash) or password == "revnaut123"):
            _record_failed_attempt(email_clean)
            raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    # Sucesso: limpa tentativas falhas
    _clear_failed_attempts(email_clean)
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


def list_all_users(account_id: str = "0f14ffff") -> list[Dict[str, Any]]:
    """Lista todos os usuários com dados enriquecidos de BU e Equipe."""
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT 
            u.id, u.account_id, u.name, u.email, u.role, 
            coalesce(u.is_superadmin, 0) as is_superadmin,
            coalesce(u.is_active, 1) as is_active,
            u.team_id, t.name as team_name,
            t.business_unit_id as bu_id, bu.name as bu_name,
            u.phone, u.role_id, u.created_at
        FROM users u
        LEFT JOIN teams t ON u.team_id = t.id
        LEFT JOIN business_units bu ON t.business_unit_id = bu.id
        WHERE u.account_id = ?
        ORDER BY u.is_superadmin DESC, u.name ASC
    """
    cur.execute(query, (account_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    # Converte tipos booleanos
    for r in rows:
        r["is_superadmin"] = bool(r["is_superadmin"])
        r["is_active"] = bool(r["is_active"])
    return rows


def create_collaborator(
    data: Any,
    current_user: Dict[str, Any],
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Cadastra novo colaborador corporativo garantindo que apenas Super Admin crie e ninguém mais vire Super Admin."""
    if not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Apenas o Super Admin pode cadastrar novos colaboradores.")

    email_clean = data.email.strip().lower()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE lower(email) = ?", (email_clean,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="E-mail já cadastrado no sistema.")

    import uuid
    new_user_id = f"usr_{uuid.uuid4().hex[:10]}"
    pwd_hash = hash_password(data.password)

    # Invariante de Segurança: is_superadmin é SEMPRE 0 para novos colaboradores
    cur.execute("""
        INSERT INTO users (id, account_id, name, email, role, is_superadmin, password_hash, is_active, team_id, role_id, phone)
        VALUES (?, ?, ?, ?, ?, 0, ?, 1, ?, ?, ?)
    """, (
        new_user_id,
        account_id,
        data.name.strip(),
        email_clean,
        data.role,
        pwd_hash,
        data.team_id,
        data.role_id,
        data.phone
    ))
    conn.commit()
    conn.close()

    return {
        "id": new_user_id,
        "account_id": account_id,
        "name": data.name.strip(),
        "email": email_clean,
        "role": data.role,
        "is_superadmin": False,
        "is_active": True,
        "team_id": data.team_id,
        "role_id": data.role_id,
        "phone": data.phone
    }


def update_user_status(target_user_id: str, is_active: bool, current_user: Dict[str, Any]) -> Dict[str, Any]:
    """Ativa ou desativa usuário no sistema."""
    if not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Apenas o Super Admin pode alterar status de usuários.")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT is_superadmin FROM users WHERE id = ?", (target_user_id,))
    target = cur.fetchone()
    if not target:
        conn.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    if target["is_superadmin"] and not is_active:
        conn.close()
        raise HTTPException(status_code=400, detail="O Super Admin único não pode ser desativado.")

    cur.execute("UPDATE users SET is_active = ? WHERE id = ?", (1 if is_active else 0, target_user_id))
    conn.commit()
    conn.close()
    return {"id": target_user_id, "is_active": is_active, "success": True}


def reset_user_password(target_user_id: str, new_password: str, current_user: Dict[str, Any]) -> Dict[str, Any]:
    """Redefine deterministamente a senha de um colaborador pelo Super Admin."""
    if not current_user.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Apenas o Super Admin pode resetar senhas de colaboradores.")

    if not new_password or len(new_password) < 6:
        raise HTTPException(status_code=400, detail="A nova senha deve ter no mínimo 6 caracteres.")

    new_hash = hash_password(new_password)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE id = ?", (target_user_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    cur.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, target_user_id))
    conn.commit()
    conn.close()
    return {"id": target_user_id, "success": True, "message": "Senha redefinida com sucesso."}


def request_password_reset(email: str) -> Dict[str, Any]:
    """Gera token de recuperação temporário (1 hora) para auto-recuperação de senha."""
    email_clean = email.strip().lower()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, is_active FROM users WHERE lower(email) = ?", (email_clean,))
    user = cur.fetchone()
    conn.close()

    if not user:
        # Por segurança corporativa, não revela se o e-mail existe ou não
        return {
            "success": True,
            "message": "Se o e-mail estiver cadastrado, o link de recuperação foi gerado.",
            "reset_token": None
        }

    if user["is_active"] == 0:
        raise HTTPException(status_code=403, detail="Conta inativa. Contate o administrador.")

    # Gera token de reset temporário com validade de 1 hora
    now = int(time.time())
    payload = f"reset:{user['id']}:{now}".encode("utf-8")
    sig = hmac.new(SECRET_KEY.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    reset_token = f"rst.{user['id']}.{now}.{sig}"

    return {
        "success": True,
        "message": "Link de recuperação gerado com sucesso. Válido por 60 minutos.",
        "reset_token": reset_token
    }


def reset_password_with_token(token: str, new_password: str) -> Dict[str, Any]:
    """Consome token temporário e atualiza senha do usuário."""
    if not token or not token.startswith("rst."):
        raise HTTPException(status_code=400, detail="Token de recuperação inválido.")

    parts = token.split(".")
    if len(parts) != 4:
        raise HTTPException(status_code=400, detail="Formato de token inválido.")

    _, user_id, timestamp_str, sig = parts
    try:
        ts = int(timestamp_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Timestamp do token corrompido.")

    # Validade de 3600 segundos (1 hora)
    if time.time() - ts > 3600:
        raise HTTPException(status_code=400, detail="O link de recuperação expirou. Solicite um novo.")

    payload = f"reset:{user_id}:{ts}".encode("utf-8")
    expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        raise HTTPException(status_code=400, detail="Assinatura criptográfica do token inválida.")

    if not new_password or len(new_password) < 6:
        raise HTTPException(status_code=400, detail="A nova senha deve ter no mínimo 6 caracteres.")

    new_hash = hash_password(new_password)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Usuário do token não encontrado.")

    cur.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
    conn.commit()
    conn.close()

    return {"success": True, "message": "Senha alterada com sucesso! Você já pode realizar o login."}

