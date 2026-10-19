# -*- coding: utf-8 -*-
"""
Vertical Slice: Dynamic Dental Catalog & Discount Governance Engine
Controle de alçadas por nível hierárquico RBAC e precificação multi-tabela.
"""

from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional
from src.core.database import get_connection, init_db


ROLE_DISCOUNT_LIMITS: Dict[str, float] = {
    "consultor": 5.0,
    "vendedor": 5.0,
    "field_sales": 5.0,
    "inside_sales": 5.0,
    "supervisor": 12.0,
    "coordenador": 12.0,
    "gerente": 15.0,
    "diretor": 25.0,
    "superadmin": 50.0,
    "super admin": 50.0,
    "admin": 25.0,
}


def parse_price(val: Any) -> float:
    """Converte valores monetários (numéricos ou strings como 'R$ 289,90' e 'US$ 145.00') em float determinístico."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    cleaned = str(val).replace("R$", "").replace("US$", "").replace("€", "").replace("$", "").strip()
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except Exception:
        return 0.0


_to_float = parse_price


def list_catalog_products(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    """Lista todos os produtos ativos do catálogo odontológico."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, account_id, sku, name, category, anvisa_reg, prosthetic_platform,
                   diameter, length, recommended_torque, base_price, is_active, created_at
            FROM products_catalog
            WHERE account_id = ? AND is_active = 1
            ORDER BY category ASC, name ASC
        """, (account_id,))
        rows = [dict(r) for r in cur.fetchall()]
        for row in rows:
            row["base_price"] = parse_price(row.get("base_price"))
        return rows
    finally:
        conn.close()


def list_price_tables(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    """Lista as tabelas de preço ativas configuradas no sistema."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, account_id, table_key, name, discount_factor, is_active, created_at
            FROM price_tables
            WHERE account_id = ? AND is_active = 1
            ORDER BY discount_factor DESC
        """, (account_id,))
        rows = [dict(r) for r in cur.fetchall()]
        return rows
    finally:
        conn.close()


def calculate_proposal_pricing(
    deal_id: str,
    table_key: str,
    items: List[Dict[str, Any]],
    requested_discount_pct: float = 0.0,
    user_id: Optional[str] = None,
    user_role: Optional[str] = "consultor",
    account_id: str = "0f14ffff",
) -> Dict[str, Any]:
    """
    Calcula valor da proposta odontológica, aplicando o fator da tabela de preço
    e validando a alçada de desconto do vendedor via governança RBAC.
    """
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()

        # 1. Determina fator da tabela de preço
        cur.execute("SELECT discount_factor FROM price_tables WHERE account_id = ? AND table_key = ?", (account_id, table_key))
        pt_row = cur.fetchone()
        table_factor = float(pt_row["discount_factor"]) if pt_row else 1.0

        # 2. Calcula total base a partir dos SKUs do catálogo
        base_total = 0.0
        for item in items:
            sku = item.get("sku")
            quantity = int(item.get("quantity", 1))
            cur.execute("SELECT base_price FROM products_catalog WHERE account_id = ? AND sku = ?", (account_id, sku))
            p_row = cur.fetchone()
            if p_row:
                unit_price = parse_price(p_row["base_price"]) * table_factor
                base_total += unit_price * quantity
            else:
                # Preço padrão unitário de segurança caso SKU não seja localizado
                base_total += 450.0 * table_factor * quantity

        # 3. Validação de alçada de desconto RBAC
        role_key = (user_role or "consultor").lower().strip()
        max_allowed = ROLE_DISCOUNT_LIMITS.get(role_key, 5.0)

        final_value = base_total * (1.0 - (requested_discount_pct / 100.0))

        if requested_discount_pct > max_allowed:
            # Excede alçada: bloqueia contrato e envia para aprovação
            request_id = f"dreq-{uuid.uuid4().hex[:6]}"
            requester = user_id or "u_consultor"
            cur.execute("""
                INSERT INTO deal_discount_requests (
                    id, account_id, deal_id, requested_by_user_id,
                    discount_pct, max_allowed_pct, status
                ) VALUES (?, ?, ?, ?, ?, ?, 'PENDING_APPROVAL')
            """, (request_id, account_id, deal_id, requester, requested_discount_pct, max_allowed))

            cur.execute("""
                UPDATE deals
                SET approval_status = 'PENDING_DISCOUNT_APPROVAL'
                WHERE id = ? AND account_id = ?
            """, (deal_id, account_id))

            conn.commit()
            return {
                "status": "PENDING_DISCOUNT_APPROVAL",
                "requires_approval": True,
                "base_value": round(base_total, 2),
                "final_value": round(final_value, 2),
                "requested_discount_pct": requested_discount_pct,
                "max_allowed_pct": max_allowed,
                "request_id": request_id,
            }
        else:
            # Dentro da alçada: aprova automaticamente e atualiza valor do Deal
            cur.execute("""
                UPDATE deals
                SET value = ?, approval_status = 'APPROVED'
                WHERE id = ? AND account_id = ?
            """, (round(final_value, 2), deal_id, account_id))

            conn.commit()
            return {
                "status": "APPROVED",
                "requires_approval": False,
                "base_value": round(base_total, 2),
                "final_value": round(final_value, 2),
                "requested_discount_pct": requested_discount_pct,
                "max_allowed_pct": max_allowed,
                "request_id": None,
            }
    finally:
        conn.close()


def approve_discount_request(
    request_id: str,
    approver_user_id: str,
    account_id: str = "0f14ffff",
) -> Dict[str, Any]:
    """
    Aprovação instantânea de desconto por gestor/supervisor liberando o Deal.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT deal_id, discount_pct FROM deal_discount_requests WHERE id = ? AND account_id = ?", (request_id, account_id))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Solicitação de desconto {request_id} não encontrada")

        deal_id = row["deal_id"]

        cur.execute("""
            UPDATE deal_discount_requests
            SET status = 'APPROVED',
                approved_by_user_id = ?,
                resolved_at = CURRENT_TIMESTAMP
            WHERE id = ? AND account_id = ?
        """, (approver_user_id, request_id, account_id))

        cur.execute("""
            UPDATE deals
            SET approval_status = 'APPROVED'
            WHERE id = ? AND account_id = ?
        """, (deal_id, account_id))

        conn.commit()
        return {
            "success": True,
            "request_id": request_id,
            "deal_id": deal_id,
            "status": "APPROVED",
        }
    finally:
        conn.close()
