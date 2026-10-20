# -*- coding: utf-8 -*-
"""
Motor de Autenticação e Emissão de Tokens de Sessão.
"""

from __future__ import annotations
import base64
import hashlib
import hmac
import os
import secrets
import time
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException
from src.core.config import SESSION_SECRET_KEY, SESSION_TTL_SECONDS
from src.core.database import get_connection

PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = int(os.getenv("PASSWORD_PBKDF2_ITERATIONS", "600000"))
MIN_PASSWORD_LENGTH = 12

# Senhas padrão e vazadas (seed de homologação e LoginPage publicado): nunca aceitas em produção
_COMPROMISED_PASSWORDS = ("admin", "admin123", "revnault", "revnault123", "123456")
COMPROMISED_LEGACY_HASHES = frozenset(
    {hashlib.sha256(p.encode("utf-8")).hexdigest() for p in _COMPROMISED_PASSWORDS}
    | {"579ac58e034634060983ac3b0100617b0e10fa05438675d44bb19b1533cdb0a6"}  # hash semeado do Super Admin
)


def _legacy_sha256(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    """Hash PBKDF2-SHA256 com sal aleatório: pbkdf2_sha256$iteracoes$sal_b64$hash_b64."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_password(password: str, stored_hash: Optional[str]) -> Tuple[bool, bool]:
    """Retorna (senha_confere, precisa_regravar_hash). Aceita PBKDF2 e o SHA-256 legado sem sal."""
    if not stored_hash:
        return False, False
    if stored_hash.startswith(f"{PBKDF2_ALGORITHM}$"):
        try:
            _, iterations, salt_b64, hash_b64 = stored_hash.split("$")
            digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), base64.b64decode(salt_b64), int(iterations))
        except (ValueError, TypeError):
            return False, False
        ok = hmac.compare_digest(base64.b64encode(digest).decode(), hash_b64)
        return ok, ok and int(iterations) < PBKDF2_ITERATIONS
    ok = hmac.compare_digest(stored_hash, _legacy_sha256(password))
    return ok, ok


def is_compromised_password(password: str) -> bool:
    return _legacy_sha256(password) in COMPROMISED_LEGACY_HASHES


def is_compromised_hash(stored_hash: Optional[str]) -> bool:
    return bool(stored_hash) and stored_hash in COMPROMISED_LEGACY_HASHES


def production_mode() -> bool:
    return os.getenv("REVNAULT_ENV", "").lower() == "production"


def validate_new_password(password: str) -> None:
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(status_code=400, detail=f"A nova senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres.")
    if is_compromised_password(password):
        raise HTTPException(status_code=400, detail="Senha padrão ou vazada não é permitida. Escolha outra senha.")


def set_user_password(user_id: str, new_password: str) -> None:
    validate_new_password(new_password)
    conn = get_connection()
    try:
        cur = conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(new_password), user_id))
        conn.commit()
        if cur.rowcount != 1:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    finally:
        conn.close()


def create_session_token(user_id: str) -> str:
    """Gera token de sessão assinado com HMAC-SHA256."""
    timestamp = str(int(time.time()))
    payload = f"{user_id}:{timestamp}".encode("utf-8")
    signature = hmac.new(SESSION_SECRET_KEY.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return f"{user_id}.{timestamp}.{signature}"


SESSION_CLOCK_SKEW_SECONDS = 300


def verify_session_token(token: str, now: Optional[float] = None) -> Optional[str]:
    """Valida assinatura e validade (SESSION_TTL_SECONDS) do token de sessão; retorna user_id se legítimo."""
    if not token or "." not in token:
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return None
    user_id, timestamp, signature = parts
    payload = f"{user_id}:{timestamp}".encode("utf-8")
    expected_sig = hmac.new(SESSION_SECRET_KEY.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_sig):
        return None
    try:
        issued_at = int(timestamp)
    except ValueError:
        return None
    current = time.time() if now is None else now
    if issued_at > current + SESSION_CLOCK_SKEW_SECONDS or current - issued_at > SESSION_TTL_SECONDS:
        return None
    return user_id


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

    stored_hash = user["password_hash"]
    is_valid, needs_rehash = verify_password(password, stored_hash)
    if not is_valid:
        _record_failed_attempt(email_clean)
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    if user["is_active"] == 0:
        raise HTTPException(status_code=403, detail="Usuário inativo. Contate o administrador.")

    if production_mode() and (is_compromised_hash(stored_hash) or is_compromised_password(password)):
        raise HTTPException(
            status_code=403,
            detail=(
                "Senha padrão ou vazada bloqueada. Redefina a senha: o Super Admin pela tela de usuários "
                "ou, para o próprio Super Admin, com python -m src.features.auth.set_password_cli <e-mail> no servidor."
            ),
        )

    if needs_rehash:
        conn = get_connection()
        try:
            conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(password), user["id"]))
            conn.commit()
        finally:
            conn.close()

    _clear_failed_attempts(email_clean)
    result = dict(user)
    result.pop("password_hash", None)
    return result


def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Busca perfil completo do usuário autenticado."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, account_id, name, email, role, is_superadmin, team_id, role_id, phone, "
        "COALESCE(is_active, 1) AS is_active "
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
    validate_new_password(data.password)
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

    set_user_password(target_user_id, new_password)
    return {"id": target_user_id, "success": True, "message": "Senha redefinida com sucesso."}


PASSWORD_RESET_TTL_SECONDS = 3600
GENERIC_RESET_MESSAGE = "Se o e-mail estiver cadastrado e ativo, enviamos o link de recuperação (válido por 60 minutos)."


def _reset_fingerprint(password_hash: Optional[str]) -> str:
    """Amarra o token ao hash atual: após a troca de senha o token deixa de valer (uso único)."""
    return hashlib.sha256((password_hash or "").encode("utf-8")).hexdigest()[:16]


def _reset_signature(user_id: str, issued_at: int, password_hash: Optional[str]) -> str:
    payload = f"reset:{user_id}:{issued_at}:{_reset_fingerprint(password_hash)}".encode("utf-8")
    return hmac.new(SESSION_SECRET_KEY.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def create_password_reset_token(user_id: str, password_hash: Optional[str], issued_at: Optional[int] = None) -> str:
    ts = int(time.time()) if issued_at is None else issued_at
    return f"rst.{user_id}.{ts}.{_reset_signature(user_id, ts, password_hash)}"


def _send_password_reset_email(email: str, name: str, token: str) -> None:
    from src.features.campaigns.listmonk_adapter import ListmonkClient

    base_url = os.getenv("APP_PUBLIC_URL", "https://revnault.vpsconexao.org").rstrip("/")
    ListmonkClient().send_transactional(
        subscriber_email=email,
        template_id=int(os.getenv("LISTMONK_PASSWORD_RESET_TEMPLATE_ID", "1")),
        data={
            "name": name,
            "reset_url": f"{base_url}/#!/reset-password?token={token}",
            "expires_minutes": PASSWORD_RESET_TTL_SECONDS // 60,
        },
    )


def request_password_reset(email: str) -> Dict[str, Any]:
    """
    Envia o link de recuperação por e-mail. A resposta é sempre a mesma (não revela se o e-mail
    existe nem devolve o token) para impedir enumeração de contas e sequestro de senha.
    """
    email_clean = email.strip().lower()
    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT id, name, email, is_active, password_hash FROM users WHERE lower(email) = ?", (email_clean,)
        ).fetchone()
    finally:
        conn.close()

    if user and user["is_active"]:
        token = create_password_reset_token(user["id"], user["password_hash"])
        try:
            _send_password_reset_email(user["email"], user["name"], token)
        except Exception:
            # Falha de entrega não altera a resposta pública
            pass
    return {"success": True, "message": GENERIC_RESET_MESSAGE, "reset_token": None}


def reset_password_with_token(token: str, new_password: str, now: Optional[float] = None) -> Dict[str, Any]:
    """Consome token de uso único (1 hora) e grava a nova senha com PBKDF2."""
    invalid = HTTPException(status_code=400, detail="Link de recuperação inválido ou expirado. Solicite um novo.")
    if not token or not token.startswith("rst."):
        raise invalid
    parts = token.split(".")
    if len(parts) != 4:
        raise invalid
    _, user_id, timestamp_str, sig = parts
    try:
        ts = int(timestamp_str)
    except ValueError:
        raise invalid
    current = time.time() if now is None else now
    if current - ts > PASSWORD_RESET_TTL_SECONDS or ts > current + SESSION_CLOCK_SKEW_SECONDS:
        raise invalid

    conn = get_connection()
    try:
        user = conn.execute("SELECT id, is_active, password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()
    if not user or not user["is_active"]:
        raise invalid
    if not hmac.compare_digest(sig, _reset_signature(user_id, ts, user["password_hash"])):
        raise invalid

    set_user_password(user_id, new_password)
    return {"success": True, "message": "Senha alterada com sucesso! Você já pode realizar o login."}


def store_tenant_credential(
    account_id: str,
    service_name: str,
    credential_type: str,
    secret_payload: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Criptografa e armazena credencial com AES-256-GCM."""
    import uuid
    import json
    from src.core.security import encrypt_secret

    cred_id = f"cred-{uuid.uuid4().hex[:12]}"
    encrypted = encrypt_secret(secret_payload)
    meta_json = json.dumps(metadata or {})

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO tenant_credentials (
                id, account_id, service_name, credential_type, encrypted_payload, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (cred_id, account_id, service_name, credential_type, encrypted, meta_json),
        )
        conn.commit()
        return cred_id
    finally:
        conn.close()


def get_decrypted_credential(account_id: str, credential_id: str) -> str:
    """Recupera e descriptografa credencial em memória para serviço autorizado."""
    from src.core.security import decrypt_secret

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT encrypted_payload FROM tenant_credentials WHERE id = ? AND account_id = ?",
            (credential_id, account_id),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Credencial não encontrada.")
        return decrypt_secret(row["encrypted_payload"])
    finally:
        conn.close()


def list_tenant_credentials(account_id: str) -> List[Dict[str, Any]]:
    """Lista credenciais do tenant com valores mascarados."""
    import json
    from src.core.security import decrypt_secret

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, account_id, service_name, credential_type, encrypted_payload, metadata_json, created_at
            FROM tenant_credentials
            WHERE account_id = ?
            ORDER BY created_at DESC
            """,
            (account_id,),
        )
        rows = cur.fetchall()
        result = []
        for r in rows:
            meta = json.loads(r["metadata_json"]) if r["metadata_json"] else {}
            try:
                decrypted = decrypt_secret(r["encrypted_payload"])
                last4 = decrypted[-4:] if len(decrypted) >= 4 else "****"
            except Exception:
                last4 = "****"
            result.append({
                "id": r["id"],
                "account_id": r["account_id"],
                "service_name": r["service_name"],
                "credential_type": r["credential_type"],
                "masked_value": f"****{last4}",
                "metadata": meta,
                "created_at": r["created_at"],
            })
        return result
    finally:
        conn.close()


def delete_tenant_credential(account_id: str, credential_id: str) -> bool:
    """Remove credencial do cofre."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM tenant_credentials WHERE id = ? AND account_id = ?",
            (credential_id, account_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


