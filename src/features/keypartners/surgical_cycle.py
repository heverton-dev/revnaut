# -*- coding: utf-8 -*-
"""
Vertical Slice: KeyPartners Surgical Cycle Engine
Máquina de estados para remessa cirúrgica, despacho, conferência de lacre e conciliação pós-operatória.
"""

from __future__ import annotations
import json
import uuid
from typing import Any, Dict, List, Optional
from src.core.database import get_connection, init_db
from src.core.events import StreamName, default_event_bus
from src.features.keypartners import service as kp_service
from src.features.dentgo import keypartners_synergy


def create_surgical_request(
    agreement_id: str,
    patient_identifier: Optional[str],
    surgery_date: str,
    items: List[Dict[str, Any]],
    field_consultant_id: Optional[str] = None,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Cria solicitação de remessa para cirurgia agendada (SOLICITADO_FIELD)."""
    init_db()
    if not items:
        raise ValueError("A solicitação cirúrgica deve conter ao menos um item")

    conn = get_connection()
    try:
        cur = conn.cursor()
        order_id = f"surg-{uuid.uuid4().hex[:8]}"
        sanitized_items = []
        for it in items:
            it_dict = dict(it)
            it_dict["sterilization_expiry_date"] = it_dict.get("sterilization_expiry_date") or "2027-12-31"
            sanitized_items.append(it_dict)
        items_json = json.dumps(sanitized_items, ensure_ascii=False)

        cur.execute("""
            INSERT INTO kp_surgical_orders (
                id, account_id, agreement_id, patient_identifier,
                surgery_date, status, field_consultant_id, remitted_items_json
            ) VALUES (?, ?, ?, ?, ?, 'SOLICITADO_FIELD', ?, ?)
        """, (
            order_id, account_id, agreement_id, patient_identifier,
            surgery_date, field_consultant_id, items_json
        ))
        conn.commit()

        cur.execute("SELECT * FROM kp_surgical_orders WHERE id = ?", (order_id,))
        return dict(cur.fetchone())
    finally:
        conn.close()


def approve_surgical_request(
    order_id: str,
    inside_analyst_id: Optional[str] = "usr-inside-01",
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Analista Interno homologa a solicitação cirúrgica (APROVADO_INSIDE)."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM kp_surgical_orders WHERE id = ? AND account_id = ?", (order_id, account_id))
        order = cur.fetchone()
        if not order:
            raise ValueError(f"Ordem cirúrgica {order_id} não encontrada")

        cur.execute("""
            UPDATE kp_surgical_orders
            SET status = 'APROVADO_INSIDE',
                inside_analyst_id = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (inside_analyst_id, order_id))
        conn.commit()

        cur.execute("SELECT * FROM kp_surgical_orders WHERE id = ?", (order_id,))
        return dict(cur.fetchone())
    finally:
        conn.close()


