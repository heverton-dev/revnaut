# -*- coding: utf-8 -*-
"""
STAGE 1 & STAGE 2 — Automated Playwright E2E, Multi-Viewport & Engine Utilization Harness
Executes deep full-stack homologation of REVNAULT:
1. Audits FastAPI (`src.main:app`) vs React 19 SPA (`frontend/src/` & `frontend/dist/`).
2. Cross-references all backend endpoints across `src/features/**/router.py` against `frontend/src/**/*.tsx`
   to compute the exact Engine Utilization Ratio (%) across all 38 domain modules.
3. Launches a live FastAPI server and runs Playwright Chromium across all 17 routes and 4 mandatory viewports:
   - Mobile: 375x812
   - Tablet: 768x1024
   - Corporate Laptop: 1366x768
   - Desktop Full HD: 1920x1080
4. Captures console errors, page errors, failed network requests (HTTP >= 400), horizontal overflow,
   sidebar/main width ratios, clipped/overlapping elements, interactive element counts vs real mutations,
   and hardcoded prop traps.
"""

from __future__ import annotations

import glob
import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

VIEWPORTS = [
    {"name": "Mobile", "width": 375, "height": 812},
    {"name": "Tablet", "width": 768, "height": 1024},
    {"name": "Corporate_Laptop", "width": 1366, "height": 768},
    {"name": "Desktop_Full_HD", "width": 1920, "height": 1080},
]

ALL_APP_ROUTES: List[Dict[str, Any]] = [
    {"id": "dashboard", "label": "Cockpit Executivo", "in_sidebar": True},
    {"id": "deals", "label": "Pipeline & Deals", "in_sidebar": True},
    {"id": "contacts", "label": "Cirurgiões & Clínicas", "in_sidebar": True},
    {"id": "omnichannel", "label": "Inbox Omnichannel", "in_sidebar": True},
    {"id": "keypartners", "label": "KeyPartners (Consignados)", "in_sidebar": True},
    {"id": "dentgo", "label": "DENTGO (Same-Day)", "in_sidebar": True},
    {"id": "video_sos", "label": "Vídeo Suporte SOS", "in_sidebar": True},
    {"id": "contracts", "label": "Contratos Documenso", "in_sidebar": True},
    {"id": "intelligence", "label": "IA Copilot Granola", "in_sidebar": True},
    {"id": "analytics", "label": "BI Superset RLS", "in_sidebar": True},
    {"id": "scheduling", "label": "Cal.com Reativação", "in_sidebar": True},
    {"id": "rbac", "label": "RBAC & Hierarquia", "in_sidebar": True},
    {"id": "support", "label": "Suporte & RMA", "in_sidebar": True},
    {"id": "settings", "label": "Configurações & ERP", "in_sidebar": True},
    {"id": "scoring", "label": "Lead Scoring ICP", "in_sidebar": True},
    {"id": "marketing", "label": "Marketing & LPs", "in_sidebar": True},
    {"id": "imaging", "label": "PACS 3D DICOM/STL", "in_sidebar": True},
]


def normalize_path(path: str) -> str:
    """Normalizes URL path parameters like {deal_id} or ${id} to {*}."""
    p = path.split("?")[0].strip()
    p = re.sub(r"\$\{[^}]+\}", "{*}", p)
    p = re.sub(r"\{[^}]+\}", "{*}", p)
    return p.rstrip("/") or "/"


