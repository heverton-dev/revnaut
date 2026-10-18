# REVNAULT — Plano Mestre de Implementação e Desmaquiagem Unificado (Micro-Tickets Cirúrgicos, Evolução de Stack, Motores Open-Source, KeyPartners & DENTGO)

## PARTE 1: Onde Estamos Hoje com a REVNAULT (Diagnóstico Forense Pós-Auditoria)

A auditoria forense linha a linha do repositório (`heverton-dev/revnaut`, commit `f366765`) revelou que a primeira passagem de execução dos Tickets `00` a `42` construiu o **esqueleto de rotas FastAPI (197 endpoints), esquemas SQLite (`init_db` com 1.686 linhas) e componentes visuais base**, mas **maquiou as integrações de motores, o acesso assíncrono a dados, os uploads no Cloudflare R2, o barramento Redis Streams e o estado real do Frontend React 19**.

### 1.1. Inventário Real do Que JáExiste vs. O Que Precisa Ser Desmaquiado (Remediação P0)

* **Core & Persistência (`src/core/`):**
  * `config.py`, `database.py`, `security.py`, `storage.py`, `events.py`, `vector_store.py`:
    * **Já Existe:** Criptografia `AES-256-GCM` com `PBKDF2HMAC` (`security.py`), cliente S3v4 `R2StorageClient` (`storage.py`), resolução de cláusulas SQL de escopo (`resolve_data_scope_clause`).
    * **Precisa Refazer/Corrigir:** `database.py` tem URL assíncrona travada em `sqlite+aiosqlite` e **nenhum** dos 95 arquivos em `src/features/` usa `AsyncSession` (`get_write_db` / `get_read_db`); `migrations/versions/` está vazio (apenas `.gitkeep`); `events.py` usa `xrevrange` sem Consumer Groups (`XGROUP CREATE` / `XREADGROUP`), não possui decorator `@event_consumer` e não possui `StreamName.AUDIT` / `publish_sync` (causando `AttributeError` silencioso em 5 módulos); `vector_store.py` faz loop em Python sobre JSON texto em vez de usar `pgvector` HNSW; `enforce_user_permission` em `security.py` permite bypass quando `user_id` é `None`.
* **Módulos de Domínio Backend (`src/features/`):**
  * `auth/`, `hierarchy/`, `rbac/`, `contacts/`, `deals/`, `campaigns/`, `scoring/`, `communications/`, `keypartners/`, `dentgo/`, `integrations/`, `intelligence/`, `automations/`, `tickets/`, `tasks/`, `webhooks/`, `storage/`, `quarteto/`:
    * **Já Existe:** Estrutura de rotas FastAPI tipadas com Pydantic v2, cálculos matemáticos de Haversine (`dentgo`), Split Financeiro (`financial_split.py`), Alçadas de Desconto (`catalog_pricing.py`), equações de $SOK$, $PR$, Margem Clínica e $HSC$, proteção Anti-SSRF e HMAC-SHA256 (`outbound_dispatcher.py`).
    * **Precisa Refazer/Desmaquiar:**
      1. Substituir simulações falsas de IA (`ord(char)/255.0` em `transcription_worker.py` e `scoring/service.py`; `sha256` n-gram em `surgical_rag.py`; `if/else` fixos em `granola_copilot.py` e `text_to_sql_agent.py`) por integrações reais (`faster-whisper`, `pyannote.audio`, `litellm`, `pgvector`) com fallback determinístico isolado exclusivamente para testes CI offline.
      2. Substituir gravações de strings fictícias do R2 (`landing_pages.py`, `documenso_service.py`, `superset_embedded.py`, `windmill_client.py`, `evolution_webhook_router.py`) por chamadas reais a `R2StorageClient.upload_bytes()` / `generate_presigned_upload_url()`.
      3. Implementar clientes HTTP `httpx.AsyncClient` reais para Listmonk, Mautic, LiveKit SIP/Egress, Documenso, Evolution API v2, Chatwoot, Cal.com, Windmill, Orthanc DICOM e ERPs (TOTVS, SAP B1, Sankhya).
      4. Corrigir bugs críticos de regra de negócio: subtração de consumo/devolução no saldo de custódia do KeyPartners (`service.py` e `predictive_inventory.py`), bloqueio efetivo de lotes em `QUARANTINE_BLOCKED` no KeyPartners e DENTGO, validação de status `ATIVO` do CRO no checkout do DENTGO, incremento real de `+40` pontos em `contacts.score` no MGM (`referral_mgm.py`) e criptografia `signing_secret_encrypted` em `webhook_subscriptions`.
* **Frontend React 19 + Design System (`frontend/`):**
  * **Já Existe:** 15 primitivos UI em `frontend/src/components/ui/`, `AppShell.tsx` e 11 componentes em `frontend/src/features/`.
  * **Precisa Refazer/Desmaquiar:**
    1. Corrigir todos os erros de compilação TypeScript (`tsc --noEmit`) em `router.tsx`, `CroVerifiedInput.tsx` e `LandingPageBuilder.tsx`.
    2. Criar o componente faltante `frontend/src/features/scoring/IcpScoringDashboard.tsx` (`TICKET-10`).
    3. Configurar `QueryClientProvider` (`@tanstack/react-query`) em `main.tsx` e eliminar todos os arrays estáticos hardcoded (`sampleDeals`, `initialOrders`, `mockOrders`, `sampleTree`, `credentials`) e botões falsos de simulação de estado em `App.tsx`, `ConsignmentSurgicalBoard.tsx`, `DentgoExpressCockpit.tsx`, `RbacHierarchyTree.tsx` e `CredentialsVaultPage.tsx`, conectando-os às rotas reais do FastAPI.
    4. Eliminar todas as cores hexadecimais (`#090d16`, `#121826`, etc.) e classes Tailwind fora do `tokens.css` nos componentes de `frontend/src/features/`.
    5. Configurar `Dockerfile` multi-stage e `src/main.py` para compilar e servir o bundle de produção do React (`frontend/dist`) como aplicação principal.

---

## PARTE 2: Diretrizes Inegociáveis de Stack Tecnológica e Blindagem Anti-Maquiagem

### 2.1. Matriz de Decisão da Stack e Critérios de Verificação Real

| Camada Arquitetural | Estado Atual no Repo | Meta Obrigatória de Produção | Critério de Verificação Anti-Maquiagem |
| :--- | :--- | :--- | :--- |
| **Backend Core & API** | Python 3.11 + FastAPI misto | **Python 3.12 + FastAPI Async + Pydantic v2** | `Dockerfile` em `python:3.12-slim`; zero endpoints sem `response_model`; zero exceções engolidas (`except Exception: pass`). |
| **Camada ORM & Migrations** | `sqlite3.connect` síncrono + `migrations/versions/` vazio | **SQLAlchemy 2.0 (`AsyncSession` + `asyncpg`/`aiosqlite`) + Alembic** | Migration inicial e incrementais presentes em `migrations/versions/*.py`; `alembic upgrade head` funcional; `target_metadata` configurado em `migrations/env.py`. |
| **Banco & Busca Vetorial** | SQLite local + loop Python sobre JSON texto | **PostgreSQL 16 (OLTP + OLAP) + `pgvector` (HNSW)** | `get_async_database_url()` lendo `DATABASE_URL` e `READ_DATABASE_URL`; queries `pgvector` com `<=>` no Postgres; proibido `ord(char)/255.0` como vetor. |
| **Filas & Workers** | `xrevrange` sem grupos + `runner.py` vazio (`logger.info`) | **Redis 7 Streams (`XGROUP`/`XREADGROUP`) + Workers Reais** | Decorator `@event_consumer` ativo; `src/workers/runner.py` registrando e executando os handlers de Marketing, Vendas, KeyPartners, DENTGO, CX e Webhooks. |
| **Object Storage** | Strings de URL fictícias salvas no banco | **Cloudflare R2 (`boto3` S3 v4 + `upload_bytes` / Presigned URLs)** | Todo fluxo que gera PDF, HTML de LP, CSV/Parquet ou XML/DANFE invoca efetivamente `R2StorageClient.upload_bytes()` e valida MIME type em `ALLOWED_MIME_TYPES`. |
| **Frontend SPA** | `05_reconstructed_app` servido; React com mocks e erros TS | **React 19 + TS Strict + Vite + TanStack Query v5 + shadcn/ui** | `npm --prefix frontend run typecheck` e `npm --prefix frontend run build` com exit code `0`; zero arrays mockados em componentes de produção; 14 itens do menu roteados. |
| **UI & Design System** | Hexadecimais `#090d16` e `slate-*` hardcoded nas features | **100% Variáveis Semânticas de `tokens.css`** | `G_UI_DESIGN_LINTER.py` auditando `frontend/src/**/*.{ts,tsx}` e reprovando qualquer cor hexadecimal `#...`, `rgb(...)` ou emoji Unicode em todo o repositório. |

---

## PARTE 3: Plano Faseado de Micro-Tickets de Correção e Implementação Real (`TICKET-00` a `TICKET-42`)

Legenda de Status Auditado:
* `[ ] REFAZER (MAQUIADO)` — O código atual é um stub/simulação e precisa ser reescrito com integração real.
* `[~] COMPLETAR / DESMAQUIAR` — A lógica base existe, mas possui bugs, mocks na UI ou desconexão com R2/Redis/HTTP.

---

### FASE 0: Evolução da Stack Base, Fundação Design System, Storage R2, Redis Streams & RBAC Dual

