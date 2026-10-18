# -*- coding: utf-8 -*-
"""
Revnaut Server Launcher — Monólito VSA (AIDD Master Standard)
Executa FastAPI com SQLite WAL na porta 8000.
"""

import shutil
import subprocess
import sys
from pathlib import Path
import uvicorn
from src.core.database import init_db

if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent
    frontend_dist_index = root_dir / "frontend" / "dist" / "index.html"
    frontend_pkg = root_dir / "frontend" / "package.json"

    if not frontend_dist_index.exists() and frontend_pkg.exists():
        print("[AUTO-BUILD] frontend/dist/index.html ausente. Compilando React 19 SPA...")
        try:
            npm_bin = shutil.which("npm") or ("npm.cmd" if sys.platform == "win32" else "npm")
            subprocess.run([npm_bin, "--prefix", "frontend", "run", "build"], cwd=str(root_dir), check=True)
            print("[AUTO-BUILD] React 19 SPA compilado com sucesso em frontend/dist!")
        except Exception as e:
            print(f"[AUTO-BUILD WARNING] Falha ao compilar frontend automaticamente: {e}")

    init_db()
    print("=================================================================")
    print(" REVNAUT ENTERPRISE ENGINE — VSA MONOLITH EM http://localhost:8000")
    print(" - Swagger Studio:     http://localhost:8000/docs")
    print(" - Webhook Studio:     http://localhost:8000/webhooks")
    print(" - MCP Studio (IA):    http://localhost:8000/mcp")
    print(" - Guia do Usuário:    http://localhost:8000/docs/guia")
    print("=================================================================")
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=False)
