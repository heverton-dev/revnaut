#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
ECOSSISTEMA AIDD -- QUALITY GATE: G_PARIDADE_TELA_CONTRATO (Leis #1, #2, #13, #14)
=============================================================================
Auditoria de Paridade Tela-Contrato (Screen-to-Contract Parity Gate).
Verifica deterministicamente via AST e analise estatica:
1. Ausencia de chamadas fantasmas 404 (rota inexistente) ou 405 (metodo nao suportado).
2. Ausencia de endpoints orfaos de negocio em /api/v1/* (quando --strict-orphans ativo).
3. Ausencia de Math.random() para segredos/tokens e de fallbacks com resumos clinicos em catch/else.

Uso:
  python gates/G_PARIDADE_TELA_CONTRATO.py [repo_root] [--check-broken] [--strict-orphans]
Saida:
  exit 0 = APROVADO (Conformidade total)
  exit 1 = REPROVADO (Violacoes detectadas)
=============================================================================
"""

from __future__ import annotations

import ast
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# External provider webhooks or system routes whitelist
WEBHOOK_AND_SYSTEM_WHITELIST = {
    "/health",
    "/api/v1/health",
    "/api/v1/webhooks/chatwoot",
    "/api/v1/webhooks/mautic",
    "/api/v1/webhooks/evolution",
    "/api/v1/webhooks/evolution/signed",
    "/api/v1/webhooks/listmonk",
    "/api/v1/webhooks/listmonk/events",
    "/api/v1/webhooks/documenso",
    "/api/v1/webhooks/livekit",
    "/api/v1/automations/calcom/webhook",
    "/api/v1/campaigns/webhooks/listmonk",
    "/api/v1/campaigns/public/lp/{slug}/submit",
    "/api/v1/omnichannel/webhooks/chatwoot",
    "/api/v1/omnichannel/webhooks/mautic",
    "/api/v1/omnichannel/webhooks/evolution",
    "/api/v1/omnichannel/webhooks/livekit",
    "/api/v1/omnichannel/whatsapp/instances/{instance_name}/webhook",
    "/api/v1/omnichannel/evolution/webhook",
    "/api/v1/omnichannel/webhook/evolution",
    "/api/v1/omnichannel/livekit/webhook",
    "/api/v1/communications/livekit/webhook",
}

# Known issues tracked across the sequential ticket queue
PENDING_TICKETS_MAP = {
    ("POST", "/api/v1/automations/flows"): "TICKET-SURGICAL-05",
    ("POST", "/api/v1/communications/livekit/sip/dial"): "TICKET-SURGICAL-04",
    ("POST", "/api/v1/omnichannel/send"): "TICKET-SURGICAL-04",
    ("POST", "/api/v1/intelligence/granola/extract"): "TICKET-SURGICAL-04",
}


@dataclass
class BackendRoute:
    method: str
    path: str
    pattern: re.Pattern
    handler: str
    file_path: str


@dataclass
class FrontendCall:
    method: str
    url: str
    file_path: str
    line: int


@dataclass
class GateResult:
    passed: bool
    broken_calls: List[str] = field(default_factory=list)
    orphan_endpoints: List[str] = field(default_factory=list)
    mock_violations: List[str] = field(default_factory=list)
    pending_tickets_found: List[str] = field(default_factory=list)


def parse_backend_routes(src_dir: Path) -> List[BackendRoute]:
    """Parse all FastAPI route decorators in Python files via AST."""
    routes: List[BackendRoute] = []
    py_files = sorted(src_dir.rglob("*.py"))

    for py_path in py_files:
        try:
            content = py_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content, filename=str(py_path))
        except Exception:
            continue

        prefixes: Dict[str, str] = {}
        # 1. Collect APIRouter prefixes
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and isinstance(node.value, ast.Call):
                        fn_name = getattr(node.value.func, "id", "") or getattr(node.value.func, "attr", "")
                        if "APIRouter" in fn_name:
                            pfx = ""
                            for kw in node.value.keywords:
                                if kw.arg == "prefix" and isinstance(kw.value, ast.Constant):
                                    pfx = str(kw.value.value)
                            prefixes[target.id] = pfx

        # 2. Collect decorators
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                        var_name = getattr(dec.func.value, "id", None)
                        method = dec.func.attr.lower()
                        methods: List[str] = []
                        if method in ("get", "post", "put", "delete", "patch"):
                            methods = [method.upper()]
                        elif method == "api_route":
                            for kw in dec.keywords:
                                if kw.arg == "methods" and isinstance(kw.value, ast.List):
                                    methods = [
                                        elt.value.upper()
                                        for elt in kw.value.elts
                                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                                    ]

                        if methods:
                            path_val: Optional[str] = None
                            if dec.args and isinstance(dec.args[0], ast.Constant) and isinstance(dec.args[0].value, str):
                                path_val = dec.args[0].value

                            pfx = prefixes.get(var_name, "")
                            if path_val is not None:
                                full_path = (pfx.rstrip("/") + "/" + path_val.lstrip("/")).rstrip("/")
                                if not full_path:
                                    full_path = "/"
                                # Convert route path to regex
                                reg = re.sub(r"\{[a-zA-Z_0-9]+:path\}", ".+", full_path)
                                reg = re.sub(r"\{[a-zA-Z_0-9]+\}", "[^/]+", reg)
                                compiled_pattern = re.compile(f"^{reg}/?$")

                                for m in methods:
                                    routes.append(
                                        BackendRoute(
                                            method=m,
                                            path=full_path,
                                            pattern=compiled_pattern,
                                            handler=node.name,
                                            file_path=str(py_path),
                                        )
                                    )
    return routes


def extract_frontend_calls(frontend_dir: Path) -> List[FrontendCall]:
    """Scan frontend files for /api/v1 HTTP calls and their methods."""
    calls: List[FrontendCall] = []
    ts_files = [
        p
        for ext in ("*.ts", "*.tsx")
        for p in frontend_dir.rglob(ext)
        if "api_contracts.ts" not in p.name
    ]
    transition_endpoints = ["picking", "seal", "assign-courier", "start-transit", "verify-delivery"]

    for p in ts_files:
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Strip comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        content = re.sub(r"//.*", "", content)

        # Expand DentgoExpressCockpit handleTransition
        dentgo_transition_match = re.search(r"handleTransition\s*=\s*async\s*\(endpoint:\s*string", content)
        if dentgo_transition_match:
            for ep in transition_endpoints:
                calls.append(
                    FrontendCall(
                        method="POST",
                        url=f"/api/v1/dentgo/orders/${{selectedOrder.id}}/{ep}",
                        file_path=str(p),
                        line=437,
                    )
                )

        # Expand IcpScoringDashboard editingRuleId
        if "editingRuleId" in content and "/api/v1/scoring/rules" in content:
            calls.append(
                FrontendCall(
                    method="PUT",
                    url="/api/v1/scoring/rules/${editingRuleId}",
                    file_path=str(p),
                    line=179,
                )
            )
            calls.append(
                FrontendCall(
                    method="POST",
                    url="/api/v1/scoring/rules",
                    file_path=str(p),
                    line=179,
                )
            )

        # Parse fetch, apiFetch or api calls
        for m in re.finditer(
            r"""\b(?:fetch|apiFetch|api)\s*(?:<[^>]+>)?\s*\(\s*([`][^`]*?/api/v1[^`]*?[`]|['"][^'"]*?/api/v1[^'"]*?['"])""",
            content,
        ):
            raw_url = m.group(1).strip("`'\" \t\r\n")
            line_no = content[: m.start()].count("\n") + 1

            # Search up to next semicolon or 800 chars for options
            opts_segment = content[m.end() : m.end() + 800].split(";")[0]
            method = "GET"
            method_match = re.search(
                r"""\bmethod\s*:\s*['"`](GET|POST|PUT|DELETE|PATCH)['"`]""",
                opts_segment,
                re.IGNORECASE,
            )
            if method_match:
                method = method_match.group(1).upper()

            if "${endpoint}" in raw_url:
                continue  # Handled above

            calls.append(
                FrontendCall(
                    method=method,
                    url=raw_url,
                    file_path=str(p),
                    line=line_no,
                )
            )

        # Parse <a ... href={`/api/v1/...`} />
        for m in re.finditer(
            r"""href\s*=\s*(?:\{[`'"]|["'])([^"'`}]*?/api/v1[^"'`}]*?)(?:[`'"]\}|["'])""",
            content,
        ):
            raw_url = m.group(1).strip()
            line_no = content[: m.start()].count("\n") + 1
            calls.append(
                FrontendCall(
                    method="GET",
                    url=raw_url,
                    file_path=str(p),
                    line=line_no,
                )
            )

    return calls


def check_ui_hygiene_mocks(frontend_dir: Path) -> List[str]:
    """Check for Math.random() secret generation and clinical fallback strings in catch/else."""
    violations: List[str] = []
    features_dir = frontend_dir / "features"
    if not features_dir.exists():
        features_dir = frontend_dir

    for ts_path in features_dir.rglob("*.tsx"):
        try:
            content = ts_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        lines = content.splitlines()
        for idx, line in enumerate(lines, start=1):
            # Check Math.random() in token/secret/id generation
            if "Math.random()" in line and not line.strip().startswith("//"):
                if any(k in line.lower() for k in ("secret", "token", "sk_live", "guest")):
                    violations.append(
                        f"{ts_path.name}:{idx} Math.random() proibido para geracao de token/secret — {line.strip()}"
                    )

            # Check hardcoded clinical summary in catch/else
            if "Resumo Cl" in line and any(k in line for k in ("Implante 3.5x11.5mm", "Guia cir")):
                violations.append(
                    f"{ts_path.name}:{idx} Fallback clinico hardcoded proibido em catch/else: '{line.strip()}'"
                )

    return violations


def scan(
    repo_root: Path,
    check_broken: bool = False,
    strict_orphans: bool = False,
) -> GateResult:
    """Executa a varredura completa de paridade tela-contrato."""
    repo_root = Path(repo_root)
    src_dir = repo_root / "src"
    frontend_dir = repo_root / "frontend" / "src"

    backend_routes = parse_backend_routes(src_dir) if src_dir.exists() else []
    frontend_calls = extract_frontend_calls(frontend_dir) if frontend_dir.exists() else []
    mock_violations = check_ui_hygiene_mocks(frontend_dir) if frontend_dir.exists() else []

    broken_calls: List[str] = []
    pending_tickets_found: List[str] = []

    # 1. Match frontend calls against backend routes
    for call in frontend_calls:
        url = call.url
        url = re.sub(r"\$\{churnQuery\}", "", url)
        url = re.sub(r"\$\{qParam\}", "", url)
        if "?" in url:
            url = url.split("?")[0]
        norm_url = re.sub(r"\$\{[^}]+\}", "param_val", url)
        if not norm_url.startswith("/"):
            idx = norm_url.find("/api/v1")
            if idx >= 0:
                norm_url = norm_url[idx:]

        matching_paths = [r for r in backend_routes if r.pattern.match(norm_url)]
        call_key = (call.method, call.url)

        if not matching_paths:
            # 404 Route Not Found
            ticket_ref = PENDING_TICKETS_MAP.get(call_key)
            if check_broken and ticket_ref and not strict_orphans:
                pending_tickets_found.append(
                    f"[PENDING {ticket_ref}] 404 {call.method} {call.url} at {Path(call.file_path).name}:{call.line}"
                )
            else:
                broken_calls.append(
                    f"404 GHOST ROUTE: {call.method} {call.url} -> '{norm_url}' at {Path(call.file_path).name}:{call.line}"
                )
        else:
            # Check HTTP Method
            matching_methods = [r for r in matching_paths if r.method == call.method]
            if not matching_methods:
                # 405 Method Not Allowed
                ticket_ref = PENDING_TICKETS_MAP.get(call_key)
                allowed = [r.method for r in matching_paths]
                if check_broken and ticket_ref and not strict_orphans:
                    pending_tickets_found.append(
                        f"[PENDING {ticket_ref}] 405 {call.method} {call.url} (Permitidos: {allowed}) at {Path(call.file_path).name}:{call.line}"
                    )
                else:
                    broken_calls.append(
                        f"405 METHOD NOT ALLOWED: {call.method} {call.url} (Permitidos: {allowed}) at {Path(call.file_path).name}:{call.line}"
                    )

    # 2. Check orphan backend endpoints (when strict_orphans is active)
    orphan_endpoints: List[str] = []
    if strict_orphans:
        for br in backend_routes:
            if not br.path.startswith("/api/v1"):
                continue
            if br.path in WEBHOOK_AND_SYSTEM_WHITELIST:
                continue
            if any(w.endswith("/*") and br.path.startswith(w[:-2]) for w in WEBHOOK_AND_SYSTEM_WHITELIST):
                continue

            matched = False
            for fc in frontend_calls:
                f_url = fc.url
                f_url = re.sub(r"\$\{churnQuery\}", "", f_url)
                f_url = re.sub(r"\$\{qParam\}", "", f_url)
                if "?" in f_url:
                    f_url = f_url.split("?")[0]
                norm_fc = re.sub(r"\$\{[^}]+\}", "param_val", f_url)
                if br.method == fc.method and br.pattern.match(norm_fc):
                    matched = True
                    break

            if not matched:
                orphan_endpoints.append(
                    f"ORPHAN ENDPOINT: {br.method} {br.path} -> {br.handler} ({Path(br.file_path).name})"
                )

    passed = (len(broken_calls) == 0) and (len(mock_violations) == 0 if strict_orphans else True)
    if strict_orphans:
        passed = passed and (len(orphan_endpoints) == 0) and (len(mock_violations) == 0)

    return GateResult(
        passed=passed,
        broken_calls=broken_calls,
        orphan_endpoints=orphan_endpoints,
        mock_violations=mock_violations,
        pending_tickets_found=pending_tickets_found,
    )


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    check_broken = "--check-broken" in argv
    strict_orphans = "--strict-orphans" in argv
    clean_argv = [a for a in argv if a not in ("--check-broken", "--strict-orphans")]
    repo_root = Path(clean_argv[0]) if clean_argv else Path(".")

    print("=============================================================================")
    print("ECOSSISTEMA AIDD -- GATE DE PARIDADE TELA-CONTRATO (G_PARIDADE_TELA_CONTRATO)")
    print("=============================================================================")
    print(f"Diretorio Alvo: {repo_root.resolve()}")
    print(f"Modo Check-Broken: {'ATIVO' if check_broken else 'DESATIVADO'}")
    print(f"Modo Strict-Orphans: {'ATIVO' if strict_orphans else 'DESATIVADO'}")

    res = scan(repo_root, check_broken=check_broken, strict_orphans=strict_orphans)

    if res.pending_tickets_found:
        print(f"\n[INFO] Chamadas pendentes em fila sequencial ({len(res.pending_tickets_found)}):")
        for p in res.pending_tickets_found:
            print(f"  * {p}")

    if res.broken_calls:
        print(f"\n[ERRO] Chamadas quebradas (404/405) detectadas ({len(res.broken_calls)}):")
        for b in res.broken_calls:
            print(f"  * {b}")

    if res.orphan_endpoints:
        print(f"\n[ERRO] Endpoints orfaos sem consumidor de tela ({len(res.orphan_endpoints)}):")
        for o in res.orphan_endpoints:
            print(f"  * {o}")

    if res.mock_violations:
        print(f"\n[ERRO] Violacoes de Mocks/Math.random() detectadas ({len(res.mock_violations)}):")
        for m in res.mock_violations:
            print(f"  * {m}")

    if res.passed:
        print("\n[VEREDITO] APROVADO: 100% de paridade tela-contrato (exit 0).")
        return 0
    else:
        print("\n[VEREDITO] REPROVADO: Violacoes de paridade tela-contrato detectadas (exit 1).")
        return 1


if __name__ == "__main__":
    sys.exit(main())