def dispatch_surgical_order(
    order_id: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Efetua o despacho da maleta e registra os itens no razão de custódia (EM_POSSE_CLINICA)."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM kp_surgical_orders WHERE id = ? AND account_id = ?", (order_id, account_id))
        order = cur.fetchone()
        if not order:
            raise ValueError(f"Ordem cirúrgica {order_id} não encontrada")

        order_dict = dict(order)
        default_exp = order_dict.get("sterilization_expiry_date") or "2027-12-31"
        items = json.loads(order["remitted_items_json"])
        for it in items:
            if not it.get("sterilization_expiry_date"):
                it["sterilization_expiry_date"] = default_exp
        agreement_id = order["agreement_id"]

        # Despacha e audita validade e limites através do kp_service
        kp_service.dispatch_consignment_custody(
            agreement_id=agreement_id,
            items=items,
            account_id=account_id
        )

        cur.execute("""
            UPDATE kp_surgical_orders
            SET status = 'EM_POSSE_CLINICA',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (order_id,))
        conn.commit()

        cur.execute("SELECT * FROM kp_surgical_orders WHERE id = ?", (order_id,))
        return dict(cur.fetchone())
    finally:
        conn.close()


def report_surgical_postop(
    order_id: str,
    consumed_items: List[Dict[str, Any]],
    seal_photo_r2_key: Optional[str] = None,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Conciliação pós-cirúrgica:
    1. Registra consumo real dos lotes implantados no paciente.
    2. Gera Pedido de Venda Faturável (CFOP 5.113 / 6.113).
    3. Abate do saldo custodiado da clínica apenas o que foi implantado.
    4. Arquiva foto comprobatória do lacre dos itens não utilizados.
    """
    init_db()
    if not consumed_items:
        raise ValueError("O reporte pós-operatório deve conter os itens consumidos")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM kp_surgical_orders WHERE id = ? AND account_id = ?", (order_id, account_id))
        order = cur.fetchone()
        if not order:
            raise ValueError(f"Ordem cirúrgica {order_id} não encontrada")

        agreement_id = order["agreement_id"]
        remitted_items = json.loads(order["remitted_items_json"])
        remitted_total_qty = sum(int(it.get("quantity", 1)) for it in remitted_items)

        consumed_total_qty = sum(int(it.get("quantity", 1)) for it in consumed_items)
        billed_amount = sum(float(it["unit_value"]) * int(it.get("quantity", 1)) for it in consumed_items)
        retained_units = max(0, remitted_total_qty - consumed_total_qty)

        billing_order_id = f"ped-cfop-{uuid.uuid4().hex[:8]}"

        # Grava consumo cirúrgico no razão imutável (kp_custody_ledger)
        for it in consumed_items:
            ledg_id = f"ledg-cons-{uuid.uuid4().hex[:8]}"
            qty = int(it.get("quantity", 1))
            u_val = float(it["unit_value"])
            tot_val = u_val * qty
            cur.execute("""
                INSERT INTO kp_custody_ledger (
                    id, account_id, agreement_id, movement_type, product_id,
                    product_name, anvisa_reg, batch_number, serial_number,
                    quantity, unit_value, total_value, sterilization_expiry_date
                ) VALUES (?, ?, ?, 'CONSUMO_CIRURGICO', ?, ?, ?, ?, NULL, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                ledg_id, account_id, agreement_id, it["product_id"],
                it["product_name"], it["anvisa_reg"], it["batch_number"],
                qty, u_val, tot_val
            ))

        # Atualiza crédito utilizado do parceiro deduzindo o valor que foi consumido e agora convertido em venda
        cur.execute("SELECT used_credit FROM kp_partner_agreements WHERE id = ?", (agreement_id,))
        curr_used = cur.fetchone()["used_credit"]
        new_used = max(0.0, float(curr_used) - billed_amount)
        cur.execute("UPDATE kp_partner_agreements SET used_credit = ? WHERE id = ?", (new_used, agreement_id))

        # Atualiza a ordem cirúrgica para FATURADO_E_REPOSTO
        consumed_json = json.dumps(consumed_items, ensure_ascii=False)
        cur.execute("""
            UPDATE kp_surgical_orders
            SET status = 'FATURADO_E_REPOSTO',
                consumed_items_json = ?,
                seal_photo_r2_key = ?,
                billing_order_id = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (consumed_json, seal_photo_r2_key, billing_order_id, order_id))

        conn.commit()
    finally:
        conn.close()

    postop_payload = {
        "status": "FATURADO_E_REPOSTO",
        "order_id": order_id,
        "agreement_id": agreement_id,
        "billed_amount": billed_amount,
        "cfop": "5.113",
        "consumed_units": consumed_total_qty,
        "retained_units": retained_units,
        "billing_order_id": billing_order_id,
    }

    # Publica evento keypartners.postop_reported no barramento
    default_event_bus.publish_sync(
        stream=StreamName.KEYPARTNERS,
        event_type="keypartners.postop_reported",
        account_id=account_id,
        payload=postop_payload,
    )

    # Dispara reposição cirúrgica automática via DENTGO
    try:
        repl_res = keypartners_synergy.trigger_automatic_replenishment_on_postop(
            postop_event=postop_payload,
            delivery_lat=-23.5615,
            delivery_lng=-46.6560,
            delivery_address=f"Reposição Pós-Cirúrgica Acordo {agreement_id}",
            account_id=account_id,
        )
        postop_payload["replenishment_order_id"] = repl_res.get("replenishment_order_id")
    except Exception:
        pass

    return postop_payload


def get_surgical_order(order_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Retorna detalhes da ordem cirúrgica."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM kp_surgical_orders WHERE id = ? AND account_id = ?", (order_id, account_id))
        order = cur.fetchone()
        if not order:
            raise ValueError(f"Ordem cirúrgica {order_id} não encontrada")
        return dict(order)
    finally:
        conn.close()


def list_surgical_orders(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    """Lista todas as ordens cirúrgicas do tenant."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM kp_surgical_orders WHERE account_id = ? ORDER BY created_at DESC",
            (account_id,),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
