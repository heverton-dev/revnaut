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
DB_PATH = DATA_DIR / "rvops.db"

PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
APP_ENV = os.getenv("APP_ENV", "production")
SECRET_KEY = os.getenv("SECRET_KEY", "revnaut-secret-key-2026-superadmin-god")

