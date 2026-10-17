# -*- coding: utf-8 -*-
"""
Adapter TOTVS Protheus — Ports & Adapters (Hexagonal Architecture)
Suporta execução offline ultra-rápida em ambiente Dev/Antigravity (< 1ms)
e chamadas HTTP REST reais em ambiente de Produção na VPS.
"""

from __future__ import annotations
import os
import uuid
from typing import Dict, Any, Optional
from src.features.integrations.totvs.schemas import TotvsCustomerSA1, TotvsOrderSC5


class TotvsProtheusAdapter:
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None, mock_mode: Optional[bool] = None):
        self.base_url = base_url or os.getenv("TOTVS_PROTHEUS_URL", "http://totvs.erp.local:8080/rest")
        self.token = token or os.getenv("TOTVS_PROTHEUS_TOKEN", "mock-protheus-secret-token")
        
        # Em Dev/Test no Antigravity, usa Mock Determinístico (0MB RAM extra, 0ms latência)
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

        # Chamada real HTTP em Produção
        import httpx
        url = f"{self.base_url}/api/v1/customers"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        resp = httpx.post(url, credentials=None, json=customer.model_dump(), headers=headers, timeout=10.0)
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
