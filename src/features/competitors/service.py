# -*- coding: utf-8 -*-
"""
Serviço do Radar de Concorrência (TICKET-MKTINTEL-06).

O cadastro apenas registra o domínio na fila passiva do worker (janela 01:00-05:00 UTC);
nenhuma requisição externa é feita durante a chamada da API.
"""

from __future__ import annotations

import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.core.database import get_connection
from src.core.events import StreamName, default_event_bus
from src.core.vector_store import compute_semantic_embedding, cosine_similarity
from src.features.market_intel.crawler_engine import (
    DEAD_WINDOW_END_HOUR_UTC,
    DEAD_WINDOW_START_HOUR_UTC,
    JITTER_MAX_SECONDS,
    JITTER_MIN_SECONDS,
    compute_next_scheduled_crawl,
)
from src.features.market_intel.opportunity_matcher import BU_CATEGORY_HINTS, determine_bu_target
from src.features.market_intel.rbac import MarketIntelForbidden, MarketIntelPrincipal

VALUE_PILLARS = [
    "Garantia ANVISA com rastreabilidade UDI por lote até o paciente",
    "Entrega expressa DENTGO em até 45 minutos no centro cirúrgico",
    "Consignação de maletas cirúrgicas com reposição automática",
    "Suporte técnico do consultor no dia da cirurgia",
]

_DOMAIN_RE = re.compile(r"^(?=.{4,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,24}$")


class CompetitorConflict(Exception):
    """Domínio já monitorado (HTTP 409)."""


def passive_queue_policy() -> Dict[str, Any]:
    return {
        "dead_window_utc": f"{DEAD_WINDOW_START_HOUR_UTC:02d}:00-{DEAD_WINDOW_END_HOUR_UTC:02d}:00",
        "jitter_seconds_min": JITTER_MIN_SECONDS,
        "jitter_seconds_max": JITTER_MAX_SECONDS,
        "dedup": "SHA-256 do DOM limpo",
        "ad_hoc_scraping_allowed": False,
    }


def normalize_domain(raw: str) -> str:
    d = raw.strip().lower()
    d = re.sub(r"^[a-z]+://", "", d)
    d = d.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    d = d.split(":", 1)[0]
    if d.startswith("www."):
        d = d[4:]
    if not _DOMAIN_RE.match(d):
        raise ValueError(f"Domínio inválido: '{raw}'.")
    return d


def _loads(raw: Optional[str], default: Any) -> Any:
    try:
        return json.loads(raw) if raw else default
    except (TypeError, ValueError):
        return default


def _serialize_competitor(row: Any, snapshots_count: int) -> Dict[str, Any]:
    item = dict(row)
    item["social_handles"] = _loads(item["social_handles"], {})
    item["active"] = bool(item["active"])
    item["snapshots_count"] = snapshots_count
    item["next_scheduled_crawl_at"] = compute_next_scheduled_crawl(item["last_scraped_at"], item["crawl_frequency_hours"])
    return item


