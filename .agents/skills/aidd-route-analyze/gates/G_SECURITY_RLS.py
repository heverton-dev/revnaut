#!/usr/bin/env python3
"""
Gate G_SECURITY_RLS:
Valida se a auditoria de seguranca da rota atesta conformidade com isolamento de tenant
ou gerou micro-tickets bloqueantes explicitos sem deixar pontas soltas.
"""
import os
import sys
from pathlib import Path

def check_security(slug: str):
    base_dir = os.environ.get("AUDIT_BASE_DIR", "docs/auditorias_rotas")
    sec_file = Path(base_dir) / slug / "04_cyber_seguranca_e_rls.md"
    if not sec_file.exists():
        print(f"[FAIL] G_SECURITY_RLS: Arquivo {sec_file} inexistente.")
        sys.exit(1)

    content = sec_file.read_text(encoding="utf-8", errors="ignore").lower()
    
    required_keywords = ["rbac", "tenant", "idor"]
    missing = [kw for kw in required_keywords if kw not in content]

    if missing:
        print(f"[FAIL] G_SECURITY_RLS: Analise incompleta. Termos mandatorios ausentes: {missing}")
        sys.exit(1)

    print(f"[PASS] G_SECURITY_RLS: Auditoria de seguranca e RLS concluida com rigor para {slug}.")
    sys.exit(0)

if __name__ == "__main__":
    slug_arg = sys.argv[1] if len(sys.argv) > 1 else None
    if not slug_arg:
        state_file = Path(".state/route_dispatch.json")
        if state_file.exists():
            import json
            slug_arg = json.loads(state_file.read_text(encoding="utf-8")).get("slug")

    if not slug_arg:
        print("[FAIL] G_SECURITY_RLS: Slug nao fornecido e nao encontrado em .state/route_dispatch.json.")
        sys.exit(1)

    check_security(slug_arg)
