# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-15: Fechamento de Propostas e Contratos com Documenso Headless e Assinatura via WhatsApp
"""

import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection
from src.features.deals import documenso_service


@pytest.fixture
def client():
    return TestClient(app, headers=bearer_headers())


def test_documenso_generate_contract_and_pending_status():
    # Setup Deal d-1
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM deal_contracts WHERE deal_id = ?", ("d-1",))
            cur.execute("UPDATE deals SET stage_id = 103 WHERE id = 'd-1'")
        conn.commit()
    finally:
        conn.close()

    # Gera contrato dinâmico para o Deal aprovado
    contract_res = documenso_service.generate_contract_for_deal(
        deal_id="d-1",
        contract_type="fornecimento_implantes",
        signer_name="Dr. Roberto Silveira",
        signer_email="roberto@grupoalfa.med.br",
        signer_phone="+5531996547890",
        account_id="0f14ffff"
    )

    assert contract_res["status"] == "PENDING_SIGNATURE"
    assert contract_res["deal_id"] == "d-1"
    assert "contracts/d-1/proposal_original.pdf" in contract_res["original_pdf_r2_key"]
    assert "https://documenso.revnaut.internal/sign/" in contract_res["signing_url"]

    # Valida persistência em deal_contracts
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, status, original_pdf_r2_key FROM deal_contracts WHERE deal_id = ?", ("d-1",))
        row = cur.fetchone()
        assert row is not None
        assert row["status"] == "PENDING_SIGNATURE"
    finally:
        conn.close()


def test_documenso_webhook_moves_deal_to_won_and_records_sha256():
    # Cria contrato prévio pendente de assinatura
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM deal_contracts WHERE deal_id = ?", ("d-1",))
            cur.execute("UPDATE deals SET stage_id = 104 WHERE id = 'd-1'")
            cur.execute("""
                INSERT INTO deal_contracts (
                    id, account_id, deal_id, documenso_document_id, title,
                    contract_type, status, original_pdf_r2_key, signer_name
                ) VALUES (
                    'cntr-test-15', '0f14ffff', 'd-1', 'doc_documenso_9911',
                    'Contrato Fornecimento Implantes CM', 'fornecimento_implantes',
                    'PENDING_SIGNATURE', 'contracts/d-1/proposal_original.pdf', 'Dr. Roberto Silveira'
                )
            """)
        conn.commit()
    finally:
        conn.close()

    # Webhook DOCUMENT_COMPLETED do Documenso
    webhook_payload = {
        "event": "DOCUMENT_COMPLETED",
        "data": {
            "id": "doc_documenso_9911",
            "title": "Contrato Fornecimento Implantes CM",
            "status": "COMPLETED",
            "recipients": [
                {
                    "name": "Dr. Roberto Silveira",
                    "email": "roberto@grupoalfa.med.br",
                    "signedAt": "2026-10-17T22:00:00Z"
                }
            ],
            "meta": {
                "deal_id": "d-1"
            }
        }
    }

    result = documenso_service.handle_documenso_webhook(webhook_payload)
    assert result["success"] is True
    assert result["deal_id"] == "d-1"
    assert result["contract_status"] == "SIGNED"
    assert result["new_stage_id"] == 105
    assert len(result["sha256_hash"]) == 64

    # Valida que o Deal foi automaticamente movido para Fechado & Ganho (stage 105)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT stage_id FROM deals WHERE id = 'd-1'")
        deal_row = cur.fetchone()
        assert deal_row["stage_id"] == 105

        # Valida atualização do contrato com chave R2 e hash criptográfico
        cur.execute("SELECT status, sha256_hash, signed_pdf_r2_key FROM deal_contracts WHERE deal_id = ?", ("d-1",))
        c_row = cur.fetchone()
        assert c_row["status"] == "SIGNED"
        assert c_row["sha256_hash"] == result["sha256_hash"]
        assert "contracts/d-1/signed_contract.pdf" in c_row["signed_pdf_r2_key"]
    finally:
        conn.close()


def test_documenso_api_endpoints(client):
    # 1. Gerar contrato via API
    gen_req = {
        "deal_id": "d-1",
        "contract_type": "termo_consignacao",
        "signer_name": "Dra. Patricia Neves",
        "signer_email": "patricia.neves@odonto.com.br",
        "signer_phone": "+552199881122"
    }
    res_gen = client.post("/api/v1/deals/d-1/generate-contract", json=gen_req)
    assert res_gen.status_code == 200
    gen_data = res_gen.json()
    assert gen_data["status"] == "PENDING_SIGNATURE"
    assert "signing_url" in gen_data

    # 2. Listar contratos do Deal
    res_list = client.get("/api/v1/deals/d-1/contracts")
    assert res_list.status_code == 200
    contracts_list = res_list.json()
    assert isinstance(contracts_list, list)
    assert len(contracts_list) >= 1

    # 3. Disparar webhook de conclusão via API
    doc_id = gen_data["documenso_document_id"]
    webhook_req = {
        "event": "DOCUMENT_COMPLETED",
        "data": {
            "id": doc_id,
            "status": "COMPLETED",
            "meta": {"deal_id": "d-1"}
        }
    }
    res_hook = client.post("/api/v1/webhooks/documenso/document-completed", json=webhook_req)
    assert res_hook.status_code == 200
    hook_data = res_hook.json()
    assert hook_data["success"] is True
    assert hook_data["new_stage_id"] == 105
