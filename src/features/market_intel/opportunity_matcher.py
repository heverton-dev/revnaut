# -*- coding: utf-8 -*-
"""
Opportunity Matcher: cruzamento Sinal/Snapshot de Concorrente x Portfólio (TICKET-MKTINTEL-05).

Indexa market_signals e products_catalog no VectorStoreService (embeddings determinísticos
compute_semantic_embedding) e recomenda SKUs reais do catálogo por similaridade semântica,
restrita à categoria compatível com a Unidade de Negócio alvo.
"""

from __future__ import annotations

import asyncio
import json
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Coroutine, Dict, List, Optional, TypeVar

from src.core.database import get_connection
from src.core.events import StreamName, default_event_bus
from src.core.vector_store import VectorStoreService, compute_semantic_embedding

ENTITY_PRODUCT = "mkt_product_catalog"
ENTITY_SIGNAL = "mkt_market_signal"

BU_IMPLANTODONTIA = "Implantodontia"
BU_PROTESE_DIGITAL = "Prótese Digital"
BU_BIOMATERIAIS = "Biomateriais"

PRICE_COUNTER_ATTACK = "PRICE_COUNTER_ATTACK"
CLINICAL_UPGRADE = "CLINICAL_UPGRADE"
EVENT_SURGE = "EVENT_SURGE"

MAX_RECOMMENDED_SKUS = 3

_BU_KEYWORDS = {
    BU_BIOMATERIAIS: ("biomateria", "enxerto", "bone graft", "graft", "osso", "membrana", "xenoenxerto", "regenera"),
    BU_PROTESE_DIGITAL: ("cad/cam", "cad cam", "zirc", "protese digital", "prótese digital", "fresagem", "scanner", "coroa", "fluxo digital"),
    BU_IMPLANTODONTIA: ("implante", "cone morse", "carga imediata", "hidrof", "hydrophilic", "udi", "kit cir", "torque"),
}

# Categorias do products_catalog compatíveis com cada BU (comparação case-insensitive por substring)
BU_CATEGORY_HINTS = {
    BU_BIOMATERIAIS: ("biomat",),
    BU_PROTESE_DIGITAL: ("componente", "equipamento", "protet", "digital"),
    BU_IMPLANTODONTIA: ("implante", "kit", "instrumenta"),
}

T = TypeVar("T")