#### [ ] [TICKET-00] Evolução da Stack Base: SQLAlchemy 2.0 Async + Alembic (Backend) & Bootstrap React 19 + TypeScript + shadcn/ui (Frontend)
- **Status Real Auditado:** `[ ] REFAZER (MAQUIADO)`
- **Diagnóstico do Gap Atual:**
  1. `src/core/database.py` ignora `DATABASE_URL` e fixa `sqlite+aiosqlite:///`.
  2. `migrations/env.py` tem `target_metadata = None` e `migrations/versions/` está vazio (apenas `.gitkeep`).
  3. `frontend/src/main.tsx` não possui `QueryClientProvider`; `frontend/src/App.tsx` usa array estático `sampleDeals` e 4 botões manuais para simular *Loading/Empty/Error/Success* com `SimulatedErrorComponent`.
  4. `src/main.py` e `Dockerfile` não servem o build do React (`frontend/dist`).
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Em `src/core/database.py`, ler `DATABASE_URL` e `READ_DATABASE_URL` do ambiente (suportando `postgresql+asyncpg://` em produção e `sqlite+aiosqlite://` em dev/test), configurar `DeclarativeBase` / `MetaData` em `migrations/env.py` e gerar a migration revision inicial em `migrations/versions/0001_initial_schema.py` cobrindo todas as tabelas do domínio.
  2. Configurar `QueryClient` e `<QueryClientProvider>` em `frontend/src/main.tsx`.
  3. Refatorar `frontend/src/App.tsx` para buscar dados reais de `/api/v1/deals` e `/api/v1/metrics` via `useQuery`, renderizando os 4 estados reais (*Loading Skeleton*, *Empty State*, *Error State com retry*, *Success State*) a partir do estado real da query (removendo `SimulatedErrorComponent` e botões falsos de simulação).
  4. Atualizar `Dockerfile` (usando `python:3.12-slim` + build do frontend) e `src/main.py` para servir `frontend/dist` quando compilado, mantendo retrocompatibilidade das rotas `/css` e `/js` de auditoria.