def classify_domain_module(method: str, full_path: str, tags: List[str]) -> str:
    """Classifies a backend endpoint into one of the 38 canonical domain modules."""
    p = full_path.lower()
    if "/contacts" in p:
        return "contacts"
    if "/deals/catalog" in p:
        return "catalog_pricing"
    if "generate-contract" in p or "/contracts" in p or "documenso" in p:
        return "documenso"
    if "/deals" in p or "/pipelines" in p or p == "/api/v1/metrics":
        return "deals"
    if "/campaigns/landing-pages" in p or "/campaigns/public/lp" in p:
        return "campaigns/landing_pages"
    if "mautic" in p:
        return "campaigns/mautic"
    if "listmonk" in p:
        return "campaigns/listmonk"
    if "/campaigns/referral" in p or "/campaigns/metrics" in p:
        return "campaigns/referral_mgm"
    if "/scoring" in p:
        return "scoring"
    if "/communications" in p or "/chat" in p or "/conversations" in p:
        return "communications/livekit"
    if "/transcriptions" in p:
        return "intelligence/transcription"
    if "/copilot" in p:
        return "intelligence/granola"
    if "/catalog-rag" in p:
        return "intelligence/surgical_rag"
    if "/bi/text-to-sql" in p:
        return "intelligence/text_to_sql"
    if "/bi/" in p:
        return "intelligence/superset"
    if "/inventory/" in p:
        return "intelligence/predictive_inventory"
    if "/margin/" in p:
        return "intelligence/clinical_margin"
    if "/health-score/" in p:
        return "intelligence/health_score_hsc"
    if "/imaging" in p or "/studies" in p:
        return "intelligence/orthanc_dicom"
    if "/intelligence/" in p:
        return "keypartners/kol"
    if "/keypartners/agreements" in p or "/keypartners/kits" in p:
        return "keypartners/custody"
    if "/keypartners/surgical-orders" in p:
        return "keypartners/surgical_cycle"
    if "/keypartners/kol-contracts" in p:
        return "keypartners/kol"
    if "/keypartners/loyalty" in p:
        return "keypartners/loyalty"
    if "/keypartners/consignments" in p or "/dentgo/synergy" in p:
        return "dentgo/synergy"
    if "/dentgo/hubs" in p:
        return "dentgo/hubs"
    if "/dentgo/orders" in p and "/split" not in p:
        return "dentgo/logistics"
    if "/split" in p:
        return "dentgo/financial_split"
    if "/dentgo/fefo" in p:
        return "dentgo/fefo_flash_deals"
    if "whatsapp" in p or "evolution" in p:
        return "omnichannel/evolution"
    if "/omnichannel/" in p or "chatwoot" in p:
        return "omnichannel/chatwoot"
    if "/surgical-sos" in p:
        return "tickets/surgical_sos"
    if "/anvisa-rma" in p or "/tickets" in p:
        return "tickets/anvisa_rma"
    if "/postop-care" in p or "/automations/flows" in p or "/automations/logs" in p or "evaluate-hot-lead" in p:
        return "automations/postop_b2c"
    if "/calcom" in p:
        return "automations/calcom"
    if "/integrations/totvs" in p or "/integrations/erp" in p:
        return "erp_hub/windmill"
    if "/webhooks" in p:
        return "webhooks/outbound"
    if "/auth" in p:
        return "auth/vault"
    if "/hierarchy" in p:
        return "rbac/hierarchy"
    if "/storage" in p:
        return "storage/r2"
    if "/institutions" in p:
        return "institutions"
    if "/tasks" in p:
        return "tasks"
    if "/quarteto" in p or p in ("/mcp", "/docs/guia"):
        return "quarteto"
    return "system"


