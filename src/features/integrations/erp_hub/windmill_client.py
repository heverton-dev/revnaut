# -*- coding: utf-8 -*-
"""
Vertical Slice: Windmill ERP Orchestrator & Cloudflare R2 Fiscal Storage
Orquestrador de fluxos fiscais (CFOP 5.917 / 1.918 / 5.113) e guarda de XML/DANFE no R2.
"""

from __future__ import annotations
import json
import os
import time
import uuid
from typing import Any, Dict, List, Optional

from src.core.database import get_connection, init_db
from src.core.events import EventBus, StreamName, default_event_bus
from src.core.storage import R2StorageClient
from src.features.integrations.totvs.adapter import get_erp_connector


def _build_nfe_xml_bytes(inv: Dict[str, Any]) -> bytes:
    """Compila o XML determinístico da NF-e 4.00 com protocolo SEFAZ."""
    xml_doc = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">\n'
        f'  <NFe><infNFe Id="NFe{inv["nfe_access_key"]}" versao="4.00">\n'
        f'    <ide><nNF>{inv["nfe_number"]}</nNF><serie>{inv["nfe_series"]}</serie><CFOP>{inv["cfop"]}</CFOP></ide>\n'
        f'    <dest><CNPJ>{inv["recipient_cnpj"]}</CNPJ><xNome>{inv["recipient_name"]}</xNome></dest>\n'
        f'    <total><ICMSTot><vNF>{inv["total_invoice_value"]:.2f}</vNF></ICMSTot></total>\n'
        '  </infNFe></NFe>\n'
        f'  <protNFe versao="4.00"><infProt><chNFe>{inv["nfe_access_key"]}</chNFe><nProt>{inv["sefaz_protocol"]}</nProt><cStat>100</cStat></infProt></protNFe>\n'
        '</nfeProc>\n'
    )
    return xml_doc.encode("utf-8")


def _build_danfe_pdf_bytes(inv: Dict[str, Any]) -> bytes:
    """Gera documento PDF válido (%PDF-1.4) do DANFE para guarda fiscal no R2."""
    text = (
        f"DANFE NF-e {inv['nfe_number']} Serie {inv['nfe_series']} | "
        f"CFOP {inv['cfop']} | Chave {inv['nfe_access_key']} | "
        f"Destinatario: {inv['recipient_name']} ({inv['recipient_cnpj']}) | "
        f"Valor Total R$ {inv['total_invoice_value']:.2f}"
    )
    safe_text = text.replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 10 Tf 36 750 Td ({safe_text}) Tj ET".encode("latin-1", errors="ignore")
    pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj\n"
        b"4 0 obj << /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n"
        + stream +
        b"\nendstream\nendobj\n"
        b"trailer << /Root 1 0 R >>\n%%EOF\n"
    )
    return pdf