- **DoD (Definition of Done):** Migration Alembic real em `migrations/versions/`; `npm --prefix frontend run typecheck` com zero erros; `App.tsx` conectado a `/api/v1/deals` via TanStack Query sem dados mockados.
- **Target Files:** `src/core/database.py`, `alembic.ini`, `migrations/env.py`, `migrations/versions/0001_initial_schema.py`, `Dockerfile`, `src/main.py`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/components/layout/AppShell.tsx`, `tests/test_async_stack_foundation.py`
- **Validation Command:** `python -m pytest tests/test_async_stack_foundation.py -q`
- **Blocked by:** Nenhum

#### [~] [TICKET-01] Camada Transversal de Object Storage com Cloudflare R2 e Presigned URLs
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `R2StorageClient` em `src/core/storage.py` define `ALLOWED_MIME_TYPES`, mas não valida o `content_type` recebido em `generate_presigned_upload_url` nem em `upload_bytes`.
  2. Falta rota `GET /api/v1/storage/presign-download/{file_id:path}` além do query param `?key=`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Validar estritamente `content_type in ALLOWED_MIME_TYPES` em `generate_presigned_upload_url` e `upload_bytes`, levantando `StorageSecurityException` para MIME types não permitidos.
  2. Suportar tanto `GET /api/v1/storage/presign-download/{file_id:path}` quanto `GET /api/v1/storage/presign-download?key=...` em `src/features/storage/router.py` com validação `validate_tenant_access`.
- **DoD:** Bloqueio de extensões e MIME types maliciosos; isolamento multi-tenant garantido; contratos de Storage exportados em `api_contracts.ts`.
- **Target Files:** `src/core/config.py`, `src/core/storage.py`, `src/features/storage/schemas.py`, `src/features/storage/router.py`, `frontend/src/components/shared/R2DirectUploader.tsx`, `tests/test_r2_storage.py`
- **Validation Command:** `python -m pytest tests/test_r2_storage.py -q`
- **Blocked by:** TICKET-00

#### [ ] [TICKET-02] Barramento de Eventos em Redis Streams e Pool de Workers Determinísticos
- **Status Real Auditado:** `[ ] REFAZER (MAQUIADO)`
- **Diagnóstico do Gap Atual:**
  1. `src/core/events.py` usa `xrevrange` em vez de `XGROUP CREATE` / `XREADGROUP`, nunca avançando o offset do grupo nem removendo eventos já processados.
  2. Falta o decorator `@event_consumer(stream_name, group_name)`.
  3. Falta `StreamName.AUDIT` e método utilitário `EventBus.publish_sync(...)` (chamados em 5 módulos do projeto e hoje falhando com `AttributeError`).
  4. `src/workers/runner.py` possui apenas um `default_handler` vazio que faz `logger.info`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Adicionar `AUDIT = "stream:audit"` em `StreamName` e implementar `EventBus.publish_sync(stream_name, payload_or_event_type, ...)` e instância singleton compartilhada `default_event_bus` para que eventos publicados em rotas síncronas/assíncronas não se percam.
  2. Implementar `XGROUP CREATE <stream> <group> 0 MKSTREAM` e leitura via `XREADGROUP GROUP <group> <consumer> COUNT <n> STREAMS <stream> >` no Redis (e fila FIFO real com offset por grupo no modo `in_memory`).
  3. Implementar decorator `@event_consumer(stream_name, group_name)` e registrar todos os handlers reais de domínio em `src/workers/runner.py`.
- **DoD:** Entrega *at-least-once* real com `XACK` e roteamento para `stream:dlq` após 3 falhas; zero `AttributeError` em chamadas `publish_sync`; `runner.py` despachando para handlers reais.
- **Target Files:** `src/core/events.py`, `src/workers/__init__.py`, `src/workers/runner.py`, `docker-stack.yml`, `tests/test_redis_streams_worker.py`
- **Validation Command:** `python -m pytest tests/test_redis_streams_worker.py -q`
- **Blocked by:** TICKET-01

#### [ ] [TICKET-03] Migração para PostgreSQL 16 + Extensão pgvector e Pool OLTP/OLAP
- **Status Real Auditado:** `[ ] REFAZER (MAQUIADO)`
- **Diagnóstico do Gap Atual:**
  1. `get_write_db` e `get_read_db` usam a mesma engine SQLite local.
  2. `VectorStoreService` faz `SELECT` de todas as linhas da tabela e calcula cosseno em loop Python.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Configurar duas engines assíncronas em `src/core/database.py`: `_write_engine` (`DATABASE_URL`) e `_read_engine` (`READ_DATABASE_URL`, com fallback para `DATABASE_URL`).
  2. Em `src/core/vector_store.py`, detectar o dialeto da sessão: quando PostgreSQL (`postgresql`), usar consulta nativa `1 - (embedding <=> :query_vec::vector) AS similarity ORDER BY embedding <=> :query_vec::vector LIMIT :top_k`; quando SQLite (ambiente de teste local), manter o cálculo matemático exato de cosseno.
  3. Implementar gerador determinístico de embeddings semânticos via LiteLLM (`text-embedding-3-small` / Ollama) com fallback vetorial TF-IDF/L2 normalizado de 1536/256 dimensões (proibindo o truque `ord(char)/255.0`).
- **DoD:** Isolamento por `tenant_id` na busca vetorial; suporte nativo a `pgvector` no PostgreSQL 16 e compatibilidade nos testes locais.
- **Target Files:** `src/core/database.py`, `src/core/vector_store.py`, `docker-stack.yml`, `tests/test_pgvector_store.py`
- **Validation Command:** `python -m pytest tests/test_pgvector_store.py -q`
- **Blocked by:** TICKET-00, TICKET-01

#### [~] [TICKET-04] Evolução do RBAC para Hierarquia Dual (Field Sales vs. Inside Sales)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `src/features/rbac/service.py` não implementa `get_scoped_user_ids` para resolver subordinados na árvore DAG tanto de Field quanto de Inside Sales.
  2. `src/core/security.py` (`resolve_data_scope_clause`) nos escopos `TEAM` e `SUBTREE` verifica apenas `team_id IN (...)` sem incluir registros onde `field_owner_id` ou `inside_owner_id` pertençam a usuários daquela equipe/subárvore.
  3. `frontend/src/features/rbac/RbacHierarchyTree.tsx` usa constante estática `sampleTree` e não aceita a prop `accountId` passada pelo `router.tsx`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Implementar `get_scoped_user_ids(conn, user_context)` em `src/features/rbac/service.py` retornando todos os IDs de usuários subordinados na subárvore DAG e atualizar `resolve_data_scope_clause` para permitir visibilidade quando `team_id IN (sub_teams) OR owner_id IN (scoped_users) OR field_owner_id IN (scoped_users) OR inside_owner_id IN (scoped_users)`.
  2. Adicionar `field_owner_id` e `inside_owner_id` também em `kp_partner_agreements` / `consignments`.
  3. Conectar `RbacHierarchyTree.tsx` ao endpoint `GET /api/v1/hierarchy/tree` via `fetch`/`useQuery`, aceitando `accountId?: string` nas props.
- **DoD:** Visibilidade dual funcionando em todos os níveis da árvore DAG; `RbacHierarchyTree.tsx` consumindo dados reais da API.
- **Target Files:** `src/core/security.py`, `src/features/rbac/schemas.py`, `src/features/rbac/service.py`, `src/features/hierarchy/service.py`, `src/features/deals/service.py`, `frontend/src/features/rbac/RbacHierarchyTree.tsx`, `tests/test_rbac_dual_field_inside.py`
- **Validation Command:** `python -m pytest tests/test_rbac_dual_field_inside.py -q`
- **Blocked by:** TICKET-02

#### [~] [TICKET-05] Gateway Edge Traefik, Rate Limiting e Criptografia AES-256 de Credenciais
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `frontend/src/features/settings/CredentialsVaultPage.tsx` usa estado local hardcoded em vez de consumir `GET/POST/DELETE /api/v1/auth/credentials` e não está conectado à rota `settings` em `frontend/src/router.tsx`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Refatorar `CredentialsVaultPage.tsx` para buscar, criar e remover credenciais reais via `/api/v1/auth/credentials` (implementando os 4 estados: Loading, Empty, Error com retry e Success).
  2. Registrar `case "settings": return <CredentialsVaultPage />;` em `frontend/src/router.tsx`.
- **DoD:** Credenciais cifradas em AES-256-GCM no banco e gerenciadas de ponta a ponta pela tela `CredentialsVaultPage.tsx`.
- **Target Files:** `src/core/security.py`, `src/features/auth/schemas.py`, `src/features/auth/service.py`, `src/features/auth/router.py`, `frontend/src/features/settings/CredentialsVaultPage.tsx`, `frontend/src/router.tsx`, `docker-stack.yml`, `tests/test_credentials_vault.py`
- **Validation Command:** `python -m pytest tests/test_credentials_vault.py -q`
- **Blocked by:** TICKET-01

---

### FASE 1: Camada de Marketing (GrapesJS, Mautic Headless, Listmonk & Lead Scoring ICP)

#### [~] [TICKET-06] Validador Ético CFO e Verificador de Registro CRO/UF em Tempo Real
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `src/features/contacts/cro_validator.py` faz cache apenas em memória local sem usar Redis quando disponível.
  2. `frontend/src/features/contacts/components/CroVerifiedInput.tsx` importa `SelectContent, SelectItem, SelectTrigger, SelectValue` de `../../../components/ui/select` (caminho em minúsculo e exports inexistentes em `Select.tsx`), quebrando o `tsc --noEmit`, além de usar classes `slate-*` / `emerald-*` fora do `tokens.css`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Adicionar suporte a cache Redis com TTL de 7 dias (`604800s`) em `verify_cro_status` mantendo fallback para `_IN_MEMORY_CRO_CACHE`.
  2. Corrigir os imports de `CroVerifiedInput.tsx` para `@/components/ui/Input`, `@/components/ui/Button`, `@/components/ui/Badge` e `@/components/ui/Select` (usando a prop `options` do componente `Select` canônico) e substituir todas as cores hardcoded por tokens de `tokens.css`.
- **DoD:** `CroVerifiedInput.tsx` compilando sem erros no `tsc --noEmit`; cache Redis de 7 dias funcional; bloqueio de peças publicitárias sem CRO responsável quando parametrizado.
- **Target Files:** `src/features/contacts/cro_validator.py`, `src/features/contacts/schemas.py`, `src/features/contacts/service.py`, `src/features/contacts/router.py`, `frontend/src/features/contacts/components/CroVerifiedInput.tsx`, `tests/test_cro_cfo_compliance.py`
- **Validation Command:** `python -m pytest tests/test_cro_cfo_compliance.py -q`
- **Blocked by:** TICKET-02

#### [ ] [TICKET-07] Construtor de Landing Pages Odontológicas com GrapesJS (React Wrapper) e Assets no R2
- **Status Real Auditado:** `[ ] REFAZER (MAQUIADO)`
- **Diagnóstico do Gap Atual:**
  1. `publish_landing_page` em `src/features/campaigns/landing_pages.py` não faz upload do HTML/CSS compilado para o Cloudflare R2 (`R2StorageClient` é importado mas nunca chamado) e permite publicar páginas com violação ética do CFO quando `block_on_cfo_violation=True`.
  2. `submit_public_lead` publica em `EventBus(in_memory=True)` local descartável.
  3. `LandingPageBuilder.tsx` importa `../../components/ui/button`, `input`, `badge` em minúsculo, usa classes `slate-*` / `sky-*` fora do `tokens.css` e recebe prop `campaignId` inexistente em `router.tsx`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Em `publish_landing_page`, compilar o documento HTML5 completo (`<!DOCTYPE html><html><head><style>{css}</style></head><body>{html}</body></html>`) e enviá-lo via `R2StorageClient().upload_bytes(key, html_bytes, "text/html")` (adicionando `"text/html"` em `ALLOWED_MIME_TYPES`), gravando a URL real retornada em `published_r2_url`.
  2. Publicar `lead.captured` no barramento global `EventBus` (`StreamName.MARKETING`).
  3. Corrigir os imports e props de `LandingPageBuilder.tsx` e substituir todas as classes `slate-*`/`sky-*` por variáveis de `tokens.css`.
- **DoD:** Upload real do bundle HTML para o R2 na publicação; evento `lead.captured` persistido no stream; zero erros TypeScript em `LandingPageBuilder.tsx`.
- **Target Files:** `src/features/campaigns/landing_pages.py`, `src/features/campaigns/schemas.py`, `src/features/campaigns/router.py`, `frontend/src/features/campaigns/LandingPageBuilder.tsx`, `docs/reconstruct_rvops/05_reconstructed_app/js/modules/landing-builder.js`, `tests/test_landing_pages_grapesjs.py`
- **Validation Command:** `python -m pytest tests/test_landing_pages_grapesjs.py -q`
- **Blocked by:** TICKET-01, TICKET-06

#### [ ] [TICKET-08] Arquitetura Híbrida Mautic Visual + Despachante Determinístico de Campanhas
- **Status Real Auditado:** `[ ] REFAZER (MAQUIADO)`
- **Diagnóstico do Gap Atual:**
  1. O endpoint `POST /api/v1/webhooks/mautic/campaign-action` não valida assinatura HMAC-SHA256 (`Webhook-Signature` / `X-Mautic-Signature`).
  2. `process_mautic_campaign_action` usa `EventBus(in_memory=True)` descartável e não despacha pela instância da Evolution API v2 do consultor.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Validar assinatura HMAC-SHA256 quando o header ou segredo do tenant estiver configurado.
  2. Publicar no `default_event_bus` (`StreamName.MARKETING`) e registrar o consumidor `handle_mautic_whatsapp_dispatch` em `src/workers/runner.py` que envia a mensagem renderizada para a instância Evolution API do consultor titular e registra em `omnichannel_messages`.
- **DoD:** Validação HMAC funcional; enfileiramento real em `stream:marketing` e registro de despacho na instância do consultor titular.
- **Target Files:** `src/features/campaigns/mautic_bridge.py`, `src/features/campaigns/service.py`, `src/features/integrations/omnichannel/router.py`, `src/features/webhooks/router.py`, `tests/test_mautic_hybrid_dispatch.py`
- **Validation Command:** `python -m pytest tests/test_mautic_hybrid_dispatch.py -q`
- **Blocked by:** TICKET-02, TICKET-04

#### [ ] [TICKET-09] Motor de Disparo em Massa de Alta Velocidade com Listmonk Engine
- **Status Real Auditado:** `[ ] REFAZER (MAQUIADO)`
- **Diagnóstico do Gap Atual:**
  1. `ListmonkClient` em `src/features/campaigns/listmonk_adapter.py` importa `httpx` mas nunca faz chamadas HTTP (`/api/subscribers`, `/api/campaigns`, `/api/tx`).
  2. Falta endpoint de webhook `POST /api/v1/webhooks/listmonk/events` para processar `bounce`, `open` e `click` atualizando o score e a timeline do contato.
  3. O arquivo de teste `tests/test_listmonk_campaigns.py` está ausente (foi criado com nome errado `tests/test_listmonk_integration.py`).
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Implementar métodos HTTP reais em `ListmonkClient` (`sync_subscribers`, `create_and_start_campaign`, `send_transactional`) usando `httpx` com Basic Auth (`self.username`, `self.password`) quando `not self.mock_mode`, e fallback determinístico controlado em ambiente de teste local.
  2. Implementar `process_listmonk_webhook_event` e endpoint `POST /api/v1/campaigns/webhooks/listmonk` (e alias em `/api/v1/webhooks/listmonk`) que marca `email_bounced`, registra na timeline do contato e incrementa o score de engajamento em cliques de catálogo.
  3. Garantir a existência de `tests/test_listmonk_campaigns.py`.
- **DoD:** Cliente REST Listmonk funcional; webhook de bounce/clique atualizando contato e score; comando de validação `pytest tests/test_listmonk_campaigns.py` passando.
- **Target Files:** `src/features/campaigns/listmonk_adapter.py`, `src/features/campaigns/router.py`, `docker-stack.yml`, `tests/test_listmonk_campaigns.py`
- **Validation Command:** `python -m pytest tests/test_listmonk_campaigns.py -q`
- **Blocked by:** TICKET-08

#### [ ] [TICKET-10] Motor Preditivo de Lead Scoring Odontológico, ICP Fit e Handoff Automático
- **Status Real Auditado:** `[ ] REFAZER (MAQUIADO / ARQUIVOS FALTANTES)`
- **Diagnóstico do Gap Atual:**
  1. Falta tabela `scoring_history` no banco de dados.
  2. Falta o componente `frontend/src/features/scoring/IcpScoringDashboard.tsx` (inexistente no repositório).
  3. `calculate_contact_score_and_handoff` usa vetor falso `ord(char)/255.0` e não atribui o Deal criado ao consultor da região (`field_owner_id`/`owner_id`) nem injeta o briefing técnico no card.
  4. Falta o arquivo `tests/test_lead_scoring_auto_handoff.py` (criado apenas como `test_lead_scoring_handoff.py`).
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Criar tabela `scoring_history` (`id`, `account_id`, `contact_id`, `previous_score`, `new_score`, `icp_fit_score`, `engagement_score`, `tier`, `trigger_reason`, `created_at`) e gravar histórico a cada cálculo em `calculate_contact_score_and_handoff`.
  2. Usar `compute_text_embedding` / `VectorStoreService` real para atualizar o vetor de afinidade do cirurgião e injetar `executive_summary` (briefing técnico) e `owner_id`/`field_owner_id` no Deal criado no estágio inicial.
  3. Construir `frontend/src/features/scoring/IcpScoringDashboard.tsx` usando estritamente `tokens.css` e os 4 estados obrigatórios conectados a `/api/v1/scoring/rules`, `/api/v1/scoring/presets` e `/api/v1/scoring/recalculate`.
  4. Garantir a existência de `tests/test_lead_scoring_auto_handoff.py`.
- **DoD:** Histórico salvo em `scoring_history`; Deal criado com briefing e dono regional; `IcpScoringDashboard.tsx` criado e integrado ao `router.tsx`.
- **Target Files:** `src/features/scoring/schemas.py`, `src/features/scoring/service.py`, `src/features/scoring/router.py`, `frontend/src/features/scoring/IcpScoringDashboard.tsx`, `tests/test_lead_scoring_auto_handoff.py`
- **Validation Command:** `python -m pytest tests/test_lead_scoring_auto_handoff.py -q`
- **Blocked by:** TICKET-03, TICKET-09

---

### FASE 2: Camada de Vendas, Copiloto de IA ("Granola-like"), VoIP/Meet LiveKit & Documenso

#### [~] [TICKET-11] Infraestrutura de Salas WebRTC e Telefonia VoIP com LiveKit SFU & LiveKit SIP
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `livekit_service.py` não configura `RoomCompositeEgress` / `TrackEgress` para exportar `.ogg`/`.wav` no Cloudflare R2.
  2. `handle_livekit_webhook` não publica o evento `call.recording_ready` no `EventBus`.
  3. `LiveKitDealRoomModal.tsx` usa classes hardcoded `slate-900`/`cyan-500`/`rose-500` em vez de `tokens.css`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Adicionar função `start_room_egress_to_r2(room_name, deal_id, account_id)` em `livekit_service.py` configurando payload S3/R2 para `RoomCompositeEgress` e `TrackEgress` (chamando API LiveKit Twirp `/twirp/livekit.Egress/StartRoomCompositeEgress` quando `not mock_mode`).
  2. Em `handle_livekit_webhook`, publicar `call.recording_ready` no `default_event_bus` (`StreamName.SALES`) com `call_id`, `deal_id`, `r2_audio_key` e `account_id`.
  3. Refatorar `LiveKitDealRoomModal.tsx` para usar exclusivamente tokens semânticos de `tokens.css`.
- **DoD:** Webhook LiveKit disparando `call.recording_ready` no EventBus; configuração de Egress R2 ativa; modal 100% aderente ao `tokens.css`.
- **Target Files:** `src/features/communications/livekit_service.py`, `src/features/communications/router.py`, `frontend/src/features/communications/LiveKitDealRoomModal.tsx`, `docs/reconstruct_rvops/05_reconstructed_app/js/modules/livekit-room.js`, `docker-stack.yml`, `tests/test_livekit_webrtc_sip.py`
- **Validation Command:** `python -m pytest tests/test_livekit_webrtc_sip.py -q`
- **Blocked by:** TICKET-01, TICKET-02

#### [ ] [TICKET-12] Pipeline STT de Alta Performance com faster-whisper e Diarização pyannote.audio
- **Status Real Auditado:** `[ ] REFAZER (MAQUIADO)`
- **Diagnóstico do Gap Atual:**
  1. `src/features/intelligence/transcription_worker.py` não possui integração com `faster-whisper` nem API Whisper/Groq, não consome `call.recording_ready` do EventBus, não baixa áudio do R2 e usa `ord(char)/255.0` como vetor.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Implementar adaptador real em `transcription_worker.py`: quando `audio_url` ou `r2_audio_key` for fornecido, baixar os bytes via `R2StorageClient`, transcrever usando `faster_whisper.WhisperModel` (se instalado localmente) ou chamada HTTP para endpoint compatível OpenAI/Groq Whisper (`/v1/audio/transcriptions`), e diarizar canais (`SPEAKER_CONSULTANT` vs. `SPEAKER_SURGEON`), mantendo `parse_dialogue_segments` quando `dialogue_text` estruturado for fornecido.
  2. Substituir o vetor falso `ord(char)/255.0` por `compute_text_embedding(content_chunk)` indexado no `VectorStoreService` (`entity_type = 'call_transcript'`).
  3. Registrar consumidor de `call.recording_ready` no `src/workers/runner.py`.
- **DoD:** Transcrição diarizada real + parser de diálogo estruturado; indexação vetorial legítima; consumidor registrado no worker runner.
- **Target Files:** `src/features/intelligence/transcription_worker.py`, `src/features/intelligence/schemas.py`, `src/features/intelligence/service.py`, `src/workers/runner.py`, `tests/test_faster_whisper_diarization.py`
- **Validation Command:** `python -m pytest tests/test_faster_whisper_diarization.py -q`
- **Blocked by:** TICKET-03, TICKET-11

#### [ ] [TICKET-13] Copiloto Comercial "Granola-like" via LiteLLM e Auto-Preenchimento Zero-Touch do Deal
- **Status Real Auditado:** `[ ] REFAZER (MAQUIADO)`
- **Diagnóstico do Gap Atual:**
  1. `src/features/intelligence/granola_copilot.py` não chama LiteLLM/LLM e usa `if/elif` fixos; não processa notas de voz rápidas de campo vindas do WhatsApp; `GranolaCopilotCard.tsx` usa cores `slate-*`/`indigo-*` hardcoded.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Integrar chamada estruturada via LiteLLM / endpoint compatível OpenAI (`response_format=MeetingIntelligenceExtraction`) quando `LITELLM_API_KEY` / `OPENAI_API_KEY` / `OLLAMA_BASE_URL` estiver definido, utilizando extrator heurístico generalizado (capaz de extrair qualquer quantidade, preço, prazo, concorrente, sistema de implante e objeção) como fallback determinístico local.
  2. Implementar `process_field_voice_note(deal_id, audio_or_text, account_id)` para suportar notas rápidas de voz de 30s enviadas pelo consultor externo no WhatsApp, atualizando o Deal e criando tarefas para Field e Inside Sales.
  3. Refatorar `GranolaCopilotCard.tsx` para usar os tokens de `tokens.css` e conectá-lo à rota `intelligence` no `router.tsx`.
- **DoD:** Extração cognitiva validada por schema Pydantic `MeetingIntelligenceExtraction`; suporte a notas de voz de campo; componente React sem cores hardcoded.
- **Target Files:** `src/features/intelligence/granola_copilot.py`, `src/features/intelligence/router.py`, `src/features/deals/service.py`, `src/features/tasks/service.py`, `frontend/src/features/deals/components/GranolaCopilotCard.tsx`, `tests/test_granola_copilot_zerotouch.py`
- **Validation Command:** `python -m pytest tests/test_granola_copilot_zerotouch.py -q`
- **Blocked by:** TICKET-12

#### [~] [TICKET-14] Motor Dinâmico de Catálogo Odontológico, Multi-Tabela de Preços e Alçadas de Desconto
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `generate_contract_for_deal` em `src/features/deals/documenso_service.py` não verifica se `deals.approval_status == 'PENDING_DISCOUNT_APPROVAL'`, permitindo gerar contrato mesmo quando o desconto excedeu a alçada do vendedor!
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Em `generate_contract_for_deal` (`documenso_service.py`), consultar `approval_status` do Deal e lançar `ValueError("Geração de contrato bloqueada: Deal aguarda aprovação de alçada de desconto pela gerência.")` caso `approval_status == 'PENDING_DISCOUNT_APPROVAL'`.
  2. Exportar interfaces `CatalogProduct`, `PriceTable` e `ProposalPricingResult` em `api_contracts.ts`.
- **DoD:** Bloqueio determinístico da geração de contrato quando `PENDING_DISCOUNT_APPROVAL`; desbloqueio imediato após `approve_discount_request`.
- **Target Files:** `src/features/deals/catalog_pricing.py`, `src/features/deals/documenso_service.py`, `src/features/deals/schemas.py`, `src/features/deals/service.py`, `src/features/deals/router.py`, `tests/test_catalog_pricing_approval.py`
- **Validation Command:** `python -m pytest tests/test_catalog_pricing_approval.py -q`
- **Blocked by:** TICKET-04

#### [ ] [TICKET-15] Fechamento de Propostas e Contratos com Documenso Headless e Assinatura via WhatsApp
- **Status Real Auditado:** `[ ] REFAZER (MAQUIADO)`
- **Diagnóstico do Gap Atual:**
  1. `src/features/deals/documenso_service.py` não gera arquivo PDF, não faz upload para o Cloudflare R2, não chama API do Documenso, não envia link de assinatura no WhatsApp e não publica `deal.won` no Redis Streams após `DOCUMENT_COMPLETED`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Em `generate_contract_for_deal`, gerar documento PDF válido em bytes contendo os dados do Deal, cirurgião e cláusulas de fornecimento/consignação, e enviá-lo para o Cloudflare R2 via `R2StorageClient().upload_bytes(original_r2_key, pdf_bytes, "application/pdf")`.
  2. Chamar a API REST do Documenso (`POST {DOCUMENSO_URL}/api/v1/documents`) quando configurada e registrar o envio do link de assinatura para o WhatsApp do cirurgião em `omnichannel_messages`.
  3. Em `handle_documenso_webhook`, arquivar o PDF assinado com manifesto SHA-256 no R2 via `upload_bytes`, mover o Deal para `stage_id = 105`, calcular comissões bipartidas (`calculate_split_commissions`) e publicar `deal.won` no `default_event_bus` (`StreamName.SALES`).
- **DoD:** Upload real do PDF original e assinado no R2; envio de link no WhatsApp registrado; publicação do evento `deal.won` no Redis Streams acionando comissões e fidelidade.
- **Target Files:** `src/features/deals/documenso_service.py`, `src/features/deals/router.py`, `src/features/webhooks/router.py`, `docker-stack.yml`, `tests/test_documenso_contract_flow.py`
- **Validation Command:** `python -m pytest tests/test_documenso_contract_flow.py -q`
- **Blocked by:** TICKET-01, TICKET-14

---

### FASE 3: Integração Integral do Motor Proprietário KEYPARTNERS (Consignação Cirúrgica & Parcerias)

#### [~] [TICKET-16] Incorporação do Domínio Core KeyPartners: Custódia de Kits, Lotes ANVISA e Saldos
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `get_partner_custody_summary` em `src/features/keypartners/service.py` (linhas 206-207) calcula `total_custodied_value` e `total_items_count` somando apenas `REMESSA`, sem subtrair `CONSUMO_CIRURGICO`, `DEVOLUCAO_INTACTA`, `TROCA_GARANTIA` e `EXTRAVIO`.
  2. `dispatch_consignment_custody` não consulta `anvisa_batch_quarantines` para bloquear lotes em `QUARANTINE_BLOCKED`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Em `dispatch_consignment_custody`, verificar se algum `batch_number` dos itens possui registro `status = 'QUARANTINE_BLOCKED'` em `anvisa_batch_quarantines`, lançando `ValueError` imediato caso esteja bloqueado pela tecnovigilância ANVISA.
  2. Em `get_partner_custody_summary`, calcular o saldo líquido real em posse da clínica (`REMESSA` menos `CONSUMO_CIRURGICO`, `DEVOLUCAO_INTACTA` e `EXTRAVIO`).
- **DoD:** Saldo líquido em custódia refletindo baixas e devoluções; bloqueio sanitário de lotes em quarentena ANVISA; validade mínima de 30 dias e trava de limite de crédito.
- **Target Files:** `src/features/keypartners/__init__.py`, `src/features/keypartners/schemas.py`, `src/features/keypartners/service.py`, `src/features/keypartners/router.py`, `src/main.py`, `tests/test_keypartners_custody_ledger.py`
- **Validation Command:** `python -m pytest tests/test_keypartners_custody_ledger.py -q`
- **Blocked by:** TICKET-04, TICKET-14

#### [~] [TICKET-17] Fluxo Operacional de Remessa, Conferência de Lacre e Baixa Pós-Cirúrgica (Inside + Field)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `report_surgical_postop` em `src/features/keypartners/surgical_cycle.py` não publica `keypartners.postop_reported` no `EventBus` (`StreamName.KEYPARTNERS`).
  2. `frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx` usa array estático `initialOrders` em memória, cores hexadecimais hardcoded (`#0b0f19`, `#121826`, `#182032`, `#131927`) e botões que não chamam a API.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Adicionar endpoint `GET /api/v1/keypartners/surgical-orders` em `src/features/keypartners/router.py` para listar ordens cirúrgicas do tenant.
  2. Em `report_surgical_postop`, publicar o evento `keypartners.postop_reported` no `default_event_bus` (`StreamName.KEYPARTNERS`) contendo `order_id`, `agreement_id`, `consumed_units`, `billed_amount` e `consumed_items`.
  3. Refatorar `ConsignmentSurgicalBoard.tsx` para buscar dados reais de `/api/v1/keypartners/surgical-orders`, chamar `POST /api/v1/keypartners/surgical-orders/{id}/approve` e `/dispatch` nos botões de ação, implementar os 4 estados reais e remover todas as cores `#...` hardcoded em favor de `tokens.css`.
