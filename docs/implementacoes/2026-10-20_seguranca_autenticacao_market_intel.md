# Relatório de Implementação: Market Intel, Autenticação da API e Endurecimento de Segurança

- **Data:** 2026-10-20
- **Repositório:** `heverton-dev/revnaut`, branch `main`
- **Produção:** https://revnault.vpsconexao.org (deploy concluído e verificado)
- **Commits desta entrega:**

| Commit | Escopo |
|---|---|
| `6cf7cb9` | Inteligência de Mercado, Radar de Concorrência e disparo determinístico com trava de 15 dias |
| `3b77e3e` | RBAC do Market Intel derivado da sessão autenticada |
| `4967465` | Agendador do lote noturno do radar e expiração do token de sessão |
| `630bc39` | Identidade só por token; `X-User-Id` apenas como impersonação de superadmin |
| `f7acbe8` | Autenticação em todas as rotas `/api/v1`, webhooks fail-closed e endurecimento de credenciais |

---

## 1. Ação obrigatória: trocar a senha do Super Admin

Em produção, o login com a senha antiga do Super Admin está bloqueado, porque ela estava publicada no código da tela de login. Rode na VPS:

```bash
docker exec -it $(docker ps -q -f name=rvops_app | head -1) python -m src.features.auth.set_password_cli hevertoneduardoperes@gmail.com
```

- O comando pede a nova senha duas vezes, sem mostrá-la na tela nem gravá-la no histórico do shell.
- Exige no mínimo 12 caracteres e recusa senhas padrão ou vazadas.
- Grava a senha com PBKDF2-SHA256 com sal.
- Se as senhas digitadas não conferirem, nada é alterado.

Depois de entrar com a senha nova, redefina pela tela de usuários (Configurações) a senha dos outros usuários canônicos, que estavam com a senha padrão `admin123`: Ricardo, Camila, Marcos, Juliana e Roberto. O mesmo comando serve para qualquer usuário, bastando trocar o e-mail.

A senha antiga continua nos commits anteriores do git. Ela não deve ser reutilizada em nenhum lugar.

---

## 2. Inteligência de Mercado e Radar de Concorrência (`6cf7cb9`)

**O que foi feito.** Implementação da spec `SPEC_TECNICA_MARKET_INTEL_REVNAULT.md` (TICKET-MKTINTEL-01 a 10):
- 6 tabelas: `market_signals`, `competitors`, `competitor_snapshots`, `market_opportunities`, `targeted_campaigns` e `campaign_recipient_locks`.
- Migração Alembic `0002` e seed odontológico realista.
- Crawler passivo, classificador LLM com fallback determinístico, matcher de oportunidades contra o catálogo, disparo de campanhas com trava anti-spam de 15 dias e tela `MarketIntelRadarWorkspace`.

**Como foi feito.**
- Slices `src/features/market_intel/` e `src/features/competitors/`.
- O crawler só roda na janela 01:00-05:00 UTC, com jitter de 7 a 22 segundos e deduplicação por SHA-256: conteúdo inalterado não chama o LLM.
- O classificador usa Ollama/LiteLLM quando configurado e, sem eles, regras determinísticas.
- O matcher indexa produtos e sinais no `VectorStoreService` e recomenda SKUs reais do catálogo.
- As minutas de campanha passam pelo validador ético CFO 196/2019.
- Contratos TypeScript sincronizados e manual `docs/manuais/27_market_intel_radar.md`.

**Por que.** Era o pedido da spec: monitorar mercado e concorrentes sem raspagem sob demanda (anti-bloqueio) e disparar campanhas por praça sem repetir contato em menos de 15 dias.

---

## 3. RBAC do Market Intel vinculado ao usuário autenticado (`3b77e3e`)

**O que foi feito.** Perfil, praça e tenant do Market Intel passaram a vir do cadastro do usuário autenticado, e não mais de headers enviados pelo cliente. Também foram criados a rota `GET /api/v1/market-intel/me` e a coluna `users.region_code` (migração `0003`).

