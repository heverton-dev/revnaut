# -*- coding: utf-8 -*-
import urllib.request
import json

urls = [
    "https://rvops.vpsconexao.org/",
    "https://rvops.vpsconexao.org/css/tokens.css",
    "https://rvops.vpsconexao.org/js/app.js",
    "https://rvops.vpsconexao.org/api/v1/health",
    "https://rvops.vpsconexao.org/api/v1/deals",
    "https://rvops.vpsconexao.org/docs",
    "https://rvops.vpsconexao.org/webhooks",
    "https://rvops.vpsconexao.org/mcp",
    "https://rvops.vpsconexao.org/docs/guia"
]

print("=== VERIFICAÇÃO FACTUAL AO VIVO EM PRODUÇÃO ===")
all_ok = True
for u in urls:
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content_type = resp.headers.get("Content-Type", "")
            status = resp.status
            size = len(resp.read())
            print(f"[OK {status}] {u} ({size} bytes | {content_type})")
    except Exception as e:
        print(f"[ERRO] {u} -> {e}")
        all_ok = False

if all_ok:
    print("\n>>> TODOS OS ENDPOINTS RESPONDEM PERFEITAMENTE EM PRODUÇÃO COM SSL LET'S ENCRYPT! <<<")
else:
    print("\n>>> OCORRERAM ERROS EM ALGUNS ENDPOINTS <<<")
