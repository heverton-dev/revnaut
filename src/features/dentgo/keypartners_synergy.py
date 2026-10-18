# -*- coding: utf-8 -*-
"""
Vertical Slice: Sinergia KeyPartners <-> DENTGO
Reposição cirúrgica On-Demand pós-operatória e Logística Reversa de Kits Consignados Ociosos.
"""

from __future__ import annotations
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from src.core.database import get_connection, init_db
from src.features.dentgo import service as dentgo_service


def trigger_automatic_replenishment_on_postop(
    postop_event: Dict[str, Any],
    delivery_lat: float,
    delivery_lng: float,
    delivery_address: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Aciona automaticamente reposição de emergência/reabastecimento via DENTGO
    imediatamente após a conclusão e faturamento de um ato cirúrgico KeyPartners.
    """
    init_db()
    order_id = postop_event.get("order_id")
    agreement_id = postop_event.get("agreement_id")

    conn = get_connection()
    try:
        cur = conn.cursor()

        # 1. Recupera os itens consumidos da ordem cirúrgica
        consumed_items = []
        if order_id:
            cur.execute(
                "SELECT consumed_items_json FROM kp_surgical_orders WHERE id = ? AND account_id = ?",
                (order_id, account_id)
            )
            order_row = cur.fetchone()
            if order_row and order_row["consumed_items_json"]:
                try:
                    consumed_items = json.loads(order_row["consumed_items_json"])
                except Exception:
                    consumed_items = []

        total_consumed_qty = sum(int(it.get("quantity", 1)) for it in consumed_items) if consumed_items else int(postop_event.get("consumed_units", 1))

        # 2. Busca CRO do parceiro
        cro_uf = "CRO-SP-00000"
        if agreement_id:
            cur.execute("SELECT partner_cro_uf FROM kp_partner_agreements WHERE id = ?", (agreement_id,))
            agr_row = cur.fetchone()
            if agr_row and agr_row["partner_cro_uf"]:
                cro_uf = agr_row["partner_cro_uf"]

        # 3. Localiza Hub mais próximo com estoque para reposição
        primary_prod_id = consumed_items[0]["product_id"] if consumed_items else "prod-default"
        primary_qty = consumed_items[0].get("quantity", 1) if consumed_items else total_consumed_qty

        candidate_hubs = dentgo_service.search_emergency_supply(
            delivery_lat=delivery_lat,
            delivery_lng=delivery_lng,
            product_id=primary_prod_id,
            required_qty=primary_qty,
            account_id=account_id
        )

        if candidate_hubs:
            best_hub = candidate_hubs[0]
            hub_id = best_hub["hub_id"]
            distance_km = float(best_hub["distance_km"])
            eta_minutes = int(best_hub["estimated_eta_minutes"])
        else:
            cur.execute("SELECT id FROM dentgo_hubs WHERE account_id = ? AND is_active = 1 LIMIT 1", (account_id,))
            hub_row = cur.fetchone()
            hub_id = hub_row["id"] if hub_row else "hub-dentgo-central"
            distance_km = 5.0
            eta_minutes = 45

        # 4. Cria pedido de reposição no DENTGO
        replenishment_order_id = f"dord-{uuid.uuid4().hex[:8]}"
        items_payload = consumed_items or [{"product_id": primary_prod_id, "quantity": total_consumed_qty}]

        cur.execute("""
            INSERT INTO dentgo_orders (
                id, account_id, hub_id, customer_cro_uf, cro_verified,
                delivery_address, delivery_lat, delivery_lng, distance_km,
                estimated_eta_minutes, items_json, subtotal, urgency_fee,
                total_amount, status
            ) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, 0.0, 0.0, 0.0, 'REPLENISHMENT_ORDER_CREATED')
        """, (
            replenishment_order_id, account_id, hub_id, cro_uf,
            delivery_address, delivery_lat, delivery_lng,
            distance_km, eta_minutes, json.dumps(items_payload)
        ))

        # Decrementa estoque no hub se aplicável
        cur.execute("""
            UPDATE dentgo_hub_inventory
            SET quantity_available = MAX(0, quantity_available - ?)
            WHERE hub_id = ? AND product_id = ? AND account_id = ?
        """, (primary_qty, hub_id, primary_prod_id, account_id))

        conn.commit()

        return {
            "status": "REPLENISHMENT_ORDER_CREATED",
            "replenishment_order_id": replenishment_order_id,
            "agreement_id": agreement_id,
            "hub_id": hub_id,
            "items_count": total_consumed_qty
        }
    finally:
        conn.close()


def trigger_dentgo_reverse_pickup(
    kit_serial: str,
    target_agreement_id: Optional[str] = None,
    pickup_address: Optional[str] = None,
    destination_address: Optional[str] = None,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """
    Aciona coleta reversa e transferência de custódia expressa via DENTGO
    para kits consignados ociosos ou com realocação urgente para outro cirurgião.
    """
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        clean_serial = kit_serial.strip().upper()

        cur.execute(
            "SELECT * FROM kp_consignment_kits WHERE serial_number = ? AND account_id = ?",
            (clean_serial, account_id)
        )
        kit = cur.fetchone()
        if not kit:
            raise ValueError(f"Kit consignado {clean_serial} não encontrado")

        origin_agreement_id = kit["current_agreement_id"]

        # Recupera dados cadastrais/sanitários do último registro de custódia
        cur.execute(
            "SELECT * FROM kp_custody_ledger WHERE serial_number = ? ORDER BY created_at DESC LIMIT 1",
            (clean_serial,)
        )
        last_ledg = cur.fetchone()

        prod_id = last_ledg["product_id"] if last_ledg else "prod-kit-guided"
        prod_name = last_ledg["product_name"] if last_ledg else kit["name"]
        anvisa_reg = last_ledg["anvisa_reg"] if last_ledg else "ANVISA-80123450001"
        batch_num = last_ledg["batch_number"] if last_ledg else "LOTE-REV-01"
        unit_val = float(last_ledg["unit_value"]) if last_ledg else 0.0
        exp_date = last_ledg["sterilization_expiry_date"] if last_ledg else (datetime.now(timezone.utc) + timedelta(days=180)).strftime("%Y-%m-%d")

        # 1. Movimentação DEVOLUCAO_INTACTA na origem
        if origin_agreement_id:
            ledg_dev_id = f"ledg-{uuid.uuid4().hex[:8]}"
            cur.execute("""
                INSERT INTO kp_custody_ledger (
                    id, account_id, agreement_id, movement_type, product_id,
                    product_name, anvisa_reg, batch_number, serial_number,
                    quantity, unit_value, total_value, sterilization_expiry_date
                ) VALUES (?, ?, ?, 'DEVOLUCAO_INTACTA', ?, ?, ?, ?, ?, 1, ?, ?, ?)
            """, (
                ledg_dev_id, account_id, origin_agreement_id, prod_id,
                prod_name, anvisa_reg, batch_num, clean_serial,
                unit_val, unit_val, exp_date
            ))

        # 2. Movimentação REMESSA no destino
        if target_agreement_id:
            ledg_rem_id = f"ledg-{uuid.uuid4().hex[:8]}"
            cur.execute("""
                INSERT INTO kp_custody_ledger (
                    id, account_id, agreement_id, movement_type, product_id,
                    product_name, anvisa_reg, batch_number, serial_number,
                    quantity, unit_value, total_value, sterilization_expiry_date
                ) VALUES (?, ?, ?, 'REMESSA', ?, ?, ?, ?, ?, 1, ?, ?, ?)
            """, (
                ledg_rem_id, account_id, target_agreement_id, prod_id,
                prod_name, anvisa_reg, batch_num, clean_serial,
                unit_val, unit_val, exp_date
            ))

        # 3. Atualiza titularidade do kit
        new_agreement = target_agreement_id if target_agreement_id else origin_agreement_id
        cur.execute("""
            UPDATE kp_consignment_kits
            SET current_agreement_id = ?, status = 'IN_FIELD'
            WHERE serial_number = ? AND account_id = ?
        """, (new_agreement, clean_serial, account_id))

        # 4. Registra ordem de coleta reversa no DENTGO
        pickup_order_id = f"dord-rev-{uuid.uuid4().hex[:8]}"
        cur.execute("SELECT id FROM dentgo_hubs WHERE account_id = ? AND is_active = 1 LIMIT 1", (account_id,))
        hub_row = cur.fetchone()
        if not hub_row:
            hub_id = "hub-dentgo-reverse-default"
            cur.execute("""
                INSERT OR IGNORE INTO dentgo_hubs (
                    id, account_id, name, cnpj, latitude, longitude,
                    coverage_radius_km, on_duty_schedule, is_active
                ) VALUES (?, ?, 'Hub DENTGO Reverse Central', '00.000.000/0001-00', -23.5505, -46.6333, 50.0, '24h', 1)
            """, (hub_id, account_id))
        else:
            hub_id = hub_row["id"]

        cur.execute("""
            INSERT INTO dentgo_orders (
                id, account_id, hub_id, customer_cro_uf, cro_verified,
                delivery_address, delivery_lat, delivery_lng, distance_km,
                estimated_eta_minutes, items_json, subtotal, urgency_fee,
                total_amount, status
            ) VALUES (?, ?, ?, 'CRO-SP-00000', 1, ?, 0.0, 0.0, 0.0, 45, ?, 0.0, 0.0, 0.0, 'REVERSE_PICKUP_DISPATCHED')
        """, (
            pickup_order_id, account_id, hub_id,
            destination_address or "Destino Cirúrgico Reversa",
            json.dumps([{"serial_number": clean_serial, "action": "REVERSE_PICKUP"}])
        ))

        conn.commit()

        return {
            "success": True,
            "status": "REVERSE_PICKUP_DISPATCHED",
            "pickup_order_id": pickup_order_id,
            "kit_serial": clean_serial,
            "origin_agreement_id": origin_agreement_id,
            "target_agreement_id": target_agreement_id
        }
    finally:
        conn.close()
