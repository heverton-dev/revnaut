# -*- coding: utf-8 -*-
"""
Testes Unitarios do Quality Gate G_PARIDADE_TELA_CONTRATO (Leis #1, #2, #13, #14).
Valida que o gate passa (exit 0) em pares validos e falha categoricamente (exit 1)
diante de chamadas fantasmas 404, metodos 405, endpoints orfaos e mocks de Math.random().
"""

from pathlib import Path
import tempfile
import pytest

from gates.G_PARIDADE_TELA_CONTRATO import (
    scan,
    parse_backend_routes,
    extract_frontend_calls,
    check_ui_hygiene_mocks,
    main,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_gate_real_repository_check_broken():
    """Valida que no modo --check-broken o repositorio atual processa sem erros inesperados."""
    result = scan(REPO_ROOT, check_broken=True, strict_orphans=False)
    assert result.passed is True
    assert len(result.broken_calls) == 0


def test_gate_detects_synthetic_404_ghost_route():
    """Lei #13: Prova que o gate morde (exit 1) ao detectar chamada 404 para rota inexistente."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "router.py").write_text(
            """
from fastapi import APIRouter
router = APIRouter(prefix="/api/v1/users")
@router.get("/list")
def list_users():
    return []
""",
            encoding="utf-8",
        )

        fe_dir = tmp_path / "frontend" / "src"
        fe_dir.mkdir(parents=True)
        (fe_dir / "Component.tsx").write_text(
            """
export function Component() {
    const load = async () => {
        await fetch("/api/v1/users/non-existent-ghost-route");
    };
    return null;
}
""",
            encoding="utf-8",
        )

        result = scan(tmp_path, check_broken=False, strict_orphans=False)
        assert result.passed is False
        assert len(result.broken_calls) == 1
        assert "404 GHOST ROUTE" in result.broken_calls[0]


def test_gate_detects_synthetic_405_method_not_allowed():
    """Lei #13: Prova que o gate morde (exit 1) ao detectar chamada com metodo HTTP incompativel."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "router.py").write_text(
            """
from fastapi import APIRouter
router = APIRouter(prefix="/api/v1/items")
@router.get("/all")
def get_items():
    return []
""",
            encoding="utf-8",
        )

        fe_dir = tmp_path / "frontend" / "src"
        fe_dir.mkdir(parents=True)
        (fe_dir / "Component.tsx").write_text(
            """
export function Component() {
    const postItem = async () => {
        await fetch("/api/v1/items/all", { method: "POST" });
    };
    return null;
}
""",
            encoding="utf-8",
        )

        result = scan(tmp_path, check_broken=False, strict_orphans=False)
        assert result.passed is False
        assert len(result.broken_calls) == 1
        assert "405 METHOD NOT ALLOWED" in result.broken_calls[0]


def test_gate_detects_synthetic_orphan_endpoint():
    """Lei #13: Prova que o gate morde (exit 1) quando endpoint backend nao possui consumidor na UI."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "router.py").write_text(
            """
from fastapi import APIRouter
router = APIRouter(prefix="/api/v1/reports")
@router.get("/orphan-uncalled-report")
def orphan_report():
    return {"status": "orphan"}
""",
            encoding="utf-8",
        )

        fe_dir = tmp_path / "frontend" / "src"
        fe_dir.mkdir(parents=True)
        (fe_dir / "Component.tsx").write_text(
            """
export function Component() {
    return null;
}
""",
            encoding="utf-8",
        )

        result = scan(tmp_path, check_broken=False, strict_orphans=True)
        assert result.passed is False
        assert len(result.orphan_endpoints) == 1
        assert "ORPHAN ENDPOINT" in result.orphan_endpoints[0]


def test_gate_detects_synthetic_math_random_mock():
    """Lei #13: Prova que o gate morde (exit 1) ao detectar Math.random() para segredos/tokens."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        fe_dir = tmp_path / "frontend" / "src" / "features"
        fe_dir.mkdir(parents=True)
        (fe_dir / "Vault.tsx").write_text(
            """
export function Vault() {
    const generateToken = () => {
        const guestToken = "tok_" + Math.random().toString(36);
        return guestToken;
    };
    return null;
}
""",
            encoding="utf-8",
        )

        violations = check_ui_hygiene_mocks(tmp_path / "frontend" / "src")
        assert len(violations) == 1
        assert "Math.random() proibido para geracao de token/secret" in violations[0]


def test_gate_detects_synthetic_clinical_fallback_mock():
    """Lei #13: Prova que o gate morde (exit 1) ao detectar fallback clinico hardcoded em catch/else."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        fe_dir = tmp_path / "frontend" / "src" / "features"
        fe_dir.mkdir(parents=True)
        (fe_dir / "Copilot.tsx").write_text(
            """
export function Copilot() {
    const handleCopilot = () => {
        try {
            // call
        } catch {
            setCopilotSummary("Resumo Clínico: Implante 3.5x11.5mm posicionado no dente 36");
        }
    };
    return null;
}
""",
            encoding="utf-8",
        )

        violations = check_ui_hygiene_mocks(tmp_path / "frontend" / "src")
        assert len(violations) == 1
        assert "Fallback clinico hardcoded proibido em catch/else" in violations[0]


def test_gate_main_cli_returns_binary_exit_codes():
    """Lei #2: Valida que a execucao por CLI retorna estritamente 0 ou 1."""
    code = main(["--check-broken", str(REPO_ROOT)])
    assert code == 0
