# -*- coding: utf-8 -*-
"""
Core Configuration — RevNault VSA Monolith
Centraliza configurações de ambiente e parâmetros canônicos do sistema.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
def get_db_path() -> Path:
    db_env = os.getenv("REVNAULT_DB_PATH") or os.getenv("REVNAUT_DB_PATH") or os.getenv("RVOPS_DB_PATH")
    if db_env:
        p = Path(db_env)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    return DATA_DIR / "revnault.db"

DB_PATH = get_db_path()

PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
APP_ENV = os.getenv("APP_ENV", "production")
LEGACY_DEFAULT_SECRET_KEY = "revnaut-secret-key-2026-superadmin-god"
# Chave legada: só é usada para decifrar dados do cofre gravados antes da separação de chaves.
SECRET_KEY = os.getenv("SECRET_KEY", LEGACY_DEFAULT_SECRET_KEY)
# Assinatura HMAC dos tokens de sessão e de redefinição de senha
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", SECRET_KEY)
# Derivação da chave AES-256-GCM do cofre de credenciais
VAULT_SECRET_KEY = os.getenv("VAULT_SECRET_KEY", SECRET_KEY)
# Validade do token de sessão emitido no login (padrão: 12 horas)
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "43200"))
SESSION_COOKIE_NAME = "revnaut_session"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "1").lower() not in ("0", "false", "no")

# Segredos de webhooks inbound (fail-closed: sem segredo configurado a chamada do provedor é recusada)
DOCUMENSO_WEBHOOK_SECRET = os.getenv("DOCUMENSO_WEBHOOK_SECRET", "")
CALCOM_WEBHOOK_SECRET = os.getenv("CALCOM_WEBHOOK_SECRET", "")
LISTMONK_WEBHOOK_SECRET = os.getenv("LISTMONK_WEBHOOK_SECRET", "")
# HMAC dos webhooks Evolution / Chatwoot / Mautic (X-*-Signature, X-Hub-Signature-256)
OMNICHANNEL_WEBHOOK_SECRET = os.getenv("OMNICHANNEL_WEBHOOK_SECRET", "")

# Origens autorizadas a chamar a API com credenciais (cookie de sessão)
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "https://revnault.vpsconexao.org,http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
    ).split(",")
    if o.strip()
]


def assert_production_secrets() -> None:
    """Em produção (REVNAUT_ENV=production) recusa subir com chaves padrão públicas ou fracas."""
    if os.getenv("REVNAUT_ENV", "").lower() != "production":
        return
    weak = [
        name
        for name, value in (("SESSION_SECRET_KEY", SESSION_SECRET_KEY), ("VAULT_SECRET_KEY", VAULT_SECRET_KEY))
        if not value or value == LEGACY_DEFAULT_SECRET_KEY or len(value) < 32
    ]
    if weak:
        raise RuntimeError(f"Segredos ausentes ou fracos em produção: {', '.join(weak)} (mínimo 32 caracteres).")

# Cloudflare R2 Object Storage Config (S3 API v4 compatible)
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "mock-r2-account-id")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID", "mock-r2-access-key")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "mock-r2-secret-key")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "revnaut-media")
R2_PUBLIC_DOMAIN = os.getenv("R2_PUBLIC_DOMAIN", "https://cdn.revnaut.io")
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL", f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com")

# Apache Superset Embedded Config
SUPERSET_SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY", "revnaut_superset_secret_jwt_key_2026")
SUPERSET_DOMAIN = os.getenv("SUPERSET_DOMAIN", "http://localhost:8088")



