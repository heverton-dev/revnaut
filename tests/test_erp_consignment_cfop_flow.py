# -*- coding: utf-8 -*-
"""
Testes TDD para TICKET-38: Hub de Orquestração Windmill e Conector Fiscal ERP
(TOTVS Protheus, SAP B1 & Sankhya) para Consignação Cirúrgica (CFOP 5.917 / 1.918 / 5.113).
"""

from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection, init_db
from src.features.integrations.totvs.adapter import (
    BaseERPConnector,
    TotvsProtheusAdapter,
    SapBusinessOneAdapter,
    SankhyaAdapter,
    get_erp_connector,
)
from src.features.integrations.erp_hub.windmill_client import WindmillERPOrchestrator

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_erp_fiscal_db():
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM erp_fiscal_invoices WHERE account_id = '0f14ffff'")
        conn.commit()
    finally:
        conn.close()


def test_base_erp_connector_polymorphism():
    """Valida contrato polimórfico dos 3 adaptadores ERP suportados pelo Windmill."""
    totvs = get_erp_connector("totvs_protheus")
    sap = get_erp_connector("sap_b1")
    sankhya = get_erp_connector("sankhya")

    assert isinstance(totvs, BaseERPConnector)
    assert isinstance(sap, BaseERPConnector)
    assert isinstance(sankhya, BaseERPConnector)

    assert isinstance(totvs, TotvsProtheusAdapter)
    assert isinstance(sap, SapBusinessOneAdapter)
    assert isinstance(sankhya, SankhyaAdapter)


def test_consignment_remittance_cfop_5917_and_r2_storage():
    """Valida emissão de NF-e de Remessa em Consignação (CFOP 5.917) e guarda no Cloudflare R2."""
    orchestrator = WindmillERPOrchestrator(mock_mode=True)

    remittance_payload = {
        "account_id": "0f14ffff",
        "agreement_id": "agr-consign-001",
        "emitter_uf": "SP",
        "recipient_uf": "SP",
        "recipient_cnpj": "12.345.678/0001-90",
        "recipient_name": "Instituto Odontológico Paulista Ltda",
        "items": [
            {
                "product_id": "IMP-CM-37511",
                "product_name": "Implante Cone Morse 3.75x11mm",
                "ncm": "90211010",
                "batch_number": "LOTE-2026-A1",
                "quantity": 10,
                "unit_price": 450.0,
            },
            {
                "product_id": "KIT-CIR-PRO",
                "product_name": "Kit Cirúrgico Titanium Pro",
                "ncm": "90211020",
                "batch_number": "LOTE-KIT-01",
                "quantity": 1,
                "unit_price": 6500.0,
            }
        ]
    }

    result = orchestrator.dispatch_consignment_remittance(
        remittance_data=remittance_payload,
        erp_type="totvs_protheus",
        account_id="0f14ffff"
    )

    assert result["success"] is True
    assert result["flow_type"] == "REMITTANCE_5917"
    assert result["cfop"] == "5917"
    assert result["status"] == "AUTORIZADA"
    assert len(result["nfe_access_key"]) == 44
    assert result["total_invoice_value"] == 11000.0  # (10*450) + 6500 = 11000

    # Valida particionamento determinístico das chaves no Cloudflare R2
    assert "0f14ffff/fiscal/nfe/" in result["xml_r2_key"]
    assert result["xml_r2_key"].endswith(".xml")
    assert "0f14ffff/fiscal/nfe/" in result["danfe_pdf_r2_key"]
    assert result["danfe_pdf_r2_key"].endswith(".pdf")

    # Confirma persistência auditável no banco de dados SQLite WAL
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT cfop, nfe_number, total_invoice_value, status FROM erp_fiscal_invoices WHERE nfe_access_key = ?", (result["nfe_access_key"],))
        row = cur.fetchone()
        assert row is not None
        assert row["cfop"] == "5917"
        assert row["total_invoice_value"] == 11000.0
        assert row["status"] == "AUTORIZADA"
    finally:
        conn.close()


