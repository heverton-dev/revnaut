# -*- coding: utf-8 -*-
"""Consultas territoriais (RBAC Seção 5) de sinais, oportunidades e campanhas táticas (TICKET-MKTINTEL-06)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from src.core.database import get_connection
from src.features.market_intel.rbac import MarketIntelForbidden, MarketIntelPrincipal


def _loads(raw: Optional[str], default: Any) -> Any:
    try:
        return json.loads(raw) if raw else default
    except (TypeError, ValueError):
        return default


def _scope_clause(principal: MarketIntelPrincipal, column: str, requested: Optional[str]) -> tuple[str, List[Any]]:
    if requested:
        scope = requested.strip().upper()
        if not principal.can_see_scope(scope):
            raise MarketIntelForbidden(f"Escopo '{scope}' fora da governança territorial do perfil ({principal.region}).")
        return f"{column} = ?", [scope]
    scopes = principal.visible_scopes
    if scopes is None:
        return "1 = 1", []
    ordered = sorted(scopes)
    return f"{column} IN ({','.join('?' for _ in ordered)})", list(ordered)


def list_signals(
    principal: MarketIntelPrincipal,
    scope: Optional[str] = None,
    specialty: Optional[str] = None,
    source_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> Dict[str, Any]:
    scope_sql, args = _scope_clause(principal, "geographic_scope", scope)
    conditions = ["account_id = ?", scope_sql]
    params: List[Any] = [principal.account_id, *args]
    if source_type:
        conditions.append("source_type = ?")
        params.append(source_type)
    if specialty:
        conditions.append(
            "EXISTS (SELECT 1 FROM json_each(market_signals.structured_payload, '$.target_specialties') WHERE LOWER(value) = LOWER(?))"
        )
        params.append(specialty)
    where = " AND ".join(conditions)

    conn = get_connection()
    try:
        total = conn.execute(f"SELECT COUNT(*) FROM market_signals WHERE {where}", tuple(params)).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM market_signals WHERE {where} ORDER BY created_at DESC, id LIMIT ? OFFSET ?",
            (*params, limit, offset),
        ).fetchall()
    finally:
        conn.close()

    items = []
    for r in rows:
        item = dict(r)
        item["structured_payload"] = _loads(item["structured_payload"], {})
        items.append(item)
    scopes = principal.visible_scopes
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "visible_scopes": ["*"] if scopes is None else sorted(scopes),
    }


def _products_by_sku(conn, skus: List[str]) -> Dict[str, Dict[str, Any]]:
    if not skus:
        return {}
    rows = conn.execute(
        f"SELECT sku, name, category, base_price FROM products_catalog WHERE sku IN ({','.join('?' for _ in skus)})",
        tuple(skus),
    ).fetchall()
    return {r["sku"]: dict(r) for r in rows}


def list_opportunities(
    principal: MarketIntelPrincipal,
    region_code: Optional[str] = None,
    bu_target: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    scope_sql, args = _scope_clause(principal, "o.region_code", region_code)
    conditions = ["o.account_id = ?", scope_sql]
    params: List[Any] = [principal.account_id, *args]
    if bu_target:
        conditions.append("o.bu_target = ?")
        params.append(bu_target)
    if status:
        conditions.append("o.status = ?")
        params.append(status.upper())

    conn = get_connection()
    try:
        rows = conn.execute(
            f"""
            SELECT o.*, COALESCE(s.title, c.name || ' - ' || cs.extracted_title) AS source_title
            FROM market_opportunities o
            LEFT JOIN market_signals s ON s.id = o.signal_id
            LEFT JOIN competitor_snapshots cs ON cs.id = o.competitor_snapshot_id
            LEFT JOIN competitors c ON c.id = cs.competitor_id
            WHERE {' AND '.join(conditions)}
            ORDER BY o.created_at DESC, o.id
            """,
            tuple(params),
        ).fetchall()
        result = []
        all_skus = sorted({sku for r in rows for sku in _loads(r["recommended_product_ids"], [])})
        catalog = _products_by_sku(conn, all_skus)
    finally:
        conn.close()

    for r in rows:
        item = dict(r)
        skus = _loads(item["recommended_product_ids"], [])
        item["recommended_product_ids"] = skus
        item["recommended_products"] = [catalog[s] for s in skus if s in catalog]
        result.append(item)
    return result


def get_opportunity_for_principal(principal: MarketIntelPrincipal, opportunity_id: str) -> Dict[str, Any]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM market_opportunities WHERE id = ? AND account_id = ?",
            (opportunity_id, principal.account_id),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        raise LookupError(f"Oportunidade '{opportunity_id}' não encontrada.")
    if not principal.can_see_scope(row["region_code"]):
        raise MarketIntelForbidden("Oportunidade fora do escopo territorial do perfil.")
    return dict(row)


def list_campaigns(principal: MarketIntelPrincipal, dispatch_status: Optional[str] = None) -> List[Dict[str, Any]]:
    conditions = ["t.account_id = ?"]
    params: List[Any] = [principal.account_id]
    scopes = principal.visible_scopes
    if scopes is not None:
        ordered = sorted(scopes)
        conditions.append(f"json_extract(t.target_audience_filter, '$.region') IN ({','.join('?' for _ in ordered)})")
        params.extend(ordered)
    if dispatch_status:
        conditions.append("t.dispatch_status = ?")
        params.append(dispatch_status.upper())

    conn = get_connection()
    try:
        rows = conn.execute(
            f"""
            SELECT t.*, o.opportunity_type, o.bu_target, o.status AS opportunity_status
            FROM targeted_campaigns t
            JOIN market_opportunities o ON o.id = t.opportunity_id
            WHERE {' AND '.join(conditions)}
            ORDER BY t.created_at DESC, t.id
            """,
            tuple(params),
        ).fetchall()
    finally:
        conn.close()

    out = []
    for r in rows:
        item = dict(r)
        item["target_audience_filter"] = _loads(item["target_audience_filter"], {"region": "GLOBAL"})
        out.append(item)
    return out
