# -*- coding: utf-8 -*-
"""
Core Configuration — Revnaut VSA Monolith
Centraliza configurações de ambiente e parâmetros canônicos do sistema.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
def get_db_path() -> Path:
    db_env = os.getenv("REVNAUT_DB_PATH") or os.getenv("RVOPS_DB_PATH")
    if db_env:
        p = Path(db_env)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    return DATA_DIR / "rvops.db"

DB_PATH = get_db_path()

PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
APP_ENV = os.getenv("APP_ENV", "production")
SECRET_KEY = os.getenv("SECRET_KEY", "revnaut-secret-key-2026-superadmin-god")

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



