# -*- coding: utf-8 -*-
"""
Database Proxy — Retrocompatibilidade Canônica VSA
Reexporta conexão e inicialização do SQLite WAL de src.core.database
"""

from src.core.database import get_connection, init_db, DB_PATH

__all__ = ["get_connection", "init_db", "DB_PATH"]
