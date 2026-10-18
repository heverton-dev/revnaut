# -*- coding: utf-8 -*-
"""
Vertical Slice: DENTGO Logistics & Marketplace Engine
Geolocalização Haversine, cálculo de ETA cirúrgico e validação estrita de CRO para implantes.
"""

from __future__ import annotations
import json
import math
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from src.core.database import get_connection, init_db
from src.features.contacts.cro_validator import validate_cro_syntax, verify_cro_status


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula a distância ortodrômica em quilômetros pela fórmula de Haversine."""
    R = 6371.0  # Raio médio da Terra em km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


def create_hub(
    name: str,
    cnpj: str,
    latitude: float,
    longitude: float,
    coverage_radius_km: float = 30.0,
    on_duty_schedule: str = "24h",
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Cadastra um novo Hub Logístico Urbano / Seller DENTGO."""
    init_db()
    conn = get_connection()
    try:
        hub_id = f"hub-{uuid.uuid4().hex[:8]}"
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO dentgo_hubs (
                id, account_id, name, cnpj, latitude, longitude,
                coverage_radius_km, on_duty_schedule, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(cnpj) DO UPDATE SET
                name = excluded.name,
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                coverage_radius_km = excluded.coverage_radius_km,
                on_duty_schedule = excluded.on_duty_schedule,
                is_active = 1
        """, (
            hub_id, account_id, name, cnpj.strip(), latitude, longitude,
            coverage_radius_km, on_duty_schedule
        ))
        conn.commit()

        cur.execute("SELECT * FROM dentgo_hubs WHERE cnpj = ?", (cnpj.strip(),))
        return dict(cur.fetchone())
    finally:
        conn.close()


def list_hubs(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    """Lista todos os Hubs ativos do tenant."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM dentgo_hubs WHERE account_id = ? AND is_active = 1 ORDER BY created_at DESC", (account_id,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def add_hub_inventory(
    hub_id: str,
    product_id: str,
    product_name: str,
    anvisa_reg: str,
    batch_number: str,
    quantity_available: int,
    unit_price: float,
    sterilization_expiry_date: str,
    account_id: str = "0f14ffff"
) -> Dict[str, Any]:
    """Registra ou atualiza saldo de estoque de pronta-entrega cirúrgica no Hub."""
    init_db()
    today = datetime.now(timezone.utc).date()
    try:
        exp_date = datetime.strptime(sterilization_expiry_date[:10], "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Data de validade inválida: {sterilization_expiry_date}")

    if (exp_date - today).days < 30:
        raise ValueError("Lote com validade inferior a 30 dias para estoque de emergência")

    conn = get_connection()
    try:
        cur = conn.cursor()
        # Verifica se já existe produto/lote no Hub
        cur.execute("""
            SELECT id, quantity_available FROM dentgo_hub_inventory
            WHERE hub_id = ? AND product_id = ? AND batch_number = ? AND account_id = ?
        """, (hub_id, product_id, batch_number, account_id))
        row = cur.fetchone()

        if row:
            new_qty = int(row["quantity_available"]) + quantity_available
            cur.execute("""
                UPDATE dentgo_hub_inventory
                SET quantity_available = ?, unit_price = ?, sterilization_expiry_date = ?
                WHERE id = ?
            """, (new_qty, unit_price, sterilization_expiry_date, row["id"]))
            inv_id = row["id"]
        else:
            inv_id = f"dinv-{uuid.uuid4().hex[:8]}"
            cur.execute("""
                INSERT INTO dentgo_hub_inventory (
                    id, hub_id, account_id, product_id, product_name,
                    anvisa_reg, batch_number, quantity_available, unit_price,
                    sterilization_expiry_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                inv_id, hub_id, account_id, product_id, product_name,
                anvisa_reg, batch_number, quantity_available, unit_price,
                sterilization_expiry_date
            ))
        conn.commit()

        cur.execute("SELECT * FROM dentgo_hub_inventory WHERE id = ?", (inv_id,))
        return dict(cur.fetchone())
    finally:
        conn.close()


def search_emergency_supply(
    delivery_lat: float,
    delivery_lng: float,
    product_id: str,
    required_qty: int = 1,
    account_id: str = "0f14ffff"
) -> List[Dict[str, Any]]:
    """
    Busca geolocalizada de Hubs com estoque válido em raio de até 30 km.
    Calcula distância precisa Haversine, ETA e taxa de urgência.
    """
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM dentgo_hubs WHERE account_id = ? AND is_active = 1", (account_id,))
        hubs = [dict(r) for r in cur.fetchall()]

        candidates: List[Dict[str, Any]] = []
        for hub in hubs:
            dist = haversine_distance_km(
                float(hub["latitude"]), float(hub["longitude"]),
                delivery_lat, delivery_lng
            )
            max_radius = float(hub.get("coverage_radius_km", 30.0))
            if dist > max_radius:
                continue

            # Verifica estoque no hub (excluindo lotes bloqueados pela ANVISA ou indisponíveis)
            cur.execute("""
                SELECT * FROM dentgo_hub_inventory
                WHERE hub_id = ? AND product_id = ? AND quantity_available >= ? AND account_id = ?
                  AND COALESCE(status, 'AVAILABLE') = 'AVAILABLE'
                  AND batch_number NOT IN (
                      SELECT batch_number FROM anvisa_batch_quarantines
                      WHERE status = 'QUARANTINE_BLOCKED' AND (account_id = ? OR account_id = '0f14ffff')
                  )
            """, (hub["id"], product_id, required_qty, account_id, account_id))
            inv_row = cur.fetchone()
            if not inv_row:
                continue

            # Cálculo de ETA cirúrgico: base de 20 min + 2.5 min/km (limitado a 90 min)
            eta_minutes = min(90, max(25, int(20 + dist * 2.5)))
            # Taxa de urgência cirúrgica: R$ 35.00 base + R$ 3.50/km
            urgency_fee = round(35.0 + dist * 3.5, 2)

            candidates.append({
                "hub_id": hub["id"],
                "hub_name": hub["name"],
                "distance_km": dist,
                "estimated_eta_minutes": eta_minutes,
                "urgency_fee": urgency_fee,
                "product_id": inv_row["product_id"],
                "product_name": inv_row["product_name"],
                "anvisa_reg": inv_row["anvisa_reg"],
                "batch_number": inv_row["batch_number"],
                "quantity_available": int(inv_row["quantity_available"]),
                "unit_price": float(inv_row["unit_price"]),
            })

        # Ordena prioritariamente pelo menor ETA e menor distância
        candidates.sort(key=lambda x: (x["estimated_eta_minutes"], x["distance_km"]))
        return candidates
    finally:
        conn.close()


def create_express_order(
    customer_cro_uf: str,
    delivery_address: str,
    delivery_lat: float,
    delivery_lng: float,
    items: List[Dict[str, Any]],
    account_id: str = "0f14ffff",
    voucher_code: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Cria pedido cirúrgico express com bloqueio estrito de CRO para implantes
    e decremento atômico de estoque para todos os itens no Hub mais próximo.
    """
    init_db()
    # 1. Validação sanitária e status ativo de CRO
    cro_check = verify_cro_status(customer_cro_uf)
    if not cro_check.get("is_valid", False) or not cro_check.get("verified", False) or cro_check.get("status") != "ATIVO":
        raise ValueError("Checkout bloqueado: Exige validação ativa de CRO para aquisição de dispositivos implantáveis")

    if not items:
        raise ValueError("O pedido deve conter ao menos um item cirúrgico")

    primary_item = items[0]
    p_id = primary_item["product_id"]
    p_qty = int(primary_item.get("quantity", 1))

    # 2. Localização do Hub ótimo com estoque
    hubs_found = search_emergency_supply(
        delivery_lat=delivery_lat,
        delivery_lng=delivery_lng,
        product_id=p_id,
        required_qty=p_qty,
        account_id=account_id
    )

    if not hubs_found:
        raise ValueError("Nenhum Hub parceiro DENTGO disponível com estoque válido para este raio cirúrgico")

    best_match = hubs_found[0]
    hub_id = best_match["hub_id"]
    urgency_fee = 0.0 if (voucher_code and str(voucher_code).strip()) else float(best_match["urgency_fee"])
    distance_km = best_match["distance_km"]
    eta = best_match["estimated_eta_minutes"]

    conn = get_connection()
    try:
        cur = conn.cursor()
        order_id = f"dord-{uuid.uuid4().hex[:8]}"

        subtotal = 0.0
        for item in items:
            item_prod_id = item["product_id"]
            item_qty = int(item.get("quantity", 1))
            cur.execute("""
                SELECT id, unit_price, quantity_available, batch_number, COALESCE(status, 'AVAILABLE') AS status
                FROM dentgo_hub_inventory
                WHERE hub_id = ? AND product_id = ? AND account_id = ?
                ORDER BY quantity_available DESC
                LIMIT 1
            """, (hub_id, item_prod_id, account_id))
            inv_row = cur.fetchone()
            if not inv_row:
                raise ValueError(f"Produto {item_prod_id} sem saldo disponível no Hub {hub_id}")

            if inv_row["status"] != "AVAILABLE" or int(inv_row["quantity_available"]) < item_qty:
                raise ValueError(f"Estoque insuficiente ou bloqueado para o item {item_prod_id} no Hub {hub_id}")

            cur.execute("""
                SELECT status FROM anvisa_batch_quarantines
                WHERE batch_number = ? AND status = 'QUARANTINE_BLOCKED'
                  AND (account_id = ? OR account_id = '0f14ffff')
                LIMIT 1
            """, (inv_row["batch_number"], account_id))
            if cur.fetchone():
                raise ValueError(f"Lote {inv_row['batch_number']} bloqueado por quarentena sanitária ANVISA")

            item_unit_price = float(inv_row["unit_price"])
            subtotal += item_unit_price * item_qty

            cur.execute("""
                UPDATE dentgo_hub_inventory
                SET quantity_available = quantity_available - ?
                WHERE id = ?
            """, (item_qty, inv_row["id"]))

        subtotal = round(subtotal, 2)
        total_amount = round(subtotal + urgency_fee, 2)

        items_json = json.dumps(items, ensure_ascii=False)
        cur.execute("""
            INSERT INTO dentgo_orders (
                id, account_id, hub_id, customer_cro_uf, cro_verified,
                delivery_address, delivery_lat, delivery_lng, distance_km,
                estimated_eta_minutes, items_json, subtotal, urgency_fee,
                total_amount, status
            ) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ORDER_PLACED')
        """, (
            order_id, account_id, hub_id, customer_cro_uf,
            delivery_address, delivery_lat, delivery_lng, distance_km,
            eta, items_json, subtotal, urgency_fee, total_amount
        ))
        conn.commit()

        cur.execute("SELECT * FROM dentgo_orders WHERE id = ?", (order_id,))
        return dict(cur.fetchone())
    finally:
        conn.close()


def get_order(order_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Retorna dados de um pedido DENTGO."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM dentgo_orders WHERE id = ? AND account_id = ?", (order_id, account_id))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Pedido {order_id} não encontrado")
        return dict(row)
    finally:
        conn.close()


def list_orders(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    """Lista todos os pedidos express do tenant."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM dentgo_orders WHERE account_id = ? ORDER BY created_at DESC", (account_id,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_hub_product_inventory(hub_id: str, product_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Retorna saldo de estoque de um produto no Hub."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM dentgo_hub_inventory
            WHERE hub_id = ? AND product_id = ? AND account_id = ?
        """, (hub_id, product_id, account_id))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Item {product_id} não encontrado no Hub {hub_id}")
        return dict(row)
    finally:
        conn.close()