- **DoD:** Conciliação pós-operatória exata; evento `keypartners.postop_reported` publicado no Redis Streams; `ConsignmentSurgicalBoard.tsx` 100% conectado à API real e sem hexadecimais hardcoded.
- **Target Files:** `src/features/keypartners/surgical_cycle.py`, `src/features/keypartners/service.py`, `src/features/keypartners/router.py`, `frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx`, `docs/reconstruct_rvops/05_reconstructed_app/js/modules/consignments.js`, `tests/test_keypartners_surgical_postop.py`
- **Validation Command:** `python -m pytest tests/test_keypartners_surgical_postop.py -q`
- **Blocked by:** TICKET-13, TICKET-15, TICKET-16

#### [~] [TICKET-18] Gestão de Key Opinion Leaders (KOLs), Embaixadores e Metas de Comodato
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `submit_clinical_evidence` em `src/features/keypartners/kol_management.py` usa data hardcoded `"2026-10-18T00:00:00Z"` e não valida o prefixo de tenant da chave R2.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Usar `datetime.now(timezone.utc).isoformat()` em `submit_clinical_evidence`, validar a chave R2 e permitir auditoria automática de consumo cruzando `kp_custody_ledger` quando `consumed_implants_count` não for informado manualmente.
- **DoD:** Auditoria de contrapartida contratual de KOLs (`COMPLIANT` vs. `NON_COMPLIANT_ALERT`) e guarda de evidências clínicas no R2.
- **Target Files:** `src/features/keypartners/kol_management.py`, `src/features/keypartners/schemas.py`, `src/features/keypartners/router.py`, `tests/test_keypartners_kol_contracts.py`
- **Validation Command:** `python -m pytest tests/test_keypartners_kol_contracts.py -q`
- **Blocked by:** TICKET-17

