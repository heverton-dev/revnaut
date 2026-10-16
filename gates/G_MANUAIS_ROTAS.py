#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quality Gate: Validação Determinística de Manuais de Rotas e Subrotas.

Verifica:
1. Se todas as views/rotas registradas no frontend (VIEW_CONFIG) possuem manual em docs/manuais/.
2. Se cada manual contém rigorosamente as 6 seções obrigatórias de governança.
3. Se há ausência total de emojis em todos os arquivos de documentação (regra inquebrável).

Uso: python gates/G_MANUAIS_ROTAS.py [repo_root]
Saída: exit 0 (aprovado) ou exit 1 (bloqueado).
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

MANDATORY_SECTIONS = [
    r"##\s*1\.\s*Objetivo",
    r"##\s*2\.\s*O\s*Que\s*o\s*Usu[aá]rio\s*Consegue\s*Realizar",
    r"##\s*3\.\s*Quem\s*Pode\s*Ver\s*e\s*Realizar\s*A[cç][oõ]es",
    r"##\s*4\.\s*Quais\s*A[cç][oõ]es\s*Podem\s*Ser\s*Realizadas",
    r"##\s*5\.\s*Como\s*o\s*Usu[aá]rio\s*Realiza\s*as\s*A[cç][oõ]es",
    r"##\s*6\.\s*O\s*Que\s*Falta\s*Implementar",
]

EMOJI_PATTERN = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)


@dataclass
class GateResult:
    passed: bool
    messages: list[str] = field(default_factory=list)


def scan(repo_root: Path) -> GateResult:
    repo_root = Path(repo_root)
    errors: list[str] = []

    index_html = repo_root / "docs" / "reconstruct_rvops" / "05_reconstructed_app" / "index.html"
    manuais_dir = repo_root / "docs" / "manuais"

    if not manuais_dir.exists():
        return GateResult(passed=False, messages=["Diretório docs/manuais/ não encontrado."])

    # 1. Extrair rotas do frontend
    views_found: list[str] = []
    if index_html.exists():
        content = index_html.read_text(encoding="utf-8")
        block_match = re.search(r"const\s+VIEW_CONFIG\s*=\s*\{(.+?)\n\s*\};", content, re.DOTALL)
        if block_match:
            views_found = re.findall(r"['\"]([a-zA-Z0-9_\-]+)['\"]\s*:\s*\{", block_match.group(1))

    # 2. Auditar arquivos de manuais
    manual_files = list(manuais_dir.glob("*.md"))
    if not manual_files:
        return GateResult(passed=False, messages=["Nenhum arquivo markdown encontrado em docs/manuais/."])

    all_manuals_text: dict[str, str] = {}
    for mf in manual_files:
        try:
            txt = mf.read_text(encoding="utf-8")
            all_manuals_text[mf.name] = txt
        except Exception as exc:
            errors.append(f"{mf.name}: falha ao ler arquivo ({exc})")

        # Verificar ausência de emojis
        emojis = EMOJI_PATTERN.findall(txt)
        if emojis:
            errors.append(f"{mf.name}: contém {len(emojis)} emojis proibidos ({set(emojis)})")

        # Verificar 6 seções obrigatórias (exceto README.md)
        if mf.name != "README.md":
            for sec_regex in MANDATORY_SECTIONS:
                if not re.search(sec_regex, txt, re.IGNORECASE):
                    errors.append(f"{mf.name}: seção obrigatória ausente correspondente a '{sec_regex}'")

    # 3. Garantir cobertura de todas as views do frontend
    combined_text = "\n".join(all_manuals_text.values())
    for view in views_found:
        pattern = rf"(#|'|\"|`){re.escape(view)}('|#|\"|`|\b)"
        if not re.search(pattern, combined_text, re.IGNORECASE):
            errors.append(f"A rota/view '{view}' não foi documentada em nenhum arquivo de docs/manuais/")

    if errors:
        return GateResult(passed=False, messages=errors)
    return GateResult(passed=True, messages=[f"100% das {len(views_found)} rotas cobertas em {len(manual_files)} manuais sem emojis."])


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    repo_root = Path(argv[0]) if argv else Path(__file__).resolve().parent.parent

    result = scan(repo_root)
    if result.passed:
        for msg in result.messages:
            print(f"[G_MANUAIS_ROTAS] PASS: {msg}")
        return 0

    print("[G_MANUAIS_ROTAS] FAIL: Foram encontradas inconformidades na documentação de rotas:")
    for msg in result.messages:
        print(f"  - {msg}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
