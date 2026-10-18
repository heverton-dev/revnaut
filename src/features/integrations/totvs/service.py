# -*- coding: utf-8 -*-
"""
Vertical Slice: TOTVS Protheus Service
Lógica de integração transacional, fila outbox e garantia de idempotência.
"""

from __future__ import annotations
import json
import uuid
from typing import Dict, Any, List, Optional
from src.core.database import get_connection
from src.features.integrations.totvs.schemas import TotvsCustomerSA1, TotvsOrderSC5, TotvsSyncResponse
from src.features.integrations.totvs.adapter import TotvsProtheusAdapter

_adapter = TotvsProtheusAdapter()


def sync_sa1_customer(
    customer: TotvsCustomerSA1,
    account_id: str = "0f14ffff",
    idempotency_key: Optional[str] = None
) -> Dict[str, Any]:
    key = idempotency_key or f"sa1_{customer.A1_CGC.replace('.', '').replace('-', '').replace('/', '')}"
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT status, response_body FROM integration_outbox WHERE idempotency_key = ?", (key,))
            existing = cur.fetchone()
            if existing and existing["status"] == "sent":
                return {
                    "success": True,
                    "action": "sync_customer_sa1",
                    "entity": "SA1",
                    "idempotency_key": key,
                    "status": "already_synced",
                    "data": json.loads(existing["response_body"])
                }

            outbox_id = f"ob_{uuid.uuid4().hex[:8]}"
            cur.execute("""
                INSERT OR IGNORE INTO integration_outbox (id, account_id, integration_type, idempotency_key, payload, status)
                VALUES (?, ?, 'totvs_sa1', ?, ?, 'pending')
            """, (outbox_id, account_id, key, json.dumps(customer.model_dump())))

            # Executa sincronização via Adapter
            protheus_data = _adapter.sync_customer_sa1(customer)

            # Atualiza contato correspondente se existir pelo CPF/CNPJ ou e-mail
            if customer.A1_X_CRO:
                cro_val = customer.A1_X_CRO
                uf_val = customer.A1_EST or "SP"
                cur.execute(
                    "UPDATE contacts SET cro = ?, cro_uf = ?, company = COALESCE(company, ?) WHERE (cro IS NULL OR cro = '') AND (name LIKE ? OR email LIKE ?)",
                    (cro_val, uf_val, customer.A1_NOME, f"%{customer.A1_NOME[:10]}%", f"%{customer.A1_NOME[:5]}%")
                )

            cur.execute("""
                UPDATE integration_outbox 
                SET status = 'sent', response_body = ?, updated_at = CURRENT_TIMESTAMP
                WHERE idempotency_key = ?
            """, (json.dumps(protheus_data), key))

            return {
                "success": True,
                "action": "sync_customer_sa1",
                "entity": "SA1",
                "idempotency_key": key,
                "status": "synced",
                "data": protheus_data
            }
    finally:
        conn.close()


def create_sc5_order(
    order: TotvsOrderSC5,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    key = order.idempotency_key
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT status, response_body FROM integration_outbox WHERE idempotency_key = ?", (key,))
            existing = cur.fetchone()
            if existing and existing["status"] == "sent":
                return {
                    "success": True,
                    "action": "create_sales_order_sc5",
                    "entity": "SC5",
                    "idempotency_key": key,
                    "status": "already_processed",
                    "data": json.loads(existing["response_body"])
                }

            outbox_id = f"ob_{uuid.uuid4().hex[:8]}"
            cur.execute("""
                INSERT OR IGNORE INTO integration_outbox (id, account_id, integration_type, idempotency_key, payload, status)
                VALUES (?, ?, 'totvs_order_sc5', ?, ?, 'pending')
            """, (outbox_id, account_id, key, json.dumps(order.model_dump())))

            # Emite pedido via Adapter
            protheus_data = _adapter.create_sales_order_sc5(order)

            # Registra auditoria no negócio se fornecido deal_id
            if order.deal_id:
                cur.execute("""
                    INSERT INTO deal_audit_logs (deal_id, author_name, action, new_value, comment)
                    VALUES (?, 'TOTVS Protheus ERP', 'ERP_ORDER_ISSUED', ?, ?)
                """, (order.deal_id, protheus_data.get("C5_NUM", "SC5"), f"Pedido de venda faturado no valor de R$ {order.C5_TOTAL:.2f}"))

            cur.execute("""
                UPDATE integration_outbox 
                SET status = 'sent', response_body = ?, updated_at = CURRENT_TIMESTAMP
                WHERE idempotency_key = ?
            """, (json.dumps(protheus_data), key))

            return {
                "success": True,
                "action": "create_sales_order_sc5",
                "entity": "SC5",
                "idempotency_key": key,
                "status": "issued",
                "data": protheus_data
            }
    finally:
        conn.close()


def list_outbox_items(account_id: str = "0f14ffff", status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        if status_filter:
            cur.execute(
                "SELECT id, account_id, integration_type, idempotency_key, status, attempts, last_error, created_at, updated_at "
                "FROM integration_outbox WHERE account_id = ? AND status = ? ORDER BY created_at DESC",
                (account_id, status_filter)
            )
        else:
            cur.execute(
                "SELECT id, account_id, integration_type, idempotency_key, status, attempts, last_error, created_at, updated_at "
                "FROM integration_outbox WHERE account_id = ? ORDER BY created_at DESC",
                (account_id,)
            )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def dispatch_erp_remittance(
    remittance_data: Dict[str, Any],
    erp_type: str = "totvs_protheus",
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    from src.features.integrations.erp_hub.windmill_client import WindmillERPOrchestrator
    orchestrator = WindmillERPOrchestrator()
    return orchestrator.dispatch_consignment_remittance(
        remittance_data=remittance_data,
        erp_type=erp_type,
        account_id=account_id
    )


def dispatch_erp_settlement(
    settlement_data: Dict[str, Any],
    erp_type: str = "totvs_protheus",
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    from src.features.integrations.erp_hub.windmill_client import WindmillERPOrchestrator
    orchestrator = WindmillERPOrchestrator()
    return orchestrator.dispatch_consignment_settlement(
        settlement_data=settlement_data,
        erp_type=erp_type,
        account_id=account_id
    )