---

### FASE 4: Integração Integral do Motor Proprietário DENTGO (Marketplace B2B & Logística Express)

#### [~] [TICKET-19] Incorporação do Domínio Core DENTGO: Hubs Logísticos, Estoque Regional e Catálogo de Urgência
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `create_express_order` (`src/features/dentgo/service.py`) chama `validate_cro_syntax` em vez de `verify_cro_status`, deixando passar CROs com status `SUSPENSO` (`999999` / `0000*`).
  2. `search_emergency_supply` não filtra `status = 'AVAILABLE'` (permitindo vender lotes em `QUARANTINE_BLOCKED`).
  3. `create_express_order` calcula subtotal e baixa estoque apenas de `items[0]`, ignorando múltiplos itens no mesmo pedido.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Usar `verify_cro_status(customer_cro_uf)` em `create_express_order` e bloquear qualquer CRO cujo `verified` seja `False` ou `status != 'ATIVO'`.
  2. Filtrar `AND status = 'AVAILABLE'` em `search_emergency_supply` e validar que o lote não consta em `anvisa_batch_quarantines` com `status = 'QUARANTINE_BLOCKED'`.
  3. Iterar sobre todos os `items` do pedido em `create_express_order` para somar o `subtotal` correto e decrementar o estoque de cada item no Hub selecionado.
- **DoD:** Busca geolocalizada Haversine precisa; bloqueio de CRO suspenso/inválido e de lotes em quarentena; baixa de estoque multi-item.
- **Target Files:** `src/features/dentgo/__init__.py`, `src/features/dentgo/schemas.py`, `src/features/dentgo/service.py`, `src/features/dentgo/router.py`, `src/main.py`, `tests/test_dentgo_marketplace_routing.py`
- **Validation Command:** `python -m pytest tests/test_dentgo_marketplace_routing.py -q`
- **Blocked by:** TICKET-06, TICKET-16

#### [~] [TICKET-20] Máquina de Despacho Last-Mile, Custódia por Lacre Térmico e Comprovante no R2
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `src/features/dentgo/logistics_dispatch.py` não publica eventos no Redis Streams (`dentgo.delivered` / `dentgo.order_delivered`).
  2. `frontend/src/features/dentgo/DentgoExpressCockpit.tsx` usa array estático `mockOrders` e cores hexadecimais hardcoded (`#090d16`, `#151c2c`, `#101622`).
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Adicionar endpoint `GET /api/v1/dentgo/orders` em `src/features/dentgo/router.py` para listar pedidos ativos do tenant.
  2. Publicar mudanças de status em `StreamName.DENTGO` via `default_event_bus` (especialmente `dentgo.delivered` e `dentgo.order_delivered` em `verify_and_complete_delivery`).
  3. Refatorar `DentgoExpressCockpit.tsx` para buscar dados reais de `/api/v1/dentgo/orders`, implementar ações reais de despacho/validação de PIN, exibir os 4 estados obrigatórios e substituir todas as cores `#090d16`/`#151c2c`/`#101622` por variáveis de `tokens.css`.
- **DoD:** Validação estrita de PIN + POD no R2 publicando `dentgo.delivered`; `DentgoExpressCockpit.tsx` 100% conectado à API real e sem hexadecimais hardcoded.
- **Target Files:** `src/features/dentgo/logistics_dispatch.py`, `src/features/dentgo/service.py`, `src/features/dentgo/router.py`, `frontend/src/features/dentgo/DentgoExpressCockpit.tsx`, `docs/reconstruct_rvops/05_reconstructed_app/js/modules/dentgo-dispatch.js`, `tests/test_dentgo_lastmile_custody.py`
- **Validation Command:** `python -m pytest tests/test_dentgo_lastmile_custody.py -q`
- **Blocked by:** TICKET-01, TICKET-19

#### [~] [TICKET-21] Sinergia Automática KeyPartners <-> DENTGO (Reposição On-Demand e Resgate de Ociosos)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `trigger_automatic_replenishment_on_postop` não está inscrita no consumidor Redis Streams para reagir automaticamente ao evento `keypartners.postop_reported`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Registrar handler consumidor para `keypartners.postop_reported` em `src/features/dentgo/keypartners_synergy.py` e no `src/workers/runner.py` para disparar `trigger_automatic_replenishment_on_postop` automaticamente.
- **DoD:** Reposição automática gerada via evento e coleta reversa atualizando `kp_custody_ledger`.
- **Target Files:** `src/features/dentgo/keypartners_synergy.py`, `src/features/keypartners/service.py`, `src/features/dentgo/service.py`, `src/workers/runner.py`, `tests/test_keypartners_dentgo_synergy.py`
- **Validation Command:** `python -m pytest tests/test_keypartners_dentgo_synergy.py -q`
- **Blocked by:** TICKET-17, TICKET-20

#### [~] [TICKET-22] Motor de Monetização do Marketplace: Take-Rate, Frete Cirúrgico e Split de Pagamentos
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. Falta exportar os contratos `DentgoFinancialSplit` em `api_contracts.ts`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Garantir conciliação centavo a centavo ($V_{\text{bruto}} = V_{\text{seller}} + V_{\text{courier}} + V_{\text{revnault}}$) e exportar os contratos TypeScript em `api_contracts.ts`.
- **DoD:** Split financeiro conciliado e tipado em `api_contracts.ts`.
- **Target Files:** `src/features/dentgo/financial_split.py`, `src/features/dentgo/schemas.py`, `src/features/dentgo/router.py`, `tests/test_dentgo_financial_split.py`
- **Validation Command:** `python -m pytest tests/test_dentgo_financial_split.py -q`
- **Blocked by:** TICKET-20

---

### FASE 5: Camada de Customer Experience - CX (Chatwoot, Evolution Cluster, Vídeo SOS & ANVISA)

#### [ ] [TICKET-23] Orquestrador de Sharding da Evolution API v2 (100 a 1.000 Instâncias) e Espelhamento em Tempo Real
- **Status Real Auditado:** `[ ] REFAZER (MAQUIADO)`
- **Diagnóstico do Gap Atual:**
  1. `provision_whatsapp_instance` não faz chamada HTTP ao shard da Evolution API quando `not mock_mode`.
  2. `handle_evolution_event` não usa `livekit_service.generate_room_token` no `CALL_OFFER`, não faz upload de mídia no R2 no `MESSAGES_UPSERT`, não trata `CONTACTS_UPSERT` e não publica no Redis Streams.
  3. O arquivo `tests/test_evolution_sharding_mirror.py` está ausente (foi salvo como `test_evolution_cluster_and_call_offer.py`).
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Em `provision_whatsapp_instance`, chamar `POST {chosen_shard}/instance/create` via `httpx` quando `not mock_mode` (configurando S3/R2 da instância) e usar fallback determinístico em ambiente de teste offline.
  2. Em `handle_evolution_event`:
     * Para `CALL_OFFER`: gerar token real via `livekit_service.generate_room_token` e registrar envio do link da sala LiveKit.
     * Para `MESSAGES_UPSERT`: quando houver mídia (`imageMessage`, `audioMessage`, `documentMessage`, `videoMessage`), gerar chave particionada via `R2StorageClient.generate_storage_key` e persistir no R2.
     * Para `CONTACTS_UPSERT`: sincronizar/atualizar o contato na tabela `contacts`.
  3. Garantir a existência do arquivo `tests/test_evolution_sharding_mirror.py`.
- **DoD:** Sharding balanceado; `CALL_OFFER` gerando sala LiveKit real; `MESSAGES_UPSERT` particionado no R2; `pytest tests/test_evolution_sharding_mirror.py` passando.
- **Target Files:** `src/features/integrations/omnichannel/evolution_cluster.py`, `src/features/integrations/omnichannel/evolution_webhook_router.py`, `src/features/integrations/omnichannel/service.py`, `src/features/integrations/omnichannel/router.py`, `tests/test_evolution_sharding_mirror.py`
- **Validation Command:** `python -m pytest tests/test_evolution_sharding_mirror.py -q`
- **Blocked by:** TICKET-01, TICKET-02, TICKET-11

