# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-06: Validador Ético CFO e Verificador de Registro CRO/UF
"""

import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.features.contacts.cro_validator import (
    validate_cro_syntax,
    verify_cro_status,
    validate_cfo_marketing_compliance,
)


@pytest.fixture
def client():
    return TestClient(app, headers=bearer_headers())


def test_cro_syntax_validation():
    # Validações sintáticas válidas
    res_sp = validate_cro_syntax(cro_number="123456", uf="SP")
    assert res_sp["is_valid"] is True
    assert res_sp["uf"] == "SP"
    assert res_sp["canonical_cro"] == "CRO-SP 123456"
    assert res_sp["category"] == "CD"

    res_pr = validate_cro_syntax(cro_number="CRO-PR 54321", uf="PR")
    assert res_pr["is_valid"] is True
    assert res_pr["clean_number"] == "54321"
    assert res_pr["canonical_cro"] == "CRO-PR 54321"

    # EPAO (Clínica)
    res_epao = validate_cro_syntax(cro_number="EPAO-1234", uf="MG", category="EPAO")
    assert res_epao["is_valid"] is True
    assert res_epao["category"] == "EPAO"
    assert res_epao["canonical_cro"] == "CRO-MG-EPAO 1234"

    # UF Inválida
    res_inv_uf = validate_cro_syntax(cro_number="12345", uf="XX")
    assert res_inv_uf["is_valid"] is False
    assert "UF inválida" in res_inv_uf["error"]

    # Número Inválido / Sem dígitos
    res_inv_num = validate_cro_syntax(cro_number="ABCDEF", uf="SP")
    assert res_inv_num["is_valid"] is False
    assert "Número de CRO inválido" in res_inv_num["error"]


def test_cro_status_verification_and_cache():
    # Verificação de status de profissional ativo
    res = verify_cro_status(cro_number="123456", uf="SP")
    assert res["is_valid"] is True
    assert res["status"] == "ATIVO"
    assert res["verified"] is True
    assert "Dr." in res["professional_name"]

    # Segunda chamada deve atingir o cache
    res_cached = verify_cro_status(cro_number="123456", uf="SP")
    assert res_cached["cached"] is True
    assert res_cached["verified"] is True

    # CRO com situação suspensa / cancelada
    res_susp = verify_cro_status(cro_number="999999", uf="SP")
    assert res_susp["status"] == "SUSPENSO"
    assert res_susp["verified"] is False


def test_cfo_marketing_compliance_scanner():
    # Copy com múltiplas infrações do CFO (Resolução 196/2019 e Código de Ética Art. 44)
    bad_copy = (
        "Implantes dentários com resultado 100% garantido! A melhor clínica de SP, "
        "preço imbatível e tratamento totalmente sem dor. Faça sua consulta grátis e concorra a sorteios!"
    )
    result_bad = validate_cfo_marketing_compliance(text=bad_copy, has_responsible_cro=False)
    assert result_bad["is_compliant"] is False
    assert len(result_bad["violations"]) >= 3
    # Verifica termos identificados
    violations_str = " ".join(result_bad["violations"]).lower()
    assert "garantido" in violations_str or "resultado" in violations_str
    assert "sem dor" in violations_str or "preço" in violations_str or "grátis" in violations_str
    assert "responsável técnico" in violations_str or "cro" in violations_str

    # Copy 100% conforme com responsável técnico explícito
    clean_copy = (
        "Tratamento de reabilitação com implantes osseointegráveis de alta precisão. "
        "Responsável Técnico: Dr. Roberto Guimarães - CRO-SP 123456."
    )
    result_clean = validate_cfo_marketing_compliance(text=clean_copy, has_responsible_cro=True)
    assert result_clean["is_compliant"] is True
    assert len(result_clean["violations"]) == 0


def test_contacts_api_cro_endpoints(client):
    # Endpoint de validação de CRO
    resp_val = client.post("/api/v1/contacts/validate-cro", json={"cro": "CRO-SP 123456", "uf": "SP"})
    assert resp_val.status_code == 200
    data_val = resp_val.json()
    assert data_val["verified"] is True
    assert data_val["canonical_cro"] == "CRO-SP 123456"

    # Endpoint de verificação de conformidade ética CFO
    resp_cfo = client.post("/api/v1/contacts/validate-cfo-compliance", json={
        "text": "Venha fazer seu implante com resultado 100% garantido!",
        "has_responsible_cro": False
    })
    assert resp_cfo.status_code == 200
    data_cfo = resp_cfo.json()
    assert data_cfo["is_compliant"] is False
    assert len(data_cfo["violations"]) > 0

    # Criação de contato com CRO válido marcando cro_verified
    payload_contact = {
        "name": "Dra. Juliana Prado",
        "email": "juliana.prado@odonto.com.br",
        "phone": "+5511988887777",
        "cro": "123456",
        "cro_uf": "SP",
        "specialty": "Implantodontia"
    }
    resp_create = client.post(
        "/api/v1/contacts",
        json=payload_contact,
        headers={"x-user-id": "usr-superadmin-god"}
    )
    assert resp_create.status_code == 201
    created_data = resp_create.json()
    assert created_data["cro"] == "CRO-SP 123456" or "123456" in created_data["cro"]
    assert created_data.get("cro_verified") is True

