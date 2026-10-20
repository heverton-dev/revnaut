# -*- coding: utf-8 -*-
"""
Crawler Passivo Anti-Bloqueio do Radar de Concorrência (TICKET-MKTINTEL-03).

Regra inegociável: nenhuma raspagem síncrona é disparada por clique do usuário final.
Toda ingestão externa ocorre em lotes agendados pelo worker, dentro da janela morta
01:00-05:00 UTC, com jitter de 7 a 22 segundos por domínio, headers rotacionados e
deduplicação por SHA-256 do DOM limpo (conteúdo inalterado não aciona o LLM).
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

import httpx

from src.core.database import get_connection
from src.core.events import StreamName, default_event_bus

DEAD_WINDOW_START_HOUR_UTC = 1
DEAD_WINDOW_END_HOUR_UTC = 5
JITTER_MIN_SECONDS = 7.0
JITTER_MAX_SECONDS = 22.0
FETCH_TIMEOUT_SECONDS = 25.0

VALID_PAGE_TYPES = ("pricing_table", "catalog", "blog_post", "social_ad")

DESKTOP_USER_AGENTS: Tuple[Dict[str, str], ...] = (
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Sec-CH-UA": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "Sec-CH-UA-Platform": '"Windows"',
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Sec-CH-UA": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "Sec-CH-UA-Platform": '"macOS"',
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Sec-CH-UA": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "Sec-CH-UA-Platform": '"Linux"',
    },
)

STEALTH_INIT_SCRIPT = (
    "Object.defineProperty(navigator, 'webdriver', {get: () => false});"
    "Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en-US', 'en']});"
    "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});"
    "window.chrome = window.chrome || { runtime: {} };"
)

_TRACKER_DOMAINS = (
    "google-analytics", "googletagmanager", "doubleclick", "facebook.net", "connect.facebook",
    "hotjar", "clarity.ms", "tiktok", "linkedin.com/px", "rdstation", "hubspot",
)

_RE_BLOCKS = re.compile(r"<(script|style|noscript|template|svg|iframe)\b[^>]*>.*?</\1\s*>", re.I | re.S)
_RE_COMMENTS = re.compile(r"<!--.*?-->", re.S)
_RE_TRACKER_TAGS = re.compile(
    r"<(img|link|iframe|script)\b[^>]*(?:" + "|".join(re.escape(d) for d in _TRACKER_DOMAINS) + r")[^>]*/?>",
    re.I,
)
_RE_BLOCK_TAGS = re.compile(r"</?(p|div|br|li|tr|h[1-6]|section|article|td|th|ul|ol|table)\b[^>]*>", re.I)
_RE_ANY_TAG = re.compile(r"<[^>]+>")


def is_within_dead_window_utc(now_utc: Optional[datetime] = None, force_scheduled_batch: bool = False) -> bool:
    """True apenas entre 01:00 (inclusive) e 05:00 (exclusive) UTC, ou em lote interno forçado (cron/testes)."""
    if force_scheduled_batch:
        return True
    now = now_utc or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    hour = now.astimezone(timezone.utc).hour
    return DEAD_WINDOW_START_HOUR_UTC <= hour < DEAD_WINDOW_END_HOUR_UTC


def compute_domain_jitter_seconds(domain: str, request_index: int = 0) -> float:
    """Jitter determinístico por (domínio, índice da requisição) no intervalo [7.0, 22.0] segundos."""
    digest = hashlib.sha256(f"{domain.strip().lower()}#{request_index}".encode("utf-8")).digest()
    fraction = int.from_bytes(digest[:8], "big") / float(2 ** 64 - 1)
    return round(JITTER_MIN_SECONDS + fraction * (JITTER_MAX_SECONDS - JITTER_MIN_SECONDS), 3)


def build_stealth_headers(user_agent_index: int = 0) -> Dict[str, Any]:
    """Headers de navegador desktop real (rotação por índice) e script de init stealth para Playwright."""
    profile = DESKTOP_USER_AGENTS[user_agent_index % len(DESKTOP_USER_AGENTS)]
    headers = {
        **profile,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    return {"headers": headers, "init_script": STEALTH_INIT_SCRIPT, "user_agent": profile["User-Agent"]}


def normalize_and_hash_dom(raw_content: str) -> Tuple[str, str]:
    """Remove scripts, estilos, rastreadores e ruído de espaços; retorna (texto_limpo, sha256_hex)."""
    content = raw_content or ""
    content = _RE_COMMENTS.sub(" ", content)
    content = _RE_TRACKER_TAGS.sub(" ", content)
    content = _RE_BLOCKS.sub(" ", content)
    content = _RE_BLOCK_TAGS.sub("\n", content)
    content = _RE_ANY_TAG.sub(" ", content)
    content = html.unescape(content)
    lines = [re.sub(r"[ \t\f\v ]+", " ", ln).strip() for ln in content.splitlines()]
    cleaned = "\n".join(ln for ln in lines if ln)
    sha256_hex = hashlib.sha256(cleaned.encode("utf-8")).hexdigest()
    return cleaned, sha256_hex


def _latest_snapshot_hash(conn, account_id: str, competitor_id: str, page_type: str) -> Optional[str]:
    row = conn.execute(
        """
        SELECT content_hash FROM competitor_snapshots
        WHERE account_id = ? AND competitor_id = ? AND page_type = ?
        ORDER BY created_at DESC, rowid DESC LIMIT 1
        """,
        (account_id, competitor_id, page_type),
    ).fetchone()
    return row["content_hash"] if row else None


def ingest_competitor_page_snapshot(
    competitor_id: str,
    page_type: str,
    raw_content: str,
    account_id: str,
    extracted_title: Optional[str] = None,
    classifier: Optional[Callable[[str, str], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Normaliza o DOM, compara o SHA-256 com o último snapshot de (competitor_id, page_type) e só
    invoca o classificador LLM quando o conteúdo mudou. Conteúdo idêntico não gera snapshot duplicado.
    """
    if page_type not in VALID_PAGE_TYPES:
        raise ValueError(f"page_type inválido: '{page_type}'. Use um de {VALID_PAGE_TYPES}.")

    cleaned_text, sha256_hex = normalize_and_hash_dom(raw_content)
    conn = get_connection()
    try:
        comp = conn.execute(
            "SELECT id, name, domain FROM competitors WHERE id = ? AND account_id = ?",
            (competitor_id, account_id),
        ).fetchone()
        if not comp:
            raise LookupError(f"Concorrente '{competitor_id}' não encontrado no tenant '{account_id}'.")

        if _latest_snapshot_hash(conn, account_id, competitor_id, page_type) == sha256_hex:
            conn.execute(
                "UPDATE competitors SET last_scraped_at = ? WHERE id = ?",
                (datetime.now(timezone.utc).isoformat(), competitor_id),
            )
            conn.commit()
            return {"status": "SKIPPED_UNCHANGED_HASH", "llm_invoked": False, "content_hash": sha256_hex}

        if classifier is None:
            from src.features.market_intel.llm_classifier import extract_competitor_offers_and_tactics
            classifier = extract_competitor_offers_and_tactics
        analysis = classifier(comp["name"], cleaned_text)

        title = (extracted_title or cleaned_text.split("\n", 1)[0] or f"{comp['name']} - {page_type}")[:255]
        snapshot_id = f"snap-{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        offers = analysis.get("detected_offers") or []
        conn.execute(
            """
            INSERT INTO competitor_snapshots (
                id, account_id, competitor_id, page_type, extracted_title, content_hash,
                detected_offers, tactical_summary, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id, account_id, competitor_id, page_type, title, sha256_hex,
                json.dumps(offers, ensure_ascii=False), str(analysis.get("tactical_summary") or ""), now_iso,
            ),
        )
        conn.execute("UPDATE competitors SET last_scraped_at = ? WHERE id = ?", (now_iso, competitor_id))
        conn.commit()
    finally:
        conn.close()

    default_event_bus.publish_sync(
        StreamName.MARKET_INTEL,
        "competitor.snapshot.ingested",
        {"snapshot_id": snapshot_id, "competitor_id": competitor_id, "page_type": page_type, "account_id": account_id},
        tenant_id=account_id,
    )
    return {
        "status": "INGESTED",
        "llm_invoked": True,
        "snapshot_id": snapshot_id,
        "content_hash": sha256_hex,
        "detected_offers": offers,
        "tactical_summary": analysis.get("tactical_summary"),
        "engine": analysis.get("engine"),
    }


def fetch_page_passively(url: str, user_agent_index: int = 0) -> str:
    """Coleta passiva de uma página pública. Usa Playwright com init stealth quando habilitado; senão HTTP direto."""
    stealth = build_stealth_headers(user_agent_index)
    if os.getenv("MARKET_INTEL_USE_PLAYWRIGHT", "").lower() in ("1", "true", "yes"):
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                context = browser.new_context(
                    user_agent=stealth["user_agent"],
                    locale="pt-BR",
                    extra_http_headers={k: v for k, v in stealth["headers"].items() if k != "User-Agent"},
                )
                context.add_init_script(stealth["init_script"])
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=int(FETCH_TIMEOUT_SECONDS * 1000))
                return page.content()
            finally:
                browser.close()

    with httpx.Client(headers=stealth["headers"], timeout=FETCH_TIMEOUT_SECONDS, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.text


def _is_due(last_scraped_at: Optional[str], frequency_hours: int, now: datetime) -> bool:
    if not last_scraped_at:
        return True
    try:
        last = datetime.fromisoformat(last_scraped_at)
    except ValueError:
        return True
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return now - last >= timedelta(hours=max(1, int(frequency_hours)))


def next_dead_window_start(after: datetime) -> datetime:
    """Próximo instante elegível (início da janela 01:00 UTC ou o próprio instante se já dentro dela)."""
    if after.tzinfo is None:
        after = after.replace(tzinfo=timezone.utc)
    after = after.astimezone(timezone.utc)
    if is_within_dead_window_utc(after):
        return after
    candidate = after.replace(hour=DEAD_WINDOW_START_HOUR_UTC, minute=0, second=0, microsecond=0)
    if candidate <= after:
        candidate += timedelta(days=1)
    return candidate


def compute_next_scheduled_crawl(last_scraped_at: Optional[str], frequency_hours: int, now: Optional[datetime] = None) -> str:
    now = now or datetime.now(timezone.utc)
    due_at = now
    if last_scraped_at:
        try:
            last = datetime.fromisoformat(last_scraped_at)
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            due_at = max(now, last + timedelta(hours=max(1, int(frequency_hours))))
        except ValueError:
            due_at = now
    return next_dead_window_start(due_at).isoformat()


def build_competitor_page_targets(domain: str) -> List[Tuple[str, str]]:
    """Páginas públicas monitoradas por domínio: (page_type, url)."""
    base = f"https://{domain}"
    return [("catalog", f"{base}/"), ("pricing_table", f"{base}/produtos"), ("blog_post", f"{base}/blog")]


def run_scheduled_competitor_batch(
    account_id: str,
    now_utc: Optional[datetime] = None,
    force_scheduled_batch: bool = False,
    fetcher: Optional[Callable[[str, int], str]] = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    classifier: Optional[Callable[[str, str], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Lote agendado do worker: só executa na janela morta e respeita frequência e jitter por domínio."""
    now = now_utc or datetime.now(timezone.utc)
    if not is_within_dead_window_utc(now, force_scheduled_batch=force_scheduled_batch):
        return {"status": "OUTSIDE_DEAD_WINDOW", "processed_pages": 0, "results": []}

    fetch = fetcher or fetch_page_passively
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, domain, crawl_frequency_hours, last_scraped_at FROM competitors WHERE account_id = ? AND active = 1 ORDER BY id",
            (account_id,),
        ).fetchall()
    finally:
        conn.close()

    results: List[Dict[str, Any]] = []
    for comp_idx, comp in enumerate(rows):
        if not _is_due(comp["last_scraped_at"], comp["crawl_frequency_hours"], now):
            results.append({"competitor_id": comp["id"], "status": "NOT_DUE"})
            continue
        for req_idx, (page_type, url) in enumerate(build_competitor_page_targets(comp["domain"])):
            if req_idx > 0:
                sleep_fn(compute_domain_jitter_seconds(comp["domain"], req_idx))
            try:
                raw = fetch(url, comp_idx + req_idx)
            except Exception as exc:
                results.append({"competitor_id": comp["id"], "page_type": page_type, "status": "FETCH_FAILED", "error": str(exc)[:200]})
                continue
            res = ingest_competitor_page_snapshot(comp["id"], page_type, raw, account_id, classifier=classifier)
            results.append({"competitor_id": comp["id"], "page_type": page_type, **res})

    processed = sum(1 for r in results if r.get("status") in ("INGESTED", "SKIPPED_UNCHANGED_HASH"))
    return {"status": "BATCH_EXECUTED", "processed_pages": processed, "results": results}