#### [~] [TICKET-24] Integração Profunda Chatwoot Omnichannel + Sidebar Contextual 360° (KeyPartners + DENTGO)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. Falta o endpoint `GET /api/v1/omnichannel/chatwoot-context-panel?contact_phone=...` especificado no Plano Mestre.
  2. Em `frontend/src/router.tsx` (linha 40), `<OmnichannelContextSidebar contactId="cnt-01" currentDealId="deal-01" />` passa props incompatíveis com `OmnichannelContextSidebarProps` (`contactIdentifier`), quebrando o TypeScript e deixando a sidebar em loading perpétuo.
  3. `OmnichannelContextSidebar.tsx` usa classes `slate-*`/`cyan-*` fora de `tokens.css`.
  4. Faltam os arquivos com os nomes exatos `docs/reconstruct_rvops/05_reconstructed_app/js/modules/inbox-context-sidebar.js` e `tests/test_chatwoot_context_sidebar.py`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Expor `GET /api/v1/omnichannel/chatwoot-context-panel` (aceitando `contact_phone` ou `contact_identifier`) além de `/api/v1/omnichannel/context/{contact_identifier}`, e incluir `open_deals` e `health_score` no payload 360°.
  2. Em `sync_contact_to_chatwoot`, chamar a API do Chatwoot (`/api/v1/accounts/{id}/contacts`) via `httpx` quando `not mock_mode`.
  3. Corrigir as props de `OmnichannelContextSidebar.tsx` (aceitando `contactIdentifier?: string; contactId?: string; currentDealId?: string`) e substituir classes `slate-*` por `tokens.css`.
  4. Criar `docs/reconstruct_rvops/05_reconstructed_app/js/modules/inbox-context-sidebar.js` e `tests/test_chatwoot_context_sidebar.py`.
- **DoD:** Endpoint `/chatwoot-context-panel` funcional; sidebar React renderizando sem erro de props; `pytest tests/test_chatwoot_context_sidebar.py` passando.
- **Target Files:** `src/features/integrations/omnichannel/chatwoot_bridge.py`, `src/features/integrations/omnichannel/router.py`, `frontend/src/features/inbox/OmnichannelContextSidebar.tsx`, `docs/reconstruct_rvops/05_reconstructed_app/js/modules/inbox-context-sidebar.js`, `tests/test_chatwoot_context_sidebar.py`
- **Validation Command:** `python -m pytest tests/test_chatwoot_context_sidebar.py -q`
- **Blocked by:** TICKET-17, TICKET-20, TICKET-23

#### [~] [TICKET-25] Vídeo Suporte Cirúrgico Crítico em 1 Clique ("SOS Mesa Cirúrgica" via LiveKit)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `trigger_surgical_sos` (`src/features/tickets/surgical_sos.py`) não chama `livekit_service.generate_room_token` nem registra o envio do link mágico no WhatsApp do cirurgião (`omnichannel_messages`).
  2. Em `frontend/src/router.tsx`, a rota `video_sos` renderiza `<DicomStl3DViewer />` em vez da central de Vídeo Suporte SOS.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Em `trigger_surgical_sos`, gerar token JWT real via `livekit_service.generate_room_token(room_name=room_id, identity=cro_uf, name=customer_name)`, anexar à URL da sala, gravar o envio imediato no WhatsApp (`omnichannel_messages`) e publicar `cx.surgical_sos_triggered` no `default_event_bus` (`StreamName.CX`).
  2. Conectar a rota `video_sos` em `frontend/src/router.tsx` para abrir a interface de Vídeo Suporte SOS (`LiveKitDealRoomModal` / painel SOS com botão de despacho rápido DENTGO).
- **DoD:** Ticket `P0_SURGICAL_TABLE` criado com token LiveKit real, link enviado no WhatsApp e despacho DENTGO em 1 clique.
- **Target Files:** `src/features/tickets/surgical_sos.py`, `src/features/tickets/service.py`, `src/features/tickets/router.py`, `frontend/src/router.tsx`, `tests/test_surgical_sos_livekit.py`
- **Validation Command:** `python -m pytest tests/test_surgical_sos_livekit.py -q`
- **Blocked by:** TICKET-11, TICKET-20, TICKET-24

#### [~] [TICKET-26] Copiloto RAG de Catálogos Técnicos, Torques e Sequência de Fresagem (pgvector)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `src/features/intelligence/surgical_rag.py` faz busca manual em SQLite sem integrar com `VectorStoreService`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Integrar `ingest_catalog_chunk` e `query_surgical_catalog` com o `VectorStoreService` (garantindo busca HNSW nativa quando conectado ao PostgreSQL 16 + `pgvector` e similaridade de cosseno normalizada em SQLite) com citação obrigatória de página e manual oficial.
- **DoD:** Respostas técnicas ancoradas estritamente nos manuais ingeridos com score de similaridade e referência de página.
- **Target Files:** `src/features/intelligence/surgical_rag.py`, `src/features/intelligence/router.py`, `tests/test_surgical_catalog_rag.py`
- **Validation Command:** `python -m pytest tests/test_surgical_catalog_rag.py -q`
- **Blocked by:** TICKET-03, TICKET-24

#### [~] [TICKET-27] Módulo de Cosmovigilância, Tecnovigilância ANVISA e Garantia de Osseointegração (RMA)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. Quando `quarantine_triggered = True` (falha acumulada $> 2.5\%$), o lote entra em `QUARANTINE_BLOCKED`, mas `keypartners/service.py` e `dentgo/service.py` não impediam novas remessas daquele lote.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Garantir que o bloqueio `QUARANTINE_BLOCKED` em `anvisa_batch_quarantines` impeça deterministicamente qualquer nova remessa daquele `batch_number` tanto em `dispatch_consignment_custody` (`keypartners/service.py`) quanto em `search_emergency_supply` / `create_express_order` (`dentgo/service.py`).
- **DoD:** Lote com índice de falha $> 2.5\%$ entra em `QUARANTINE_BLOCKED` e qualquer tentativa subsequente de remessa no KeyPartners ou checkout no DENTGO para aquele lote é bloqueada com erro sanitário.
- **Target Files:** `src/features/tickets/anvisa_technovigilance.py`, `src/features/keypartners/service.py`, `src/features/dentgo/service.py`, `src/features/tickets/schemas.py`, `src/features/tickets/router.py`, `tests/test_anvisa_technovigilance_rma.py`
- **Validation Command:** `python -m pytest tests/test_anvisa_technovigilance_rma.py -q`
- **Blocked by:** TICKET-01, TICKET-16, TICKET-20

#### [~] [TICKET-28] Réguas Automatizadas de Acompanhamento Pós-Operatório Clínico B2C (24h / 48h / 72h / 7d)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `process_patient_feedback` em `src/features/automations/postop_patient_care.py` não suporta transcrição de áudio do paciente via `transcription_worker` e não grava as mensagens de alerta enviadas ao cirurgião/paciente em `omnichannel_messages`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Permitir receber `audio_url` / `dialogue_text` em `process_patient_feedback` (transcrevendo via `transcription_worker` quando aplicável) e gravar o disparo de alerta para o WhatsApp do cirurgião (`surgeon_phone`) e resposta ao paciente (`patient_phone`) na tabela `omnichannel_messages`, além de publicar evento em `StreamName.CX`.
- **DoD:** Triagem de texto e áudio abrindo ticket crítico e disparando notificações reais para o cirurgião e paciente.
- **Target Files:** `src/features/automations/postop_patient_care.py`, `src/features/automations/router.py`, `tests/test_postop_patient_care_b2c.py`
- **Validation Command:** `python -m pytest tests/test_postop_patient_care_b2c.py -q`
- **Blocked by:** TICKET-12, TICKET-23

---

### FASE 6: Camada de Business Intelligence - BI (Apache Superset, Text-to-SQL & Predição SOK/PR)

#### [~] [TICKET-29] Integração do Apache Superset Embedded com Guest Tokens JWT e Row-Level Security (RLS)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `export_analytics_dataset` em `src/features/intelligence/superset_embedded.py` escreve CSV em um `io.StringIO()` na memória e **nunca faz upload para o Cloudflare R2** (`R2StorageClient` sequer é chamado).
  2. `SupersetEmbeddedDashboard.tsx` usa cores `slate-*`/`indigo-*` fora de `tokens.css` e em `router.tsx` é instanciado sem a prop `userId`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Em `export_analytics_dataset`, serializar o dataset em bytes (`.csv` ou `.parquet` binário) e enviá-lo para o Cloudflare R2 usando `R2StorageClient().upload_bytes(r2_key, data_bytes, content_type)`, gerando URL pré-assinada de download via `generate_presigned_download_url`.
  2. Definir valor default `userId = 'usr-director-br'` em `SupersetEmbeddedDashboard.tsx`, corrigir a chamada em `router.tsx` e substituir todas as cores `slate-*` por variáveis de `tokens.css`.
- **DoD:** Guest Token JWT com cláusula RLS exata por escopo; exportação analítica fazendo upload real para o R2; dashboard React sem erros de props ou tokens.
- **Target Files:** `src/features/intelligence/superset_embedded.py`, `src/features/intelligence/router.py`, `frontend/src/features/bi/SupersetEmbeddedDashboard.tsx`, `docs/reconstruct_rvops/05_reconstructed_app/js/modules/bi-superset.js`, `docker-stack.yml`, `tests/test_superset_rls_embedded.py`
- **Validation Command:** `python -m pytest tests/test_superset_rls_embedded.py -q`
- **Blocked by:** TICKET-03, TICKET-04

#### [~] [TICKET-30] Agente Analítico Conversacional Text-to-SQL (Web & WhatsApp da Diretoria)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `src/features/intelligence/text_to_sql_agent.py` não indexa o dicionário de metadados das tabelas analíticas no `VectorStoreService` / `pgvector` e não possui integração com LiteLLM para traduzir perguntas abertas.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Implementar `index_analytical_schema_metadata(account_id)` indexando a estrutura das tabelas (`deals`, `kp_custody_ledger`, `dentgo_orders`, `anvisa_rma_claims`, `clinical_procedure_margins`, `kp_surgical_health_scores`) no `VectorStoreService`.
  2. Em `natural_language_to_sql`, recuperar o contexto de schema relevante e usar LiteLLM (quando configurado) ou o compilador semântico determinístico expandido, validando a query gerada pelo parser `validate_safe_readonly_sql` e injetando obrigatoriamente `inject_rls_filter`.
