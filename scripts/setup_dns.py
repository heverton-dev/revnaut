# -*- coding: utf-8 -*-
import json
import urllib.request
import os

ZONE_ID = os.environ.get("CLOUDFLARE_ZONE_ID", "")
TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
VPS_IP = os.environ.get("VPS_HOST", "127.0.0.1")
SUBDOMAINS = ["revnaut.vpsconexao.org", "rvops.vpsconexao.org"]

def setup_dns():
    for sub in SUBDOMAINS:
        prefix = sub.split(".")[0]
        url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records?name={sub}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                records = data.get("result", [])
                if records:
                    print(f"[OK] Registro DNS {sub} já existe: ID={records[0]['id']} -> {records[0]['content']}")
                else:
                    create_url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"
                    payload = json.dumps({
                        "type": "A",
                        "name": prefix,
                        "content": VPS_IP,
                        "ttl": 1,
                        "proxied": False
                    }).encode("utf-8")
                    create_req = urllib.request.Request(
                        create_url,
                        data=payload,
                        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
                        method="POST"
                    )
                    with urllib.request.urlopen(create_req) as c_resp:
                        c_data = json.loads(c_resp.read().decode("utf-8"))
                        rec_id = c_data.get("result", {}).get("id")
                        print(f"[CRIADO] Registro DNS {sub} criado com sucesso: ID={rec_id} -> {VPS_IP}")
        except Exception as e:
            print(f"[ERRO] Falha ao configurar {sub}:", e)

if __name__ == "__main__":
    setup_dns()