**Como foi feito.**
- `resolve_authenticated_principal` valida o token Bearer.
- `X-User-Role` só rebaixa o perfil (simulação usada pela Diretoria).
- `X-User-Region` só é aceito quando o usuário real é Diretoria.

**Por que.** Antes, qualquer requisição podia enviar `X-User-Role: director` e cadastrar concorrentes ou disparar campanhas em qualquer praça.

---

## 4. Lote noturno do radar e expiração da sessão (`4967465`)

**O que foi feito.**
- O worker publica `market_intel.batch.tick` uma vez por hora dentro da janela 01:00-05:00 UTC, para cada empresa com concorrente ativo.
- O token de sessão passou a expirar em 12 horas (`SESSION_TTL_SECONDS`).
- O interceptor do frontend passou a enviar o token salvo pelo login.

**Como foi feito.**
- `src/workers/market_intel_scheduler.py` grava cada slot na tabela `market_intel_batch_ticks` (chave slot + tenant, migração `0004`). Assim, as 2 réplicas do worker e os reinícios não duplicam o disparo. Pode ser desligado com `MARKET_INTEL_SCHEDULER_ENABLED=0`.
- `verify_session_token` confere a validade do token e recusa tokens com data futura.
- `frontend/src/lib/api.ts` lia chaves erradas do `localStorage`; agora lê `revnaut_auth_token`. Quando o servidor recusa a sessão, o usuário volta ao login.

**Por que.** Sem o agendador, a coleta de concorrentes nunca rodava sozinha. Sem expiração, um token vazado valia para sempre. Por causa do bug do interceptor, o frontend nunca enviava o token.

---

## 5. Identidade só por token (`630bc39`)

**O que foi feito.** `get_current_user` e os routers de deals e contatos deixaram de aceitar `X-User-Id` sem token.

**Como foi feito.**
- `resolve_effective_user_id` exige o token Bearer válido.
- `X-User-Id` só troca a identidade quando quem está logado é Super Admin (seletor de usuário do `AppShell`). Para os demais usuários, o header é ignorado.
- Os testes passaram a autenticar com tokens reais (`tests/auth_helpers.py`).

**Por que.** Qualquer pessoa podia se passar por qualquer usuário, inclusive o Super Admin, só enviando um header.

---

## 6. Autenticação em todas as rotas e endurecimento de credenciais (`f7acbe8`)

### 6.1 Middleware central de autenticação

**O que foi feito.** Todas as rotas `/api/v1` exigem sessão válida, exceto uma lista fechada de rotas públicas. Antes, 215 das 247 rotas não tinham nenhuma autenticação.

**Como foi feito.** `src/core/auth_middleware.py` (`ApiAuthMiddleware`, ASGI):

| Regra | Comportamento |
|---|---|
| Rotas públicas | `GET /api/v1/health`, login, logout, `forgot-password`, `reset-password-with-token`, envio de landing page e cadastro por indicação |
| Demais rotas | Exigem `Authorization: Bearer <token>`; sem token, a resposta é 401. Rotas novas nascem protegidas. |
| Cookie `revnaut_session` | HttpOnly, Secure, SameSite=Lax, `Path=/api/v1`. Vale só para GET/HEAD (imagens, áudios e downloads). Métodos que alteram dados exigem o header Bearer. |
| Tenant | `account_id` de outra empresa em query, header `X-Account-ID` ou corpo JSON resulta em 403. Sem `account_id`, o tenant do usuário é injetado. |
| CORS | Só as origens de `CORS_ALLOWED_ORIGINS`. Antes era `*` com credenciais. |
| Swagger (`/docs`) | Botão Authorize com o token de sessão (esquema `SessionBearer`). |

**Por que.** A API aceitava chamadas anônimas e deixava o cliente escolher a empresa pela URL. Com cookie de sessão, o CORS aberto permitiria que qualquer site lesse respostas autenticadas.