class WindmillERPOrchestrator:
    """
    Cliente e orquestrador de automações fiscais do Windmill (Rust/Go engine).
    Em ambiente local/test opera em mock mode determinístico (< 1ms).
    Na VPS/Produção conecta via HTTP ao servidor Windmill.
    """

    def __init__(self, windmill_url: Optional[str] = None, token: Optional[str] = None, mock_mode: Optional[bool] = None):
        self.windmill_url = windmill_url or os.getenv("WINDMILL_URL", "http://windmill:8000")
        self.token = token or os.getenv("WINDMILL_TOKEN", "mock-windmill-token")
        app_env = os.getenv("APP_ENV", "local")
        self.mock_mode = mock_mode if mock_mode is not None else (app_env in ("local", "test", "development"))
        self.storage = R2StorageClient()

    def _trigger_windmill_job_http(self, script_path: str, payload: Dict[str, Any]) -> str:
        """Aciona job no servidor Windmill via HTTP quando not self.mock_mode."""
        if not self.mock_mode:
            import httpx
            url = f"{self.windmill_url.rstrip('/')}/api/w/revnaut/jobs/run/p/{script_path.lstrip('/')}"
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
            resp = httpx.post(url, json=payload, headers=headers, timeout=15.0)
            resp.raise_for_status()
            return str(resp.text).strip().strip('"') or f"wm-job-{uuid.uuid4().hex[:8]}"
        return f"wm-job-{uuid.uuid4().hex[:8]}"

    def dispatch_consignment_remittance(
        self,
        remittance_data: Dict[str, Any],
        erp_type: str = "totvs_protheus",
        account_id: str = "0f14ffff",
    ) -> Dict[str, Any]:
        """
        Dispara fluxo no Windmill para emissão de NF-e de Remessa em Consignação (CFOP 5.917 / 6.917),
        armazena XML e DANFE PDF no Cloudflare R2 e persiste no banco SQLite WAL.
        """
        init_db()
        connector = get_erp_connector(erp_type=erp_type)
        inv = connector.emit_consignment_remittance_nfe(remittance_data)

        access_key = inv["nfe_access_key"]
        ref_id = remittance_data.get("agreement_id") or remittance_data.get("order_id") or f"ref-{uuid.uuid4().hex[:6]}"

        # Particionamento determinístico das chaves no Cloudflare R2 + Upload real dos bytes
        xml_key = self.storage.generate_storage_key(
            tenant_id=account_id,
            module="fiscal/nfe",
            filename=f"{access_key}.xml"
        )
        pdf_key = self.storage.generate_storage_key(
            tenant_id=account_id,
            module="fiscal/nfe",
            filename=f"{access_key}.pdf"
        )

        xml_bytes = _build_nfe_xml_bytes(inv)
        pdf_bytes = _build_danfe_pdf_bytes(inv)
        xml_upload = self.storage.upload_bytes(xml_key, xml_bytes, "application/xml")
        pdf_upload = self.storage.upload_bytes(pdf_key, pdf_bytes, "application/pdf")

        r2_domain = os.getenv("R2_PUBLIC_URL", "https://r2.revnaut.internal")
        xml_url = xml_upload if isinstance(xml_upload, str) else (xml_upload.get("public_url") or f"{r2_domain}/{xml_key}")
        pdf_url = pdf_upload if isinstance(pdf_upload, str) else (pdf_upload.get("public_url") or f"{r2_domain}/{pdf_key}")
        job_id = self._trigger_windmill_job_http("f/erp/emit_remittance_nfe", {"erp_type": erp_type, "invoice": inv})
        if job_id.startswith("wm-job-") and not job_id.startswith("wm-job-rem-"):
            job_id = f"wm-job-rem-{uuid.uuid4().hex[:8]}"
        invoice_id = f"inv-rem-{uuid.uuid4().hex[:8]}"

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO erp_fiscal_invoices (
                    id, account_id, erp_type, flow_type, reference_id,
                    cfop, nfe_number, nfe_series, nfe_access_key,
                    recipient_cnpj_cpf, recipient_name, total_invoice_value,
                    xml_r2_key, danfe_pdf_r2_key, status, sefaz_protocol,
                    windmill_job_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id, account_id, erp_type, inv["flow_type"], ref_id,
                inv["cfop"], inv["nfe_number"], inv["nfe_series"], access_key,
                inv["recipient_cnpj"], inv["recipient_name"], inv["total_invoice_value"],
                xml_key, pdf_key, inv["status"], inv["sefaz_protocol"],
                job_id
            ))
            conn.commit()
        finally:
            conn.close()

        # Telemetria no EventBus
        default_event_bus.publish_sync(
            stream=StreamName.AUDIT,
            event_type="erp.consignment_remittance_emitted",
            account_id=account_id,
            payload={
                "event": "erp.consignment_remittance_emitted",
                "invoice_id": invoice_id,
                "cfop": inv["cfop"],
                "access_key": access_key,
                "total_value": inv["total_invoice_value"],
                "erp_type": erp_type,
            },
        )

        return {
            "id": invoice_id,
            "account_id": account_id,
            "success": True,
            "erp_type": erp_type,
            "flow_type": inv["flow_type"],
            "reference_id": ref_id,
            "cfop": inv["cfop"],
            "nfe_number": inv["nfe_number"],
            "nfe_series": inv["nfe_series"],
            "nfe_access_key": access_key,
            "recipient_cnpj": inv["recipient_cnpj"],
            "recipient_cnpj_cpf": inv["recipient_cnpj"],
            "recipient_name": inv["recipient_name"],
            "total_invoice_value": inv["total_invoice_value"],
            "xml_r2_key": xml_key,
            "danfe_pdf_r2_key": pdf_key,
            "xml_url": xml_url,
            "danfe_pdf_url": pdf_url,
            "status": inv["status"],
            "sefaz_protocol": inv["sefaz_protocol"],
            "windmill_job_id": job_id,
        }

    def dispatch_consignment_settlement(
        self,
        settlement_data: Dict[str, Any],
        erp_type: str = "totvs_protheus",
        account_id: str = "0f14ffff",
    ) -> Dict[str, Any]:
        """
        Liquidação pós-cirúrgica:
        1. Emite NF-e de Retorno Simbólico de Consignação (CFOP 1.918 / 2.918).
        2. Fatura a NF-e de Venda de Material Consignado (CFOP 5.113 / 6.113) sobre os itens consumidos.
        3. Guarda os XMLs e PDFs no Cloudflare R2 por 5 anos fiscais.
        """
        init_db()
        connector = get_erp_connector(erp_type=erp_type)

        # 1. Retorno Simbólico (CFOP 1.918 / 2.918)
        ret_inv = connector.emit_symbolic_return_nfe(settlement_data)
        ret_access_key = ret_inv["nfe_access_key"]
        ref_id = settlement_data.get("surgical_report_id") or settlement_data.get("agreement_id") or f"ref-{uuid.uuid4().hex[:6]}"

        ret_xml_key = self.storage.generate_storage_key(
            tenant_id=account_id,
            module="fiscal/nfe",
            filename=f"{ret_access_key}.xml"
        )
        ret_pdf_key = self.storage.generate_storage_key(
            tenant_id=account_id,
            module="fiscal/nfe",
            filename=f"{ret_access_key}.pdf"
        )
        self.storage.upload_bytes(ret_xml_key, _build_nfe_xml_bytes(ret_inv), "application/xml")
        self.storage.upload_bytes(ret_pdf_key, _build_danfe_pdf_bytes(ret_inv), "application/pdf")
        ret_invoice_id = f"inv-ret-{uuid.uuid4().hex[:8]}"

        # 2. Venda Consignada (CFOP 5.113 / 6.113)
        sale_inv = connector.emit_consignment_sale_nfe(settlement_data)
        sale_access_key = sale_inv["nfe_access_key"]

        sale_xml_key = self.storage.generate_storage_key(
            tenant_id=account_id,
            module="fiscal/nfe",
            filename=f"{sale_access_key}.xml"
        )
        sale_pdf_key = self.storage.generate_storage_key(
            tenant_id=account_id,
            module="fiscal/nfe",
            filename=f"{sale_access_key}.pdf"
        )
        self.storage.upload_bytes(sale_xml_key, _build_nfe_xml_bytes(sale_inv), "application/xml")
        self.storage.upload_bytes(sale_pdf_key, _build_danfe_pdf_bytes(sale_inv), "application/pdf")
        sale_invoice_id = f"inv-sale-{uuid.uuid4().hex[:8]}"

        job_id = self._trigger_windmill_job_http(
            "f/erp/emit_settlement_nfe",
            {"erp_type": erp_type, "symbolic_return": ret_inv, "sale": sale_inv},
        )
        if job_id.startswith("wm-job-") and not job_id.startswith("wm-job-settle-"):
            job_id = f"wm-job-settle-{uuid.uuid4().hex[:8]}"

        conn = get_connection()
        try:
            cur = conn.cursor()
            # Insere retorno simbólico
            cur.execute("""
                INSERT INTO erp_fiscal_invoices (
                    id, account_id, erp_type, flow_type, reference_id,
                    cfop, nfe_number, nfe_series, nfe_access_key,
                    recipient_cnpj_cpf, recipient_name, total_invoice_value,
                    xml_r2_key, danfe_pdf_r2_key, status, sefaz_protocol,
                    windmill_job_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ret_invoice_id, account_id, erp_type, ret_inv["flow_type"], ref_id,
                ret_inv["cfop"], ret_inv["nfe_number"], ret_inv["nfe_series"], ret_access_key,
                ret_inv["recipient_cnpj"], ret_inv["recipient_name"], ret_inv["total_invoice_value"],
                ret_xml_key, ret_pdf_key, ret_inv["status"], ret_inv["sefaz_protocol"],
                job_id
            ))

            # Insere venda consignada
            cur.execute("""
                INSERT INTO erp_fiscal_invoices (
                    id, account_id, erp_type, flow_type, reference_id,
                    cfop, nfe_number, nfe_series, nfe_access_key,
                    recipient_cnpj_cpf, recipient_name, total_invoice_value,
                    xml_r2_key, danfe_pdf_r2_key, status, sefaz_protocol,
                    windmill_job_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sale_invoice_id, account_id, erp_type, sale_inv["flow_type"], ref_id,
                sale_inv["cfop"], sale_inv["nfe_number"], sale_inv["nfe_series"], sale_access_key,
                sale_inv["recipient_cnpj"], sale_inv["recipient_name"], sale_inv["total_invoice_value"],
                sale_xml_key, sale_pdf_key, sale_inv["status"], sale_inv["sefaz_protocol"],
                job_id
            ))
            conn.commit()
        finally:
            conn.close()

        default_event_bus.publish_sync(
            stream=StreamName.AUDIT,
            event_type="erp.consignment_settlement_emitted",
            account_id=account_id,
            payload={
                "settlement_job_id": job_id,
                "return_invoice_id": ret_invoice_id,
                "sale_invoice_id": sale_invoice_id,
                "erp_type": erp_type,
            },
        )

        r2_domain = os.getenv("R2_PUBLIC_URL", "https://r2.revnaut.internal")

        return {
            "success": True,
            "settlement_job_id": job_id,
            "symbolic_return_invoice": {
                "id": ret_invoice_id,
                "cfop": ret_inv["cfop"],
                "flow_type": ret_inv["flow_type"],
                "nfe_number": ret_inv["nfe_number"],
                "nfe_access_key": ret_access_key,
                "total_invoice_value": ret_inv["total_invoice_value"],
                "xml_r2_key": ret_xml_key,
                "danfe_pdf_r2_key": ret_pdf_key,
                "xml_url": f"{r2_domain}/{ret_xml_key}",
                "danfe_pdf_url": f"{r2_domain}/{ret_pdf_key}",
                "status": ret_inv["status"],
            },
            "sale_invoice": {
                "id": sale_invoice_id,
                "cfop": sale_inv["cfop"],
                "flow_type": sale_inv["flow_type"],
                "nfe_number": sale_inv["nfe_number"],
                "nfe_access_key": sale_access_key,
                "total_invoice_value": sale_inv["total_invoice_value"],
                "xml_r2_key": sale_xml_key,
                "danfe_pdf_r2_key": sale_pdf_key,
                "xml_url": f"{r2_domain}/{sale_xml_key}",
                "danfe_pdf_url": f"{r2_domain}/{sale_pdf_key}",
                "status": sale_inv["status"],
            }
        }