def run_coroutine_sync(coro: Coroutine[Any, Any, T]) -> T:
    """Executa uma corrotina a partir de código síncrono, inclusive quando já há event loop ativo."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    box: Dict[str, Any] = {}

    def _runner() -> None:
        try:
            box["value"] = asyncio.run(coro)
        except BaseException as exc:  # propaga para a thread chamadora
            box["error"] = exc

    th = threading.Thread(target=_runner, daemon=True)
    th.start()
    th.join()
    if "error" in box:
        raise box["error"]
    return box["value"]


def _loads(raw: Optional[str], default: Any) -> Any:
    try:
        return json.loads(raw) if raw else default
    except (TypeError, ValueError):
        return default


def determine_bu_target(text: str, topics: Optional[List[str]] = None) -> str:
    """BU com maior incidência de palavras-chave; empate resolvido na ordem Biomateriais > Prótese Digital > Implantodontia."""
    corpus = f"{text} {' '.join(topics or [])}".lower()
    scores = {bu: sum(corpus.count(k) for k in kws) for bu, kws in _BU_KEYWORDS.items()}
    best = max(scores.values())
    if best == 0:
        return BU_IMPLANTODONTIA
    for bu in (BU_BIOMATERIAIS, BU_PROTESE_DIGITAL, BU_IMPLANTODONTIA):
        if scores[bu] == best:
            return bu
    return BU_IMPLANTODONTIA


def determine_opportunity_type(source_type: Optional[str], is_competitor_snapshot: bool, trends: Optional[List[str]] = None) -> str:
    if is_competitor_snapshot:
        return PRICE_COUNTER_ATTACK
    if source_type == "congress_ciosp":
        return EVENT_SURGE
    if source_type in ("scientific_journal", "regulatory_anvisa"):
        return CLINICAL_UPGRADE
    if any("expans" in t.lower() or "consolida" in t.lower() for t in (trends or [])):
        return EVENT_SURGE
    return CLINICAL_UPGRADE


def _product_text(row: Any) -> str:
    parts = [row["name"], row["category"], row["prosthetic_platform"] or "", row["sku"]]
    return " ".join(str(p) for p in parts if p)


async def index_market_intel_embeddings(account_id: str) -> Dict[str, int]:
    """Indexa (idempotente) produtos ativos e sinais do tenant no VectorStoreService."""
    store = VectorStoreService()
    conn = get_connection()
    try:
        indexed = {
            (r["entity_type"], r["entity_id"])
            for r in conn.execute(
                "SELECT entity_type, entity_id FROM semantic_embeddings WHERE tenant_id = ? AND entity_type IN (?, ?)",
                (account_id, ENTITY_PRODUCT, ENTITY_SIGNAL),
            ).fetchall()
        }
        products = conn.execute(
            "SELECT sku, name, category, prosthetic_platform, base_price FROM products_catalog WHERE is_active = 1"
        ).fetchall()
        signals = conn.execute(
            "SELECT id, title, raw_content, structured_payload FROM market_signals WHERE account_id = ?",
            (account_id,),
        ).fetchall()
    finally:
        conn.close()

    new_products = 0
    for p in products:
        if (ENTITY_PRODUCT, p["sku"]) in indexed:
            continue
        text_chunk = _product_text(p)
        await store.store_embedding(
            account_id, ENTITY_PRODUCT, p["sku"], text_chunk, compute_semantic_embedding(text_chunk),
            {"sku": p["sku"], "category": p["category"], "base_price": p["base_price"]},
        )
        new_products += 1

    new_signals = 0
    for s in signals:
        if (ENTITY_SIGNAL, s["id"]) in indexed:
            continue
        payload = _loads(s["structured_payload"], {})
        text_chunk = f"{s['title']} {' '.join(payload.get('topics', []))} {s['raw_content'][:1500]}"
        await store.store_embedding(
            account_id, ENTITY_SIGNAL, s["id"], text_chunk, compute_semantic_embedding(text_chunk),
            {"signal_id": s["id"]},
        )
        new_signals += 1
    return {"products_indexed": new_products, "signals_indexed": new_signals}


def _category_matches(bu: str, category: str) -> bool:
    cat = (category or "").lower()
    return any(h in cat for h in BU_CATEGORY_HINTS[bu])


async def recommend_skus(account_id: str, query_text: str, bu_target: str, top_k: int = MAX_RECOMMENDED_SKUS) -> List[Dict[str, Any]]:
    """Ranqueia SKUs reais do catálogo por similaridade de cosseno, filtrando pela categoria da BU."""
    await index_market_intel_embeddings(account_id)
    store = VectorStoreService()
    hits = await store.search_similar(account_id, compute_semantic_embedding(query_text), entity_type=ENTITY_PRODUCT, top_k=50)

    conn = get_connection()
    try:
        catalog = {
            r["sku"]: dict(r)
            for r in conn.execute("SELECT sku, name, category, base_price FROM products_catalog WHERE is_active = 1").fetchall()
        }
    finally:
        conn.close()

    ranked: List[Dict[str, Any]] = []
    for hit in hits:
        prod = catalog.get(hit["entity_id"])
        if not prod or not _category_matches(bu_target, prod["category"]):
            continue
        ranked.append({**prod, "similarity": hit["similarity"]})
        if len(ranked) >= top_k:
            break
    if not ranked:
        # Catálogo sem produto da BU com similaridade positiva: recomenda os SKUs ativos da categoria compatível.
        ranked = [
            {**p, "similarity": 0.0}
            for sku, p in sorted(catalog.items())
            if _category_matches(bu_target, p["category"])
        ][:top_k]
    return ranked


def _format_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def build_suggested_action(
    opportunity_type: str,
    bu_target: str,
    region_code: str,
    products: List[Dict[str, Any]],
    source_label: str,
    offers: Optional[List[Dict[str, Any]]] = None,
) -> str:
    portfolio = "; ".join(f"{p['sku']} ({p['name']}, {_format_brl(float(p['base_price']))})" for p in products) or "portfólio da BU"
    if opportunity_type == PRICE_COUNTER_ATTACK:
        offer_txt = ""
        if offers:
            top = offers[0]
            offer_txt = f" Oferta detectada: {top.get('product')} a {_format_brl(float(top.get('price', 0.0)))} (desconto {top.get('discount', '0%')})."
        return (
            f"Contra-ataque a {source_label} na praça {region_code}.{offer_txt} Posicionar {portfolio} com pacote de valor "
            "(garantia ANVISA com rastreabilidade UDI, entrega DENTGO em 45 min e suporte cirúrgico do consultor). "
            "Priorizar contas com recompra prevista em até 30 dias e aprovar condição comercial pela tabela de preço da praça, "
            "sem divulgar preço promocional em peça publicitária (Resolução CFO 196/2019)."
        )
    if opportunity_type == EVENT_SURGE:
        return (
            f"Pico de demanda ligado a '{source_label}' na praça {region_code}. Garantir estoque e kits de demonstração de "
            f"{portfolio}, agendar visitas técnicas pré e pós-evento com cirurgiões de {bu_target} e reservar janela DENTGO "
            "para reposição expressa durante o período do evento."
        )
    return (
        f"Atualização clínica/regulatória '{source_label}' com impacto em {bu_target} na praça {region_code}. Enviar resumo "
        f"técnico aos cirurgiões da carteira apresentando {portfolio}, com protocolo de torque e documentação ANVISA/UDI, "
        "e oferecer visita do consultor clínico para revisão de casos."
    )


async def amatch_and_create_opportunity(
    account_id: str,
    signal_id: Optional[str] = None,
    competitor_snapshot_id: Optional[str] = None,
    region_code: Optional[str] = None,
) -> Dict[str, Any]:
    if bool(signal_id) == bool(competitor_snapshot_id):
        raise ValueError("Informe exatamente um entre signal_id e competitor_snapshot_id.")

    conn = get_connection()
    try:
        if signal_id:
            src = conn.execute(
                "SELECT * FROM market_signals WHERE id = ? AND account_id = ?", (signal_id, account_id)
            ).fetchone()
            if not src:
                raise LookupError(f"Sinal '{signal_id}' não encontrado.")
            payload = _loads(src["structured_payload"], {})
            topics = payload.get("topics", [])
            trends = payload.get("detected_trends", [])
            query_text = f"{src['title']} {' '.join(topics)} {src['raw_content'][:1500]}"
            opp_type = determine_opportunity_type(src["source_type"], False, trends)
            eff_region = region_code or src["geographic_scope"] or "GLOBAL"
            source_label = src["title"]
            offers: List[Dict[str, Any]] = []
            existing_sql, existing_args = "signal_id = ?", (signal_id,)
        else:
            src = conn.execute(
                """
                SELECT s.*, c.name AS competitor_name FROM competitor_snapshots s
                JOIN competitors c ON c.id = s.competitor_id
                WHERE s.id = ? AND s.account_id = ?
                """,
                (competitor_snapshot_id, account_id),
            ).fetchone()
            if not src:
                raise LookupError(f"Snapshot '{competitor_snapshot_id}' não encontrado.")
            offers = _loads(src["detected_offers"], [])
            topics = []
            query_text = " ".join([src["extracted_title"], src["tactical_summary"]] + [str(o.get("product", "")) for o in offers])
            opp_type = PRICE_COUNTER_ATTACK
            eff_region = region_code or "BR-SP"
            source_label = src["competitor_name"]
            existing_sql, existing_args = "competitor_snapshot_id = ?", (competitor_snapshot_id,)

        existing = conn.execute(
            f"SELECT * FROM market_opportunities WHERE account_id = ? AND {existing_sql} AND region_code = ?",
            (account_id, *existing_args, eff_region),
        ).fetchone()
        if existing:
            out = dict(existing)
            out["recommended_product_ids"] = _loads(out["recommended_product_ids"], [])
            out["created"] = False
            return out
    finally:
        conn.close()

    bu_target = determine_bu_target(query_text, topics)
    products = await recommend_skus(account_id, query_text, bu_target)
    skus = [p["sku"] for p in products]
    action = build_suggested_action(opp_type, bu_target, eff_region, products, source_label, offers)

    opp_id = f"opp-{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO market_opportunities (
                id, account_id, signal_id, competitor_snapshot_id, bu_target, recommended_product_ids,
                opportunity_type, suggested_action, region_code, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)
            """,
            (opp_id, account_id, signal_id, competitor_snapshot_id, bu_target, json.dumps(skus), opp_type, action, eff_region, now_iso),
        )
        conn.commit()
    finally:
        conn.close()

    default_event_bus.publish_sync(
        StreamName.MARKET_INTEL,
        "market_opportunity.created",
        {"opportunity_id": opp_id, "opportunity_type": opp_type, "bu_target": bu_target, "region_code": eff_region},
        tenant_id=account_id,
    )
    return {
        "id": opp_id,
        "account_id": account_id,
        "signal_id": signal_id,
        "competitor_snapshot_id": competitor_snapshot_id,
        "bu_target": bu_target,
        "recommended_product_ids": skus,
        "opportunity_type": opp_type,
        "suggested_action": action,
        "region_code": eff_region,
        "status": "PENDING",
        "created_at": now_iso,
        "created": True,
    }


def match_and_create_opportunity(
    account_id: str,
    signal_id: Optional[str] = None,
    competitor_snapshot_id: Optional[str] = None,
    region_code: Optional[str] = None,
) -> Dict[str, Any]:
    """Versão síncrona (endpoints FastAPI síncronos e scripts) do matcher assíncrono."""
    return run_coroutine_sync(
        amatch_and_create_opportunity(
            account_id=account_id,
            signal_id=signal_id,
            competitor_snapshot_id=competitor_snapshot_id,
            region_code=region_code,
        )
    )
