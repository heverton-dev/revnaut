# Segurança Operacional da API Revnault

## 1. Autenticação obrigatória

Toda rota `/api/v1/*` exige o token de sessão emitido em `POST /api/v1/auth/login`, enviado como `Authorization: Bearer <token>` (validade padrão de 12 horas, `SESSION_TTL_SECONDS`). Sem token válido a resposta é HTTP 401. O controle fica no middleware `src/core/auth_middleware.py`; rotas novas já nascem protegidas.

Rotas públicas por desenho (lista fechada em `PUBLIC_ROUTES`):

| Método | Rota |
|---|---|
| GET | `/api/v1/health` |
| POST | `/api/v1/auth/login`, `/api/v1/auth/logout`, `/api/v1/auth/forgot-password`, `/api/v1/auth/reset-password-with-token` |
| POST | `/api/v1/campaigns/public/lp/{slug}/submit` (formulário de landing page) |
| POST | `/api/v1/campaigns/referral/register` (cadastro por link de indicação) |

Regras adicionais:
- Cookie de sessão `revnaut_session` (HttpOnly, Secure, SameSite=Lax, `Path=/api/v1`) vale apenas para GET/HEAD, para arquivos abertos em `<img>`, `<audio>` e downloads. Métodos que alteram dados exigem o header Bearer.
- O tenant é sempre o do usuário autenticado. `account_id` em query, header `X-Account-ID` ou corpo JSON de outro tenant retorna 403.
- `X-User-Id` só troca a identidade quando o usuário autenticado é Super Admin (seletor de usuário).
- CORS com credenciais aceita apenas as origens de `CORS_ALLOWED_ORIGINS`.

## 2. Webhooks de provedores (fail-closed)

Sem o segredo configurado, a chamada do provedor é recusada com 401. Os botões de simulação da interface funcionam com a sessão do usuário logado. Cadastre no painel de cada provedor o mesmo valor que está no `.env` (nunca publique os valores).

| Provedor | URL | Como autenticar | Variável |
|---|---|---|---|
| Evolution API, Chatwoot, Mautic | `/api/v1/webhooks/evolution`, `/api/v1/webhooks/chatwoot`, `/api/v1/webhooks/mautic`, `/api/v1/webhooks/mautic/campaign-action`, `/api/v1/omnichannel/webhook/evolution` | HMAC-SHA256 do corpo em `X-Evolution-Signature`, `X-Chatwoot-Signature`, `X-Mautic-Signature`, `Webhook-Signature` ou `X-Hub-Signature-256` | `OMNICHANNEL_WEBHOOK_SECRET` |
| Documenso | `/api/v1/webhooks/documenso/document-completed` | Campo "secret" do webhook, enviado em `X-Documenso-Secret` | `DOCUMENSO_WEBHOOK_SECRET` |
| Cal.com | `/api/v1/automations/calcom/webhook` | Campo "secret" do webhook (assinatura `X-Cal-Signature-256`) | `CALCOM_WEBHOOK_SECRET` |
| Listmonk | `/api/v1/webhooks/listmonk`, `/api/v1/webhooks/listmonk/events`, `/api/v1/campaigns/webhooks/listmonk` | Header `X-Webhook-Token` ou `?token=` na URL cadastrada | `LISTMONK_WEBHOOK_SECRET` |
| LiveKit | `/api/v1/communications/webhooks/livekit`, `/api/v1/communications/livekit/webhook` | JWT assinado pelo servidor LiveKit no header `Authorization` | `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET` (os mesmos do `livekit.yaml`) |

## 3. Senhas

- Armazenamento em PBKDF2-SHA256 com sal (600000 iterações). Hashes SHA-256 antigos são aceitos uma vez e regravados no próximo login.
- Mínimo de 12 caracteres. Senhas padrão ou vazadas são recusadas na troca.
- Em produção (`REVNAUT_ENV=production`), contas que ainda usam senha padrão ou vazada não conseguem entrar até redefinir a senha.
- O `init_db()` não regrava mais senhas nem status dos usuários a cada inicialização.
- `forgot-password` responde sempre a mesma mensagem e envia o link por e-mail (Listmonk transacional, template `LISTMONK_PASSWORD_RESET_TEMPLATE_ID`). O token é de uso único e vale 60 minutos.

Troca de senha do Super Admin pelo servidor (a senha é digitada sem aparecer na tela):

```bash
docker exec -it $(docker ps -q -f name=rvops_app | head -1) python -m src.features.auth.set_password_cli <e-mail>
```

Depois de entrar, o Super Admin redefine a senha dos demais usuários pela tela de usuários.

## 4. Segredos de runtime e deploy

- `SESSION_SECRET_KEY` assina sessões e links de recuperação. `VAULT_SECRET_KEY` cifra o cofre de credenciais e os segredos dos webhooks de saída.
- Em produção o app não sobe com chaves padrão ou com menos de 32 caracteres.
- Na inicialização, `rotate_vault_encryption` re-cifra (idempotente) os dados do cofre gravados com a chave legada.
- `scripts/deploy_vps.py` lê os segredos do `.env` local (fora do git) e grava `/opt/rvops/.env.secrets` (permissão 600) na VPS, carregado antes do `docker stack deploy`.
- O banco de produção vive em `/opt/rvops/data` na VPS. Os bancos locais (`data/*.db`) não são mais enviados no deploy. Use `python scripts/deploy_vps.py --seed-database` apenas para montar um servidor novo, ciente de que substitui o banco remoto.
