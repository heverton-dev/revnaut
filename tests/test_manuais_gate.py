# -*- coding: utf-8 -*-
"""
Testes automatizados para validação do Quality Gate G_MANUAIS_ROTAS
e da exposição dinâmica dos manuais em /docs/guia e /api/v1/quarteto/manuais.
"""

from pathlib import Path
from fastapi.testclient import TestClient
from src.main import app
from gates.G_MANUAIS_ROTAS import scan

client = TestClient(app)
REPO_ROOT = Path(__file__).resolve().parent.parent


def test_gate_manuais_rotas_passes():
    """Valida se o Quality Gate passa com exit 0 para o repositório atual."""
    result = scan(REPO_ROOT)
    assert result.passed is True
    assert len(result.messages) > 0
    assert "100% das" in result.messages[0]


def test_api_quarteto_manuais_list_and_detail():
    """Valida se os endpoints de manuais retornam o catálogo em JSON."""
    res = client.get("/api/v1/quarteto/manuais")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert data["total"] >= 14
    assert "manuals" in data
    
    # Testar detalhe de um manual específico
    detail_res = client.get("/api/v1/quarteto/manuais/00_autenticacao_login.md")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["filename"] == "00_autenticacao_login.md"
    assert "Manual da Rota: Autenticação" in detail["content"]


def test_docs_guia_renders_dynamic_html():
    """Valida se /docs/guia responde com 200 e carrega a interface de documentação."""
    res = client.get("/docs/guia?manual=01_comercial_vendas_funis.md")
    assert res.status_code == 200
    html = res.text
    assert "Central de Manuais & Guia Operacional" in html
    assert "01_comercial_vendas_funis.md" in html
    assert "marked.js" in html
