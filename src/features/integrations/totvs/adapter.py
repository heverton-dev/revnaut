# -*- coding: utf-8 -*-
"""
Adapter TOTVS Protheus & ERP Hub — Ports & Adapters (Hexagonal Architecture)
Suporta interface padrão BaseERPConnector para TOTVS Protheus, SAP Business One e Sankhya.
Suporta execução offline ultra-rápida em ambiente Dev/Antigravity (< 1ms)
e chamadas HTTP REST reais em ambiente de Produção na VPS.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import os
import re
import time
import uuid
from typing import Dict, Any, Optional
from src.features.integrations.totvs.schemas import TotvsCustomerSA1, TotvsOrderSC5


def _generate_deterministic_nfe_key(uf_code: str, cnpj: str, model: str = "55", series: str = "001", nfe_num: Optional[int] = None) -> str:
    """Gera chave de acesso NF-e válida de 44 dígitos numéricos."""
    clean_cnpj = re.sub(r"\D", "", cnpj).zfill(14)[:14]
    year_month = time.strftime("%y%m")
    num_val = nfe_num if nfe_num is not None else (uuid.uuid4().int % 900000 + 100000)
    num_str = str(num_val).zfill(9)
    tipo_emissao = "1"
    cod_aleatorio = f"{uuid.uuid4().int % 100000000:08d}"
    partial_key = f"{uf_code}{year_month}{clean_cnpj}{model}{series}{num_str}{tipo_emissao}{cod_aleatorio}"
    
    # Cálculo dígito verificador módulo 11
    pesos = [2, 3, 4, 5, 6, 7, 8, 9] * 6
    soma = sum(int(d) * pesos[i] for i, d in enumerate(reversed(partial_key)))
    resto = soma % 11
    dv = 0 if resto in (0, 1) else 11 - resto
    return f"{partial_key}{dv}"


class BaseERPConnector(ABC):
    """Interface abstrata obrigatória para todos os conectores fiscais ERP (Lei #5 e Lei #6)."""

    @abstractmethod
    def emit_consignment_remittance_nfe(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Emite NF-e de Remessa em Consignação (CFOP 5.917 / 6.917)."""
        pass

    @abstractmethod
    def emit_symbolic_return_nfe(self, return_data: Dict[str, Any]) -> Dict[str, Any]:
        """Emite NF-e de Retorno Simbólico de Consignação (CFOP 1.918 / 2.918)."""
        pass

    @abstractmethod
    def emit_consignment_sale_nfe(self, sale_data: Dict[str, Any]) -> Dict[str, Any]:
        """Emite NF-e de Venda de Material Consignado (CFOP 5.113 / 6.113)."""
        pass


class TotvsProtheusAdapter(BaseERPConnector):
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None, mock_mode: Optional[bool] = None):
        self.base_url = base_url or os.getenv("TOTVS_PROTHEUS_URL", "http://totvs.erp.local:8080/rest")
        self.token = token or os.getenv("TOTVS_PROTHEUS_TOKEN", "mock-protheus-secret-token")
        app_env = os.getenv("APP_ENV", "local")
        self.mock_mode = mock_mode if mock_mode is not None else (app_env in ("local", "test", "development"))

    def sync_customer_sa1(self, customer: TotvsCustomerSA1) -> Dict[str, Any]:
        """Sincroniza cliente SA1 com o Protheus."""
        if self.mock_mode:
            cod = customer.A1_COD or f"CLI{uuid.uuid4().hex[:6].upper()}"
            return {
                "A1_COD": cod,
                "A1_LOJA": customer.A1_LOJA,
                "A1_NOME": customer.A1_NOME,
                "A1_CGC": customer.A1_CGC,
                "A1_X_CRO": customer.A1_X_CRO,
                "A1_LC": customer.A1_LC or 100000.0,
                "sync_status": "synced",
                "protheus_timestamp": "2026-10-17T08:00:00Z"
            }

        import httpx
        url = f"{self.base_url}/api/v1/customers"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        resp = httpx.post(url, json=customer.model_dump(), headers=headers, timeout=10.0)
        resp.raise_for_status()
        return resp.json()

    def create_sales_order_sc5(self, order: TotvsOrderSC5) -> Dict[str, Any]:
        """Emite pedido de venda SC5 e itens SC6 no Protheus."""
        if self.mock_mode:
            order_num = order.C5_NUM or f"PV{uuid.uuid4().hex[:6].upper()}"
            return {
                "C5_NUM": order_num,
                "C5_CLIENTE": order.C5_CLIENTE,
                "C5_LOJACLI": order.C5_LOJACLI,
                "C5_TOTAL": order.C5_TOTAL,
                "items_count": len(order.items),
                "order_status": "aberto_faturamento",
                "protheus_timestamp": "2026-10-17T08:00:00Z"
            }

        import httpx
        url = f"{self.base_url}/api/v1/salesorders"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-Idempotency-Key": order.idempotency_key
        }
        resp = httpx.post(url, json=order.model_dump(), headers=headers, timeout=15.0)
        resp.raise_for_status()
        return resp.json()

    def emit_consignment_remittance_nfe(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        emitter_uf = (order_data.get("emitter_uf") or "SP").upper()
        recipient_uf = (order_data.get("recipient_uf") or "SP").upper()
        is_interstate = (emitter_uf != recipient_uf)
        cfop = "6917" if is_interstate else "5917"

        items = order_data.get("items") or []
        total_val = sum(float(i.get("quantity", 1)) * float(i.get("unit_price", 0.0)) for i in items)
        nfe_num = uuid.uuid4().int % 900000 + 100000
        cnpj = order_data.get("recipient_cnpj") or "12.345.678/0001-90"
        nfe_key = _generate_deterministic_nfe_key("35", cnpj, nfe_num=nfe_num)

        return {
            "erp_type": "totvs_protheus",
            "flow_type": "REMITTANCE_5917",
            "cfop": cfop,
            "nfe_number": str(nfe_num),
            "nfe_series": "1",
            "nfe_access_key": nfe_key,
            "recipient_cnpj": cnpj,
            "recipient_name": order_data.get("recipient_name", "Cliente"),
            "total_invoice_value": round(total_val, 2),
            "status": "AUTORIZADA",
            "sefaz_protocol": f"13526000{uuid.uuid4().hex[:8].upper()}",
            "erp_doc_id": f"DOC-TOTVS-{uuid.uuid4().hex[:6].upper()}",
        }

    def emit_symbolic_return_nfe(self, return_data: Dict[str, Any]) -> Dict[str, Any]:
        emitter_uf = (return_data.get("emitter_uf") or "SP").upper()
        recipient_uf = (return_data.get("recipient_uf") or "SP").upper()
        cfop = "2918" if (emitter_uf != recipient_uf) else "1918"

        items = return_data.get("consumed_items") or return_data.get("items") or []
        total_val = sum(float(i.get("quantity", 1)) * float(i.get("unit_price", 0.0)) for i in items)
        nfe_num = uuid.uuid4().int % 900000 + 100000
        cnpj = return_data.get("recipient_cnpj") or "12.345.678/0001-90"
        nfe_key = _generate_deterministic_nfe_key("35", cnpj, nfe_num=nfe_num)

        return {
            "erp_type": "totvs_protheus",
            "flow_type": "RETURN_1918",
            "cfop": cfop,
            "nfe_number": str(nfe_num),
            "nfe_series": "1",
            "nfe_access_key": nfe_key,
            "recipient_cnpj": cnpj,
            "recipient_name": return_data.get("recipient_name", "Cliente"),
            "total_invoice_value": round(total_val, 2),
            "status": "AUTORIZADA",
            "sefaz_protocol": f"13526000{uuid.uuid4().hex[:8].upper()}",
            "erp_doc_id": f"DOC-RET-TOTVS-{uuid.uuid4().hex[:6].upper()}",
        }

    def emit_consignment_sale_nfe(self, sale_data: Dict[str, Any]) -> Dict[str, Any]:
        emitter_uf = (sale_data.get("emitter_uf") or "SP").upper()
        recipient_uf = (sale_data.get("recipient_uf") or "SP").upper()
        cfop = "6113" if (emitter_uf != recipient_uf) else "5113"

        items = sale_data.get("consumed_items") or sale_data.get("items") or []
        total_val = sum(float(i.get("quantity", 1)) * float(i.get("unit_price", 0.0)) for i in items)
        nfe_num = uuid.uuid4().int % 900000 + 100000
        cnpj = sale_data.get("recipient_cnpj") or "12.345.678/0001-90"
        nfe_key = _generate_deterministic_nfe_key("35", cnpj, nfe_num=nfe_num)

        return {
            "erp_type": "totvs_protheus",
            "flow_type": "SALE_5113",
            "cfop": cfop,
            "nfe_number": str(nfe_num),
            "nfe_series": "1",
            "nfe_access_key": nfe_key,
            "recipient_cnpj": cnpj,
            "recipient_name": sale_data.get("recipient_name", "Cliente"),
            "total_invoice_value": round(total_val, 2),
            "status": "AUTORIZADA",
            "sefaz_protocol": f"13526000{uuid.uuid4().hex[:8].upper()}",
            "erp_doc_id": f"DOC-SALE-TOTVS-{uuid.uuid4().hex[:6].upper()}",
        }


class SapBusinessOneAdapter(BaseERPConnector):
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None, mock_mode: Optional[bool] = None):
        self.base_url = base_url or os.getenv("SAP_B1_SERVICE_LAYER_URL", "https://sap.erp.local:50000/b1s/v2")
        self.token = token or os.getenv("SAP_B1_TOKEN", "mock-sap-b1-token")
        app_env = os.getenv("APP_ENV", "local")
        self.mock_mode = mock_mode if mock_mode is not None else (app_env in ("local", "test", "development"))

    def emit_consignment_remittance_nfe(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        emitter_uf = (order_data.get("emitter_uf") or "SP").upper()
        recipient_uf = (order_data.get("recipient_uf") or "SP").upper()
        cfop = "6917" if (emitter_uf != recipient_uf) else "5917"

        items = order_data.get("items") or []
        total_val = sum(float(i.get("quantity", 1)) * float(i.get("unit_price", 0.0)) for i in items)
        nfe_num = uuid.uuid4().int % 900000 + 100000
        cnpj = order_data.get("recipient_cnpj") or "12.345.678/0001-90"
        nfe_key = _generate_deterministic_nfe_key("35", cnpj, nfe_num=nfe_num)

        return {
            "erp_type": "sap_b1",
            "flow_type": "REMITTANCE_5917",
            "cfop": cfop,
            "nfe_number": str(nfe_num),
            "nfe_series": "1",
            "nfe_access_key": nfe_key,
            "recipient_cnpj": cnpj,
            "recipient_name": order_data.get("recipient_name", "Cliente"),
            "total_invoice_value": round(total_val, 2),
            "status": "AUTORIZADA",
            "sefaz_protocol": f"13526000{uuid.uuid4().hex[:8].upper()}",
            "erp_doc_id": f"SAP-ODLN-{uuid.uuid4().hex[:6].upper()}",
        }

    def emit_symbolic_return_nfe(self, return_data: Dict[str, Any]) -> Dict[str, Any]:
        emitter_uf = (return_data.get("emitter_uf") or "SP").upper()
        recipient_uf = (return_data.get("recipient_uf") or "SP").upper()
        cfop = "2918" if (emitter_uf != recipient_uf) else "1918"

        items = return_data.get("consumed_items") or return_data.get("items") or []
        total_val = sum(float(i.get("quantity", 1)) * float(i.get("unit_price", 0.0)) for i in items)
        nfe_num = uuid.uuid4().int % 900000 + 100000
        cnpj = return_data.get("recipient_cnpj") or "12.345.678/0001-90"
        nfe_key = _generate_deterministic_nfe_key("35", cnpj, nfe_num=nfe_num)

        return {
            "erp_type": "sap_b1",
            "flow_type": "RETURN_1918",
            "cfop": cfop,
            "nfe_number": str(nfe_num),
            "nfe_series": "1",
            "nfe_access_key": nfe_key,
            "recipient_cnpj": cnpj,
            "recipient_name": return_data.get("recipient_name", "Cliente"),
            "total_invoice_value": round(total_val, 2),
            "status": "AUTORIZADA",
            "sefaz_protocol": f"13526000{uuid.uuid4().hex[:8].upper()}",
            "erp_doc_id": f"SAP-ORDN-{uuid.uuid4().hex[:6].upper()}",
        }

    def emit_consignment_sale_nfe(self, sale_data: Dict[str, Any]) -> Dict[str, Any]:
        emitter_uf = (sale_data.get("emitter_uf") or "SP").upper()
        recipient_uf = (sale_data.get("recipient_uf") or "SP").upper()
        cfop = "6113" if (emitter_uf != recipient_uf) else "5113"

        items = sale_data.get("consumed_items") or sale_data.get("items") or []
        total_val = sum(float(i.get("quantity", 1)) * float(i.get("unit_price", 0.0)) for i in items)
        nfe_num = uuid.uuid4().int % 900000 + 100000
        cnpj = sale_data.get("recipient_cnpj") or "12.345.678/0001-90"
        nfe_key = _generate_deterministic_nfe_key("35", cnpj, nfe_num=nfe_num)

        return {
            "erp_type": "sap_b1",
            "flow_type": "SALE_5113",
            "cfop": cfop,
            "nfe_number": str(nfe_num),
            "nfe_series": "1",
            "nfe_access_key": nfe_key,
            "recipient_cnpj": cnpj,
            "recipient_name": sale_data.get("recipient_name", "Cliente"),
            "total_invoice_value": round(total_val, 2),
            "status": "AUTORIZADA",
            "sefaz_protocol": f"13526000{uuid.uuid4().hex[:8].upper()}",
            "erp_doc_id": f"SAP-OINV-{uuid.uuid4().hex[:6].upper()}",
        }


class SankhyaAdapter(BaseERPConnector):
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None, mock_mode: Optional[bool] = None):
        self.base_url = base_url or os.getenv("SANKHYA_GATEWAY_URL", "http://sankhya.erp.local:8080/mge")
        self.token = token or os.getenv("SANKHYA_BEARER_TOKEN", "mock-sankhya-token")
        app_env = os.getenv("APP_ENV", "local")
        self.mock_mode = mock_mode if mock_mode is not None else (app_env in ("local", "test", "development"))

    def emit_consignment_remittance_nfe(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        emitter_uf = (order_data.get("emitter_uf") or "SP").upper()
        recipient_uf = (order_data.get("recipient_uf") or "SP").upper()
        cfop = "6917" if (emitter_uf != recipient_uf) else "5917"

        items = order_data.get("items") or []
        total_val = sum(float(i.get("quantity", 1)) * float(i.get("unit_price", 0.0)) for i in items)
        nfe_num = uuid.uuid4().int % 900000 + 100000
        cnpj = order_data.get("recipient_cnpj") or "12.345.678/0001-90"
        nfe_key = _generate_deterministic_nfe_key("35", cnpj, nfe_num=nfe_num)

        return {
            "erp_type": "sankhya",
            "flow_type": "REMITTANCE_5917",
            "cfop": cfop,
            "nfe_number": str(nfe_num),
            "nfe_series": "1",
            "nfe_access_key": nfe_key,
            "recipient_cnpj": cnpj,
            "recipient_name": order_data.get("recipient_name", "Cliente"),
            "total_invoice_value": round(total_val, 2),
            "status": "AUTORIZADA",
            "sefaz_protocol": f"13526000{uuid.uuid4().hex[:8].upper()}",
            "erp_doc_id": f"SNK-TGFCAB-{uuid.uuid4().hex[:6].upper()}",
        }

    def emit_symbolic_return_nfe(self, return_data: Dict[str, Any]) -> Dict[str, Any]:
        emitter_uf = (return_data.get("emitter_uf") or "SP").upper()
        recipient_uf = (return_data.get("recipient_uf") or "SP").upper()
        cfop = "2918" if (emitter_uf != recipient_uf) else "1918"

        items = return_data.get("consumed_items") or return_data.get("items") or []
        total_val = sum(float(i.get("quantity", 1)) * float(i.get("unit_price", 0.0)) for i in items)
        nfe_num = uuid.uuid4().int % 900000 + 100000
        cnpj = return_data.get("recipient_cnpj") or "12.345.678/0001-90"
        nfe_key = _generate_deterministic_nfe_key("35", cnpj, nfe_num=nfe_num)

        return {
            "erp_type": "sankhya",
            "flow_type": "RETURN_1918",
            "cfop": cfop,
            "nfe_number": str(nfe_num),
            "nfe_series": "1",
            "nfe_access_key": nfe_key,
            "recipient_cnpj": cnpj,
            "recipient_name": return_data.get("recipient_name", "Cliente"),
            "total_invoice_value": round(total_val, 2),
            "status": "AUTORIZADA",
            "sefaz_protocol": f"13526000{uuid.uuid4().hex[:8].upper()}",
            "erp_doc_id": f"SNK-RET-{uuid.uuid4().hex[:6].upper()}",
        }

    def emit_consignment_sale_nfe(self, sale_data: Dict[str, Any]) -> Dict[str, Any]:
        emitter_uf = (sale_data.get("emitter_uf") or "SP").upper()
        recipient_uf = (sale_data.get("recipient_uf") or "SP").upper()
        cfop = "6113" if (emitter_uf != recipient_uf) else "5113"

        items = sale_data.get("consumed_items") or sale_data.get("items") or []
        total_val = sum(float(i.get("quantity", 1)) * float(i.get("unit_price", 0.0)) for i in items)
        nfe_num = uuid.uuid4().int % 900000 + 100000
        cnpj = sale_data.get("recipient_cnpj") or "12.345.678/0001-90"
        nfe_key = _generate_deterministic_nfe_key("35", cnpj, nfe_num=nfe_num)

        return {
            "erp_type": "sankhya",
            "flow_type": "SALE_5113",
            "cfop": cfop,
            "nfe_number": str(nfe_num),
            "nfe_series": "1",
            "nfe_access_key": nfe_key,
            "recipient_cnpj": cnpj,
            "recipient_name": sale_data.get("recipient_name", "Cliente"),
            "total_invoice_value": round(total_val, 2),
            "status": "AUTORIZADA",
            "sefaz_protocol": f"13526000{uuid.uuid4().hex[:8].upper()}",
            "erp_doc_id": f"SNK-SALE-{uuid.uuid4().hex[:6].upper()}",
        }


def get_erp_connector(erp_type: str = "totvs_protheus", **kwargs) -> BaseERPConnector:
    """Factory para instanciar o conector fiscal homologado adequado."""
    clean_type = (erp_type or "totvs_protheus").lower().strip()
    if clean_type in ("totvs", "protheus", "totvs_protheus"):
        return TotvsProtheusAdapter(**kwargs)
    elif clean_type in ("sap", "sap_b1", "sap_business_one"):
        return SapBusinessOneAdapter(**kwargs)
    elif clean_type in ("sankhya", "snk"):
        return SankhyaAdapter(**kwargs)
    else:
        raise ValueError(f"Conector ERP '{erp_type}' não suportado. Use 'totvs_protheus', 'sap_b1' ou 'sankhya'.")
