# -*- coding: utf-8 -*-
"""Testes Automatizados de UI Design Hygiene & Quality Gate de Zero Emojis (Lei #14).

Invariantes Validadas:
1. Lei #14 (Zero Emojis): Proibição absoluta de emojis Unicode em código e frontend.
2. Lei #13 (O Portão Deve Provar que Morde): Rejeição binária imediata com exit 1 e falha do gate.
3. Conformidade total do ecossistema de templates e views com iconografia vetorial SVG.
"""

from pathlib import Path
from gates.G_UI_DESIGN_LINTER import scan, EMOJI_PATTERN, ALLOWED_CHARS

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_gate_ui_design_hygiene_passes():
    """Valida se o Quality Gate G_UI_DESIGN_LINTER passa com 100% de conformidade."""
    result = scan(REPO_ROOT, simulate_bite=False)
    assert result.passed is True, f"Violações de UI/Emojis detectadas: {result.violations}"
    assert len(result.violations) == 0
    assert result.files_scanned > 0


def test_gate_ui_design_hygiene_proves_it_bites():
    """Valida a Lei #13: O Quality Gate DEVE falhar (morder) quando uma violação é injetada."""
    result = scan(REPO_ROOT, simulate_bite=True)
    assert result.passed is False
    assert len(result.violations) > 0
    assert "Violação intencional injetada" in result.violations[0]


def test_zero_emojis_in_frontend_app():
    """Verifica individualmente o index.html e arquivos do frontend quanto a emojis proibidos."""
    frontend_dir = REPO_ROOT / "docs" / "reconstruct_revnault" / "05_reconstructed_app"
    assert frontend_dir.exists()

    for file_ext in ("*.html", "*.js", "*.css"):
        for filepath in frontend_dir.glob(file_ext):
            content = filepath.read_text(encoding="utf-8", errors="ignore")
            for line_idx, line in enumerate(content.splitlines(), start=1):
                raw_matches = EMOJI_PATTERN.findall(line)
                real_emojis = [m for m in raw_matches if m not in ALLOWED_CHARS]
                assert not real_emojis, (
                    f"Emoji proibido {real_emojis} detectado em {filepath.name}:{line_idx} -> '{line.strip()[:60]}'"
                )


def test_zero_emojis_in_backend_src():
    """Verifica que o backend (src/) não injeta emojis em títulos, rotas ou templates."""
    src_dir = REPO_ROOT / "src"
    assert src_dir.exists()

    for py_file in src_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        for line_idx, line in enumerate(content.splitlines(), start=1):
            raw_matches = EMOJI_PATTERN.findall(line)
            real_emojis = [m for m in raw_matches if m not in ALLOWED_CHARS]
            assert not real_emojis, (
                f"Emoji proibido {real_emojis} detectado em {py_file.name}:{line_idx} -> '{line.strip()[:60]}'"
            )
