#!/usr/bin/env python3
"""
Gate G_ROUTE_DISPATCH: Valida se o dispatch deterministico identificou com sucesso o alvo.
Retorna exit 0 se aprovado, exit 1 se bloqueado.
"""
import sys
import json
from pathlib import Path

def check_dispatch():
    state_file = Path(".state/route_dispatch.json")
    if not state_file.exists():
        print("[FAIL] G_ROUTE_DISPATCH: Arquivo .state/route_dispatch.json inexistente. Execute o dispatcher primeiro.")
        sys.exit(1)

    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[FAIL] G_ROUTE_DISPATCH: Erro ao ler JSON de dispatch: {e}")
        sys.exit(1)

    slug = data.get("slug")
    route_type = data.get("route_type")

    if not slug or route_type == "unknown":
        print(f"[FAIL] G_ROUTE_DISPATCH: Slug invalido ou tipo desconhecido (slug={slug}, type={route_type}).")
        sys.exit(1)

    print(f"[PASS] G_ROUTE_DISPATCH: Alvo valido identificado [Slug: {slug} | Tipo: {route_type}].")
    sys.exit(0)

if __name__ == "__main__":
    check_dispatch()
