#!/usr/bin/env python3
"""
Dispatcher deterministico para aidd-route-analyze.
Classifica a rota (SPA, API, Webhook, Hibrida), resolve o slug e mapeia os arquivos locais.
"""
import sys
import json
import re
from pathlib import Path

def parse_target(target: str) -> dict:
    target = target.strip()
    result = {
        "raw_target": target,
        "slug": "",
        "route_type": "unknown",
        "frontend_element_id": None,
        "frontend_files": [],
        "backend_files": [],
        "matched_endpoints": []
    }

    # Caso 1: Hashbang SPA (ex: https://dominio.com/#!/dashboard ou #!/dashboard ou /dashboard)
    spa_match = re.search(r"#!\/([a-zA-Z0-9_\-]+)", target)
    if spa_match:
        view_name = spa_match.group(1)
        result["slug"] = view_name
        result["route_type"] = "spa_view"
        result["frontend_element_id"] = f"{view_name}-view"
    elif target.startswith("http") and "#" not in target:
        # URL de API
        endpoint_part = re.sub(r"^https?:\/\/[^\/]+", "", target)
        result["slug"] = re.sub(r"[^a-zA-Z0-9]+", "_", endpoint_part).strip("_")
        result["route_type"] = "api_endpoint"
    elif target.startswith("/api/") or target.startswith("api/") or target.startswith("POST ") or target.startswith("GET "):
        clean = re.sub(r"^(GET|POST|PUT|PATCH|DELETE)\s+", "", target)
        result["slug"] = re.sub(r"[^a-zA-Z0-9]+", "_", clean).strip("_")
        result["route_type"] = "api_endpoint"
    else:
        # Fallback de slug simples
        clean = re.sub(r"^[\/#\!]+", "", target)
        clean = re.sub(r"[^a-zA-Z0-9_\-]+", "_", clean).strip("_")
        result["slug"] = clean or "root"
        result["route_type"] = "spa_view"
        result["frontend_element_id"] = f"{result['slug']}-view"

    # Mapear arquivos no workspace
    workspace = Path(".")
    
    # 1. Frontend: index.html ou views em src/
    index_html = workspace / "public" / "index.html"
    if not index_html.exists():
        index_html = workspace / "index.html"
    
    if index_html.exists():
        content = index_html.read_text(encoding="utf-8", errors="ignore")
        if result["frontend_element_id"] and result["frontend_element_id"] in content:
            result["frontend_files"].append(str(index_html))

    # 2. Buscar referencias adicionais em src/ ou public/
    for js_file in workspace.glob("public/**/*.js"):
        result["frontend_files"].append(str(js_file))
        break

    # 3. Backend: localizar routers relacionados ao slug
    for r in workspace.glob("src/**/router.py"):
        r_text = r.read_text(encoding="utf-8", errors="ignore")
        slug_clean = result["slug"].replace("_", "-")
        if result["slug"] in r_text.lower() or slug_clean in r_text.lower():
            result["backend_files"].append(str(r))

    return result

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Parametro obrigatorio: <rota_ou_url>"}))
        sys.exit(1)

    target = sys.argv[1]
    res = parse_target(target)

    # Persistir em .state/route_dispatch.json
    state_dir = Path(".state")
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / "route_dispatch.json"
    state_file.write_text(json.dumps(res, indent=2), encoding="utf-8")

    print(json.dumps(res, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