def analyze_engine_utilization() -> Dict[str, Any]:
    """Cross-references FastAPI OpenAPI schema and routers against frontend TS/TSX fetch calls."""
    from src.main import app

    openapi = app.openapi()
    paths_obj = openapi.get("paths", {})

    # Extract all frontend fetch calls
    frontend_files = sorted(glob.glob(str(PROJECT_ROOT / "frontend" / "src" / "**" / "*.ts*"), recursive=True))
    frontend_calls: List[Dict[str, Any]] = []
    hardcoded_props: List[Dict[str, Any]] = []

    fetch_pattern = re.compile(
        r"fetch\(\s*(?:`([^`]+)`|'([^']+)'|\"([^\"]+)\")(?:\s*,\s*\{([^}]*)\})?",
        re.DOTALL,
    )
    method_pattern = re.compile(r"method\s*:\s*['\"](GET|POST|PUT|PATCH|DELETE)['\"]", re.IGNORECASE)

    prop_trap_patterns = [
        ("dealId", r'dealId\s*=\s*["\']([^"\']+)["\']'),
        ("contactIdentifier", r'contactIdentifier\s*=\s*["\']([^"\']+)["\']'),
        ("contactId", r'contactId\s*=\s*["\']([^"\']+)["\']'),
        ("studyId", r'studyId\s*=\s*["\']([^"\']+)["\']'),
        ("campaignId", r'campaignId\s*=\s*["\']([^"\']+)["\']'),
        ("dashboardId", r'dashboardId\s*=\s*["\']([^"\']+)["\']'),
        ("accountId", r'accountId\s*=\s*["\']([^"\']+)["\']'),
        ("userId", r'userId\s*=\s*["\']([^"\']+)["\']'),
    ]

    for fpath in frontend_files:
        rel_file = os.path.relpath(fpath, PROJECT_ROOT).replace("\\", "/")
        content = Path(fpath).read_text(encoding="utf-8")

        for m in fetch_pattern.finditer(content):
            raw_url = m.group(1) or m.group(2) or m.group(3) or ""
            opts = m.group(4) or ""
            mm = method_pattern.search(opts)
            http_method = mm.group(1).upper() if mm else "GET"
            norm_url = normalize_path(raw_url)
            frontend_calls.append(
                {
                    "file": rel_file,
                    "method": http_method,
                    "raw_url": raw_url,
                    "normalized_path": norm_url,
                }
            )

        for prop_name, pat in prop_trap_patterns:
            for pm in re.finditer(pat, content):
                line_no = content[: pm.start()].count("\n") + 1
                hardcoded_props.append(
                    {
                        "file": rel_file,
                        "line": line_no,
                        "prop": prop_name,
                        "hardcoded_value": pm.group(1),
                    }
                )

    frontend_lookup: Dict[Tuple[str, str], List[str]] = {}
    for call in frontend_calls:
        key = (call["method"], call["normalized_path"])
        frontend_lookup.setdefault(key, []).append(call["file"])

    domain_stats: Dict[str, Dict[str, Any]] = {}
    all_backend_operations: List[Dict[str, Any]] = []

    for raw_path, methods_dict in sorted(paths_obj.items()):
        norm_p = normalize_path(raw_path)
        for m_lower, spec in methods_dict.items():
            if m_lower.upper() not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                continue
            method = m_lower.upper()
            tags = spec.get("tags", [])
            summary = spec.get("summary", "")
            domain = classify_domain_module(method, raw_path, tags)

            matched_files = frontend_lookup.get((method, norm_p), [])
            is_exposed = len(matched_files) > 0

            op_info = {
                "domain": domain,
                "method": method,
                "path": raw_path,
                "normalized_path": norm_p,
                "summary": summary,
                "is_exposed_in_ui": is_exposed,
                "ui_files": sorted(set(matched_files)),
            }
            all_backend_operations.append(op_info)

            d_entry = domain_stats.setdefault(
                domain,
                {
                    "domain": domain,
                    "total_endpoints": 0,
                    "exposed_endpoints": 0,
                    "orphaned_endpoints": 0,
                    "utilization_pct": 0.0,
                    "exposed_list": [],
                    "orphaned_list": [],
                },
            )
            d_entry["total_endpoints"] += 1
            if is_exposed:
                d_entry["exposed_endpoints"] += 1
                d_entry["exposed_list"].append(f"{method} {raw_path}")
            else:
                d_entry["orphaned_endpoints"] += 1
                d_entry["orphaned_list"].append(f"{method} {raw_path}")

    for d_entry in domain_stats.values():
        tot = d_entry["total_endpoints"]
        exp = d_entry["exposed_endpoints"]
        d_entry["utilization_pct"] = round((exp / tot) * 100.0, 1) if tot > 0 else 0.0

    total_ops = len(all_backend_operations)
    exposed_ops = sum(1 for op in all_backend_operations if op["is_exposed_in_ui"])
    orphaned_ops = total_ops - exposed_ops
    global_pct = round((exposed_ops / total_ops) * 100.0, 2) if total_ops > 0 else 0.0

    return {
        "total_openapi_paths": len(paths_obj),
        "total_backend_operations": total_ops,
        "exposed_in_frontend_count": exposed_ops,
        "orphaned_in_backend_count": orphaned_ops,
        "global_utilization_pct": global_pct,
        "frontend_fetch_calls": frontend_calls,
        "hardcoded_prop_traps": hardcoded_props,
        "domain_utilization": dict(sorted(domain_stats.items())),
        "all_operations": all_backend_operations,
    }


