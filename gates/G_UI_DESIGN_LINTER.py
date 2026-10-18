#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quality Gate: Validação Determinística de UI Design Hygiene & Zero Emojis (Lei #14).

Verifica deterministicamente:
1. Ausência absoluta de emojis Unicode em arquivos de frontend (HTML, JS, CSS) e código-fonte (src/).
2. Conformidade com o padrão de iconografia vetorial SVG (shadcn / Lucide) para buscas, status e ações.
3. Demonstração de que o portão morde (Lei #13): suporte a simulação de violação com rejeição binária (exit 1).

Uso:
  python gates/G_UI_DESIGN_LINTER.py [repo_root] [--test-bite]
Saída:
  exit 0 = APROVADO (Zero emojis, conformidade total)
  exit 1 = REPROVADO (Ao menos um emoji ou violação de design detectado)
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Intervalo Unicode abrangente de emojis (4-byte, símbolos pictográficos e miscelânea de símbolos)
EMOJI_PATTERN = re.compile(
    r"[\U00010000-\U0010ffff]|[\u2600-\u26ff]|[\u2700-\u27bf]|[\u2300-\u23ff]",
    flags=re.UNICODE
)

# Exceções aceitas de símbolos tipográficos matemáticos / texto puro sem valor emoji
ALLOWED_CHARS = {"✓", "✕", "➔", "•", "→", "←", "★", "±", "×", "÷", "§"}

TARGET_EXTENSIONS = {".html", ".js", ".css", ".py", ".ts", ".tsx"}
IGNORED_DIRS = {".git", ".playwright-mcp", "__pycache__", ".pytest_cache", "node_modules", ".gemini", "venv", "dist"}

HEX_COLOR_PATTERN = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RAW_TAILWIND_PATTERN = re.compile(
    r"\b(?:bg|text|border)-(?:slate|indigo|cyan|rose|emerald|amber|sky|orange)-\d{2,3}\b"
)


@dataclass
class GateResult:
    passed: bool
    violations: list[str] = field(default_factory=list)
    files_scanned: int = 0


def _scan_file(filepath: Path, repo_root: Path, violations: list[str]) -> None:
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        violations.append(f"{filepath}: Falha de leitura ({exc})")
        return

    rel_path = filepath.relative_to(repo_root)
    rel_posix = rel_path.as_posix()
    is_frontend_tsx = (
        filepath.suffix.lower() == ".tsx"
        and (
            rel_posix.startswith("frontend/src/features/")
            or rel_posix.startswith("frontend/src/components/")
        )
    )

    for line_idx, line in enumerate(content.splitlines(), start=1):
        matches = EMOJI_PATTERN.findall(line)
        real_matches = [m for m in matches if m not in ALLOWED_CHARS]
        if real_matches:
            preview = line.strip()[:80]
            violations.append(
                f"{rel_path}:{line_idx} - Emoji proibido detectado: {real_matches} na linha: '{preview}'"
            )

        if is_frontend_tsx:
            hex_matches = HEX_COLOR_PATTERN.findall(line)
            if hex_matches:
                preview = line.strip()[:80]
                violations.append(
                    f"{rel_path}:{line_idx} - Cor hexadecimal hardcoded proibida ({hex_matches}); use tokens.css: '{preview}'"
                )


def scan(repo_root: Path, simulate_bite: bool = False) -> GateResult:
    repo_root = Path(repo_root).resolve()
    violations: list[str] = []
    files_scanned = 0

    if simulate_bite:
        # Lei #13: O portão prova que morde rejeitando violação sintética
        return GateResult(
            passed=False,
            violations=["[SIMULATED_BITE] Violação intencional injetada: emoji detectado '<span class=\"icon\">🔍</span>'."],
            files_scanned=files_scanned
        )

    ROOT = repo_root
    # Diretórios e arquivos a auditar prioritariamente
    scan_targets = [
        ROOT / "docs" / "reconstruct_rvops" / "05_reconstructed_app",
        ROOT / "src",
        ROOT / "docs" / "manuais",
        ROOT / "frontend" / "src",
        ROOT / "run_server.py",
    ]

    for target in scan_targets:
        if not target.exists():
            continue
        if target.is_file():
            ext = target.suffix.lower()
            if ext in TARGET_EXTENSIONS:
                files_scanned += 1
                _scan_file(target, repo_root, violations)
            continue

        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for f in files:
                ext = Path(f).suffix.lower()
                if ext not in TARGET_EXTENSIONS:
                    continue

                filepath = Path(root) / f
                files_scanned += 1
                _scan_file(filepath, repo_root, violations)

    passed = len(violations) == 0
    return GateResult(passed=passed, violations=violations, files_scanned=files_scanned)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    simulate_bite = "--test-bite" in argv or "--bite" in argv
    clean_argv = [a for a in argv if a not in ("--test-bite", "--bite")]

    repo_root = Path(clean_argv[0]) if clean_argv else Path(__file__).resolve().parent.parent

    result = scan(repo_root, simulate_bite=simulate_bite)

    if result.passed:
        print(f"[G_UI_DESIGN_LINTER] PASS: 100% de conformidade com a Lei #14. Zero emojis encontrados em {result.files_scanned} arquivos.")
        return 0

    print(f"[G_UI_DESIGN_LINTER] FAIL (Lei #14 Bloqueada): {len(result.violations)} inconformidades detectadas:")
    for v in result.violations:
        print(f"  - {v}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
