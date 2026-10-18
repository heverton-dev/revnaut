# -*- coding: utf-8 -*-
"""
Vertical Slice: Liquidação Inteligente FEFO de Lotes com Validade Curta
via Flash Deals no DENTGO (First-Expired, First-Out).
"""

from __future__ import annotations
import json
import math
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.core.database import get_connection, init_db
from src.core.events import EventBus, StreamName


# Coordenadas de referência para geolocalização determinística de municípios
CITY_COORDINATES: Dict[str, tuple[float, float]] = {
    "campinas": (-22.9056, -47.0608),
    "paulinia": (-22.7639, -47.1539),
    "paulínia": (-22.7639, -47.1539),
    "valinhos": (-22.9708, -46.9961),
    "vinhedo": (-23.0297, -46.9750),
    "sumare": (-22.8214, -47.2667),
    "sumaré": (-22.8214, -47.2667),
    "hortolandia": (-22.8583, -47.2200),
    "hortolândia": (-22.8583, -47.2200),
    "indaiatuba": (-23.0903, -47.2181),
    "americana": (-22.7394, -47.3314),
    "sao paulo": (-23.5505, -46.6333),
    "são paulo": (-23.5505, -46.6333),
    "santos": (-23.9608, -46.3336),
    "rio de janeiro": (-22.9068, -43.1729),
    "belo horizonte": (-19.9167, -43.9345),
    "curitiba": (-25.4284, -49.2733),
}


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula a distância ortodrômica em quilômetros pela fórmula de Haversine."""
    R = 6371.0
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


def get_contact_coordinates(contact: Dict[str, Any]) -> Optional[tuple[float, float]]:
    """Obtém as coordenadas geográficas do contato a partir dos campos diretos ou da cidade."""
    lat = contact.get("latitude")
    lng = contact.get("longitude")
    if lat is not None and lng is not None:
        try:
            return (float(lat), float(lng))
        except (ValueError, TypeError):
            pass

    city = (contact.get("city") or "").strip().lower()
    if city in CITY_COORDINATES:
        return CITY_COORDINATES[city]

    return None


def scan_and_generate_flash_deals(
    reference_date: Optional[str] = None,
    discount_percentage: float = 35.0,
    max_target_surgeons: int = 50,
    radius_km: float = 50.0,
    account_id: str = "0f14ffff",
) -> Dict[str, Any]:
    """
    Varredura ativa FEFO (First-Expired, First-Out):
    1. Identifica lotes em dentgo_hub_inventory com validade entre 6 e 9 meses (180 a 275 dias).
    2. Calcula preço promocional Flash Deal.
    3. Cruza os cirurgiões num raio de 50 km com perfil de consumo daquele produto.
    4. Cria a oferta Flash Deal e despacha mensagens via WhatsApp (omnichannel) com link em 1 clique.
    """
    init_db()
    if reference_date:
        try:
            ref_dt = datetime.strptime(reference_date[:10], "%Y-%m-%d")
        except Exception:
            ref_dt = datetime.now()
    else:
        ref_dt = datetime.now()

    conn = get_connection()
    created_deals: List[Dict[str, Any]] = []
    scanned_batches_count = 0

    try:
        cur = conn.cursor()

        # Busca estoque disponível nos hubs com dados de localização do hub
        cur.execute("""
            SELECT i.id as inventory_id, i.hub_id, i.account_id, i.product_id,
                   i.product_name, i.anvisa_reg, i.batch_number, i.quantity_available,
                   i.unit_price, i.sterilization_expiry_date,
                   h.name as hub_name, h.latitude as hub_lat, h.longitude as hub_lng,
                   h.coverage_radius_km
            FROM dentgo_hub_inventory i
            JOIN dentgo_hubs h ON i.hub_id = h.id
            WHERE i.account_id = ? AND i.quantity_available > 0
        """, (account_id,))

        inventory_rows = [dict(r) for r in cur.fetchall()]
        scanned_batches_count = len(inventory_rows)

        # Carrega cirurgiões cadastrados
        cur.execute("""
            SELECT id, name, email, phone, cro, cro_uf, city, state, tags,
                   monthly_implants_volume, score, customer_type
            FROM contacts
            WHERE account_id = ?
        """, (account_id,))
        surgeons = [dict(r) for r in cur.fetchall()]

        for item in inventory_rows:
            expiry_str = item["sterilization_expiry_date"][:10]
            try:
                exp_dt = datetime.strptime(expiry_str, "%Y-%m-%d")
            except Exception:
                continue

            days_to_expire = (exp_dt - ref_dt).days
            months_to_expire = round(days_to_expire / 30.0, 1)

            # Janela de alerta FEFO: validade esterilizante residual entre 6 e 9 meses (180 a 275 dias)
            if not (180 <= days_to_expire <= 275):
                continue

            # Verifica se já existe oferta ativa para este lote
            cur.execute("""
                SELECT id FROM fefo_flash_deals
                WHERE inventory_id = ? AND status = 'ACTIVE'
            """, (item["inventory_id"],))
            existing_deal = cur.fetchone()
            if existing_deal:
                continue

            orig_price = float(item["unit_price"])
            flash_price = round(orig_price * (1.0 - discount_percentage / 100.0), 2)
            deal_id = f"fefo-{uuid.uuid4().hex[:8]}"
            checkout_url = f"https://dentgo.app/flash-deals/{deal_id}"

            hub_lat = float(item["hub_lat"])
            hub_lng = float(item["hub_lng"])
            hub_name = item["hub_name"]

            # Segmentação de cirurgiões num raio de 50 km com consumo compatível
            matched_surgeons: List[Dict[str, Any]] = []
            is_biomaterial = any(k in item["product_id"].upper() or k in item["product_name"].lower() for k in ["BIO", "MEM", "ENXERTO", "COLAGENO", "COLÁGENO"])

            for s in surgeons:
                coords = get_contact_coordinates(s)
                in_radius = False

                if coords:
                    dist = haversine_distance_km(hub_lat, hub_lng, coords[0], coords[1])
                    if dist <= radius_km:
                        in_radius = True
                else:
                    # Fallback por correspondência textual de cidade
                    s_city = (s.get("city") or "").strip().lower()
                    if s_city and s_city in hub_name.lower():
                        in_radius = True

                if not in_radius:
                    continue

                # Valida compatibilidade de produto / alto giro
                s_tags = s.get("tags") or "[]"
                if is_biomaterial:
                    consumes = "biomateriais" in s_tags.lower() or "enxerto" in s_tags.lower() or (s.get("monthly_implants_volume") or 0) > 0
                else:
                    consumes = "implante" in s_tags.lower() or (s.get("monthly_implants_volume") or 0) > 0

                if consumes or s.get("customer_type") == "CIRURGIAO":
                    matched_surgeons.append(s)

            # Ordena por volume de consumo e score
            matched_surgeons.sort(
                key=lambda s: (s.get("monthly_implants_volume") or 0, s.get("score") or 0),
                reverse=True
            )
            targeted_surgeons = matched_surgeons[:max_target_surgeons]

            # Registra a oferta no banco
            cur.execute("""
                INSERT INTO fefo_flash_deals (
                    id, account_id, hub_id, hub_name, inventory_id,
                    product_id, product_name, batch_number, original_quantity,
                    available_quantity, original_unit_price, discount_percentage,
                    flash_unit_price, sterilization_expiry_date, months_to_expire,
                    target_surgeons_count, status, checkout_one_click_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
            """, (
                deal_id, account_id, item["hub_id"], hub_name, item["inventory_id"],
                item["product_id"], item["product_name"], item["batch_number"],
                item["quantity_available"], item["quantity_available"], orig_price,
                discount_percentage, flash_price, expiry_str, months_to_expire,
                len(targeted_surgeons), checkout_url
            ))

            # Dispara campanha no WhatsApp para cada cirurgião segmentado
            for surgeon in targeted_surgeons:
                s_phone = surgeon.get("phone") or ""
                s_name = surgeon.get("name") or "Doutor(a)"
                s_cro = f"{surgeon.get('cro', '')}-{surgeon.get('cro_uf', '')}".strip("-")
                one_click_link = f"{checkout_url}?cro={s_cro}"

                msg_content = (
                    f"Olá {s_name}! Flash Deal DENTGO ({discount_percentage:.0f}% OFF): "
                    f"Lote exclusivo de {item['product_name']} (Lote {item['batch_number']}) "
                    f"com validade de {months_to_expire} meses no {hub_name}. "
                    f"De R$ {orig_price:.2f} por apenas R$ {flash_price:.2f}/un. "
                    f"Garanta suas unidades em 1 clique: {one_click_link}"
                )

                msg_id = f"msg-fefo-{uuid.uuid4().hex[:8]}"
                clean_phone = s_phone.replace("+", "").replace("-", "").replace(" ", "")
                remote_jid = f"{clean_phone}@s.whatsapp.net" if clean_phone else "cirurgiao@s.whatsapp.net"

                cur.execute("""
                    INSERT INTO omnichannel_messages (
                        id, account_id, instance_name, remote_jid, sender_phone,
                        message_type, content, from_me
                    ) VALUES (?, ?, 'evolution_main', ?, ?, 'text', ?, 1)
                """, (msg_id, account_id, remote_jid, s_phone, msg_content))

            deal_payload = {
                "id": deal_id,
                "account_id": account_id,
                "hub_id": item["hub_id"],
                "hub_name": hub_name,
                "inventory_id": item["inventory_id"],
                "product_id": item["product_id"],
                "product_name": item["product_name"],
                "batch_number": item["batch_number"],
                "original_quantity": item["quantity_available"],
                "available_quantity": item["quantity_available"],
                "original_unit_price": orig_price,
                "discount_percentage": discount_percentage,
                "flash_unit_price": flash_price,
                "sterilization_expiry_date": expiry_str,
                "months_to_expire": months_to_expire,
                "target_surgeons_count": len(targeted_surgeons),
                "status": "ACTIVE",
                "checkout_one_click_url": checkout_url,
                "target_surgeons": targeted_surgeons,
            }
            created_deals.append(deal_payload)

        conn.commit()
    finally:
        conn.close()

    # Publica telemetria no EventBus
    for d in created_deals:
        try:
            EventBus.publish_sync(
                StreamName.AUDIT,
                {
                    "event": "dentgo.fefo_flash_deal_created",
                    "deal_id": d["id"],
                    "product_id": d["product_id"],
                    "batch_number": d["batch_number"],
                    "available_quantity": d["available_quantity"],
                    "flash_unit_price": d["flash_unit_price"],
                }
            )
        except Exception:
            pass

    return {
        "scanned_batches": scanned_batches_count,
        "created_deals_count": len(created_deals),
        "reference_date": ref_dt.strftime("%Y-%m-%d"),
        "created_deals": created_deals,
    }


def reserve_flash_deal_batch(
    deal_id: str,
    surgeon_cro_uf: str,
    surgeon_name: str,
    quantity: int,
    contact_id: Optional[int] = None,
    account_id: str = "0f14ffff",
) -> Dict[str, Any]:
    """
    Reserva atômica de unidades do lote Flash Deal no momento do clique.
    Deduz saldo do estoque do Hub e atualiza status para EXHAUSTED quando zerar.
    """
    init_db()
    if quantity <= 0:
        raise ValueError("Quantidade para reserva deve ser maior que zero.")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, account_id, hub_id, inventory_id, product_name,
                   available_quantity, flash_unit_price, status
            FROM fefo_flash_deals
            WHERE id = ? AND account_id = ?
        """, (deal_id, account_id))

        deal = cur.fetchone()
        if not deal:
            raise ValueError(f"Flash deal '{deal_id}' não encontrado.")

        if deal["status"] != "ACTIVE" or deal["available_quantity"] < quantity:
            raise ValueError("Estoque insuficiente ou lote esgotado para este Flash Deal.")

        current_avail = deal["available_quantity"]
        new_avail = current_avail - quantity
        new_status = "EXHAUSTED" if new_avail == 0 else "ACTIVE"
        total_amount = round(quantity * float(deal["flash_unit_price"]), 2)

        # Baixa atômica no Flash Deal
        cur.execute("""
            UPDATE fefo_flash_deals
            SET available_quantity = ?, status = ?
            WHERE id = ?
        """, (new_avail, new_status, deal_id))

        # Baixa atômica no estoque do Hub (dentgo_hub_inventory)
        cur.execute("""
            UPDATE dentgo_hub_inventory
            SET quantity_available = quantity_available - ?
            WHERE id = ?
        """, (quantity, deal["inventory_id"]))

        # Registro da reserva
        res_id = f"res-fefo-{uuid.uuid4().hex[:8]}"
        cur.execute("""
            INSERT INTO fefo_flash_deal_reservations (
                id, account_id, deal_id, contact_id, surgeon_name,
                surgeon_cro_uf, quantity_reserved, total_amount, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'RESERVED')
        """, (
            res_id, account_id, deal_id, contact_id, surgeon_name,
            surgeon_cro_uf, quantity, total_amount
        ))

        conn.commit()
    finally:
        conn.close()

    try:
        EventBus.publish_sync(
            StreamName.AUDIT,
            {
                "event": "dentgo.flash_deal_reserved",
                "deal_id": deal_id,
                "reservation_id": res_id,
                "surgeon_cro_uf": surgeon_cro_uf,
                "quantity": quantity,
                "total_amount": total_amount,
                "remaining_available": new_avail,
            }
        )
    except Exception:
        pass

    return {
        "reservation_id": res_id,
        "deal_id": deal_id,
        "surgeon_name": surgeon_name,
        "surgeon_cro_uf": surgeon_cro_uf,
        "quantity_reserved": quantity,
        "total_amount": total_amount,
        "remaining_available": new_avail,
        "deal_status": new_status,
        "status": "RESERVED",
    }


