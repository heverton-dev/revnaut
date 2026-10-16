# -*- coding: utf-8 -*-
"""
Revnaut Server Launcher — Monólito VSA (AIDD Master Standard)
Executa FastAPI com SQLite WAL na porta 8000.
"""

import uvicorn
from src.core.database import init_db

if __name__ == "__main__":
    init_db()
    print("=================================================================")
    print(" 🚀 REVNAUT ENTERPRISE ENGINE — VSA MONOLITH EM http://localhost:8000")
    print(" - Swagger Studio:     http://localhost:8000/docs")
    print(" - Webhook Studio:     http://localhost:8000/webhooks")
    print(" - MCP Studio (IA):    http://localhost:8000/mcp")
    print(" - Guia do Usuário:    http://localhost:8000/docs/guia")
    print("=================================================================")
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=False)
