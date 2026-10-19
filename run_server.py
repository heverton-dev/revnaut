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

    try:
        import sqlite3
        from src.core.config import get_db_path
        db_file = get_db_path()
        conn = sqlite3.connect(str(db_file), timeout=10.0)
        cur = conn.cursor()
        contacts_count = cur.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
        teams_count = cur.execute("SELECT COUNT(*) FROM teams").fetchone()[0]
        wallets_count = cur.execute("SELECT COUNT(*) FROM kp_loyalty_wallets").fetchone()[0]
        conn.close()
        if contacts_count < 5 or teams_count > 20 or wallets_count < 10:
            print(f"[AUTO-SEED] Disparando auto-seed (contacts: {contacts_count}, teams: {teams_count}, wallets: {wallets_count})...")
            from scripts.seed_multinational_enterprise import seed_all
            seed_all(clean_reset=True)
            revnaut_db = root_dir / "data" / "revnaut.db"
            rvops_db = root_dir / "data" / "rvops.db"
            if revnaut_db.exists():
                shutil.copy2(revnaut_db, rvops_db)
                print("[AUTO-SEED] Banco limpo sincronizado com sucesso para data/rvops.db!")
    except Exception as e:
        print(f"[AUTO-SEED] Erro na verificacao/execucao de seed: {e}")
    print("=================================================================")
    print(" REVNAUT ENTERPRISE ENGINE — VSA MONOLITH EM http://localhost:8000")
    print(" - Swagger Studio:     http://localhost:8000/docs")
    print(" - Webhook Studio:     http://localhost:8000/webhooks")
    print(" - MCP Studio (IA):    http://localhost:8000/mcp")
    print(" - Guia do Usuário:    http://localhost:8000/docs/guia")
    print("=================================================================")
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=False)