- **DoD:** Proteção 100% determinística contra mutações/SQLi; injeção obrigatória de RLS; indexação de schema analítico ativa.
- **Target Files:** `src/features/intelligence/text_to_sql_agent.py`, `src/features/intelligence/router.py`, `tests/test_text_to_sql_security.py`
- **Validation Command:** `python -m pytest tests/test_text_to_sql_security.py -q`
- **Blocked by:** TICKET-03, TICKET-29

#### [~] [TICKET-31] Motor Matemático de Score de Ociosidade de Kit Consignado ($SOK$) e Ponto de Reposição ($PR$)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. Quando $SOK \ge 1.0$, `calculate_kit_idle_score_sok` não cria a tarefa crítica na tabela `tasks` para o consultor externo (embora o DoD exija).
  2. Em `calculate_replenishment_point_pr`, o cálculo de `current_stock` no `kp_custody_ledger` soma todas as linhas sem descontar `CONSUMO_CIRURGICO` e `DEVOLUCAO_INTACTA`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Em `calculate_kit_idle_score_sok`, quando `is_idle` for `True`, inserir automaticamente a tarefa crítica na tabela `tasks` para o consultor externo responsável pelo acordo, além de criar a ordem de coleta reversa no DENTGO.
  2. Em `calculate_replenishment_point_pr`, calcular o saldo líquido real (`SUM(CASE WHEN movement_type='REMESSA' THEN quantity ELSE -quantity END)`) quando `current_stock` não for passado explicitamente.
- **DoD:** Equações de $SOK$ e $PR$ exatas; tarefa crítica criada em `tasks` e ordem reversa criada no DENTGO quando $SOK \ge 1.0$; Deal de recompra e alerta WhatsApp gerados quando estoque $\le PR$.
- **Target Files:** `src/features/intelligence/predictive_inventory.py`, `src/features/intelligence/service.py`, `src/features/intelligence/router.py`, `tests/test_predictive_sok_pr_math.py`
- **Validation Command:** `python -m pytest tests/test_predictive_sok_pr_math.py -q`
- **Blocked by:** TICKET-17, TICKET-21

#### [~] [TICKET-32] Calculadora de Margem Líquida Real por Procedimento Clínico (Módulo para Clínicas e Franquias)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `calculate_procedure_net_margin` em `src/features/intelligence/clinical_margin.py` não busca automaticamente o custo dos insumos consumidos em `kp_surgical_orders` / `kp_custody_ledger` quando `surgery_order_id` é informado e `supplies_cost` é omitido ou zero.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Se `surgery_order_id` for fornecido e `supplies_cost == 0`, consultar `consumed_items_json` em `kp_surgical_orders` (ou `dentgo_orders`) para apurar automaticamente o custo real dos lotes consumidos na cirurgia.
- **DoD:** Cálculo exato da margem líquida ($V_{\text{procedimento}} - C_{\text{total}}$), cruzamento automático com ordens cirúrgicas e alerta para margem $< 15\%$.
- **Target Files:** `src/features/intelligence/clinical_margin.py`, `src/features/intelligence/router.py`, `tests/test_clinical_procedure_margin.py`
- **Validation Command:** `python -m pytest tests/test_clinical_procedure_margin.py -q`
- **Blocked by:** TICKET-17, TICKET-29

---

### FASE 7: Camada de Growth & RevOps (Health Score HSC, Moeda Cirúrgica, MGM & Reativação Cal.com)

#### [~] [TICKET-33] Motor Determinístico de Health Score Cirúrgico ($HSC$) e Prevenção Ativa de Churn
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `calculate_surgical_health_score` em `src/features/intelligence/health_score_hsc.py` não publica `growth.hsc_critical` no `EventBus` quando $HSC < 40$.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Publicar `growth.hsc_critical` no `default_event_bus` (`StreamName.SALES` / `StreamName.WEBHOOKS`) quando $HSC < 40.0$, além de criar a tarefa presencial urgente e enviar o voucher `DENTGO-EXPRESS-*` no WhatsApp.
- **DoD:** Cálculo determinístico de $HSC$, execução dos playbooks ($HSC < 40$ e $HSC > 75$) e emissão do evento `growth.hsc_critical`.
- **Target Files:** `src/features/intelligence/health_score_hsc.py`, `src/features/intelligence/service.py`, `src/features/intelligence/router.py`, `tests/test_surgical_health_score_hsc.py`
- **Validation Command:** `python -m pytest tests/test_surgical_health_score_hsc.py -q`
- **Blocked by:** TICKET-21, TICKET-27, TICKET-31

#### [~] [TICKET-34] Programa de Fidelidade "Moeda Cirúrgica" (KeyPartners Loyalty Engine)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `loyalty_engine.py` não possui consumidor registrado no `src/workers/runner.py` para creditar pontos automaticamente nos eventos `deal.won` e `keypartners.postop_reported`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Registrar handler no `src/workers/runner.py` que escuta `deal.won` e `keypartners.postop_reported` e invoca `credit_loyalty_points`.
  2. Permitir informar `voucher_code` opcional no checkout do DENTGO (`create_express_order`) para zerar a `urgency_fee` quando um voucher `MOEDA-EXPRESS-*` ou `DENTGO-EXPRESS-*` válido for utilizado.
- **DoD:** Crédito automático de Moedas Cirúrgicas por evento, progressão `SILVER` $ightarrow$ `GOLD` $ightarrow$ `BLACK_KOL` e resgate de voucher abatendo frete no DENTGO.
- **Target Files:** `src/features/keypartners/loyalty_engine.py`, `src/features/keypartners/schemas.py`, `src/features/keypartners/router.py`, `src/features/dentgo/service.py`, `src/workers/runner.py`, `tests/test_surgical_loyalty_engine.py`
- **Validation Command:** `python -m pytest tests/test_surgical_loyalty_engine.py -q`
- **Blocked by:** TICKET-18, TICKET-22, TICKET-33

#### [~] [TICKET-35] Loop Viral de Indicação B2B (Member-Get-Member Cirúrgico entre Colegas de Pós/CRO)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `register_referral_lead` em `src/features/campaigns/referral_mgm.py` **não atualiza `contacts.score` somando `+40` pontos** (apenas grava `40` na tabela `referral_conversions`, deixando o contato com score default no CRM) e não valida a sintaxe do CRO do indicado via `cro_validator.py`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Validar o CRO do indicado com `validate_cro_syntax(referred_cro_uf)` em `register_referral_lead`.
  2. Ao criar ou atualizar o contato indicado na tabela `contacts`, incrementar seu `score` em `+40` pontos (ex.: `MIN(100, COALESCE(score, 10) + 40)`) além de aplicar a tag `origem_indicacao_kol`.
- **DoD:** Prevenção contra auto-indicação; validação de CRO; boost real de `+40` pontos em `contacts.score`; crédito bilateral de R$ 600 em Moedas Cirúrgicas após `deal.won`.
- **Target Files:** `src/features/campaigns/referral_mgm.py`, `src/features/campaigns/router.py`, `tests/test_b2b_referral_mgm_loop.py`
- **Validation Command:** `python -m pytest tests/test_b2b_referral_mgm_loop.py -q`
- **Blocked by:** TICKET-06, TICKET-33, TICKET-34

#### [~] [TICKET-36] Motor de Agendamento Inteligente Cal.com e Loop de Reativação Preventiva de Pacientes (6/12/18m)
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `process_calcom_webhook` em `src/features/automations/calcom_reactivation.py` (linha 357) chama `EventBus.publish_sync(StreamName.AUDIT, ...)`, que falhava com `AttributeError`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Com `StreamName.AUDIT` e `EventBus.publish_sync` implementados no `TICKET-02`, garantir que a publicação do evento `calcom.booking_created` ocorra sem exceções silenciosas e adicionar cliente HTTP opcional para sincronização com a API do Cal.com.
- **DoD:** Agendamento dos marcos de 180/365/540 dias, disparo no WhatsApp, webhook `BOOKING_CREATED` gerando sala LiveKit/Deal/Task e evento `calcom.booking_created` publicado no EventBus.
- **Target Files:** `src/features/automations/calcom_reactivation.py`, `src/features/automations/router.py`, `src/features/webhooks/router.py`, `docker-stack.yml`, `tests/test_calcom_patient_reactivation.py`
- **Validation Command:** `python -m pytest tests/test_calcom_patient_reactivation.py -q`
- **Blocked by:** TICKET-11, TICKET-23, TICKET-28

#### [~] [TICKET-37] Liquidação Inteligente FEFO de Lotes com Validade Curta via Flash Deals no DENTGO
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `scan_and_generate_flash_deals` em `src/features/dentgo/fefo_flash_deals.py` varre apenas `dentgo_hub_inventory` e ignora lotes próximos do vencimento em `kp_custody_ledger`.
  2. As chamadas a `EventBus.publish_sync(StreamName.AUDIT, ...)` falhavam por falta do enum/método em `events.py`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Incluir na varredura FEFO também os lotes em `kp_custody_ledger` na janela de 180 a 275 dias e garantir que `EventBus.publish_sync(StreamName.AUDIT, ...)` funcione sem erro.
- **DoD:** Varredura FEFO (6 a 9 meses) cobrindo hubs e custódia, segmentação geolocalizada Haversine de 50 km, disparo no WhatsApp e reserva atômica de estoque.
- **Target Files:** `src/features/dentgo/fefo_flash_deals.py`, `src/features/dentgo/router.py`, `tests/test_dentgo_fefo_flash_deals.py`
- **Validation Command:** `python -m pytest tests/test_dentgo_fefo_flash_deals.py -q`
- **Blocked by:** TICKET-08, TICKET-19

---

### FASE 8: Camada de Desenvolvimento, Plataforma & Conectores Plug-and-Play (Windmill, Orthanc DICOM & ERPs)