def find_free_port(default_port: int = 8019) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", default_port)) != 0:
            return default_port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run_playwright_audit(base_url: str) -> Dict[str, Any]:
    """Runs Playwright across all 17 routes and 4 mandatory viewports."""
    from playwright.sync_api import sync_playwright

    route_results: Dict[str, Any] = {}
    viewport_summary: Dict[str, Any] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for vp in VIEWPORTS:
            vp_name = vp["name"]
            vp_w = vp["width"]
            vp_h = vp["height"]
            viewport_summary[vp_name] = {
                "width": vp_w,
                "height": vp_h,
                "routes_tested": 0,
                "routes_with_horizontal_overflow": 0,
                "routes_with_cramped_main_area": 0,
                "total_console_errors": 0,
                "total_failed_requests": 0,
            }

            context = browser.new_context(viewport={"width": vp_w, "height": vp_h})
            page = context.new_page()

            console_errors: List[str] = []
            page_errors: List[str] = []
            failed_requests: List[Dict[str, Any]] = []
            api_mutations: List[Dict[str, Any]] = []

            page.on(
                "console",
                lambda msg: console_errors.append(f"[{msg.type}] {msg.text}")
                if msg.type == "error"
                else None,
            )
            page.on("pageerror", lambda err: page_errors.append(str(err)))
            page.on(
                "response",
                lambda res: failed_requests.append(
                    {"url": res.url, "status": res.status, "method": res.request.method}
                )
                if res.status >= 400
                else None,
            )
            page.on(
                "request",
                lambda req: api_mutations.append({"url": req.url, "method": req.method})
                if "/api/v1/" in req.url and req.method in ("POST", "PUT", "PATCH", "DELETE")
                else None,
            )

            # Initial navigation
            page.goto(base_url, wait_until="networkidle", timeout=15000)
            page.wait_for_timeout(400)

            for route_cfg in ALL_APP_ROUTES:
                r_id = route_cfg["id"]
                r_label = route_cfg["label"]
                in_sidebar = route_cfg["in_sidebar"]

                console_errors.clear()
                page_errors.clear()
                failed_requests.clear()
                api_mutations.clear()

                navigation_method = "sidebar_click"
                nav_success = False

                if in_sidebar:
                    # Find sidebar button by text label
                    btn = page.locator("aside nav button", has_text=r_label).first
                    if btn.count() > 0:
                        btn.click(force=True)
                        page.wait_for_timeout(500)
                        nav_success = True
                else:
                    # Orphan route not in sidebar!
                    navigation_method = "orphan_unreachable_from_sidebar"
                    nav_success = False

                # Evaluate DOM geometry, overflow, interactive elements
                dom_metrics = page.evaluate(
                    """() => {
                    const docEl = document.documentElement;
                    const scrollWidth = docEl.scrollWidth;
                    const clientWidth = docEl.clientWidth;
                    const hasHorizontalOverflow = scrollWidth > clientWidth;

                    const aside = document.querySelector('aside');
                    const main = document.querySelector('main');
                    const header = document.querySelector('header');

                    const asideRect = aside ? aside.getBoundingClientRect() : null;
                    const mainRect = main ? main.getBoundingClientRect() : null;
                    const headerRect = header ? header.getBoundingClientRect() : null;

                    const mainButtons = main ? Array.from(main.querySelectorAll('button')) : [];
                    const mainInputs = main ? Array.from(main.querySelectorAll('input, textarea')) : [];
                    const mainSelects = main ? Array.from(main.querySelectorAll('select')) : [];
                    const mainTables = main ? Array.from(main.querySelectorAll('table')) : [];
                    const mainIframes = main ? Array.from(main.querySelectorAll('iframe')) : [];

                    // Check clipped or overflowing elements inside main
                    let clippedCount = 0;
                    const clippedDetails = [];
                    if (main && mainRect) {
                        const allEls = main.querySelectorAll('button, input, select, table, h1, h2, h3, .rounded-lg, .rounded-xl');
                        for (const el of allEls) {
                            const r = el.getBoundingClientRect();
                            if (r.width > 0 && (r.right > clientWidth + 2 || r.left < mainRect.left - 2)) {
                                clippedCount++;
                                if (clippedDetails.length < 5) {
                                    clippedDetails.push({
                                        tag: el.tagName,
                                        text: (el.innerText || '').slice(0, 40).trim(),
                                        right: Math.round(r.right),
                                        viewportWidth: clientWidth
                                    });
                                }
                            }
                        }
                    }

                    // Check header overflow / overlapping
                    let headerOverflow = false;
                    if (header) {
                        headerOverflow = header.scrollWidth > header.clientWidth;
                    }

                    return {
                        scrollWidth,
                        clientWidth,
                        hasHorizontalOverflow,
                        headerOverflow,
                        sidebarWidth: asideRect ? Math.round(asideRect.width) : 0,
                        mainWidth: mainRect ? Math.round(mainRect.width) : 0,
                        sidebarRatioPct: asideRect && clientWidth ? Math.round((asideRect.width / clientWidth) * 100) : 0,
                        mainRatioPct: mainRect && clientWidth ? Math.round((mainRect.width / clientWidth) * 100) : 0,
                        interactive: {
                            buttonsCount: mainButtons.length,
                            buttonLabels: mainButtons.map(b => (b.innerText || b.getAttribute('aria-label') || 'icon-btn').trim()),
                            inputsCount: mainInputs.length,
                            selectsCount: mainSelects.length,
                            tablesCount: mainTables.length,
                            iframesCount: mainIframes.length,
                        },
                        clippedElementsCount: clippedCount,
                        clippedSample: clippedDetails,
                        mainTextPreview: main ? (main.innerText || '').slice(0, 220).replace(/\\s+/g, ' ').trim() : ''
                    };
                }"""
                )

                r_entry = route_results.setdefault(
                    r_id,
                    {
                        "id": r_id,
                        "label": r_label,
                        "in_sidebar": in_sidebar,
                        "navigation_method": navigation_method,
                        "viewports": {},
                    },
                )
                r_entry["viewports"][vp_name] = {
                    "nav_success": nav_success,
                    "dom_metrics": dom_metrics,
                    "console_errors": list(console_errors),
                    "page_errors": list(page_errors),
                    "failed_requests": list(failed_requests),
                    "auto_mutations_fired": list(api_mutations),
                }

                viewport_summary[vp_name]["routes_tested"] += 1
                if dom_metrics["hasHorizontalOverflow"] or dom_metrics["clippedElementsCount"] > 0:
                    viewport_summary[vp_name]["routes_with_horizontal_overflow"] += 1
                if dom_metrics["mainWidth"] < 250:
                    viewport_summary[vp_name]["routes_with_cramped_main_area"] += 1
                viewport_summary[vp_name]["total_console_errors"] += len(console_errors)
                viewport_summary[vp_name]["total_failed_requests"] += len(failed_requests)

            context.close()
        browser.close()

    return {
        "viewport_summary": viewport_summary,
        "routes": route_results,
    }