def list_flash_deals(
    status: Optional[str] = None,
    hub_id: Optional[str] = None,
    account_id: str = "0f14ffff",
) -> List[Dict[str, Any]]:
    """Consulta Flash Deals cadastrados."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = """
            SELECT id, account_id, hub_id, hub_name, inventory_id,
                   product_id, product_name, batch_number, original_quantity,
                   available_quantity, original_unit_price, discount_percentage,
                   flash_unit_price, sterilization_expiry_date, months_to_expire,
                   target_surgeons_count, status, checkout_one_click_url, created_at
            FROM fefo_flash_deals
            WHERE account_id = ?
        """
        params: List[Any] = [account_id]
        if status:
            query += " AND status = ?"
            params.append(status)
        if hub_id:
            query += " AND hub_id = ?"
            params.append(hub_id)

        query += " ORDER BY created_at DESC"
        cur.execute(query, tuple(params))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_flash_deal(deal_id: str, account_id: str = "0f14ffff") -> Optional[Dict[str, Any]]:
    """Obtém detalhes de um Flash Deal específico."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, account_id, hub_id, hub_name, inventory_id,
                   product_id, product_name, batch_number, original_quantity,
                   available_quantity, original_unit_price, discount_percentage,
                   flash_unit_price, sterilization_expiry_date, months_to_expire,
                   target_surgeons_count, status, checkout_one_click_url, created_at
            FROM fefo_flash_deals
            WHERE id = ? AND account_id = ?
        """, (deal_id, account_id))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