#### [ ] [TICKET-38] Hub de Orquestração Windmill e Conector Fiscal ERP (TOTVS Protheus, SAP B1 & Sankhya) para Consignação
- **Status Real Auditado:** `[ ] REFAZER (MAQUIADO)`
- **Diagnóstico do Gap Atual:**
  1. `WindmillERPOrchestrator` em `src/features/integrations/erp_hub/windmill_client.py` **não faz upload dos bytes do XML e do DANFE PDF no Cloudflare R2** (apenas formata a string da chave com `generate_storage_key`).
  2. `WindmillERPOrchestrator` e os métodos `emit_*_nfe` de `TotvsProtheusAdapter`, `SapBusinessOneAdapter` e `SankhyaAdapter` não possuem chamadas HTTP reais (`httpx.post`) quando `self.mock_mode is False`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Gerar o documento XML NFe 4.00 determinístico (`<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">...`) e o binário PDF do DANFE (`%PDF-1.4...`) e enviá-los ao Cloudflare R2 via `self.storage.upload_bytes(xml_key, xml_bytes, "application/json")` / `"application/pdf"` (adicionando `"application/xml"` e `"text/xml"` em `ALLOWED_MIME_TYPES`).
  2. Adicionar suporte a chamada HTTP real via `httpx` para o servidor Windmill (`POST {self.windmill_url}/api/w/revnaut/jobs/run/p/f/erp/emit_nfe`) e para os endpoints REST do TOTVS Protheus, SAP B1 Service Layer e Sankhya quando `not self.mock_mode`.
- **DoD:** Emissão de NF-e de Remessa (`5917`/`6917`), Retorno Simbólico (`1918`/`2918`) e Venda Consignada (`5113`/`6113`) com upload real do XML e DANFE PDF no Cloudflare R2.
- **Target Files:** `src/features/integrations/totvs/adapter.py`, `src/features/integrations/totvs/service.py`, `src/features/integrations/totvs/router.py`, `src/features/integrations/erp_hub/windmill_client.py`, `docker-stack.yml`, `tests/test_erp_consignment_cfop_flow.py`
- **Validation Command:** `python -m pytest tests/test_erp_consignment_cfop_flow.py -q`
- **Blocked by:** TICKET-01, TICKET-05, TICKET-17

#### [~] [TICKET-39] Servidor de Imagiologia Médica Orthanc DICOM e Visualizador 3D de Tomografias / STL no R2
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `OrthancDicomClient` em `src/features/intelligence/orthanc_dicom.py` não possui método HTTP para consultar/sincronizar estudos com o servidor Orthanc (`http://orthanc:8042/studies`) quando `not self.mock_mode`.
  2. `frontend/src/features/imaging/DicomStl3DViewer.tsx` utiliza cores hexadecimais hardcoded (`#1e293b`, `#475569`, `#0f172a`, `#334155`, `#020617`, `#e11d48`, `#f43f5e`, `#0284c7`, `#38bdf8`, `#bae6fd`, `#fbbf24`, `#f59e0b`) e classes `slate-*`/`indigo-*`/`rose-*` que violam a regra de zero cores fora do `tokens.css`.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Adicionar sincronização HTTP real com a API REST do Orthanc (`/studies/{id}`) quando `not self.mock_mode`.
  2. Refatorar `DicomStl3DViewer.tsx` para substituir todas as cores hexadecimais `#...` e classes `slate-*` por variáveis CSS semânticas (`var(--color-*)`) de `tokens.css`.
- **DoD:** Presigned URL R2, anonimização LGPD HMAC-SHA256, isolamento multi-tenant (403/404) e componente `DicomStl3DViewer.tsx` com zero cores hexadecimais hardcoded.
- **Target Files:** `src/features/intelligence/orthanc_dicom.py`, `src/features/intelligence/router.py`, `frontend/src/features/imaging/DicomStl3DViewer.tsx`, `docs/reconstruct_rvops/05_reconstructed_app/js/modules/dicom-stl-viewer.js`, `docker-stack.yml`, `tests/test_orthanc_dicom_stl_r2.py`
- **Validation Command:** `python -m pytest tests/test_orthanc_dicom_stl_r2.py -q`
- **Blocked by:** TICKET-01, TICKET-27

#### [~] [TICKET-40] Motor de Webhooks Outbound Plug-and-Play com Assinatura Criptográfica HMAC-SHA256
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `OutboundWebhookDispatcher` armazena `signing_secret` em texto puro na tabela `webhook_subscriptions` em vez de criptografá-lo em repouso com `encrypt_secret` (AES-256-GCM do `TICKET-05`) na coluna `signing_secret_encrypted`.
  2. Não está registrado no `src/workers/runner.py` para consumir eventos do Redis Streams e despachá-los automaticamente.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Cifrar o segredo com `encrypt_secret(secret)` ao persistir em `webhook_subscriptions` (`signing_secret_encrypted`) e descriptografá-lo em memória com `decrypt_secret(...)` no momento de assinar o payload HMAC-SHA256.
  2. Conectar o `OutboundWebhookDispatcher` ao `src/workers/runner.py` para despachar eventos publicados em `StreamName.WEBHOOKS`.
- **DoD:** Segredo de assinatura cifrado em repouso no banco (AES-256-GCM); assinatura `X-Revnault-Signature: sha256=...` verificável; proteção anti-SSRF e circuit breaker em 15 falhas.
- **Target Files:** `src/features/webhooks/outbound_dispatcher.py`, `src/features/webhooks/schemas.py`, `src/features/webhooks/router.py`, `src/workers/runner.py`, `tests/test_outbound_webhooks_hmac.py`
- **Validation Command:** `python -m pytest tests/test_outbound_webhooks_hmac.py -q`
- **Blocked by:** TICKET-02, TICKET-05

#### [ ] [TICKET-41] Unificação do Cockpit Odontológico 360° (React 19 + TypeScript SPA) e Sincronia Estrita de Contratos
- **Status Real Auditado:** `[ ] REFAZER (MAQUIADO / QUEBRADO)`
- **Diagnóstico do Gap Atual:**
  1. `npm --prefix frontend run typecheck` (`tsc --noEmit`) falha por erros de tipos e imports em `router.tsx`, `CroVerifiedInput.tsx` e `LandingPageBuilder.tsx`.
  2. 7 das 14 rotas do `AppShell.tsx` (`deals`, `contacts`, `contracts`, `intelligence`, `scheduling`, `support`, `settings`) caem no `default:` do `switch` em `frontend/src/router.tsx`.
  3. `frontend/src/types/api_contracts.ts` e `docs/reconstruct_rvops/02_decompiled/api_contracts.ts` não possuem as interfaces nem o mapa de rotas dos Tickets 01 a 37.
  4. `tests/test_api_contracts_sync.py` verifica apenas 6 strings antigas.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Mapear todas as 14 rotas do `AppShell` em `frontend/src/router.tsx` (`dashboard`, `deals`, `contacts`, `omnichannel`, `keypartners`, `dentgo`, `video_sos`, `contracts`, `intelligence`, `analytics`, `scheduling`, `rbac`, `support`, `settings`, além de `marketing`, `scoring` e `imaging`) para seus respectivos componentes reais conectados à API.
  2. Atualizar `frontend/src/types/api_contracts.ts` e `docs/reconstruct_rvops/02_decompiled/api_contracts.ts` incluindo todas as interfaces de domínio dos Tickets 00 a 42 e a constante tipada `API_V1_ROUTES` mapeando 1:1 todas as rotas `/api/v1/*` expostas pelo FastAPI.
  3. Fortalecer `tests/test_api_contracts_sync.py` para inspecionar dinamicamente todas as rotas `/api/v1/*` registradas no `src.main:app` e exigir que 100% delas estejam declaradas em `api_contracts.ts`, além de executar `tsc --noEmit` se o Node/TypeScript estiver disponível.
- **DoD:** Zero erros em `tsc --noEmit`; 100% das rotas FastAPI `/api/v1/*` sincronizadas 1:1 em `api_contracts.ts`; todas as 14 seções do menu lateral do React renderizando views reais conectadas ao backend.
- **Target Files:** `frontend/src/App.tsx`, `frontend/src/router.tsx`, `frontend/src/types/api_contracts.ts`, `docs/reconstruct_rvops/02_decompiled/api_contracts.ts`, `docs/reconstruct_rvops/05_reconstructed_app/index.html`, `docs/reconstruct_rvops/05_reconstructed_app/js/app.js`, `tests/test_api_contracts_sync.py`
- **Validation Command:** `python -m pytest tests/test_api_contracts_sync.py -q`
- **Blocked by:** TICKET-00 a TICKET-40

#### [~] [TICKET-42] Orquestração do Cluster Docker Swarm (100 a 1.000 Consultores), Manuais e Auditoria Final dos 14 Gates AIDD
- **Status Real Auditado:** `[~] COMPLETAR / DESMAQUIAR`
- **Diagnóstico do Gap Atual:**
  1. `docker-stack.yml` não inclui os serviços `traefik`, `frontend`, `mautic`, `chatwoot`, `evolution-api` e `postgres-replica`.
  2. `docs/manuais/` não documenta nenhuma das novas rotas de KeyPartners, DENTGO, Copiloto Granola, Storage R2, Superset, Orthanc, Documenso e LiveKit.
  3. `gates/G_UI_DESIGN_LINTER.py` não escaneia a pasta `frontend/` (`.tsx`/`.ts`) nem bloqueia cores hexadecimais hardcoded em `frontend/src/features/`, e `run_server.py` contém um emoji `🚀` na linha 13.
- **Como Implementar / Corrigir (Detalhes Técnicos):**
  1. Completar `docker-stack.yml` com todos os serviços da arquitetura unificada (`traefik`, `frontend`, `app`, `worker`, `postgres`, `postgres-replica`, `redis`, `evolution-api`, `chatwoot`, `mautic`, `listmonk`, ` listmonk-db`, `livekit`, `documenso`, `calcom`, `superset`, `windmill`, `orthanc`, `wal-backup`) com limites de CPU/RAM e healthchecks.
  2. Atualizar `docs/manuais/` e `docs/manuais/README.md` documentando todas as novas rotas e motores (mantendo as 6 seções obrigatórias e zero emojis).
  3. Remover o emoji de `run_server.py` e atualizar `gates/G_UI_DESIGN_LINTER.py` para escanear também `frontend/src` (`.ts`, `.tsx`), `run_server.py` e `scripts/`, bloqueando emojis Unicode e cores hexadecimais `#...` fora de `tokens.css`.
- **DoD:** Todos os testes (`pytest -q`) e todos os 14 Quality Gates (`gates/G_*.py`) passando com exit code `0` sob inspeção real de código.
- **Target Files:** `docker-stack.yml`, `.env.example`, `run_server.py`, `docs/manuais/README.md`, `scripts/audit_rotas_manuais.py`, `gates/G_MANUAIS_ROTAS.py`, `gates/G_UI_DESIGN_LINTER.py`, `gates/G_CONTRACTS.py`
- **Validation Command:** `python -m pytest -q && python gates/G_SAIDA_BINARIA.py`
- **Blocked by:** TICKET-41