def main() -> int:
    print("=" * 80)
    print("REVNAULT FULL-STACK E2E PLAYWRIGHT & ENGINE UTILIZATION HOMOLOGATION")
    print("=" * 80)

    # 1. Analyze Engine Utilization
    engine_report = analyze_engine_utilization()
    print(f"[STAGE 2] Total OpenAPI Paths: {engine_report['total_openapi_paths']}")
    print(f"[STAGE 2] Total Backend Operations: {engine_report['total_backend_operations']}")
    print(f"[STAGE 2] Exposed in Frontend UI: {engine_report['exposed_in_frontend_count']}")
    print(f"[STAGE 2] Orphaned in Backend: {engine_report['orphaned_in_backend_count']}")
    print(f"[STAGE 2] Global Engine Utilization Ratio: {engine_report['global_utilization_pct']}%")

    # 2. Ensure frontend/dist is built for React 19 SPA audit, then clean up afterwards
    dist_dir = PROJECT_ROOT / "frontend" / "dist"
    built_temporarily = False
    if not (dist_dir / "index.html").exists():
        print("[STAGE 1] Building frontend/dist for React 19 SPA Playwright inspection...")
        subprocess.run(
            ["npm", "--prefix", "frontend", "run", "build"],
            cwd=str(PROJECT_ROOT),
            shell=(os.name == "nt"),
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        built_temporarily = True

    port = find_free_port(8019)
    base_url = f"http://127.0.0.1:{port}"
    print(f"[STAGE 1] Starting FastAPI server on {base_url} ...")

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        # Wait for server readiness
        ready = False
        for _ in range(30):
            try:
                import urllib.request
                with urllib.request.urlopen(f"{base_url}/health", timeout=1) as resp:
                    if resp.status == 200:
                        ready = True
                        break
            except Exception:
                time.sleep(0.3)

        if not ready:
            raise RuntimeError("FastAPI server failed to start within timeout.")

        print("[STAGE 1] Running Playwright across 17 routes x 4 viewports (68 checks)...")
        pw_report = run_playwright_audit(base_url)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        if built_temporarily and dist_dir.exists():
            import shutil
            shutil.rmtree(dist_dir, ignore_errors=True)

    full_report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "engine_utilization": engine_report,
        "playwright_e2e": pw_report,
    }

    out_path = PROJECT_ROOT / "docs" / "homolog_e2e_playwright_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(full_report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[DONE] Saved full forensic report to: {out_path}")

    # Print Domain Utilization Table Summary
    print("\n--- ENGINE UTILIZATION BY DOMAIN MODULE ---")
    for dom, stats in engine_report["domain_utilization"].items():
        print(
            f"  {dom:34s} | {stats['exposed_endpoints']:2d}/{stats['total_endpoints']:2d} ({stats['utilization_pct']:5.1f}%)"
        )

    print("\n--- VIEWPORT SUMMARY ---")
    for vp_name, vp_stat in pw_report["viewport_summary"].items():
        print(
            f"  {vp_name:18s} ({vp_stat['width']}x{vp_stat['height']}) | "
            f"Overflow/Clipped: {vp_stat['routes_with_horizontal_overflow']}/{vp_stat['routes_tested']} | "
            f"Cramped (<250px main): {vp_stat['routes_with_cramped_main_area']}/{vp_stat['routes_tested']} | "
            f"Failed Req: {vp_stat['total_failed_requests']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
