# -*- coding: utf-8 -*-
"""
Backend Proxy — Retrocompatibilidade Canônica VSA
Reexporta a aplicação Monólito Modular de src.main
"""

from src.main import app
from src.core.database import get_connection, init_db