def list_competitors(principal: MarketIntelPrincipal) -> Dict[str, Any]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT c.*, (SELECT COUNT(*) FROM competitor_snapshots s WHERE s.competitor_id = c.id) AS snap_count
            FROM competitors c WHERE c.account_id = ? ORDER BY c.name
            """,
            (principal.account_id,),
        ).fetchall()
    finally:
        conn.close()
    items = []
    for r in rows:
        data = {k: r[k] for k in r.keys() if k != "snap_count"}
        items.append(_serialize_competitor(data, int(r["snap_count"])))
    return {"items": items, "passive_queue": passive_queue_policy(), "can_manage_competitors": principal.can_manage_competitors}


def create_competitor(
    principal: MarketIntelPrincipal,
    name: str,
    domain: str,
    social_handles: Optional[Dict[str, str]] = None,
    crawl_frequency_hours: int = 72,
) -> Dict[str, Any]:
    if not principal.can_manage_competitors:
        raise MarketIntelForbidden("Somente Diretoria/Admin configura concorrentes monitorados.")
    clean_domain = normalize_domain(domain)
    comp_id = f"comp-{uuid.uuid4().hex[:10]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        try:
            conn.execute(
                """
                INSERT INTO competitors (id, account_id, name, domain, social_handles, active, crawl_frequency_hours, last_scraped_at, created_at)
                VALUES (?, ?, ?, ?, ?, 1, ?, NULL, ?)
                """,
                (comp_id, principal.account_id, name.strip(), clean_domain, json.dumps(social_handles or {}), int(crawl_frequency_hours), now_iso),
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise CompetitorConflict(f"Domínio '{clean_domain}' já está em monitoramento.") from exc
        row = conn.execute("SELECT * FROM competitors WHERE id = ?", (comp_id,)).fetchone()
    finally:
        conn.close()

    created = _serialize_competitor(row, 0)
    default_event_bus.publish_sync(
        StreamName.MARKET_INTEL,
        "competitor.registered",
        {"competitor_id": comp_id, "domain": clean_domain, "next_scheduled_crawl_at": created["next_scheduled_crawl_at"]},
        tenant_id=principal.account_id,
    )
    return created


def list_snapshots(principal: MarketIntelPrincipal, competitor_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        comp = conn.execute(
            "SELECT id FROM competitors WHERE id = ? AND account_id = ?", (competitor_id, principal.account_id)
        ).fetchone()
        if not comp:
            raise LookupError(f"Concorrente '{competitor_id}' não encontrado.")
        rows = conn.execute(
            """
            SELECT id, competitor_id, page_type, extracted_title, content_hash, detected_offers, tactical_summary, created_at
            FROM competitor_snapshots WHERE competitor_id = ? AND account_id = ?
            ORDER BY created_at DESC, id
            """,
            (competitor_id, principal.account_id),
        ).fetchall()
    finally:
        conn.close()
    out = []
    for r in rows:
        item = dict(r)
        item["detected_offers"] = _loads(item["detected_offers"], [])
        out.append(item)
    return out


def _best_catalog_match(product_text: str, catalog: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    bu = determine_bu_target(product_text)
    hints = BU_CATEGORY_HINTS[bu]
    candidates = [p for p in catalog if any(h in str(p["category"]).lower() for h in hints)] or catalog
    if not candidates:
        return None
    query_vec = compute_semantic_embedding(product_text)
    scored = sorted(
        candidates,
        key=lambda p: (-cosine_similarity(query_vec, p["_vec"]), p["sku"]),
    )
    return scored[0]


def build_tactical_insights(principal: MarketIntelPrincipal) -> Dict[str, Any]:
    conn = get_connection()
    try:
        snaps = conn.execute(
            """
            SELECT s.id, s.competitor_id, s.detected_offers, c.name AS competitor_name
            FROM competitor_snapshots s
            JOIN competitors c ON c.id = s.competitor_id
            WHERE s.account_id = ? AND s.created_at = (
                SELECT MAX(s2.created_at) FROM competitor_snapshots s2
                WHERE s2.competitor_id = s.competitor_id AND s2.page_type = s.page_type
            )
            ORDER BY c.name, s.page_type
            """,
            (principal.account_id,),
        ).fetchall()
        catalog = [
            dict(r) for r in conn.execute(
                "SELECT sku, name, category, base_price FROM products_catalog WHERE is_active = 1 ORDER BY sku"
            ).fetchall()
        ]
    finally:
        conn.close()

    for p in catalog:
        p["_vec"] = compute_semantic_embedding(f"{p['name']} {p['category']}")

    insights: List[Dict[str, Any]] = []
    for snap in snaps:
        for offer in _loads(snap["detected_offers"], []):
            product = str(offer.get("product") or "")
            price = float(offer.get("price") or 0.0)
            match = _best_catalog_match(product, catalog)
            gap = None
            if match and price > 0:
                gap = round((float(match["base_price"]) - price) / price * 100.0, 1)
            if match:
                if gap is not None and gap > 0:
                    counter = (
                        f"Nosso {match['sku']} está {gap}% acima do preço anunciado por {snap['competitor_name']}. "
                        "Não reduzir preço de lista: compor pacote com consignação, entrega DENTGO em 45 min e garantia "
                        "ANVISA/UDI; liberar condição comercial pela tabela de preço da praça apenas para contas de alto volume."
                    )
                else:
                    counter = (
                        f"Nosso {match['sku']} já é competitivo frente a {snap['competitor_name']}. Reforçar diferenciais "
                        "de rastreabilidade UDI e logística DENTGO e acelerar visitas às contas expostas à oferta."
                    )
            else:
                counter = "Sem equivalente direto no catálogo: avaliar inclusão de SKU ou oferta de linha substituta."
            insights.append({
                "competitor_id": snap["competitor_id"],
                "competitor_name": snap["competitor_name"],
                "snapshot_id": snap["id"],
                "competitor_product": product,
                "competitor_price": price,
                "competitor_discount": str(offer.get("discount") or "0%"),
                "matched_sku": match["sku"] if match else None,
                "matched_product_name": match["name"] if match else None,
                "our_base_price": float(match["base_price"]) if match else None,
                "price_gap_pct": gap,
                "counter_attack": counter,
            })
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "value_pillars": VALUE_PILLARS, "insights": insights}