### 6.2 Webhooks fail-closed

**O que foi feito.** Cada webhook de provedor exige a verificação nativa do provedor. Sem segredo configurado, a chamada é recusada (401). Os botões "Simular webhook" da interface funcionam com a sessão do usuário logado.

**Como foi feito.** `src/core/webhook_auth.py`:

| Provedor | Rotas | Verificação | Variável |
|---|---|---|---|
| Evolution, Chatwoot, Mautic | `/api/v1/webhooks/evolution`, `/chatwoot`, `/mautic`, `/mautic/campaign-action`, `/api/v1/omnichannel/webhook/evolution` | HMAC-SHA256 do corpo | `OMNICHANNEL_WEBHOOK_SECRET` |
| Documenso | `/api/v1/webhooks/documenso/document-completed` | Header `X-Documenso-Secret` | `DOCUMENSO_WEBHOOK_SECRET` |
| Cal.com | `/api/v1/automations/calcom/webhook` | `X-Cal-Signature-256` (HMAC) | `CALCOM_WEBHOOK_SECRET` |
| Listmonk | `/api/v1/webhooks/listmonk`, `/listmonk/events`, `/api/v1/campaigns/webhooks/listmonk` | `X-Webhook-Token` ou `?token=` | `LISTMONK_WEBHOOK_SECRET` |
| LiveKit | `/api/v1/communications/webhooks/livekit`, `/api/v1/communications/livekit/webhook` | JWT do servidor LiveKit no header `Authorization` | chaves do `livekit.yaml` |

**Por que.** Oito webhooks não tinham validação nenhuma. Os outros quatro usavam um segredo HMAC escrito no código-fonte, que qualquer pessoa podia usar para assinar chamadas falsas.

### 6.3 Chaves separadas e rotação do cofre

**O que foi feito.**
- `SESSION_SECRET_KEY` assina as sessões e os links de recuperação de senha.
- `VAULT_SECRET_KEY` cifra o cofre de credenciais.
- Em produção, o app não sobe com chave padrão ou com menos de 32 caracteres.

**Como foi feito.**
- `assert_production_secrets()` roda na inicialização quando `REVNAUT_ENV=production`.
- `rotate_vault_encryption()` re-cifra com a chave nova, de forma idempotente, o que estava gravado com a chave antiga: `tenant_credentials.encrypted_payload` e `webhook_subscriptions.signing_secret_encrypted`. Durante a transição, a leitura aceita as duas chaves.

**Por que.** A chave de sessão em produção era a padrão do código, então qualquer pessoa conseguia forjar um token de Super Admin. A mesma chave cifrava o cofre, por isso a separação veio com migração: trocar a chave sem re-cifrar perderia as credenciais gravadas.

### 6.4 Senhas

**O que foi feito.**

| Problema encontrado | Correção |
|---|---|
| E-mail e senha do Super Admin preenchidos na tela de login e publicados no JavaScript | Campos vazios e bloco "Credenciais de Demonstração" removido |
| Super Admin entrava com `admin`, `admin123`, `123456` e similares (backdoor em `authenticate_user`) | Backdoor removido; só vale o hash armazenado |
| `init_db()` regravava senha e status dos usuários canônicos a cada inicialização | O seed só define a senha na criação do usuário |
| Senhas em SHA-256 sem sal | PBKDF2-SHA256 com sal (600000 iterações); hash antigo é convertido no próximo login |
| Senhas padrão e vazada continuavam válidas | Em produção, o login com elas é recusado com orientação para redefinir |
| `forgot-password` devolvia o token de redefinição na resposta | Resposta genérica; token de uso único (amarrado ao hash atual) enviado por e-mail via Listmonk, válido por 60 minutos |
| Não havia como redefinir a senha bloqueada do Super Admin | CLI `python -m src.features.auth.set_password_cli <e-mail>` |

