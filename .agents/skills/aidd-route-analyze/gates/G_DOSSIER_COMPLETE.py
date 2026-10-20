#!/usr/bin/env python3
"""
Gate G_DOSSIER_COMPLETE:
Valida se os 8 arquivos obrigatorios do dossie da rota foram gerados e possuem conteudo minimo.
"""
import sys
from pathlib import Path

REQUIRED_FILES = [
    "01_visao_geral_e_jornada.md",
    "02_ui_ux_impeccable.md",
    "03_motores_e_subprodutizacao.md",
    "04_cyber_seguranca_e_rls.md",
    "05_arquitetura_e_engenharia.md",
    "06_especificacao_dd.md",
    "07_plano_micro_tickets.md",
    "08_botoes_modais_e_acoes.md",
    "RELATORIO_CONSOLIDADO.md"
]

def check_dossier(slug: str):
    target_dir = Path("docs/auditorias_rotas") / slug
    if not target_dir.exists():
        print(f"[FAIL] G_DOSSIER_COMPLETE: Diretorio {target_dir} inexistente.")
        sys.exit(1)

    missing = []
    empty = []

    for fname in REQUIRED_FILES:
        fpath = target_dir / fname
        if not fpath.exists():
            missing.append(fname)
        elif fpath.stat().st_size < 100:
            empty.append(fname)

    if missing:
        print(f"[FAIL] G_DOSSIER_COMPLETE: Arquivos mandatorios ausentes no dossie: {missing}")
        sys.exit(1)

    if empty:
        print(f"[FAIL] G_DOSSIER_COMPLETE: Arquivos insuficientes (< 100 bytes): {empty}")
        sys.exit(1)

    print(f"[PASS] G_DOSSIER_COMPLETE: Todos os 8 artefatos canônicos estao presentes e completos para {slug}.")
    sys.exit(0)

if __name__ == "__main__":
    slug_arg = sys.argv[1] if len(sys.argv) > 1 else None
    if not slug_arg:
        state_file = Path(".state/route_dispatch.json")
        if state_file.exists():
            import json
            slug_arg = json.loads(state_file.read_text(encoding="utf-8")).get("slug")

    if not slug_arg:
        print("[FAIL] G_DOSSIER_COMPLETE: Slug nao fornecido e nao encontrado em .state/route_dispatch.json.")
        sys.exit(1)

    check_dossier(slug_arg)
