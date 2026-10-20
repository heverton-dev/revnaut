import urllib.request
import urllib.error
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base_url = "https://revnault.vpsconexao.org"

endpoints = [
    "/",
    "/api/v1/health",
    "/api/v1/metrics",
    "/api/v1/deals",
    "/api/v1/pipelines",
    "/api/v1/users",
    "/docs",
]

print("=== VERIFICACAO LIVE EM", base_url, "===")
for ep in endpoints:
    url = f"{base_url}{ep}"
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "RevNaultVerifier/1.0",
                "X-User-Id": "usr-director-br"
            }
        )
        with urllib.request.urlopen(req, timeout=10, context=ctx) as res:
            body = res.read().decode('utf-8', errors='ignore')
            preview = body[:60].replace("\n", " ")
            print(f"[{res.status}] {ep} -> OK ({len(body)} bytes) | {preview}")
    except urllib.error.HTTPError as e:
        print(f"[{e.code}] {ep} -> ERRO: {e.reason}")
    except Exception as e:
        print(f"[FAIL] {ep} -> FALHA DE CONEXAO: {e}")
