# -*- coding: utf-8 -*-
"""
Vertical Slice: DENTGO Financial Split & Marketplace Monetization Engine
Cálculo e segregação transacional na fonte: Seller (Indústria/Dental), Courier (Last-mile) e Take-Rate RevNault.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from src.core.database import get_connection, init_db


def process_order_financial_split(
    order_id: str,
    platform_take_rate_pct: float = 5.0,
    payment_method: str = "PIX_INSTANT",
    agreement_id: Optional[str] = None,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Calcula e registra a segregação financeira centavo a centavo do pedido DENTGO.
    Suporta liquidação instantânea via Pix ou faturamento corporativo quinzenal KeyPartners.
    """
    init_db()
    if payment_method not in ("PIX_INSTANT", "CORPORATE_CREDIT"):
        raise ValueError(f"Método de pagamento inválido: {payment_method}")

    conn = get_connection()
    try:
        cur = conn.cursor()

        # 1. Recupera o pedido DENTGO
        cur.execute("SELECT * FROM dentgo_orders WHERE id = ? AND account_id = ?", (order_id, account_id))
        order = cur.fetchone()
        if not order:
            raise ValueError(f"Pedido DENTGO {order_id} não encontrado")

        gross_amount = round(float(order["total_amount"]), 2)
        items_amount = round(float(order["subtotal"]), 2)
        delivery_fee_total = round(float(order["urgency_fee"]), 2)

        # 2. Cálculo determinístico das parcelas
        take_rate = float(platform_take_rate_pct)
        platform_fee_amount = round(items_amount * (take_rate / 100.0), 2)
        seller_net_payout = round(items_amount - platform_fee_amount, 2)
        courier_net_payout = round(delivery_fee_total, 2)

        # 3. Conciliação estrita sem resíduos de arredondamento
        calculated_total = round(seller_net_payout + courier_net_payout + platform_fee_amount, 2)
        diff = round(gross_amount - calculated_total, 2)
        if diff != 0.0:
            platform_fee_amount = round(platform_fee_amount + diff, 2)

        # 4. Tratamento do método de pagamento
        if payment_method == "CORPORATE_CREDIT":
            if not agreement_id:
                raise ValueError("Faturamento corporativo exige um agreement_id de parceria KeyPartners")

            cur.execute("SELECT * FROM kp_partner_agreements WHERE id = ? AND account_id = ?", (agreement_id, account_id))
            agr_row = cur.fetchone()
            if not agr_row:
                raise ValueError(f"Acordo KeyPartners {agreement_id} não encontrado")
            agr = dict(agr_row)
            credit_limit = float(agr["credit_limit"])
            used_credit = float(agr.get("used_credit") or 0.0)

            if used_credit + gross_amount > credit_limit:
                raise ValueError("Limite de crédito corporativo excedido para este parceiro")

            new_used = round(used_credit + gross_amount, 2)
            cur.execute("UPDATE kp_partner_agreements SET used_credit = ? WHERE id = ?", (new_used, agreement_id))
            settlement_status = "INVOICED_CORPORATE"
        else:
            settlement_status = "SETTLED"

        # 5. Registra o split financeiro
        split_id = f"split-{uuid.uuid4().hex[:8]}"
        cur.execute("""
            INSERT INTO dentgo_financial_splits (
                id, account_id, order_id, gross_amount, items_amount,
                delivery_fee_total, platform_take_rate_pct, platform_fee_amount,
                courier_net_payout, seller_net_payout, payment_method,
                agreement_id, settlement_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            split_id, account_id, order_id, gross_amount, items_amount,
            delivery_fee_total, take_rate, platform_fee_amount,
            courier_net_payout, seller_net_payout, payment_method,
            agreement_id, settlement_status
        ))

        conn.commit()

        cur.execute("SELECT * FROM dentgo_financial_splits WHERE id = ?", (split_id,))
        return dict(cur.fetchone())
    finally:
        conn.close()


def get_order_financial_split(order_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Retorna o split financeiro vinculado a um pedido DENTGO."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM dentgo_financial_splits WHERE order_id = ? AND account_id = ? ORDER BY created_at DESC LIMIT 1",
            (order_id, account_id)
        )
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Nenhum split financeiro registrado para o pedido {order_id}")
        return dict(row)
    finally:
        conn.close()


def list_financial_splits(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    """Lista todos os splits financeiros processados no tenant."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM dentgo_financial_splits WHERE account_id = ? ORDER BY created_at DESC",
            (account_id,)
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
