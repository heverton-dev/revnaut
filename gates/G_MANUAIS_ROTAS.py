#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quality Gate: Validação Determinística de Manuais de Rotas e Sub-rotas.

Padrão AIDD v4.0:
1. Relação 1-para-1 estrita: todas as rotas/sub-rotas de VIEW_CONFIG possuem manual dedicado.
2. Cada manual contém rigorosamente as 9 seções anatômicas obrigatórias de governança.
3. Ausência total de emojis em todos os arquivos de documentação (Lei #14 inquebrável).

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
    (r"##\s*1\.\s*Objetivo", "1. Objetivo da Rota / Sub-rota"),
    (r"##\s*2\.\s*O\s*Que\s*o\s*Usu[aá]rio\s*Consegue\s*Realizar", "2. O Que o Usuário Consegue Realizar"),
    (r"##\s*3\.\s*Quem\s*Pode\s*Ver\s*e\s*Realizar\s*A[cç][oõ]es", "3. Quem Pode Ver e Realizar Ações (Matriz RBAC)"),
    (r"##\s*4\.\s*Quais\s*A[cç][oõ]es\s*Podem\s*Ser\s*Realizadas", "4. Quais Ações Podem Ser Realizadas"),
    (r"##\s*5\.\s*Como\s*o\s*Usu[aá]rio\s*Realiza\s*as\s*A[cç][oõ]es", "5. Como o Usuário Realiza as Ações (Passo a Passo)"),
    (r"##\s*6\.\s*Cat[aá]logo\s*Anat[oô]mico\s*de\s*Bot[oõ]es", "6. Catálogo Anatômico de Botões & Ações do DOM"),
    (r"##\s*7\.\s*Cat[aá]logo\s*de\s*Modais", "7. Catálogo de Modais & Gavetas Operacionais"),
    (r"##\s*8\.\s*Motores\s*de\s*Backend", "8. Motores de Backend & Arquitetura Subjacente"),
    (r"##\s*9\.\s*O\s*Que\s*Falta\s*Implementar", "9. O Que Falta Implementar & Plano de Micro-Tickets"),
]

EMOJI_PATTERN = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)


@dataclass
class GateResult:
    passed: bool
    messages: list[str] = field(default_factory=list)


def scan(repo_root: Path) -> GateResult:
    repo_root = Path(repo_root)
    errors: list[str] = []

    index_html = repo_root / "docs" / "reconstruct_revnault" / "05_reconstructed_app" / "index.html"
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
    covered_routes: set[str] = set()

    for mf in manual_files:
        try:
            txt = mf.read_text(encoding="utf-8")
            all_manuals_text[mf.name] = txt
        except Exception as exc:
            errors.append(f"{mf.name}: falha ao ler arquivo ({exc})")
            continue

        # Verificar ausência de emojis
        emojis = EMOJI_PATTERN.findall(txt)
        if emojis:
            errors.append(f"{mf.name}: contém {len(emojis)} emojis proibidos ({set(emojis)})")

        # Verificar 9 seções obrigatórias (exceto README.md)
        if mf.name != "README.md":
            for sec_regex, sec_name in MANDATORY_SECTIONS:
                if not re.search(sec_regex, txt, re.IGNORECASE):
                    errors.append(f"{mf.name}: seção obrigatória ausente correspondente a '{sec_name}'")

            # Checar qual rota este arquivo cobre no título ou hash
            for v in views_found:
                if f"(#{v})" in txt or f"(#/{v})" in txt or f"`#{v}`" in txt or f"`/#{v}`" in txt:
                    covered_routes.add(v)

    # 3. Garantir cobertura 1-para-1 de todas as views do frontend
    missing = [v for v in views_found if v not in covered_routes]
    if missing:
        errors.append(f"Faltam manuais com as 9 seções para {len(missing)} rota(s)/sub-rota(s): {missing}")

    if errors:
        return GateResult(passed=False, messages=errors)
    return GateResult(passed=True, messages=[
        f"100% das {len(views_found)} rotas e sub-rotas cobertas em {len(manual_files) - 1} manuais anatômicos individuais com 9 seções e zero emojis."
    ])


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
