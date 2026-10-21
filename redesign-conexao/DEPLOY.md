# Deploy do redesign: site-redesign.vpsconexao.org

Site estático (nginx) atrás do Traefik existente (`network_conexao`, resolver `letsencryptresolver`).

## 1. Cloudflare
- DNS > Adicionar registro: tipo `A`, nome `site-redesign`, conteúdo = IP da VPS.
- Proxy (nuvem laranja): se ligado, SSL/TLS em "Full (strict)". Se o Let's Encrypt falhar na emissão, deixe "somente DNS" até o certificado sair.

## 2. VPS
```bash
git clone <repo> && cd <repo>/redesign-conexao   # ou copie a pasta
cp .env.example .env                              # ajuste se necessário
docker compose up -d --build
```

## 3. Conferir
```bash
curl -I https://site-redesign.vpsconexao.org/racional.html   # 200 + X-Robots-Tag: noindex
```
Página de racional: `/racional.html`. Protótipo: `/`.

## Produção definitiva
Defina `NOINDEX=no` e `SITE_HOST` do domínio final no `.env`, rebuild.
