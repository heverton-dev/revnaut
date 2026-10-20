#!/usr/bin/env python3
"""
Gate G_PDF_GENERATED:
Valida se o relatorio PDF corporativo foi compilado e possui tamanho compativel (> 50KB).
Retorna exit 0 se aprovado, exit 1 se ausente ou corrompido.
"""
import sys
from pathlib import Path

def check_pdf(slug: str):
    target_dir = Path("docs/auditorias_rotas") / slug
    pdf_path = target_dir / f"RELATORIO_AUDITORIA_{slug}.pdf"

    if not pdf_path.exists():
        print(f"[FAIL] G_PDF_GENERATED: Arquivo PDF {pdf_path} inexistente. Execute o compilador de PDF.")
        sys.exit(1)

    size = pdf_path.stat().st_size
    if size < 50_000:
        print(f"[FAIL] G_PDF_GENERATED: Arquivo PDF muito pequeno ({size} bytes). Provavel falha de renderizacao.")
        sys.exit(1)

    print(f"[PASS] G_PDF_GENERATED: Relatorio corporativo em PDF gerado com sucesso ({size:,} bytes).")
    sys.exit(0)

if __name__ == "__main__":
    slug_arg = sys.argv[1] if len(sys.argv) > 1 else None
    if not slug_arg:
        state_file = Path(".state/route_dispatch.json")
        if state_file.exists():
            import json
            slug_arg = json.loads(state_file.read_text(encoding="utf-8")).get("slug")

    if not slug_arg:
        print("[FAIL] G_PDF_GENERATED: Slug nao fornecido e nao encontrado em .state/route_dispatch.json.")
        sys.exit(1)

    check_pdf(slug_arg)
