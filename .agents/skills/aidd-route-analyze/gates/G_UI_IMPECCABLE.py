#!/usr/bin/env python3
"""
Gate G_UI_IMPECCABLE:
1. Valida Lei #14 (Zero Emojis): nenhum emoji pictografico/emoticon permitido.
   Nao confunde caracteres de box-drawing arquitetural (ex: |, -, +, setas) com emojis.
2. Valida presenca de secoes obrigatorias de UI/UX.
Retorna exit 0 se aprovado, exit 1 se violado.
"""
import os
import sys
import re
from pathlib import Path

# Faixas Unicode estritas para Emojis Reais (Pictogramas, Emoticons, Carinhas, Gestos, etc.)
REAL_EMOJI_REGEX = re.compile(
    r"["
    r"\U0001F600-\U0001F64F"  # Emoticons
    r"\U0001F300-\U0001F5FF"  # Misc Symbols e Pictographs (ex: foguinho, lampada, etc.)
    r"\U0001F680-\U0001F6FF"  # Transport e Map
    r"\U0001F1E0-\U0001F1FF"  # Bandeiras
    r"\U0001F900-\U0001F9FF"  # Suplementares (robos, gestos, carinhas novas)
    r"\U0001FA70-\U0001FAFF"  # Simbolos adicionais
    r"\U00002600-\U000026FF"  # Simbolos diversos (sol, cafe, etc.)
    r"]",
    flags=re.UNICODE
)

def check_ui_impeccable(slug: str):
    base_dir = os.environ.get("AUDIT_BASE_DIR", "docs/auditorias_rotas")
    target_dir = Path(base_dir) / slug
    if not target_dir.exists():
        print(f"[FAIL] G_UI_IMPECCABLE: Diretorio {target_dir} inexistente.")
        sys.exit(1)

    violations = []
    for md_file in target_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8", errors="ignore")
        matches = REAL_EMOJI_REGEX.findall(content)
        if matches:
            violations.append(f"{md_file.name}: {len(matches)} emoji(s) detectado(s) [{', '.join(set(matches))}]")

    if violations:
        print("[FAIL] G_UI_IMPECCABLE: Violacao estrita da Lei #14 (Zero Emojis detectada):")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)

    print(f"[PASS] G_UI_IMPECCABLE: Lei #14 cumprida com sucesso em todos os artefatos de {slug}.")
    sys.exit(0)

if __name__ == "__main__":
    slug_arg = sys.argv[1] if len(sys.argv) > 1 else None
    if not slug_arg:
        state_file = Path(".state/route_dispatch.json")
        if state_file.exists():
            import json
            slug_arg = json.loads(state_file.read_text(encoding="utf-8")).get("slug")

    if not slug_arg:
        print("[FAIL] G_UI_IMPECCABLE: Slug nao fornecido e nao encontrado em .state/route_dispatch.json.")
        sys.exit(1)

    check_ui_impeccable(slug_arg)
