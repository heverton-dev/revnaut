# -*- coding: utf-8 -*-
"""
Seed idempotente e realista da Inteligência de Mercado (TICKET-MKTINTEL-02).

Usado pelo auto-seed de init_db() e por scripts/seed_multinational_enterprise.py.
Hashes de snapshots são SHA-256 reais do DOM limpo (normalize_and_hash_dom) e as
oportunidades referenciam SKUs reais garantidos em products_catalog.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List, Tuple

SEED_ACCOUNT_ID = "0f14ffff"

# SKUs canônicos da Inteligência de Mercado garantidos no catálogo (INSERT OR IGNORE por SKU)
MARKET_INTEL_CATALOG: List[Tuple[str, str, str, str, str, str, Any, Any, Any, float]] = [
    ("prd-mi-cm-3511", "IMP-CM-3511", "Implante Cone Morse Hidrofílico 3.5x11mm", "IMPLANTES", "ANVISA-1034567011", "CONE_MORSE", 3.5, 11.0, 45, 198.0),
    ("prd-mi-he-4013", "IMP-HE-4013", "Implante Hexágono Externo 4.0x13mm", "IMPLANTES", "ANVISA-1034567012", "HEXAGONO_EXTERNO", 4.0, 13.0, 40, 176.0),
    ("prd-mi-bio-05g", "BIO-OSSO-05G", "Biomaterial Enxerto Ósseo Xenógeno Particulado 0.5g", "BIOMATERIAIS", "ANVISA-1034567013", "N/A", None, None, None, 289.0),
    ("prd-mi-kit-full", "KIT-CIRURGICO-FULL", "Kit Cirúrgico Full Arch Guiado com Brocas Cônicas", "INSTRUMENTAIS", "ANVISA-1034567014", "UNIVERSAL", None, None, None, 7900.0),
    ("prd-mi-zr-block", "PRO-ZR-BLOCK-98", "Bloco de Zircônia Multicamada CAD/CAM 98mm", "COMPONENTES PROTETICOS DIGITAIS", "ANVISA-1034567015", "DIGITAL", None, None, None, 640.0),
]

MARKET_SIGNALS: List[Dict[str, Any]] = [
    {
        "id": "msig-anvisa-udi-cm",
        "title": "ANVISA RDC 2026: rastreabilidade UDI obrigatória para implantes Cone Morse",
        "source_url": "https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/2026/rdc-udi-implantes-dentarios",
        "source_type": "regulatory_anvisa",
        "geographic_scope": "BR-SP",
        "raw_content": (
            "A ANVISA publicou RDC que torna obrigatória a identificação única de dispositivo (UDI) em implantes "
            "dentários Cone Morse e componentes protéticos a partir do segundo semestre. Distribuidores deverão "
            "manter rastreabilidade de lote até o paciente, com registro de etiqueta no prontuário cirúrgico."
        ),
    },
    {
        "id": "msig-ciosp-2026-cadcam",
        "title": "Congresso CIOSP 2026: fluxo digital CAD/CAM e zircônia multicamada dominam a agenda",
        "source_url": "https://www.ciosp.com.br/2026/programacao/fluxo-digital-cad-cam",
        "source_type": "congress_ciosp",
        "geographic_scope": "BR-SP",
        "raw_content": (
            "A programação científica do CIOSP 2026 destaca o fluxo digital completo: scanner intraoral, "
            "planejamento CAD/CAM, fresagem chairside e coroas de zircônia multicamada sobre implantes com carga "
            "imediata. Organizadores projetam aumento de 30% no público de protesistas."
        ),
    },
    {
        "id": "msig-fda-510k-ti-sla",
        "title": "FDA 510(k) clearance for hydrophilic Ti-SLA implant surface",
        "source_url": "https://www.accessdata.fda.gov/cdrh_docs/2026/K261234-hydrophilic-ti-sla.pdf",
        "source_type": "regulatory_anvisa",
        "geographic_scope": "US-FL",
        "raw_content": (
            "FDA granted 510(k) clearance to a hydrophilic Ti-SLA implant surface indicated for immediate load "
            "protocols. DSO chains in Florida report growth in same-day implant procedures."
        ),
    },
    {
        "id": "msig-periimplantitis-meta",
        "title": "Meta-análise: peri-implantite e superfícies hidrofílicas em 10 anos de acompanhamento",
        "source_url": "https://doi.org/10.1111/clr.2026.peri-implantitis-meta-analysis",
        "source_type": "scientific_journal",
        "geographic_scope": "GLOBAL",
        "raw_content": (
            "Revisão sistemática com meta-análise de 42 estudos clínicos indica menor incidência de peri-implantite "
            "em implantes com superfície hidrofílica e conexão Cone Morse, com manutenção periodontal semestral."
        ),
    },
    {
        "id": "msig-biomat-sul-surge",
        "title": "Alta de demanda por biomateriais e enxerto ósseo na Região Sul",
        "source_url": "https://www.revistaimplantnews.com.br/2026/mercado/biomateriais-regiao-sul",
        "source_type": "news",
        "geographic_scope": "BR-PR",
        "raw_content": (
            "Distribuidores do Paraná e Santa Catarina relatam crescimento de 22% no consumo de biomateriais, "
            "enxerto ósseo xenógeno e membranas de colágeno para regeneração óssea guiada antes da instalação de implantes."
        ),
    },
    {
        "id": "msig-dso-nordeste-expansion",
        "title": "Redes corporativas de clínicas odontológicas aceleram expansão no Nordeste",
        "source_url": "https://www.valor.globo.com/empresas/2026/redes-clinicas-odontologicas-nordeste",
        "source_type": "news",
        "geographic_scope": "BR-PE",
        "raw_content": (
            "Redes de clínicas odontológicas anunciam expansão de 40 unidades em Pernambuco e Bahia em 2026, com "
            "centrais de compra de implantes e kits cirúrgicos padronizados para reabilitação full arch."
        ),
    },
]

COMPETITORS: List[Dict[str, Any]] = [
    {"id": "comp-implantesul", "name": "ImplanteSul B2B Corp", "domain": "implantesul-b2b.com.br",
     "social_handles": {"instagram": "@implantesulb2b", "linkedin": "implantesul-b2b"}, "crawl_frequency_hours": 72},
    {"id": "comp-neobone", "name": "NeoBone Dental Systems", "domain": "neobone-dental.com",
     "social_handles": {"instagram": "@neobonedental", "youtube": "NeoBoneDental"}, "crawl_frequency_hours": 72},
    {"id": "comp-zirconcad", "name": "ZirconCAD Direct", "domain": "zirconcad.io",
     "social_handles": {"instagram": "@zirconcad", "linkedin": "zirconcad-direct"}, "crawl_frequency_hours": 96},
    {"id": "comp-biograft", "name": "BioGraft LatAm", "domain": "biograft-latam.org",
     "social_handles": {"linkedin": "biograft-latam"}, "crawl_frequency_hours": 120},
]

# (id, competitor_id, page_type, html bruto capturado, created_at)
COMPETITOR_SNAPSHOT_PAGES: List[Tuple[str, str, str, str, str]] = [
    ("snap-seed-is-pricing-01", "comp-implantesul", "pricing_table",
     "<html><head><script>gtag('config','UA-1');</script></head><body><h1>Tabela B2B Implantes Outubro</h1>"
     "<p>Implante Conico 3.75x11mm por R$ 165,00 com 18% de desconto para pedidos acima de 20 unidades.</p>"
     "<p>Kit Cirurgico Guiado por R$ 6.900,00 com 10% de desconto.</p></body></html>",
     "2026-10-12T02:14:07+00:00"),
    ("snap-seed-is-catalog-02", "comp-implantesul", "catalog",
     "<html><body><h1>Lancamento Linha Cone Morse Hidrofilica</h1><p>Implante Cone Morse Hidrofilico 3.5x11mm: R$ 189,90 - 5% off na pre-venda.</p></body></html>",
     "2026-10-15T03:02:51+00:00"),
    ("snap-seed-nb-pricing-01", "comp-neobone", "pricing_table",
     "<html><body><h1>NeoBone Outubro Regeneracao</h1><p>Enxerto osseo xenogeno 0.5g por R$ 239,00 com 15% de desconto.</p>"
     "<p>Membrana de colageno 25x25 por R$ 210,00 com 12% de desconto.</p></body></html>",
     "2026-10-13T01:47:22+00:00"),
    ("snap-seed-zc-social-01", "comp-zirconcad", "social_ad",
     "<html><body><h1>ZirconCAD Direct Black Week Laboratorios</h1><p>Bloco de zirconia multicamada 98mm por R$ 520,00 com 20% de desconto.</p></body></html>",
     "2026-10-14T02:33:10+00:00"),
    ("snap-seed-zc-blog-02", "comp-zirconcad", "blog_post",
     "<html><body><h1>Guia de fresagem chairside em zirconia</h1><p>Conteudo educativo sobre sinterizacao e protocolos CAD/CAM para coroas monoliticas.</p></body></html>",
     "2026-10-16T04:05:44+00:00"),
    ("snap-seed-bg-catalog-01", "comp-biograft", "catalog",
     "<html><body><h1>BioGraft LatAm Catalogo 2026</h1><p>Biomaterial bovino particulado 1g por R$ 299,00 com 8% de desconto para Parana e Santa Catarina.</p></body></html>",
     "2026-10-11T01:21:39+00:00"),
]

# (id, signal_id, snapshot_id, bu_target, skus, type, region, suggested_action)
MARKET_OPPORTUNITIES: List[Tuple[str, Any, Any, str, List[str], str, str, str]] = [
    ("opp-seed-udi-cm", "msig-anvisa-udi-cm", None, "Implantodontia", ["IMP-CM-3511", "KIT-CIRURGICO-FULL"], "CLINICAL_UPGRADE", "BR-SP",
     "Antecipar a RDC de UDI: apresentar IMP-CM-3511 com etiqueta UDI por lote e KIT-CIRURGICO-FULL aos cirurgiões da carteira "
     "de São Paulo, com checklist de rastreabilidade no prontuário e visita do consultor clínico."),
    ("opp-seed-ciosp-cadcam", "msig-ciosp-2026-cadcam", None, "Prótese Digital", ["PRO-ZR-BLOCK-98", "IMP-CM-3511"], "EVENT_SURGE", "BR-SP",
     "Pico de demanda do CIOSP 2026: reservar estoque de PRO-ZR-BLOCK-98 e demonstrações de carga imediata com IMP-CM-3511, "
     "agendar visitas técnicas pré e pós-congresso com protesistas e laboratórios CAD/CAM."),
    ("opp-seed-fda-hydrophilic", "msig-fda-510k-ti-sla", None, "Implantodontia", ["IMP-CM-3511"], "CLINICAL_UPGRADE", "US-FL",
     "Hydrophilic surface momentum in Florida DSOs: posicionar IMP-CM-3511 para protocolos de carga imediata com dossiê técnico "
     "e suporte cirúrgico do time NA-DSO."),
    ("opp-seed-counter-implantesul", None, "snap-seed-is-pricing-01", "Implantodontia", ["IMP-HE-4013", "IMP-CM-3511", "KIT-CIRURGICO-FULL"],
     "PRICE_COUNTER_ATTACK", "BR-SP",
     "Contra-ataque à ImplanteSul (Implante Conico 3.75x11mm a R$ 165,00, 18%): não disputar preço unitário; ofertar IMP-HE-4013 e "
     "IMP-CM-3511 em pacote com KIT-CIRURGICO-FULL, garantia ANVISA com rastreabilidade UDI e entrega DENTGO em 45 min."),
    ("opp-seed-counter-neobone", None, "snap-seed-nb-pricing-01", "Biomateriais", ["BIO-OSSO-05G"], "PRICE_COUNTER_ATTACK", "BR-PR",
     "Contra-ataque à NeoBone em enxerto xenógeno: posicionar BIO-OSSO-05G com laudo de esterilização por lote, "
     "kit de regeneração óssea guiada e reposição DENTGO para clínicas do Paraná."),
    ("opp-seed-biomat-sul", "msig-biomat-sul-surge", None, "Biomateriais", ["BIO-OSSO-05G", "KIT-CIRURGICO-FULL"], "EVENT_SURGE", "BR-PR",
     "Alta de 22% em biomateriais na Região Sul: garantir estoque regional de BIO-OSSO-05G, treinar consultores em ROG "
     "e cruzar com contas de full arch que usam KIT-CIRURGICO-FULL."),
]


def seed_market_intel(conn: sqlite3.Connection, account_id: str = SEED_ACCOUNT_ID) -> Dict[str, int]:
    """Insere (idempotente) catálogo de referência, sinais, concorrentes, snapshots e oportunidades."""
    from src.features.market_intel.crawler_engine import normalize_and_hash_dom
    from src.features.market_intel.llm_classifier import (
        build_tactical_summary,
        classify_market_signal_deterministic,
        extract_offers_deterministic,
    )

    cur = conn.cursor()
    acc = cur.execute("SELECT 1 FROM accounts WHERE id = ?", (account_id,)).fetchone()
    if not acc:
        cur.execute("INSERT OR IGNORE INTO accounts (id, name) VALUES (?, ?)", (account_id, "Revnault Global Dental Group"))

    for pid, sku, name, category, anvisa, platform, diameter, length, torque, price in MARKET_INTEL_CATALOG:
        cur.execute(
            """
            INSERT OR IGNORE INTO products_catalog (
                id, account_id, sku, name, category, anvisa_reg, prosthetic_platform,
                diameter, length, recommended_torque, base_price, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (pid, account_id, sku, name, category, anvisa, platform, diameter, length, torque, price),
        )

    for idx, sig in enumerate(MARKET_SIGNALS):
        payload = classify_market_signal_deterministic(sig["title"], sig["raw_content"])
        payload.pop("engine", None)
        cur.execute(
            """
            INSERT OR IGNORE INTO market_signals (
                id, account_id, title, source_url, source_type, raw_content, structured_payload, geographic_scope, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (sig["id"], account_id, sig["title"], sig["source_url"], sig["source_type"], sig["raw_content"],
             json.dumps(payload, ensure_ascii=False), sig["geographic_scope"], f"2026-10-{10 + idx:02d}T09:00:00+00:00"),
        )

    for comp in COMPETITORS:
        cur.execute(
            """
            INSERT OR IGNORE INTO competitors (
                id, account_id, name, domain, social_handles, active, crawl_frequency_hours, last_scraped_at, created_at
            ) VALUES (?, ?, ?, ?, ?, 1, ?, NULL, '2026-10-01T12:00:00+00:00')
            """,
            (comp["id"], account_id, comp["name"], comp["domain"], json.dumps(comp["social_handles"]), comp["crawl_frequency_hours"]),
        )

    names = {c["id"]: c["name"] for c in COMPETITORS}
    for snap_id, comp_id, page_type, raw_html, created_at in COMPETITOR_SNAPSHOT_PAGES:
        if cur.execute("SELECT 1 FROM competitor_snapshots WHERE id = ?", (snap_id,)).fetchone():
            continue
        cleaned, sha = normalize_and_hash_dom(raw_html)
        offers = extract_offers_deterministic(cleaned)
        cur.execute(
            """
            INSERT INTO competitor_snapshots (
                id, account_id, competitor_id, page_type, extracted_title, content_hash, detected_offers, tactical_summary, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (snap_id, account_id, comp_id, page_type, cleaned.split("\n", 1)[0][:255], sha,
             json.dumps(offers, ensure_ascii=False), build_tactical_summary(names[comp_id], offers), created_at),
        )
        cur.execute(
            "UPDATE competitors SET last_scraped_at = ? WHERE id = ? AND (last_scraped_at IS NULL OR last_scraped_at < ?)",
            (created_at, comp_id, created_at),
        )

    for idx, (opp_id, sig_id, snap_id, bu, skus, opp_type, region, action) in enumerate(MARKET_OPPORTUNITIES):
        cur.execute(
            """
            INSERT OR IGNORE INTO market_opportunities (
                id, account_id, signal_id, competitor_snapshot_id, bu_target, recommended_product_ids,
                opportunity_type, suggested_action, region_code, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)
            """,
            (opp_id, account_id, sig_id, snap_id, bu, json.dumps(skus), opp_type, action, region, f"2026-10-{12 + idx:02d}T10:00:00+00:00"),
        )

    counts = {}
    for tbl in ("market_signals", "competitors", "competitor_snapshots", "market_opportunities"):
        counts[tbl] = cur.execute(f"SELECT COUNT(*) FROM {tbl} WHERE account_id = ?", (account_id,)).fetchone()[0]
    return counts


def seed_market_intel_campaign_history(conn: sqlite3.Connection, account_id: str = SEED_ACCOUNT_ID) -> Dict[str, int]:
    """
    Histórico de uma campanha tática executada (usado pelo seed multinacional completo).
    A trava é anterior a 15 dias, portanto não bloqueia novos disparos de demonstração.
    """
    from src.features.market_intel.campaign_dispatcher import build_campaign_template

    cur = conn.cursor()
    opp = cur.execute(
        "SELECT opportunity_type, bu_target FROM market_opportunities WHERE id = 'opp-seed-udi-cm' AND account_id = ?",
        (account_id,),
    ).fetchone()
    if not opp:
        return {"targeted_campaigns": 0, "campaign_recipient_locks": 0}
    template = build_campaign_template(
        {"opportunity_type": opp[0], "bu_target": opp[1]},
        ["Implante Cone Morse Hidrofílico 3.5x11mm", "Kit Cirúrgico Full Arch Guiado com Brocas Cônicas"],
        "WHATSAPP",
    )
    cur.execute(
        """
        INSERT OR IGNORE INTO targeted_campaigns (
            id, account_id, opportunity_id, target_audience_filter, message_template, channel, dispatch_status,
            scheduled_for, sent_count, skipped_cooldown_15d_count, created_by_user_id, approved_by_user_id, executed_at, created_at
        ) VALUES (?, ?, 'opp-seed-udi-cm', ?, ?, 'WHATSAPP', 'EXECUTED', NULL, 1, 0, 'usr-inside-camila', 'usr-manager-roberto', ?, ?)
        """,
        ("tcmp-seed-udi-sp-01", account_id,
         json.dumps({"region": "BR-SP", "specialty": "Implantodontia", "purchase_window": 90}),
         template, "2026-09-20T13:05:00+00:00", "2026-09-20T12:40:00+00:00"),
    )
    cur.execute(
        """
        INSERT OR IGNORE INTO campaign_recipient_locks (id, account_id, contact_id, campaign_id, opportunity_id, channel, sent_at)
        VALUES ('lock-seed-udi-sp-01', ?, '1', 'tcmp-seed-udi-sp-01', 'opp-seed-udi-cm', 'WHATSAPP', '2026-09-20T13:05:00+00:00')
        """,
        (account_id,),
    )
    return {
        "targeted_campaigns": cur.execute("SELECT COUNT(*) FROM targeted_campaigns WHERE account_id = ?", (account_id,)).fetchone()[0],
        "campaign_recipient_locks": cur.execute(
            "SELECT COUNT(*) FROM campaign_recipient_locks WHERE account_id = ?", (account_id,)
        ).fetchone()[0],
    }
