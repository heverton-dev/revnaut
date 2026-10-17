# -*- coding: utf-8 -*-
"""
Teste de Contrato & Sincronização Tipada (TICKET-04)
Valida que 100% dos endpoints /api/v1/* possuem response_model tipado em Pydantic
e que api_contracts.ts contém todos os contratos canônicos do Revnaut Dental Ops.
"""

import subprocess
import sys
from pathlib import Path
from pydantic import BaseModel
from src.main import app


def test_api_routes_have_typed_response_models():
    """Garante que nenhum endpoint da API v1 retorne dict sem schema/response_model."""
    unmodeled_routes = []
    total_api_v1_routes = 0

    # Percorre todas as rotas registradas no FastAPI
    all_routes = []
    for route in app.routes:
        if hasattr(route, "path") and route.path.startswith("/api/v1"):
            all_routes.append(route)
        elif hasattr(route, "original_router"):
            for sub_route in route.original_router.routes:
                if hasattr(sub_route, "path") and sub_route.path.startswith("/api/v1"):
                    all_routes.append(sub_route)

    for r in all_routes:
        # Exceção para downloads binários/arquivos text/csv
        if r.path.endswith("/export/csv"):
            continue

        total_api_v1_routes += 1

        resp_model = getattr(r, "response_model", None)
        if resp_model is None:
            unmodeled_routes.append((r.path, r.methods))

    assert len(unmodeled_routes) == 0, f"Rotas sem response_model tipado: {unmodeled_routes}"
    assert total_api_v1_routes >= 25, f"Esperado ao menos 25 rotas tipadas, encontrado {total_api_v1_routes}"


def test_api_contracts_ts_contains_dental_contracts():
    """Valida se api_contracts.ts contém os tipos do domínio Revnaut Dental Ops."""
    contracts_path = Path(__file__).resolve().parent.parent / "docs" / "reconstruct_rvops" / "02_decompiled" / "api_contracts.ts"
    assert contracts_path.exists(), "api_contracts.ts não encontrado"

    content = contracts_path.read_text(encoding="utf-8")
    required_contracts = [
        "UserContext",
        "DataScopeEnum",
        "DentalContact",
        "ConsignmentBox",
        "TotvsOrderPayload",
        "HierarchyPreset"
    ]
    for contract in required_contracts:
        assert contract in content, f"Contrato '{contract}' ausente em api_contracts.ts"


def test_quality_gate_g_contracts_passes():
    """Executa o quality gate determinístico G_CONTRACTS."""
    root_dir = Path(__file__).resolve().parent.parent
    gate_script = root_dir / "gates" / "G_CONTRACTS.py"
    res = subprocess.run([sys.executable, str(gate_script), str(root_dir)], capture_output=True, text=True)
    assert res.returncode == 0, f"G_CONTRACTS falhou: {res.stderr}\n{res.stdout}"