**Por que.** Qualquer visitante podia ler as credenciais do Super Admin no navegador, entrar com `admin`, ou sequestrar contas pelo `forgot-password` sabendo apenas o e-mail.

### 6.5 Deploy

**O que foi feito.**
- Os segredos de produção vão para a VPS sem passar pelo git.
- O deploy deixou de enviar os bancos SQLite locais.
- O script passou a sair com erro quando o deploy falha.

**Como foi feito.**
- `scripts/deploy_vps.py` lê os segredos do `.env` local (ignorado pelo git) e grava `/opt/rvops/.env.secrets` com permissão 600, carregado antes do `docker stack deploy`.
- `docker-stack.yml` e `docker-compose.prod.yml` recebem `REVNAUT_ENV=production` e os segredos nos serviços `app` e `worker`.
- Os arquivos `data/*.db` ficam fora do pacote; só seguem com `python scripts/deploy_vps.py --seed-database`, para montar um servidor novo.

**Por que.** O deploy extraía o banco local por cima do volume de produção (`/opt/rvops/data`). Cada deploy substituía os dados de produção, o que também desfaria qualquer troca de senha feita no servidor. Os deploys anteriores, inclusive os de hoje, já fizeram essa substituição; os dados alterados em produção entre um deploy e outro não puderam ser recuperados.

---

## 7. Verificação

**Testes e gates**
- Suíte automatizada: 651 testes passando.
- O arquivo `tests/test_api_auth_enforcement.py` exige 401 sem token e com token forjado em cada rota protegida.
- Quality gates: os 14 gates em `gates/` saem com 0. O hook de pre-commit aprovou o commit.
- Frontend: `typecheck` e `build` saem com 0.

**Checagens em produção depois do deploy**

| Checagem | Resultado |
|---|---|
| `GET /api/v1/health` (app subiu em modo produção, com segredos válidos) | 200 |
| Rotas sem token (dentgo, keypartners, hierarchy, campaigns, tickets, storage, webhooks) | 401 |
| Token forjado com a chave padrão antiga | 401 |
| Webhook Documenso sem segredo | 401 |
| Webhook Evolution assinado com o segredo público antigo | 401 |
| Login do Super Admin com `admin` | 401 |
| `forgot-password` devolve token? | Não (`null`) |
| CORS para origem não autorizada | Sem `Access-Control-Allow-Origin` |
| E-mail do Super Admin no bundle JavaScript | Ausente |

**Não verificado:**
- A re-cifragem do cofre no banco de produção e o worker publicando os disparos noturnos, porque não houve acesso ao servidor.
- O login real em produção, porque as senhas são do usuário.

---

## 8. Pendências do responsável

1. **Trocar a senha do Super Admin** com o comando da seção 1 e, em seguida, a senha dos outros 5 usuários canônicos.
2. **Cadastrar os segredos nos provedores** (Documenso, Cal.com, Listmonk e Evolution/Chatwoot/Mautic), usando os valores do `.env` local. Até isso ser feito, os webhooks reais desses serviços recebem 401. O passo a passo está em `docs/SEGURANCA_OPERACIONAL.md`.
3. **Fazer novo login:** todos os usuários foram deslogados com a troca da chave de sessão.
4. **Template de e-mail:** configurar no Listmonk o template de recuperação de senha (`LISTMONK_PASSWORD_RESET_TEMPLATE_ID`) e, se necessário, `APP_PUBLIC_URL`.

## 9. Limitações conhecidas

- Os deploys empacotam o working tree local. Por isso, as edições não commitadas de outros agentes no frontend também foram publicadas.
- A rota `/api/v1/storage/files/{key}` não confere o tenant pelo prefixo da chave. Hoje existe uma única empresa (`0f14ffff`); com mais empresas, isso precisa de checagem própria.
- O link do e-mail de recuperação aponta para `/#!/reset-password?token=...`, mas o frontend ainda não tem essa tela. A troca pode ser feita pela API `POST /api/v1/auth/reset-password-with-token` ou pelo comando da seção 1.
