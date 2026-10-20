# -*- coding: utf-8 -*-
"""
Testes reais da Inteligência de Mercado, Radar de Concorrência e Disparo Determinístico
(TICKET-MKTINTEL-01 a TICKET-MKTINTEL-10). Banco SQLite isolado via tests/conftest.py.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from src.core.database import get_connection, init_db
from src.core.events import StreamName, default_event_bus
from src.features.auth.service import create_session_token
from src.features.market_intel import llm_classifier
from src.features.market_intel.campaign_dispatcher import COOLDOWN_DAYS
from src.features.market_intel.crawler_engine import (
    build_stealth_headers,
    compute_domain_jitter_seconds,
    ingest_competitor_page_snapshot,
    is_within_dead_window_utc,
    normalize_and_hash_dom,
    run_scheduled_competitor_batch,
)
from src.features.market_intel.llm_classifier import (
    classify_market_signal,
    extract_competitor_offers_and_tactics,
)
from src.features.market_intel.opportunity_matcher import match_and_create_opportunity
from src.main import app

ACC = "0f14ffff"


def _ensure_user(user_id: str, role: str, region: str, is_active: int = 1) -> None:
    """Usuário real na tabela users (a matriz RBAC lê papel e praça do cadastro, não de headers)."""
    init_db()
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO users (id, account_id, name, email, role, is_superadmin, is_active) VALUES (?, ?, ?, ?, ?, 0, ?)",
            (user_id, ACC, f"Usuário {user_id}", f"{user_id}@teste.revnault.com", role, is_active),
        )
        conn.execute("UPDATE users SET role = ?, region_code = ?, is_active = ? WHERE id = ?", (role, region, is_active, user_id))
        conn.commit()
    finally:
        conn.close()


def _auth(user_id: str, **extra: str) -> dict:
    return {"Authorization": f"Bearer {create_session_token(user_id)}", **extra}


_ensure_user("usr-manager-pr", "Gerente Regional", "BR-PR")
_ensure_user("usr-inactive-mi", "Gerente Regional", "BR-SP", is_active=0)

# Usuários canônicos do seed: superadmin (Diretoria), Gerente Comercial, Consultor Interno e Externo (praça padrão BR-SP)
DIRECTOR = _auth("usr-superadmin-god")
MANAGER_SP = _auth("usr-manager-roberto")
MANAGER_PR = _auth("usr-manager-pr")
INSIDE_SP = _auth("usr-inside-camila")
FIELD_SP = _auth("usr-field-ricardo")

SEED_SKUS = {"IMP-CM-3511", "IMP-HE-4013", "BIO-OSSO-05G", "KIT-CIRURGICO-FULL"}


@pytest.fixture(autouse=True)
def _deterministic_llm(monkeypatch):
    """Garante o classificador determinístico (sem Ollama/LiteLLM) em todos os testes."""
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("LITELLM_API_KEY", raising=False)


@pytest.fixture
def client():
    init_db()
    return TestClient(app)


def _insert_contact(cur, uf: str, specialty: str, phone: str = "+55 11 98888-0000") -> int:
    cur.execute(
        "INSERT INTO contacts (account_id, name, email, phone, company, specialty, cro_uf) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ACC, f"Dr. Teste {uuid.uuid4().hex[:6]}", f"t{uuid.uuid4().hex[:8]}@clinica.com.br", phone, "Clínica Teste", specialty, uf),
    )
    return int(cur.lastrowid)


# ---------------------------------------------------------------------------------------------
# 1. Schema e seed realista
# ---------------------------------------------------------------------------------------------

def test_schema_tables_and_lock_index_exist():
    conn = get_connection()
    try:
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for t in ("market_signals", "competitors", "competitor_snapshots", "market_opportunities",
                  "targeted_campaigns", "campaign_recipient_locks"):
            assert t in tables, t
        idx_cols = [r["name"] for r in conn.execute("PRAGMA index_info(idx_camp_locks_contact)")]
        assert idx_cols == ["account_id", "contact_id", "sent_at"]
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(targeted_campaigns)")}
        assert {"skipped_cooldown_15d_count", "approved_by_user_id", "created_by_user_id", "executed_at"} <= cols
    finally:
        conn.close()


def test_realistic_dental_seed_is_complete_and_consistent():
    conn = get_connection()
    try:
        scopes = {r[0] for r in conn.execute("SELECT geographic_scope FROM market_signals WHERE account_id = ?", (ACC,))}
        assert {"GLOBAL", "BR-SP", "BR-PR", "BR-PE", "US-FL"} <= scopes
        assert conn.execute("SELECT COUNT(*) FROM market_signals WHERE account_id = ?", (ACC,)).fetchone()[0] >= 6

        domains = {r[0] for r in conn.execute("SELECT domain FROM competitors")}
        assert {"implantesul-b2b.com.br", "neobone-dental.com", "zirconcad.io", "biograft-latam.org"} <= domains

        snaps = conn.execute("SELECT content_hash, detected_offers FROM competitor_snapshots WHERE id LIKE 'snap-seed-%'").fetchall()
        assert len(snaps) == 6
        for s in snaps:
            assert re.fullmatch(r"[0-9a-f]{64}", s["content_hash"])
        offers = json.loads(conn.execute(
            "SELECT detected_offers FROM competitor_snapshots WHERE id = 'snap-seed-is-pricing-01'"
        ).fetchone()[0])
        assert {"product": "Implante Conico 3.75x11mm", "price": 165.0, "discount": "18%"} in offers

        catalog_skus = {r[0] for r in conn.execute("SELECT sku FROM products_catalog")}
        assert SEED_SKUS <= catalog_skus
        types = set()
        for opp in conn.execute("SELECT opportunity_type, recommended_product_ids FROM market_opportunities WHERE id LIKE 'opp-seed-%'"):
            types.add(opp["opportunity_type"])
            for sku in json.loads(opp["recommended_product_ids"]):
                assert sku in catalog_skus, sku
        assert types == {"PRICE_COUNTER_ATTACK", "CLINICAL_UPGRADE", "EVENT_SURGE"}
    finally:
        conn.close()


def test_seed_snapshot_hash_matches_normalized_dom():
    from src.features.market_intel.seed import COMPETITOR_SNAPSHOT_PAGES

    conn = get_connection()
    try:
        for snap_id, _comp, _pt, raw_html, _ts in COMPETITOR_SNAPSHOT_PAGES:
            stored = conn.execute("SELECT content_hash FROM competitor_snapshots WHERE id = ?", (snap_id,)).fetchone()[0]
            assert stored == normalize_and_hash_dom(raw_html)[1]
    finally:
        conn.close()


# ---------------------------------------------------------------------------------------------
# 2. Crawler passivo: janela morta, jitter, headers stealth e dedup SHA-256
# ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize(
    "hour,expected",
    [(0, False), (1, True), (3, True), (4, True), (5, False), (12, False), (23, False)],
)
def test_dead_window_utc_boundaries(hour, expected):
    assert is_within_dead_window_utc(datetime(2026, 10, 20, hour, 30, tzinfo=timezone.utc)) is expected


def test_dead_window_converts_timezone_and_force_flag():
    brt = timezone(timedelta(hours=-3))
    assert is_within_dead_window_utc(datetime(2026, 10, 19, 23, 0, tzinfo=brt)) is True  # 02:00 UTC
    assert is_within_dead_window_utc(datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc), force_scheduled_batch=True) is True


def test_domain_jitter_is_bounded_and_deterministic():
    values = [compute_domain_jitter_seconds(f"dominio{i}.com.br", i) for i in range(300)]
    assert all(7.0 <= v <= 22.0 for v in values)
    assert compute_domain_jitter_seconds("zirconcad.io", 2) == compute_domain_jitter_seconds("zirconcad.io", 2)
    assert len(set(values)) > 200


def test_stealth_headers_rotate_and_hide_webdriver():
    a, b = build_stealth_headers(0), build_stealth_headers(1)
    assert a["headers"]["User-Agent"] != b["headers"]["User-Agent"]
    assert "pt-BR" in a["headers"]["Accept-Language"]
    assert "Object.defineProperty(navigator, 'webdriver', {get: () => false})" in a["init_script"]


def test_normalize_and_hash_dom_strips_scripts_styles_and_trackers():
    noisy = (
        "<html><head><style>.x{color:red}</style><script>track()</script>"
        "<script src='https://www.googletagmanager.com/gtm.js'></script></head>"
        "<body><!-- banner --><h1>Oferta</h1>   <p>Implante   Cone Morse</p>"
        "<img src='https://www.facebook.net/tr?id=1'/></body></html>"
    )
    clean_variant = "<div><h1>Oferta</h1><p>Implante Cone Morse</p></div>"
    text_a, hash_a = normalize_and_hash_dom(noisy)
    text_b, hash_b = normalize_and_hash_dom(clean_variant)
    assert "track" not in text_a and "color" not in text_a and "banner" not in text_a
    assert text_a == "Oferta\nImplante Cone Morse"
    assert hash_a == hash_b and len(hash_a) == 64


def test_unchanged_hash_skips_llm_and_does_not_duplicate_snapshot():
    calls = []

    def spy_classifier(name, text):
        calls.append(name)
        return extract_competitor_offers_and_tactics(name, text)

    html = "<html><body><h1>Promo Implantes</h1><p>Implante Conico 4.0x10mm por R$ 149,00 com 12% de desconto.</p></body></html>"
    first = ingest_competitor_page_snapshot("comp-implantesul", "social_ad", html, ACC, classifier=spy_classifier)
    assert first["status"] == "INGESTED" and first["llm_invoked"] is True
    assert {"product": "Implante Conico 4.0x10mm", "price": 149.0, "discount": "12%"} in first["detected_offers"]

    conn = get_connection()
    try:
        before = conn.execute("SELECT COUNT(*) FROM competitor_snapshots").fetchone()[0]
    finally:
        conn.close()

    # Mesmo conteúdo com ruído de scripts/rastreadores: hash idêntico -> LLM não é chamado
    noisy = html.replace("<body>", "<body><script>fbq('track')</script><!-- ab test -->")
    second = ingest_competitor_page_snapshot("comp-implantesul", "social_ad", noisy, ACC, classifier=spy_classifier)
    assert second == {"status": "SKIPPED_UNCHANGED_HASH", "llm_invoked": False, "content_hash": first["content_hash"]}
    assert len(calls) == 1

    conn = get_connection()
    try:
        assert conn.execute("SELECT COUNT(*) FROM competitor_snapshots").fetchone()[0] == before
    finally:
        conn.close()


def test_scheduled_batch_refuses_outside_dead_window_and_runs_inside():
    fetched = []

    def fake_fetch_never(url, idx):
        fetched.append(url)
        return ""

    noon = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)
    out = run_scheduled_competitor_batch(ACC, now_utc=noon, fetcher=fake_fetch_never, sleep_fn=lambda s: None)
    assert out["status"] == "OUTSIDE_DEAD_WINDOW" and fetched == []

    sleeps = []
    pages = {}

    def page_fetch(url, idx):
        pages[url] = idx
        return f"<html><body><h1>{url}</h1><p>Implante Conico 3.5x10mm por R$ 158,00 com 9% de desconto.</p></body></html>"

    night = datetime(2026, 10, 25, 2, 0, tzinfo=timezone.utc)
    res = run_scheduled_competitor_batch(ACC, now_utc=night, fetcher=page_fetch, sleep_fn=sleeps.append)
    assert res["status"] == "BATCH_EXECUTED"
    assert res["processed_pages"] >= 3
    assert sleeps and all(7.0 <= s <= 22.0 for s in sleeps)


def test_competitor_registration_never_scrapes_synchronously(client, monkeypatch):
    import src.features.market_intel.crawler_engine as ce

    def explode(*_a, **_k):
        raise AssertionError("Raspagem síncrona proibida em clique do usuário")

    monkeypatch.setattr(ce, "fetch_page_passively", explode)
    domain = f"concorrente-{uuid.uuid4().hex[:6]}.com.br"
    res = client.post("/api/v1/competitors", json={"name": "Concorrente Teste", "domain": f"https://www.{domain}/loja"}, headers=DIRECTOR)
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["domain"] == domain
    assert body["last_scraped_at"] is None
    nxt = datetime.fromisoformat(body["next_scheduled_crawl_at"])
    assert 1 <= nxt.astimezone(timezone.utc).hour < 5

    dup = client.post("/api/v1/competitors", json={"name": "Duplicado", "domain": domain}, headers=DIRECTOR)
    assert dup.status_code == 409


# ---------------------------------------------------------------------------------------------
# 3. Classificador odontológico e Opportunity Matcher
# ---------------------------------------------------------------------------------------------

def test_deterministic_dental_classifier_extracts_topics_trends_specialties():
    res = classify_market_signal(
        "CIOSP 2026 destaca CAD/CAM e zircônia",
        "Fluxo digital com scanner intraoral, coroas de zircônia sobre implantes Cone Morse com carga imediata e enxerto ósseo. "
        "Crescimento de 30% no público.",
    )
    assert res["engine"] == llm_classifier.ENGINE_DETERMINISTIC
    assert {"Cone Morse", "Carga Imediata", "CAD/CAM", "Zirconia", "Biomateriais"} <= set(res["topics"])
    assert {"Implantodontia", "Protese Digital"} <= set(res["target_specialties"])
    assert "Expansao de demanda regional" in res["detected_trends"]


def test_classifier_uses_ollama_json_when_available(monkeypatch):
    captured = {}

    class FakeResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"response": json.dumps({
                "topics": ["Rastreabilidade UDI ANVISA"],
                "detected_trends": ["Endurecimento regulatorio"],
                "target_specialties": ["Implantodontia"],
            })}

    def fake_post(url, json=None, timeout=None, **_kw):
        captured["url"] = url
        captured["body"] = json
        return FakeResp()

    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.local:11434")
    monkeypatch.setattr(llm_classifier.httpx, "post", fake_post)
    res = classify_market_signal("RDC UDI", "Rastreabilidade obrigatória")
    assert captured["url"] == "http://ollama.local:11434/api/generate"
    assert captured["body"]["format"] == "json" and captured["body"]["model"] == "qwen2.5:7b"
    assert res["engine"] == "ollama:qwen2.5:7b"
    assert res["topics"] == ["Rastreabilidade UDI ANVISA"]


def test_classifier_falls_back_when_llm_unreachable(monkeypatch):
    def boom(*_a, **_k):
        raise ConnectionError("ollama offline")

    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:9")
    monkeypatch.setattr(llm_classifier.httpx, "post", boom)
    res = classify_market_signal("Peri-implantite", "Meta-análise sobre peri-implantite")
    assert res["engine"] == llm_classifier.ENGINE_DETERMINISTIC
    assert "Peri-implantite" in res["topics"] and "Periodontia" in res["target_specialties"]


def test_offer_extraction_parses_brl_prices_and_discounts():
    res = extract_competitor_offers_and_tactics(
        "NeoBone",
        "Kit Cirurgico Guiado por R$ 6.900,00 com 10% de desconto. Enxerto osseo 1g: R$ 1.250,50 - 7% off",
    )
    offers = {o["product"]: o for o in res["detected_offers"]}
    assert offers["Kit Cirurgico Guiado"]["price"] == 6900.0 and offers["Kit Cirurgico Guiado"]["discount"] == "10%"
    assert offers["Enxerto osseo 1g"]["price"] == 1250.5 and offers["Enxerto osseo 1g"]["discount"] == "7%"
    assert "DENTGO" in res["tactical_summary"] and "ANVISA" in res["tactical_summary"]


def test_matcher_counter_attack_from_snapshot_uses_real_catalog_skus():
    opp = match_and_create_opportunity(ACC, competitor_snapshot_id="snap-seed-bg-catalog-01", region_code="BR-PR")
    assert opp["created"] is True
    assert opp["opportunity_type"] == "PRICE_COUNTER_ATTACK"
    assert opp["bu_target"] == "Biomateriais"
    assert opp["recommended_product_ids"]
    conn = get_connection()
    try:
        for sku in opp["recommended_product_ids"]:
            cat = conn.execute("SELECT category FROM products_catalog WHERE sku = ?", (sku,)).fetchone()
            assert cat is not None and "BIOMAT" in cat[0].upper()
    finally:
        conn.close()
    assert "R$ 299,00" in opp["suggested_action"]

    again = match_and_create_opportunity(ACC, competitor_snapshot_id="snap-seed-bg-catalog-01", region_code="BR-PR")
    assert again["created"] is False and again["id"] == opp["id"]

    seeded = match_and_create_opportunity(ACC, competitor_snapshot_id="snap-seed-nb-pricing-01", region_code="BR-PR")
    assert seeded["created"] is False and seeded["id"] == "opp-seed-counter-neobone"


@pytest.mark.parametrize(
    "signal_id,expected_type,expected_bu",
    [
        ("msig-ciosp-2026-cadcam", "EVENT_SURGE", "Prótese Digital"),
        ("msig-anvisa-udi-cm", "CLINICAL_UPGRADE", "Implantodontia"),
        ("msig-periimplantitis-meta", "CLINICAL_UPGRADE", "Implantodontia"),
    ],
)
def test_matcher_signal_type_and_bu(signal_id, expected_type, expected_bu):
    opp = match_and_create_opportunity(ACC, signal_id=signal_id, region_code="GLOBAL")
    assert opp["opportunity_type"] == expected_type
    assert opp["bu_target"] == expected_bu
    assert opp["recommended_product_ids"]


def test_match_endpoint_and_vector_indexing(client):
    res = client.post(
        "/api/v1/market-intel/opportunities/match",
        json={"signal_id": "msig-biomat-sul-surge", "region_code": "BR-PR"},
        headers={**MANAGER_PR},
    )
    assert res.status_code == 200, res.text
    assert res.json()["bu_target"] == "Biomateriais"
    conn = get_connection()
    try:
        n = conn.execute(
            "SELECT COUNT(*) FROM semantic_embeddings WHERE tenant_id = ? AND entity_type = 'mkt_product_catalog'", (ACC,)
        ).fetchone()[0]
        assert n >= len(SEED_SKUS)
    finally:
        conn.close()
    bad = client.post("/api/v1/market-intel/opportunities/match", json={}, headers=DIRECTOR)
    assert bad.status_code == 422


# ---------------------------------------------------------------------------------------------
# 4. Endpoints e matriz RBAC territorial (Seção 5)
# ---------------------------------------------------------------------------------------------

def test_signals_endpoint_scope_filters_and_pagination(client):
    all_dir = client.get("/api/v1/market-intel/signals?limit=50", headers=DIRECTOR).json()
    assert all_dir["total"] >= 6 and all_dir["visible_scopes"] == ["*"]

    sp = client.get("/api/v1/market-intel/signals?limit=50", headers=INSIDE_SP).json()
    assert {s["geographic_scope"] for s in sp["items"]} <= {"GLOBAL", "BR-SP"}
    assert client.get("/api/v1/market-intel/signals?scope=BR-PE", headers=INSIDE_SP).status_code == 403

    anvisa = client.get("/api/v1/market-intel/signals?source_type=regulatory_anvisa", headers=DIRECTOR).json()
    assert anvisa["items"] and all(s["source_type"] == "regulatory_anvisa" for s in anvisa["items"])

    perio = client.get("/api/v1/market-intel/signals?specialty=Periodontia", headers=DIRECTOR).json()
    assert perio["items"] and all("Periodontia" in s["structured_payload"]["target_specialties"] for s in perio["items"])

    page = client.get("/api/v1/market-intel/signals?limit=2&offset=1", headers=DIRECTOR).json()
    assert len(page["items"]) == 2 and page["offset"] == 1


def test_opportunities_endpoint_filters_and_products(client):
    res = client.get("/api/v1/market-intel/opportunities?bu_target=Biomateriais", headers=DIRECTOR)
    assert res.status_code == 200
    items = res.json()
    assert items and all(o["bu_target"] == "Biomateriais" for o in items)
    assert any(p["sku"] == "BIO-OSSO-05G" for o in items for p in o["recommended_products"])

    field = client.get("/api/v1/market-intel/opportunities", headers=FIELD_SP).json()
    assert field and {o["region_code"] for o in field} <= {"GLOBAL", "BR-SP"}


def test_competitor_creation_restricted_to_director(client):
    payload = {"name": "Concorrente RBAC", "domain": f"rbac-{uuid.uuid4().hex[:6]}.com"}
    for headers in (MANAGER_SP, INSIDE_SP, FIELD_SP):
        assert client.post("/api/v1/competitors", json=payload, headers=headers).status_code == 403
    listing = client.get("/api/v1/competitors", headers=FIELD_SP).json()
    assert listing["can_manage_competitors"] is False
    assert listing["passive_queue"]["dead_window_utc"] == "01:00-05:00"
    assert listing["passive_queue"]["ad_hoc_scraping_allowed"] is False


def test_competitor_snapshots_timeline_and_tactical_insights(client):
    snaps = client.get("/api/v1/competitors/comp-zirconcad/snapshots", headers=FIELD_SP)
    assert snaps.status_code == 200
    data = snaps.json()
    assert len(data) >= 2
    assert [s["created_at"] for s in data] == sorted([s["created_at"] for s in data], reverse=True)
    assert client.get("/api/v1/competitors/comp-inexistente/snapshots", headers=DIRECTOR).status_code == 404

    insights = client.get("/api/v1/competitors/tactical-insights", headers=INSIDE_SP).json()
    assert any("DENTGO" in p for p in insights["value_pillars"])
    zr = [i for i in insights["insights"] if i["competitor_id"] == "comp-zirconcad" and "zirconia" in i["competitor_product"].lower()]
    assert zr and zr[0]["matched_sku"] == "PRO-ZR-BLOCK-98"
    assert zr[0]["price_gap_pct"] == pytest.approx(round((640.0 - 520.0) / 520.0 * 100, 1))


def test_field_sales_cannot_generate_draft_and_inside_sales_can(client):
    body = {"opportunity_id": "opp-seed-udi-cm", "channel": "WHATSAPP"}
    assert client.post("/api/v1/market-intel/campaigns/generate-draft", json=body, headers=FIELD_SP).status_code == 403

    res = client.post("/api/v1/market-intel/campaigns/generate-draft", json=body, headers=INSIDE_SP)
    assert res.status_code == 201, res.text
    draft = res.json()
    assert draft["dispatch_status"] == "DRAFT"
    assert draft["compliance"]["is_compliant"] is True
    assert draft["target_audience_filter"]["region"] == "BR-SP"
    assert "CRO-SP" in draft["message_template"]

    # Consultor interno de SP não opera praça do Paraná
    pr = client.post(
        "/api/v1/market-intel/campaigns/generate-draft",
        json={"opportunity_id": "opp-seed-counter-neobone", "channel": "WHATSAPP"},
        headers=INSIDE_SP,
    )
    assert pr.status_code == 403


def test_draft_rejects_cfo_violating_copy(client):
    res = client.post(
        "/api/v1/market-intel/campaigns/generate-draft",
        json={
            "opportunity_id": "opp-seed-udi-cm",
            "channel": "WHATSAPP",
            "message_template": "Preço imbatível! Resultado garantido com desconto de 30%. CRO-SP 12345",
        },
        headers=DIRECTOR,
    )
    assert res.status_code == 422
    assert res.json()["detail"]["violations"]


def test_dispatch_forbidden_for_inside_and_field_sales(client):
    draft = client.post(
        "/api/v1/market-intel/campaigns/generate-draft",
        json={"opportunity_id": "opp-seed-ciosp-cadcam", "channel": "EMAIL"},
        headers=DIRECTOR,
    ).json()
    for headers in (INSIDE_SP, FIELD_SP):
        assert client.post(f"/api/v1/campaigns/{draft['id']}/dispatch", headers=headers).status_code == 403
        assert client.post(f"/api/v1/market-intel/campaigns/{draft['id']}/dispatch", headers=headers).status_code == 403
    # Gerente do Paraná não dispara campanha de São Paulo
    assert client.post(f"/api/v1/campaigns/{draft['id']}/dispatch", headers=MANAGER_PR).status_code == 403


# ---------------------------------------------------------------------------------------------
# 5. Trava anti-spam determinística de 15 dias
# ---------------------------------------------------------------------------------------------

def test_deterministic_15_day_cooldown_lock(client):
    specialty = f"Implantodontia Cooldown {uuid.uuid4().hex[:6]}"
    conn = get_connection()
    try:
        cur = conn.cursor()
        fresh = [_insert_contact(cur, "SP", specialty) for _ in range(3)]
        old_locked = _insert_contact(cur, "SP", specialty)
        cur.execute(
            "INSERT INTO campaign_recipient_locks (id, account_id, contact_id, campaign_id, opportunity_id, channel, sent_at) "
            "VALUES (?, ?, ?, 'tcmp-antigo', 'opp-seed-udi-cm', 'WHATSAPP', ?)",
            (f"lock-{uuid.uuid4().hex[:8]}", ACC, str(old_locked),
             (datetime.now(timezone.utc) - timedelta(days=COOLDOWN_DAYS + 1)).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()

    def new_draft():
        r = client.post(
            "/api/v1/market-intel/campaigns/generate-draft",
            json={"opportunity_id": "opp-seed-udi-cm", "channel": "WHATSAPP", "specialty": specialty},
            headers=MANAGER_SP,
        )
        assert r.status_code == 201, r.text
        return r.json()["id"]

    first_id = new_draft()
    first = client.post(f"/api/v1/campaigns/{first_id}/dispatch", headers=MANAGER_SP)
    assert first.status_code == 200, first.text
    f = first.json()
    assert f["eligible_count"] == 4
    assert f["sent_count"] == 4  # trava de 16 dias atrás já expirou
    assert f["skipped_cooldown_15d_count"] == 0

    second_id = new_draft()
    second = client.post(f"/api/v1/market-intel/campaigns/{second_id}/dispatch", headers=DIRECTOR).json()
    assert second["sent_count"] == 0
    assert second["skipped_cooldown_15d_count"] == 4

    conn = get_connection()
    try:
        camp = conn.execute("SELECT * FROM targeted_campaigns WHERE id = ?", (first_id,)).fetchone()
        assert camp["dispatch_status"] == "EXECUTED" and camp["approved_by_user_id"] == "usr-manager-roberto"
        assert camp["executed_at"]
        second_row = conn.execute("SELECT sent_count, skipped_cooldown_15d_count FROM targeted_campaigns WHERE id = ?", (second_id,)).fetchone()
        assert tuple(second_row) == (0, 4)
        assert conn.execute(
            "SELECT status FROM market_opportunities WHERE id = 'opp-seed-udi-cm'"
        ).fetchone()[0] == "CAMPAIGN_TRIGGERED"
        locks = conn.execute(
            f"SELECT COUNT(*) FROM campaign_recipient_locks WHERE campaign_id = ? AND contact_id IN ({','.join('?' * 4)})",
            (first_id, *[str(c) for c in fresh + [old_locked]]),
        ).fetchone()[0]
        assert locks == 4
        msgs = conn.execute(
            "SELECT COUNT(*) FROM omnichannel_messages WHERE instance_name = 'inst_market_intel' AND content LIKE '%CRO-SP%'"
        ).fetchone()[0]
        assert msgs >= 4
    finally:
        conn.close()

    # Campanha já executada não pode ser disparada de novo
    assert client.post(f"/api/v1/campaigns/{first_id}/dispatch", headers=DIRECTOR).status_code == 409


def test_campaigns_listing_with_opportunity_metadata(client):
    res = client.get("/api/v1/market-intel/campaigns", headers=DIRECTOR)
    assert res.status_code == 200
    items = res.json()
    assert items and all(c["opportunity_type"] and c["bu_target"] for c in items)
    field = client.get("/api/v1/market-intel/campaigns", headers=FIELD_SP).json()
    assert all(c["target_audience_filter"]["region"] in ("GLOBAL", "BR-SP") for c in field)


def test_market_intel_stream_registered_in_worker():
    from src.workers.runner import build_registered_worker_consumers, handle_market_intel_stream

    assert StreamName.MARKET_INTEL.value == "stream:market_intel"
    pairs = build_registered_worker_consumers(default_event_bus)
    assert any(handler is handle_market_intel_stream for _c, handler in pairs)


def test_worker_handles_snapshot_event_into_opportunity():
    import asyncio
    from src.workers.runner import handle_market_intel_stream

    out = asyncio.run(handle_market_intel_stream({
        "event_type": "competitor.snapshot.ingested",
        "tenant_id": ACC,
        "payload": {"snapshot_id": "snap-seed-zc-social-01", "region_code": "BR-SP"},
    }))
    assert out["status"] == "processed" and out["opportunity_id"] and out["created"] is True
    conn = get_connection()
    try:
        row = conn.execute("SELECT bu_target, opportunity_type FROM market_opportunities WHERE id = ?", (out["opportunity_id"],)).fetchone()
        assert tuple(row) == ("Prótese Digital", "PRICE_COUNTER_ATTACK")
    finally:
        conn.close()


# ---------------------------------------------------------------------------------------------
# 6. Autenticação: RBAC derivado do usuário autenticado, nunca de headers livres
# ---------------------------------------------------------------------------------------------

PROTECTED_CALLS = [
    ("GET", "/api/v1/market-intel/me", None),
    ("GET", "/api/v1/market-intel/signals", None),
    ("GET", "/api/v1/market-intel/opportunities", None),
    ("POST", "/api/v1/market-intel/opportunities/match", {"signal_id": "msig-anvisa-udi-cm"}),
    ("POST", "/api/v1/market-intel/campaigns/generate-draft", {"opportunity_id": "opp-seed-udi-cm", "channel": "WHATSAPP"}),
    ("GET", "/api/v1/market-intel/campaigns", None),
    ("POST", "/api/v1/market-intel/campaigns/tcmp-x/dispatch", None),
    ("POST", "/api/v1/campaigns/tcmp-x/dispatch", None),
    ("GET", "/api/v1/competitors", None),
    ("POST", "/api/v1/competitors", {"name": "Sem Auth", "domain": "sem-auth.com.br"}),
    ("GET", "/api/v1/competitors/tactical-insights", None),
    ("GET", "/api/v1/competitors/comp-zirconcad/snapshots", None),
]


@pytest.mark.parametrize("method,path,body", PROTECTED_CALLS)
@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"X-User-Role": "director", "X-User-Id": "usr-superadmin-god", "X-User-Region": "GLOBAL"},
        {"Authorization": "Bearer usr-superadmin-god.1700000000.assinatura-forjada"},
        {"Authorization": "usr-superadmin-god"},
    ],
    ids=["sem-credencial", "headers-livres", "token-forjado", "sem-esquema-bearer"],
)
def test_all_market_intel_routes_require_valid_session_token(client, method, path, body, headers):
    res = client.request(method, path, json=body, headers=headers)
    assert res.status_code == 401, (path, res.status_code, res.text)


def test_inactive_user_token_is_rejected(client):
    assert client.get("/api/v1/market-intel/me", headers=_auth("usr-inactive-mi")).status_code == 401


def test_role_header_cannot_escalate_privileges(client):
    escalate = {"X-User-Role": "director", "X-User-Region": "GLOBAL"}

    me = client.get("/api/v1/market-intel/me", headers={**FIELD_SP, **escalate}).json()
    assert me["actual_role"] == "field_sales" and me["effective_role"] == "field_sales"
    assert me["region"] == "BR-SP" and me["can_simulate"] is False

    payload = {"name": "Escalada", "domain": f"escalada-{uuid.uuid4().hex[:6]}.com"}
    assert client.post("/api/v1/competitors", json=payload, headers={**FIELD_SP, **escalate}).status_code == 403
    assert client.post(
        "/api/v1/market-intel/campaigns/generate-draft",
        json={"opportunity_id": "opp-seed-udi-cm", "channel": "WHATSAPP"},
        headers={**FIELD_SP, **escalate},
    ).status_code == 403
    # Praça falsificada não amplia o escopo territorial
    assert client.get("/api/v1/market-intel/signals?scope=BR-PE", headers={**INSIDE_SP, **escalate}).status_code == 403

    draft = client.post(
        "/api/v1/market-intel/campaigns/generate-draft",
        json={"opportunity_id": "opp-seed-udi-cm", "channel": "EMAIL"},
        headers={**INSIDE_SP, **escalate},
    )
    assert draft.status_code == 201
    assert client.post(f"/api/v1/campaigns/{draft.json()['id']}/dispatch", headers={**INSIDE_SP, **escalate}).status_code == 403

    # Gerente do Paraná não vira gerente de São Paulo trocando X-User-Region
    me_pr = client.get("/api/v1/market-intel/me", headers={**MANAGER_PR, "X-User-Region": "BR-SP"}).json()
    assert me_pr["effective_role"] == "regional_manager" and me_pr["region"] == "BR-PR"
    assert client.post(
        f"/api/v1/campaigns/{draft.json()['id']}/dispatch", headers={**MANAGER_PR, "X-User-Region": "BR-SP"}
    ).status_code == 403


def test_director_can_simulate_lower_profiles(client):
    me = client.get("/api/v1/market-intel/me", headers=DIRECTOR).json()
    assert me["actual_role"] == "director" and me["can_simulate"] is True and me["visible_scopes"] == ["*"]

    sim = {**DIRECTOR, "X-User-Role": "field_sales", "X-User-Region": "BR-PE"}
    me_sim = client.get("/api/v1/market-intel/me", headers=sim).json()
    assert me_sim["effective_role"] == "field_sales" and me_sim["region"] == "BR-PE"
    assert me_sim["visible_scopes"] == ["BR-PE", "GLOBAL"]
    assert client.post(
        "/api/v1/market-intel/campaigns/generate-draft",
        json={"opportunity_id": "opp-seed-udi-cm", "channel": "WHATSAPP"},
        headers=sim,
    ).status_code == 403
    assert client.get("/api/v1/market-intel/me", headers={**DIRECTOR, "X-User-Role": "papel-inexistente"}).status_code == 400


def test_tenant_comes_from_user_not_from_account_header(client):
    assert client.get("/api/v1/market-intel/me", headers=DIRECTOR).json()["account_id"] == ACC
    # Tenant de outra conta em header ou query é recusado pelo middleware de autenticação
    assert client.get("/api/v1/market-intel/me", headers={**DIRECTOR, "X-Account-ID": "tenant-alheio"}).status_code == 403
    assert client.get("/api/v1/market-intel/signals?account_id=tenant-alheio", headers=DIRECTOR).status_code == 403
    assert client.get("/api/v1/market-intel/signals", headers={**DIRECTOR, "X-Account-ID": ACC}).json()["total"] >= 6
