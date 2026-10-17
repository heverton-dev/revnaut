#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Linter de Design Tokens & UI Hygiene (AIDD Skill aidd-linter-design).

Garante:
1. Zero Emojis & UI Design Hygiene (Lei #14): Nenhum emoji Unicode em interface ou código.
2. Iconografia canônica vetorial SVG inline (shadcn / Lucide) para buscas e status.
3. Teste de portão que morde (Lei #13): flag `--bite` ou `--test-bite`.

Uso:
  python scripts/lint_design_tokens.py [--audit | --strict | --bite | --fix]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from gates.G_UI_DESIGN_LINTER import scan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Linter de Design Tokens e UI Hygiene do AIDD.")
    parser.add_argument("--audit", action="store_true", help="Audita arquivos principais de UI.")
    parser.add_argument("--strict", action="store_true", help="Audita todo o repositório em modo estrito.")
    parser.add_argument("--bite", "--test-bite", dest="bite", action="store_true", help="Prova que o portão morde (Lei #13).")
    parser.add_argument("--fix", action="store_true", help="Sugere correção para violações encontradas.")

    args = parser.parse_args(argv)

    print("========================================================================")
    print(" [AIDD-LINTER-DESIGN] Auditoria de Design Tokens & UI Hygiene (Lei #14)")
    print("========================================================================")

    result = scan(REPO_ROOT, simulate_bite=args.bite)

    if result.passed:
        print(f"[OK] 100% em conformidade com as Leis de Design AIDD.")
        print(f"     Arquivos auditados: {result.files_scanned}")
        print(f"     Emojis Unicode detectados: 0")
        print("========================================================================")
        return 0

    print(f"[BLOQUEADO] Violações detectadas ({len(result.violations)} ocorrências):")
    for v in result.violations:
        print(f"  ❌ {v}")
    print("========================================================================")
    return 1


if __name__ == "__main__":
    sys.exit(main())
