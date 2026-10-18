# -*- coding: utf-8 -*-
"""
Vertical Slice: KeyPartners Custody Service
Motor de Gestão de Consignação Cirúrgica, Limites de Crédito e Rastreabilidade Sanitária ANVISA.
"""

from __future__ import annotations
from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List, Optional
from src.core.database import get_connection, init_db


def create_partner_agreement(
    partner_name: str,
    partner_cro_uf: Optional[str] = None,
    tier: str = "SILVER",
    credit_limit: float = 15000.0,
    min_monthly_revenue: float = 0.0,
    max_turnover_days: int = 60,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Cria novo acordo de parceria e consignação odontológica."""
    init_db()
    conn = get_connection()
    try:
        agr_id = f"kpa-{uuid.uuid4().hex[:8]}"
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO kp_partner_agreements (
                id, account_id, partner_name, partner_cro_uf, tier,
                credit_limit, used_credit, min_monthly_revenue,
                max_turnover_days, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, 0.0, ?, ?, 1)
        """, (
            agr_id, account_id, partner_name, partner_cro_uf, tier,
            credit_limit, min_monthly_revenue, max_turnover_days
        ))
        conn.commit()

        cur.execute("SELECT * FROM kp_partner_agreements WHERE id = ?", (agr_id,))
        row = cur.fetchone()
        return dict(row)
    finally:
        conn.close()


def list_partner_agreements(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    """Lista todos os acordos de parceria do tenant."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM kp_partner_agreements
            WHERE account_id = ?
            ORDER BY created_at DESC
        """, (account_id,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def register_consignment_kit(
    serial_number: str,
    name: str,
    composition_json: Optional[str] = "{}",
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Registra um kit cirúrgico/protético seriadocom rastreio por QR Code."""
    init_db()
    conn = get_connection()
    try:
        kit_id = f"kit-{uuid.uuid4().hex[:8]}"
        qr_code = f"KEYPARTNERS:KIT:{serial_number.strip().upper()}"
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO kp_consignment_kits (
                id, account_id, serial_number, qr_code, name,
                composition_json, status, current_agreement_id
            ) VALUES (?, ?, ?, ?, ?, ?, 'IN_STOCK', NULL)
            ON CONFLICT(serial_number) DO UPDATE SET
                name = excluded.name,
                composition_json = excluded.composition_json,
                status = 'IN_STOCK',
                current_agreement_id = NULL
        """, (
            kit_id, account_id, serial_number.strip().upper(), qr_code,
            name, composition_json or "{}"
        ))
        conn.commit()

        cur.execute("SELECT * FROM kp_consignment_kits WHERE serial_number = ?", (serial_number.strip().upper(),))
        row = cur.fetchone()
        return dict(row)
    finally:
        conn.close()


def dispatch_consignment_custody(
    agreement_id: str,
    items: List[Dict[str, Any]],
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Realiza a remessa de custódia cirúrgica para a clínica/cirurgião.
    Aplica Quality Gates de Negócio:
    1. Validade sanitária ANVISA >= 30 dias a partir de hoje.
    2. Bloqueio estrito de limite de crédito consignado.
    """
    init_db()
    if not items:
        raise ValueError("A remessa deve conter pelo menos um item")

    # 1. Auditoria sanitária de validade
    today = datetime.now(timezone.utc).date()
    for item in items:
        expiry_str = item.get("sterilization_expiry_date")
        if not expiry_str:
            raise ValueError("Data de validade da esterilização é obrigatória para cada lote")
        try:
            exp_date = datetime.strptime(expiry_str[:10], "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Formato de data inválido: {expiry_str}")

        days_remaining = (exp_date - today).days
        if days_remaining < 30:
            raise ValueError("Lote vencido ou com validade inferior a 30 dias para consignação sanitária")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM kp_partner_agreements WHERE id = ? AND account_id = ?", (agreement_id, account_id))
        agr = cur.fetchone()
        if not agr:
            raise ValueError(f"Acordo de parceria {agreement_id} não encontrado")

        credit_limit = float(agr["credit_limit"])
        current_used = float(agr["used_credit"])

        total_remittance = sum(float(it["unit_value"]) * int(it.get("quantity", 1)) for it in items)

        if current_used + total_remittance > credit_limit:
            raise ValueError("Limite de crédito consignado excedido para este parceiro")

        # Registra movimentações no razão imutável (kp_custody_ledger)
        for it in items:
            ledg_id = f"ledg-{uuid.uuid4().hex[:8]}"
            qty = int(it.get("quantity", 1))
            u_val = float(it["unit_value"])
            tot_val = u_val * qty
            serial = it.get("serial_number")

            cur.execute("""
                INSERT INTO kp_custody_ledger (
                    id, account_id, agreement_id, movement_type, product_id,
                    product_name, anvisa_reg, batch_number, serial_number,
                    quantity, unit_value, total_value, sterilization_expiry_date
                ) VALUES (?, ?, ?, 'REMESSA', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ledg_id, account_id, agreement_id, it["product_id"],
                it["product_name"], it["anvisa_reg"], it["batch_number"],
                serial, qty, u_val, tot_val, it["sterilization_expiry_date"]
            ))

            # Se o item é um kit seriado registrado, atualiza status para IN_FIELD
            if serial:
                cur.execute("""
                    UPDATE kp_consignment_kits
                    SET status = 'IN_FIELD', current_agreement_id = ?
                    WHERE serial_number = ? AND account_id = ?
                """, (agreement_id, serial.strip().upper(), account_id))

        new_used_credit = current_used + total_remittance
        cur.execute("""
            UPDATE kp_partner_agreements
            SET used_credit = ?
            WHERE id = ?
        """, (new_used_credit, agreement_id))

        conn.commit()

        return {
            "status": "DISPATCHED",
            "agreement_id": agreement_id,
            "total_remittance_value": total_remittance,
            "updated_used_credit": new_used_credit,
            "available_credit": max(0.0, credit_limit - new_used_credit),
            "entries_count": len(items)
        }
    finally:
        conn.close()


def get_partner_custody_summary(agreement_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Retorna saldo consolidado e extrato de itens em posse da clínica."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM kp_partner_agreements WHERE id = ? AND account_id = ?", (agreement_id, account_id))
        agr = cur.fetchone()
        if not agr:
            raise ValueError(f"Acordo de parceria {agreement_id} não encontrado")

        cur.execute("""
            SELECT id, agreement_id, movement_type, product_id, product_name,
                   anvisa_reg, batch_number, serial_number, quantity,
                   unit_value, total_value, sterilization_expiry_date, created_at
            FROM kp_custody_ledger
            WHERE agreement_id = ? AND account_id = ?
            ORDER BY created_at DESC
        """, (agreement_id, account_id))
        ledger_rows = [dict(r) for r in cur.fetchall()]

        total_value = sum(float(r["total_value"]) for r in ledger_rows if r["movement_type"] == "REMESSA")
        total_items = sum(int(r["quantity"]) for r in ledger_rows if r["movement_type"] == "REMESSA")
        credit_limit = float(agr["credit_limit"])
        used_credit = float(agr["used_credit"])

        return {
            "agreement_id": agreement_id,
            "partner_name": agr["partner_name"],
            "partner_cro_uf": agr["partner_cro_uf"],
            "tier": agr["tier"],
            "credit_limit": credit_limit,
            "used_credit": used_credit,
            "available_credit": max(0.0, credit_limit - used_credit),
            "total_custodied_value": total_value,
            "total_items_count": total_items,
            "ledger_entries": ledger_rows
        }
    finally:
        conn.close()