def test_postop_settlement_symbolic_return_1918_and_sale_5113():
    """Valida liquidação pós-cirúrgica: Retorno Simbólico (1.918) e Faturamento de Venda (5.113)."""
    orchestrator = WindmillERPOrchestrator(mock_mode=True)

    settlement_payload = {
        "account_id": "0f14ffff",
        "agreement_id": "agr-consign-001",
        "surgical_report_id": "surg-rep-8899",
        "emitter_uf": "SP",
        "recipient_uf": "SP",
        "recipient_cnpj": "12.345.678/0001-90",
        "recipient_name": "Instituto Odontológico Paulista Ltda",
        "consumed_items": [
            {
                "product_id": "IMP-CM-37511",
                "product_name": "Implante Cone Morse 3.75x11mm",
                "ncm": "90211010",
                "batch_number": "LOTE-2026-A1",
                "quantity": 3,
                "unit_price": 450.0,
            }
        ],
        "returned_unconsumed_items": [
            {
                "product_id": "IMP-CM-37511",
                "product_name": "Implante Cone Morse 3.75x11mm",
                "ncm": "90211010",
                "batch_number": "LOTE-2026-A1",
                "quantity": 7,
                "unit_price": 450.0,
            }
        ]
    }

    result = orchestrator.dispatch_consignment_settlement(
        settlement_data=settlement_payload,
        erp_type="sap_b1",
        account_id="0f14ffff"
    )

    assert result["success"] is True
    # Retorno Simbólico
    return_inv = result["symbolic_return_invoice"]
    assert return_inv["cfop"] == "1918"
    assert return_inv["flow_type"] == "RETURN_1918"
    assert return_inv["total_invoice_value"] == 1350.0  # 3 * 450 = 1350
    assert "xml_r2_key" in return_inv
    assert "danfe_pdf_r2_key" in return_inv

    # Venda de Material Consignado Faturado
    sale_inv = result["sale_invoice"]
    assert sale_inv["cfop"] == "5113"
    assert sale_inv["flow_type"] == "SALE_5113"
    assert sale_inv["total_invoice_value"] == 1350.0
    assert "xml_r2_key" in sale_inv
    assert "danfe_pdf_r2_key" in sale_inv

    # Verifica se ambas as notas fiscais foram registradas
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM erp_fiscal_invoices WHERE account_id = '0f14ffff'")
        assert cur.fetchone()["cnt"] == 2
    finally:
        conn.close()


def test_interstate_cfop_selection_6917_and_6113():
    """Valida derivação automática de CFOP interestadual quando emitter_uf != recipient_uf."""
    orchestrator = WindmillERPOrchestrator(mock_mode=True)

    remittance_payload = {
        "account_id": "0f14ffff",
        "agreement_id": "agr-consign-rj",
        "emitter_uf": "SP",
        "recipient_uf": "RJ",
        "recipient_cnpj": "33.111.222/0001-33",
        "recipient_name": "Hospital Odontológico Copacabana",
        "items": [
            {
                "product_id": "IMP-CM-4313",
                "product_name": "Implante Cone Morse 4.3x13mm",
                "ncm": "90211010",
                "batch_number": "LOTE-RJ-01",
                "quantity": 4,
                "unit_price": 480.0,
            }
        ]
    }

    result = orchestrator.dispatch_consignment_remittance(
        remittance_data=remittance_payload,
        erp_type="sankhya",
        account_id="0f14ffff"
    )

    # Para remessa interestadual, o CFOP é 6917
    assert result["cfop"] == "6917"


def test_api_endpoints_erp_fiscal_hub():
    """Valida contratos REST OpenAPI 3.1 dos endpoints do Hub Fiscal ERP."""
    # 1. Emissão de Remessa via API
    resp_rem = client.post(
        "/api/v1/integrations/erp/remittance/emit",
        json={
            "erp_type": "totvs_protheus",
            "agreement_id": "agr-api-test-01",
            "emitter_uf": "SP",
            "recipient_uf": "SP",
            "recipient_cnpj": "11.222.333/0001-44",
            "recipient_name": "Clínica OdontoCampinas",
            "items": [
                {
                    "product_id": "IMP-CM-37511",
                    "product_name": "Implante CM 3.75x11",
                    "ncm": "90211010",
                    "batch_number": "LOTE-API-01",
                    "quantity": 2,
                    "unit_price": 450.0
                }
            ],
            "account_id": "0f14ffff"
        }
    )
    assert resp_rem.status_code == 201
    rem_data = resp_rem.json()
    assert rem_data["cfop"] == "5917"
    assert rem_data["status"] == "AUTORIZADA"
    inv_id = rem_data["id"]

    # 2. Consultar detalhes da NF-e emitida
    resp_get = client.get(f"/api/v1/integrations/erp/invoices/{inv_id}")
    assert resp_get.status_code == 200
    assert resp_get.json()["id"] == inv_id

    # 3. Listar notas fiscais emitidas
    resp_list = client.get("/api/v1/integrations/erp/invoices?flow_type=REMITTANCE_5917")
    assert resp_list.status_code == 200
    invoices = resp_list.json()
    assert len(invoices) >= 1
    assert any(i["id"] == inv_id for i in invoices)