def list_fiscal_invoices(
    flow_type: Optional[str] = None,
    erp_type: Optional[str] = None,
    account_id: str = "0f14ffff",
) -> List[Dict[str, Any]]:
    """Consulta notas fiscais de remessa, retorno e venda consignada emitidas."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = """
            SELECT id, account_id, erp_type, flow_type, reference_id,
                   cfop, nfe_number, nfe_series, nfe_access_key,
                   recipient_cnpj_cpf, recipient_name, total_invoice_value,
                   xml_r2_key, danfe_pdf_r2_key, status, sefaz_protocol,
                   windmill_job_id, created_at
            FROM erp_fiscal_invoices
            WHERE account_id = ?
        """
        params: List[Any] = [account_id]
        if flow_type:
            query += " AND flow_type = ?"
            params.append(flow_type)
        if erp_type:
            query += " AND erp_type = ?"
            params.append(erp_type)

        query += " ORDER BY created_at DESC"
        cur.execute(query, tuple(params))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_fiscal_invoice(invoice_id: str, account_id: str = "0f14ffff") -> Optional[Dict[str, Any]]:
    """Consulta detalhes de uma NF-e específica."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, account_id, erp_type, flow_type, reference_id,
                   cfop, nfe_number, nfe_series, nfe_access_key,
                   recipient_cnpj_cpf, recipient_name, total_invoice_value,
                   xml_r2_key, danfe_pdf_r2_key, status, sefaz_protocol,
                   windmill_job_id, created_at
            FROM erp_fiscal_invoices
            WHERE id = ? AND account_id = ?
        """, (invoice_id, account_id))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
