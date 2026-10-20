# -*- coding: utf-8 -*-
"""
Teste de Contrato & Sincronização Tipada 1:1 (TICKET-04 & TICKET-41)
Valida que:
1. 100% dos endpoints /api/v1/* possuem response_model tipado em Pydantic.
2. frontend/src/types/api_contracts.ts e docs/reconstruct_rvops/02_decompiled/api_contracts.ts são 100% idênticos.
3. Todas as rotas /api/v1/* registradas em src.main:app estão declaradas em API_V1_ROUTES dentro de api_contracts.ts.
4. O gate G_CONTRACTS passa sem erros.
"""

import subprocess
import sys
from pathlib import Path
from src.main import app


def _collect_all_api_v1_routes():
    all_routes = []
    for route in app.routes:
        if hasattr(route, "path") and route.path.startswith("/api/v1"):
            all_routes.append(route)
        elif hasattr(route, "original_router"):
            for sub_route in route.original_router.routes:
                if hasattr(sub_route, "path") and sub_route.path.startswith("/api/v1"):
                    all_routes.append(sub_route)
    return all_routes


def test_api_routes_have_typed_response_models():
    """Garante que nenhum endpoint da API v1 retorne dict sem schema/response_model."""
    unmodeled_routes = []
    total_api_v1_routes = 0

    for r in _collect_all_api_v1_routes():
        if r.path.endswith("/export/csv") or r.path.endswith("/export") or "/storage/files/" in r.path:
            continue
        total_api_v1_routes += 1
        resp_model = getattr(r, "response_model", None)
        if resp_model is None:
            unmodeled_routes.append((r.path, r.methods))

    assert len(unmodeled_routes) == 0, f"Rotas sem response_model tipado: {unmodeled_routes}"
    assert total_api_v1_routes >= 150, f"Esperado ao menos 150 rotas tipadas, encontrado {total_api_v1_routes}"


def test_api_contracts_ts_1_to_1_sync_and_domain_contracts():
    """Valida sincronia 1:1 entre os arquivos api_contracts.ts e cobertura de 100% das rotas /api/v1/*."""
    root_dir = Path(__file__).resolve().parent.parent
    decompiled_contracts = root_dir / "docs" / "reconstruct_rvops" / "02_decompiled" / "api_contracts.ts"
    frontend_contracts = root_dir / "frontend" / "src" / "types" / "api_contracts.ts"

    assert decompiled_contracts.exists(), "docs/reconstruct_rvops/02_decompiled/api_contracts.ts não encontrado"
    assert frontend_contracts.exists(), "frontend/src/types/api_contracts.ts não encontrado"

    decompiled_text = decompiled_contracts.read_text(encoding="utf-8")
    frontend_text = frontend_contracts.read_text(encoding="utf-8")

    assert decompiled_text == frontend_text, (
        "Divergência detectada entre frontend/src/types/api_contracts.ts e "
        "docs/reconstruct_rvops/02_decompiled/api_contracts.ts"
    )

    required_contracts = [
        "UserContext",
        "DataScopeEnum",
        "DentalContact",
        "ConsignmentBox",
        "TotvsOrderPayload",
        "HierarchyPreset",
        "PresignedUploadResponse",
        "VaultCredentialContract",
        "CroVerificationContract",
        "LandingPageContract",
        "ScoringRuleContract",
        "ScoringHistoryContract",
        "LiveKitRoomTokenContract",
        "MeetingIntelligenceExtraction",
        "CatalogProduct",
        "PriceTable",
        "ProposalPricingResult",
        "DocumensoContractRecord",
        "KeyPartnersAgreement",
        "KeyPartnersSurgicalOrder",
        "KolContract",
        "DentgoHub",
        "DentgoOrderContract",
        "DentgoFinancialSplit",
        "SurgicalSosTicket",
        "AnvisaRmaClaim",
        "SupersetGuestTokenContract",
        "PredictiveSokResult",
        "PredictivePrResult",
        "ClinicalProcedureMargin",
        "SurgicalHealthScoreHsc",
        "LoyaltyWallet",
        "ErpFiscalInvoice",
        "ImagingStudy",
        "ImagingStudyViewerSession",
        "WebhookSubscription",
        "WebhookDeliveryLog",
        "API_V1_ROUTES",
    ]
    for contract in required_contracts:
        assert contract in frontend_text, f"Contrato '{contract}' ausente em api_contracts.ts"

    # Inspeciona dinamicamente todas as rotas /api/v1/* de src.main:app
    registered_paths = sorted({r.path for r in _collect_all_api_v1_routes()})
    missing_paths = [p for p in registered_paths if f"'{p}'" not in frontend_text and f'"{p}"' not in frontend_text]
    assert len(missing_paths) == 0, f"Rotas /api/v1/* ausentes em api_contracts.ts: {missing_paths}"


def test_quality_gate_g_contracts_passes():
    """Executa o quality gate determinístico G_CONTRACTS."""
    root_dir = Path(__file__).resolve().parent.parent
    gate_script = root_dir / "gates" / "G_CONTRACTS.py"
    res = subprocess.run([sys.executable, str(gate_script), str(root_dir)], capture_output=True, text=True)
    assert res.returncode == 0, f"G_CONTRACTS falhou: {res.stderr}\n{res.stdout}"
