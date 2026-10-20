# RevNault — Plano Mestre de Implementação Unificado (Micro-Tickets Cirúrgicos, Evolução de Stack, Motores Open-Source, KeyPartners & DENTGO)

## PARTE 1: Onde Estamos Hoje com a RevNault (Diagnóstico do Estado Atual)

A auditoria técnica do repositório atual (`heverton-dev/revnaut`) demonstra que a plataforma já possui uma fundação arquitetural moderna, regida por **AIDD (AI-Driven Development)** e protegida por **11 Gates Determinísticos de Qualidade e Segurança** (`gates/G_*.py`).

### 1.1. Inventário Técnico Já Implementado no Repositório

* **Core & Persistência (`src/core/`):**
  * `config.py`, `database.py` e `security.py`: Autenticação JWT, hashing seguro, pool de conexões SQLite/PostgreSQL e controle de variáveis de ambiente.
* **Módulos de Domínio Backend (`src/features/`):**
  * `auth/`: Login, validação de credenciais e emissão de tokens.
  * `hierarchy/` & `rbac/`: Estrutura de organograma em grafo acíclico direcionado (DAG), presets setoriais odontológicos, matriz de permissões e *Data Scoping* hierárquico (`SPEC_RBAC_DATA_SCOPING_HIERARQUICO.md`).
  * `contacts/` & `institutions/`: Gestão de cirurgiões-dentistas (CRO, especialidade), clínicas, hospitais e importador de carteiras (`05_importador_carteiras_clientes.md`).
  * `deals/`: Pipeline comercial multi-funil, cálculo de metas, comissões e gatilhos de receita (`test_deals_advanced_features.py`, `test_targets_and_commissions.py`).
  * `campaigns/` & `scoring/`: Integração base com Mautic e algoritmo inicial de Lead Scoring & ICP Odontológico (`11_lead_scoring_icp_odontologico.md`).
  * `communications/` & `integrations/omnichannel/`: Estrutura de webhooks para recebimento de mensagens de WhatsApp e inbox unificado.
  * `integrations/totvs/`: Adaptador inicial para sincronização de clientes e pedidos com ERP TOTVS Protheus (`src/features/integrations/totvs/adapter.py`).
  * `intelligence/`: Serviços iniciais de grafo clínico e predição de churn (`test_clinical_graph_churn.py`).
  * `tickets/` & `tasks/`: Gestão de chamados de suporte cirúrgico e tarefas operacionais.
  * `quarteto/`: Governança de estúdios e aprovação cruzada (`15_governanca_studios_quarteto.md`).
* **Design System & Protótipo Reconstruído (`docs/reconstruct_revnault/`):**
  * Benchmark heurístico (`03_mobbin_benchmark/audit_heuristica.md`), Design Tokens mapeados (`04_design_system/tokens.css`, `tokens.json`), contratos TypeScript (`02_decompiled/api_contracts.ts`) e aplicação reconstruída inicial em Vanilla JS (`05_reconstructed_app/`).
* **Esteira de Governança e Qualidade (`gates/`):**
  * Validação automatizada de segredos (`G_BLOQUEAR_SEGREDOS.py`), contratos de API (`G_CONTRACTS.py`), segurança OWASP (`G_CYBERSECURITY_OWASP.py`), determinismo (`G_DETERMINISMO_LEI_1.py`), AST (`G_ESTRUTURA_AST.py`), manuais (`G_MANUAIS_ROTAS.py`), performance (`G_PERFORMANCE.py`) e testes reais (`G_TESTES_REAIS.py`).

---

## PARTE 2: Diretrizes de Stack Tecnológica (O que Manter vs. O que Evoluir) e Metodologia de Esteira

Para suportar a escala de 100 a 1.000 consultores simultâneos e a complexidade de embutir salas de vídeo WebRTC, visualizadores 3D de tomografias DICOM, construtores de páginas e dashboards analíticos, adotamos uma diretriz cirúrgica de evolução tecnológica.

### 2.1. Matriz de Decisão da Stack: O que Manter vs. O que Evoluir

| Camada Arquitetural | Como Está Hoje no Repositório | Decisão Estratégica | Stack Robusta de Produção (Alvo) | Justificativa Técnica Principal |
| :--- | :--- | :--- | :--- | :--- |
| **Backend Core & API** | Python + FastAPI (`src/main.py`) | **MANTER & BLINDAR** | **Python 3.12 + FastAPI + Pydantic v2 + Uvicorn/Gunicorn** | Simbiose nativa com os motores de IA (`faster-whisper`, `pyannote.audio`, `LiteLLM`) e algoritmos matemáticos preditivos ($SOK$, $PR$, $HSC$). |
| **Camada de Acesso a Dados (ORM/DB)** | Queries diretas / Pool misto (`src/core/database.py`) | **EVOLUIR** | **SQLAlchemy 2.0 (100% Async + `asyncpg`) + Alembic Migrations** | Evita bloqueio da Event Loop sob alta concorrência de webhooks e garante versionamento determinístico de schema entre RevNault, KeyPartners e DENTGO. |
| **Banco de Dados & Busca Semântica** | SQLite (dev) / PostgreSQL inicial | **EVOLUIR** | **PostgreSQL 16 (Primário OLTP + Réplica OLAP) + `pgvector` (HNSW)** | Unifica transações críticas, leitura analítica pesada do BI e busca vetorial de catálogos/transcrições no mesmo motor. |
| **Filas, Eventos & Workflows** | Processamento síncrono de rotas | **EVOLUIR** | **Redis 7 Streams + Workers Determinísticos (ARQ/Celery) + Windmill** | Substitui o peso de memória do n8n por workers determinísticos em Python/Rust com *exponential backoff* e *Dead-Letter Queue*. |
| **Armazenamento de Arquivos (Storage)** | Disco local do contêiner | **EVOLUIR** | **Cloudflare R2 (API S3 v4 + Presigned URLs)** | 10 GB gratuitos, US\$ 0,015/GB adicional e **Zero Egress Fee** (taxa zero de tráfego de download), mantendo os discos NVMe das VPSs limpos. |
| **Frontend & Aplicação Cliente** | Vanilla JS + HTML (`05_reconstructed_app`) | **MIGRAR / EVOLUIR** | **React 19 + TypeScript + Vite + TanStack Query + Zustand** | O Vanilla JS não escala para gerenciar estados em tempo real (WebSockets), cache assíncrono e SDKs nativos (`@livekit/components-react`, `@superset-ui`, Cornerstone3D DICOM). |
| **UI, Design System & Estilização** | CSS Puro (`app.css` + `tokens.css`) | **EVOLUIR** | **Tailwind CSS + shadcn/ui (Radix UI) ancorado em `tokens.css`** | Permite que agentes de IA componham telas de nível *Linear/Stripe* instantaneamente sem escrever CSS ad-hoc ou quebrar escopo visual. |

### 2.2. Metodologia da Esteira de Desenvolvimento: Design System First & Estética Definitiva de Produção

Rejeitamos a abordagem tradicional de *"construir protótipos de baixa fidelidade para embelezar depois"*. Em uma esteira orientada por IA (**AIDD**), refatorar interfaces rudimentares dobra o retrabalho e quebra contratos de componentes e testes E2E. O desenvolvimento seguirá **3 Regras de Ouro**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│           ESTEIRA AIDD DE ALTA PRODUTIVIDADE: DESIGN SYSTEM FIRST + SLICES             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  1. FUNDAÇÃO VISUAL ÚNICA (TICKET-00)                                                  │
│     • Importação de tokens.css e tokens.json no Tailwind CSS + shadcn/ui               │
│     • Criação dos 15 Primitivos UI (DataTable, KanbanBoard, Drawer, Dialog, Badge...)  │
│     • Shell de Navegação Unificado (Sidebar RBAC Dual, Command Palette Cmd+K, Topbar)  │
│                                           │                                            │
│                                           ▼                                            │
│  2. EXECUÇÃO EM FATIAS VERTICAIS (TICKETS 01 A 42)                                     │
│     • Cada Micro-Ticket entrega: Migration + Backend Async + Worker + Tela React/TSX   │
│     • Proibição de CSS Ad-Hoc: As telas apenas compõem os blocos prontos do Passo 1    │
│     • Fidelidade Total de Estados: Loading Skeleton, Empty State, Error e Success Real │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Estética de Produção desde o Dia 1:** Através da fundação em **shadcn/ui + `tokens.css`**, toda tela gerada já nasce com acabamento visual definitivo, acessibilidade ARIA (Radix Primitives), modo claro/escuro clínico e responsividade (*Desktop Multi-Monitor* para Inside Sales/Diretoria e *Mobile-First PWA* para Consultores de Campo, Cirurgiões e Entregadores DENTGO).
2. **Proibição de CSS Ad-Hoc nos Micro-Tickets:** Nenhum ticket de feature criará folhas de estilo manuais soltas. Todas as views utilizarão estritamente os tokens semânticos e os componentes primitivos homologados no `TICKET-00`.
3. **Fidelidade dos 4 Estados Obrigatórios:** Nenhuma tela é considerada pronta (*Done*) sem implementar os 4 estados reais conectados ao TanStack Query: *Loading State* (Skeletons anatômicos), *Empty State* (com CTA claro para a primeira ação), *Error State* (com botão de retry e rastreio de erro) e *Success State* (dados reais tipados via `api_contracts.ts`).

---

## PARTE 3: Ecossistema de Motores Integrados (Proprietários, Transversais e Open-Source)

### 3.1. Motores Proprietários Integrados Nativamente

| Motor Proprietário | Repositório Origem | O que Agrega ao Ecossistema | Papel Estratégico no RevNault |
| :--- | :--- | :--- | :--- |
| **KeyPartners** | `heverton-dev/keypartners` | Gestão de estoque consignado em posse de terceiros, rastreabilidade sanitária por lote/série e validade (ANVISA), conciliação de kits cirúrgicos pós-operatórios, divisão operacional *Field Sales* vs. *Inside Sales* e programa de fidelidade KOL (*Moeda Cirúrgica*). | **Coração da Venda B2B Cirúrgica:** Estanca o extravio de implantes e caixas cirúrgicas ($3\%$ a $7\%$ do estoque fabril) e automatiza o faturamento condicional pós-cirurgia. |
| **DENTGO** | `heverton-web/dentgo` | Marketplace B2B on-demand ("iFood Odontológico"), roteamento para o Centro de Distribuição (CD) ou dental mais próxima, despacho de entregadores (couriers) com custódia por lacre térmico e split automático de pagamentos. | **Braço Físico & Liquidez Imediata:** Salva cirurgias em andamento com entregas em $45\text{ a }90\text{ min}$ ("Emergência de Mesa") e executa a coleta/reposição física dos kits do KeyPartners. |

### 3.2. Motores Open-Source por Camada de Atuação

| Camada | Motor Open-Source | Licença | O que Agrega e Papel Técnico no Ecossistema |
| :--- | :--- | :--- | :--- |
| **Marketing** | **GrapesJS** | BSD-3-Clause | Construtor visual *drag-and-drop* de Landing Pages odontológicas embutido em componente React com bloco nativo de validação de CRO/UF e compliance CFO. |
| **Marketing** | **Mautic + Listmonk** | GPLv3 / AGPLv3 | O **Mautic** atua como construtor visual da árvore de decisão de campanhas; o **Listmonk** (escrito em Go) executa disparos massivos de e-mails e catálogos em altíssima velocidade. |
| **Vendas & CX** | **Evolution API v2** | Apache 2.0 | Gateway multi-instâncias de WhatsApp (Baileys e Cloud API oficial). Permite espelhar até 1.000 números de consultores com consumo de $\approx 45\text{ MB}$ RAM por sessão. |
| **Vendas & CX** | **LiveKit (SFU + SIP)** | Apache 2.0 | Servidor WebRTC em Go de ultra-baixa latência. Provê videoconferências embutidas (`@livekit/components-react`), salas instantâneas de **Vídeo Suporte Cirúrgico SOS** e **VoIP via LiveKit SIP** com gravação isolada por faixa (Egress). |
| **Vendas & IA** | **faster-whisper + pyannote + LiteLLM** | MIT / Apache 2.0 | **Motor "Granola-like":** Transcreve reuniões e chamadas até $4\times$ mais rápido com quantização `int8`, separa a voz do consultor e do cirurgião (diarização) e extrai JSON estruturado (resumo, objeções, tarefas) preenchendo o CRM sem toque humano (*Zero-Touch*). |
| **Vendas & Legal** | **Documenso** | AGPLv3 | Motor auto-hospedado de assinatura eletrônica com validade jurídica, integrado via API para colher rubricas de pedidos e termos de consignação via WhatsApp em 1 clique. |
| **CX & Suporte** | **Chatwoot** | MIT | Central de atendimento omnichannel (WhatsApp, chat web, Instagram, e-mail) customizada com painel lateral React exibindo saldo consignado do KeyPartners e entregas ativas do DENTGO. |
| **BI & Analytics** | **Apache Superset** | Apache 2.0 | Plataforma corporativa de Business Intelligence embutida via `@superset-ui/embedded-sdk` com *Guest Tokens JWT* e *Row-Level Security (RLS)* espelhando o RBAC hierárquico. |
| **Growth** | **Cal.com** | AGPLv3 | Motor de agendamento inteligente para marcação de consultorias técnicas, cursos de imersão KOL e retorno preventivo de pacientes em clínicas. |
| **Dev & ERP** | **Windmill** | AGPLv3 | Orquestrador de scripts determinísticos em Rust/Go (Python/TypeScript) até $100\times$ mais leve que o n8n, responsável pelos conectores de ERPs (TOTVS Protheus, SAP, Sankhya) e split bancário. |
| **Imagiologia** | **Orthanc DICOM** | GPLv3 | Servidor médico leve para armazenamento e visualização 3D no navegador (Cornerstone3D / Three.js) de tomografias computadorizadas (CBCT DICOM) e escaneamentos intraorais (STL/PLY). |

---

## PARTE 4: Onde Chegaremos com a RevNault Após a Implementação

Ao concluir os Micro-Tickets deste plano, a **RevNault** consolidar-se-á como a **primeira Plataforma Global de Receita Operacional (RevNault), Consignação Cirúrgica e Logística On-Demand para a Cadeia Odontológica**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             ARQUITETURA FINAL UNIFICADA RevNault                                │
├───────────────┬──────────────────┬──────────────────┬──────────────────┬────────────────────────┤
│   MARKETING   │  VENDAS & IA     │   KEYPARTNERS    │     DENTGO       │   CX & COSMOVIGILÂNCIA │
│ • GrapesJS LP │ • Kanban Multi   │ • Custódia Lotes │ • App Urgência   │ • Chatwoot Omnichannel │
│ • Mautic Flow │ • Granola Voice  │ • Termo Digital  │ • Entrega 45min  │ • Vídeo SOS (LiveKit)  │
│ • Listmonk    │ • Documenso 1-Clq│ • Inside + Field │ • Coleta Ociosos │ • RAG Catálogo Técnico │
├───────────────┴──────────────────┴──────────────────┴──────────────────┴────────────────────────┤
│                INTELIGÊNCIA ANALÍTICA (BI), GROWTH PREDITIVO & CONECTORES ERP                   │
│ • Apache Superset RLS  • Text-to-SQL WhatsApp  • Health Score Cirúrgico  • Windmill TOTVS/SAP   │
│ • Orthanc DICOM 3D     • Cal.com Reactivation  • Moeda Cirúrgica KOL     • Split Pagamentos     │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                     INFRAESTRUTURA TRANSVERSAL DE ALTA ESCALABILIDADE                           │
│   FastAPI Async + SQLAlchemy 2.0 • React 19 + TS + shadcn/ui • Postgres 16 + pgvector • R2 S3   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Atendimento da Cadeia Completa (B2B2C):** Opera desde mega-indústrias (Neodent, Straumann, Conexão) gerenciando 1.000 representantes e milhares de kits consignados, até redes de franquias e consultórios particulares gerenciando pacientes e procedimentos clínicos.
2. **Unit Economics Imbatível:** Custo de infraestrutura em cluster de servidores Contabo + Cloudflare R2 na faixa de $\approx \text{R\$ } 1,45$ por consultor/mês em escala de 1.000 operadores.
3. **Quádrupla Monetização (Oceano Azul):** SaaS Recorrente + Take-Rate B2B ($3\%$ a $7\%$ no DENTGO) + *Express Surgical Delivery Fee* + Fintech Float/Split de Recebíveis.

---

## PARTE 5: Plano Faseado de Micro-Tickets de Implementação

Todos os Micro-Tickets seguem estritamente **TDD (Test-Driven Development)**, entregam fatias verticais com **estética definitiva de produção** e exigem aprovação nos Gates Determinísticos (`gates/G_*.py`).

---

### FASE 0: Evolução da Stack Base, Fundação Design System, Storage R2, Redis Streams & RBAC Dual

#### [x] [TICKET-00] Evolução da Stack Base: SQLAlchemy 2.0 Async + Alembic (Backend) & Bootstrap React 19 + TypeScript + shadcn/ui (Frontend)
- **Status:** [x] DONE (Commit: `ad8eb45`, Tests: 5/5 passed, Full Suite: 96/96 passed, Gates: 11/11 approved)
- **Descrição:** Adequação estrutural da stack tecnológica do projeto: configuração do motor assíncrono SQLAlchemy 2.0 + `asyncpg` e migrações determinísticas com **Alembic** no backend (`src/core/database.py`), e criação do workspace moderno **React 19 + TypeScript + Vite + TanStack Query + Tailwind CSS + shadcn/ui** (`frontend/`) importando diretamente os Design Tokens oficiais (`docs/reconstruct_revnault/04_design_system/tokens.css` e `tokens.json`) e contratos (`api_contracts.ts`).
- **Como Implementar (Detalhes Técnicos):**
  1. Configurar `AsyncEngine` e `async_sessionmaker` em `src/core/database.py` mantendo compatibilidade reversa com os testes existentes e inicializar diretório `migrations/` do Alembic.
  2. Inicializar a aplicação React 19 + TypeScript + Vite em `frontend/`, mapeando todas as variáveis CSS de `tokens.css` no `tailwind.config.ts`.
  3. Construir em `frontend/src/components/ui/` os 15 primitivos de estética de produção (`Button`, `Input`, `Badge`, `Card`, `DataTable`, `KanbanBoard`, `Sheet`, `Dialog`, `Select`, `Tabs`, `Skeleton`, `EmptyState`, `ErrorBoundary`, `Toast`, `Avatar`) e o `AppShell.tsx` (Sidebar RBAC responsiva + Topbar + Command Palette `Cmd+K`).
- **DoD (Definition of Done):** Sessões assíncronas de banco operando sem bloqueio de event loop; build TypeScript estrito (`tsc --noEmit`) sem erros; Design System renderizando os 4 estados obrigatórios (*Loading*, *Empty*, *Error*, *Success*) com estética final de produção.
- **TDD (Cenários de Teste):** Testar ciclo de sessão assíncrona e migration inicial do Alembic; validar sincronia de tipos entre `frontend/src/types/api_contracts.ts` e os schemas Pydantic v2 do backend.
- **Target Files:** `src/core/database.py`, `alembic.ini`, `migrations/env.py`, `frontend/package.json`, `frontend/tsconfig.json`, `frontend/tailwind.config.ts`, `frontend/src/App.tsx`, `frontend/src/components/layout/AppShell.tsx`, `tests/test_async_stack_foundation.py`
- **Validation Command:** `python -m pytest tests/test_async_stack_foundation.py -q`
- **Blocked by:** Nenhum (Ticket Zero de Fundação da Stack)

#### [x] [TICKET-01] Camada Transversal de Object Storage com Cloudflare R2 e Presigned URLs
- **Status:** [x] DONE (Commit: `f6cbe75`, Tests: 5/5 passed, Full Suite: 101/101 passed, Gates: 11/11 approved)
- **Descrição:** Implementação do módulo core `src/core/storage.py` utilizando `boto3` (protocolo S3 v4) apontando para o endpoint do Cloudflare R2, com geração de URLs pré-assinadas temporárias para leitura/escrita direta, particionamento multi-tenant por prefixo (`{tenant_id}/{module}/{yyyy}/{mm}/{uuid}.{ext}`), validação de MIME types médicos/documentais (`.pdf`, `.dcm`, `.stl`, `.ogg`, `.mp4`, `.png`) e componente React `<R2DirectUploader />`.
- **Como Implementar (Detalhes Técnicos):**
  1. Adicionar variáveis `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME` e `R2_PUBLIC_DOMAIN` em `src/core/config.py`.
  2. Criar classe `R2StorageClient` em `src/core/storage.py` com métodos `generate_presigned_upload_url(key, content_type, expires_in=900)`, `generate_presigned_download_url(key, expires_in=900)` e `upload_bytes(key, data, content_type)`.
  3. Expor endpoints autenticados em `src/features/storage/router.py` (`POST /api/v1/storage/presign-upload` e `GET /api/v1/storage/presign-download/{file_id}`) e criar o componente React `frontend/src/components/shared/R2DirectUploader.tsx` com barra de progresso real via `XMLHttpRequest`/`fetch` direto para o bucket R2.
- **DoD:** Uploads de arquivos não trafegam pelo buffer de memória da VPS em arquivos $> 10\text{ MB}$; chaves de acesso nunca expostas no frontend; cobertura de testes $\ge 95\%$.
- **TDD:** Testar geração de URL assinada com expiração de $900\text{ s}$; testar bloqueio de acesso cruzado entre tenants distintos (`tenant_a` tentando ler chave do `tenant_b`); testar rejeição de extensões executáveis maliciosas (`.exe`, `.sh`).
- **Target Files:** `src/core/config.py`, `src/core/storage.py`, `src/features/storage/schemas.py`, `src/features/storage/router.py`, `frontend/src/components/shared/R2DirectUploader.tsx`, `src/main.py`, `tests/test_r2_storage.py`
- **Validation Command:** `python -m pytest tests/test_r2_storage.py -q`
- **Blocked by:** TICKET-00

#### [x] [TICKET-02] Barramento de Eventos em Redis Streams e Pool de Workers Determinísticos
- **Status:** [x] DONE (Commit: `1728083`, Tests: 3/3 passed, Full Suite: 104/104 passed, Gates: 11/11 approved)
- **Descrição:** Implementação do broker de eventos assíncrono `src/core/events.py` baseado em Redis Streams (`XADD`, `XREADGROUP`, `XACK`) com suporte a *Dead-Letter Queue (DLQ)* e *exponential backoff*, substituindo fluxos pesados do n8n por workers determinísticos leves em Python.
- **Como Implementar (Detalhes Técnicos):**
  1. Configurar cliente Redis assíncrono em `src/core/events.py` com suporte a canais tipados: `stream:marketing`, `stream:sales`, `stream:keypartners`, `stream:dentgo`, `stream:cx`, `stream:webhooks`.
  2. Implementar decorator `@event_consumer(stream_name, group_name)` com controle de retentativas ($3$ tentativas com atraso de $2^n$ segundos) e movendo falhas persistentes para `stream:dlq`.
  3. Criar comando de inicialização do worker em `src/workers/runner.py` e configurar serviço no `docker-stack.yml`.
- **DoD:** Eventos publicados em menos de $5\text{ ms}$; garantia de entrega *at-least-once* com idempotência por `event_id`; zero perda de mensagens em queda temporária de worker.
- **TDD:** Publicar evento `deal.won`, simular falha na 1ª tentativa do consumidor, validar reprocessamento automático na 2ª tentativa e confirmar `XACK` no stream.
- **Target Files:** `src/core/events.py`, `src/workers/__init__.py`, `src/workers/runner.py`, `docker-stack.yml`, `tests/test_redis_streams_worker.py`
- **Validation Command:** `python -m pytest tests/test_redis_streams_worker.py -q`
- **Blocked by:** TICKET-01

#### [x] [TICKET-03] Migração para PostgreSQL 16 + Extensão pgvector e Pool OLTP/OLAP
- **Status:** [x] DONE (Commit: `7daf72e`, Tests: 2/2 passed, Full Suite: 106/106 passed, Gates: 11/11 approved)
- **Descrição:** Evolução de `src/core/database.py` para suportar PostgreSQL 16 com extensão `vector` (`pgvector`) habilitada, índices HNSW para busca semântica e separação de conexões assíncronas entre escrita primária (`get_write_db`) e réplica de leitura analítica (`get_read_db`).
- **Como Implementar (Detalhes Técnicos):**
  1. Criar migration Alembic habilitando `CREATE EXTENSION IF NOT EXISTS vector;` no PostgreSQL e manter fallback matemático em cosseno para SQLite em ambiente de testes unitários rápidos.
  2. Criar tabela `semantic_embeddings` (`id`, `tenant_id`, `entity_type`, `entity_id`, `content_chunk`, `embedding VECTOR(1536)`, `metadata_json`).
  3. Implementar serviço `VectorStoreService` em `src/core/vector_store.py` com busca por similaridade de cosseno $1 - (\vec{A} \cdot \vec{B}) / (\|\vec{A}\| \|\vec{B}\|)$ filtrada obrigatoriamente por `tenant_id`.
- **DoD:** Consultas vetoriais retornando top-$k$ resultados em menos de $30\text{ ms}$; isolamento estrito por tenant na busca vetorial.
- **TDD:** Inserir 5 fragmentos técnicos de catálogos de implantes (Cone Morse vs. Hexágono Externo), executar busca semântica por *"torque de inserção implante cônico"* e validar que o ranking traz o fragmento correto no topo.
- **Target Files:** `src/core/database.py`, `src/core/vector_store.py`, `docker-stack.yml`, `tests/test_pgvector_store.py`
- **Validation Command:** `python -m pytest tests/test_pgvector_store.py -q`
- **Blocked by:** TICKET-00, TICKET-01

#### [x] [TICKET-04] Evolução do RBAC para Hierarquia Dual (Field Sales vs. Inside Sales)
- **Status:** [x] DONE (Commit: `bb85fec`, Tests: 2/2 passed, Full Suite: 108/108 passed, Gates: 11/11 approved)
- **Descrição:** Expansão do motor de RBAC (`src/features/rbac/` e `src/features/hierarchy/`) e da árvore visual em React (`frontend/src/features/rbac/RbacHierarchyTree.tsx`) para suportar a operação conjunta entre **Vendas Externas (Consultor de Campo)** e **Vendas Internas (Analista de Backoffice/SDR)** no mesmo cliente/deal sem perda de isolamento territorial.
- **Como Implementar (Detalhes Técnicos):**
  1. Adicionar colunas `field_owner_id` e `inside_owner_id` nas tabelas `contacts`, `deals` e `consignments`.
  2. Atualizar `get_scoped_user_ids` em `src/features/rbac/service.py` para permitir visibilidade compartilhada quando o usuário logado for o `field_owner_id`, o `inside_owner_id` ou superior hierárquico direto de qualquer um dos dois na árvore DAG.
  3. Implementar regra de comissão bipartida (`split_commission_field_pct` e `split_commission_inside_pct`) no fechamento do negócio e atualizar o componente visual da matriz RBAC.
- **DoD:** Consultor externo de SP enxerga apenas sua carteira; analista interno da filial SP enxerga todas as carteiras vinculadas à sua mesa operacional; comissões calculadas separadamente sem duplicidade contábil.
- **TDD:** Criar cenário com 1 Gerente Regional, 2 Consultores de Campo e 1 Analista Interno; validar que o Analista Interno visualiza os deals de ambos os consultores, mas o Consultor A não visualiza os deals do Consultor B.
- **Target Files:** `src/features/rbac/schemas.py`, `src/features/rbac/service.py`, `src/features/hierarchy/service.py`, `src/features/deals/service.py`, `frontend/src/features/rbac/RbacHierarchyTree.tsx`, `tests/test_rbac_dual_field_inside.py`
- **Validation Command:** `python -m pytest tests/test_rbac_dual_field_inside.py -q`
- **Blocked by:** TICKET-02

#### [x] [TICKET-05] Gateway Edge Traefik, Rate Limiting e Criptografia AES-256 de Credenciais
- **Status:** CONCLUÍDO (Commit `7756add`)
- **Descrição:** Configuração do proxy reverso Traefik e implementação do cofre de credenciais de terceiros (`tenant_credentials`) com criptografia simétrica AES-256-GCM em repouso para armazenar tokens da Evolution API, certificados fiscais A1, chaves de ERPs e webhooks secrets.
- **Como Implementar (Detalhes Técnicos):**
  1. Implementar funções `encrypt_secret(plaintext: str) -> str` e `decrypt_secret(ciphertext: str) -> str` em `src/core/security.py` usando chave mestre derivada via PBKDF2.
  2. Criar CRUD de `tenant_credentials` em `src/features/auth/router.py` mascarando valores sensíveis na saída (`****abcd`) e tela de gestão de chaves em `frontend/src/features/settings/CredentialsVaultPage.tsx`.
  3. Configurar labels de roteamento e middleware de rate-limiting no `docker-stack.yml`.
- **DoD:** Zero segredos salvos em texto puro no banco de dados; aprovação integral nos gates `G_BLOQUEAR_SEGREDOS.py` e `G_CYBERSECURITY_OWASP.py`.
- **TDD:** Salvar credencial de certificado A1 e token de ERP via API, inspecionar a linha bruta no banco de dados para confirmar que está cifrada e validar descriptografia em memória pelo serviço autorizado.
- **Target Files:** `src/core/security.py`, `src/features/auth/schemas.py`, `src/features/auth/service.py`, `src/features/auth/router.py`, `frontend/src/features/settings/CredentialsVaultPage.tsx`, `docker-stack.yml`, `tests/test_credentials_vault.py`
- **Validation Command:** `python -m pytest tests/test_credentials_vault.py -q`
- **Blocked by:** TICKET-01


---

### FASE 1: Camada de Marketing (GrapesJS, Mautic Headless, Listmonk & Lead Scoring ICP)

#### [x] [TICKET-06] Validador Ético CFO e Verificador de Registro CRO/UF em Tempo Real
- **Status:** CONCLUÍDO (Commit `44d163a`)
- **Descrição:** Criação do serviço de validação profissional odontológica (`src/features/contacts/cro_validator.py`) para validar formato, dígito e situação cadastral de registros **CRO/UF** (Cirurgião-Dentista, Clínica EPAO, Laboratório TPD) e scanner de compliance com o Código de Ética Odontológica (CFO Resolução 196/2019) para peças de marketing.
- **Como Implementar (Detalhes Técnicos):**
  1. Implementar validador sintático e conector de consulta cadastral de CRO por UF (`SP`, `RJ`, `MG`, `PR`, `RS`, etc.) com cache de 7 dias no Redis.
  2. Implementar filtro determinístico `validate_cfo_marketing_compliance(text: str, has_responsible_cro: bool)` que alerta sobre termos vedados pelo CFO (ex.: promessa de resultado garantido, divulgação de preços abusivos sem responsável técnico inscrito).
  3. Integrar na criação/atualização de contatos e no componente React `<CroVerifiedInput />`.
- **DoD:** Contatos de cirurgiões validados com flag `cro_verified = True`; bloqueio de publicação de páginas sem identificação obrigatória do responsável técnico quando parametrizado.
- **TDD:** Testar CRO válido (`CRO-SP 123456`), CRO inválido, e submeter copy de landing page sem número de CRO para confirmar alerta de compliance ético.
- **Target Files:** `src/features/contacts/cro_validator.py`, `src/features/contacts/schemas.py`, `src/features/contacts/service.py`, `src/features/contacts/router.py`, `frontend/src/features/contacts/components/CroVerifiedInput.tsx`, `tests/test_cro_cfo_compliance.py`
- **Validation Command:** `python -m pytest tests/test_cro_cfo_compliance.py -q`
- **Blocked by:** TICKET-02


#### [x] [TICKET-07] Construtor de Landing Pages Odontológicas com GrapesJS (React Wrapper) e Assets no R2
- **Status:** CONCLUÍDO (Commit `55c778a`)
- **Descrição:** Integração do motor open-source **GrapesJS** encapsulado em componente React (`frontend/src/features/campaigns/LandingPageBuilder.tsx`) e criação do backend de persistência e publicação de páginas de captura (`src/features/campaigns/landing_pages.py`) com templates verticais pré-prontos (Imersão Fluxo Digital, Lançamento Kit Cirúrgico, Captação Paciente Protocolo).
- **Como Implementar (Detalhes Técnicos):**
  1. Criar tabelas `landing_pages` (`id`, `tenant_id`, `slug`, `title`, `gjs_html`, `gjs_css`, `gjs_components_json`, `cfo_responsible_cro`, `published_r2_url`) e `landing_page_submissions`.
  2. Implementar endpoints `POST /api/v1/campaigns/landing-pages`, `PUT /api/v1/campaigns/landing-pages/{id}/publish` (que compila o HTML estático e publica no Cloudflare R2) e `POST /api/v1/public/lp/{slug}/submit`.
  3. Implementar `LandingPageBuilder.tsx` com ciclo de vida limpo (`useEffect` destroy) e manter paridade no módulo `landing-builder.js` carregando os blocos customizados odontológicos (Input CRO/UF, Seletor de Especialidade, Seletor de Sistema de Implante).
- **DoD:** Criação, edição visual, salvamento de assets no R2 e submissão de lead criando contato no banco e publicando evento `lead.captured` no Redis Streams.
- **TDD:** Criar landing page a partir de template de Cirurgia Guiada, publicar, simular submissão de formulário por um implantodontista e verificar criação do contato com atribuição UTM.
- **Target Files:** `src/features/campaigns/landing_pages.py`, `src/features/campaigns/schemas.py`, `src/features/campaigns/router.py`, `frontend/src/features/campaigns/LandingPageBuilder.tsx`, `docs/reconstruct_revnault/05_reconstructed_app/js/modules/landing-builder.js`, `tests/test_landing_pages_grapesjs.py`
- **Validation Command:** `python -m pytest tests/test_landing_pages_grapesjs.py -q`
- **Blocked by:** TICKET-01, TICKET-06


#### [x] [TICKET-08] Arquitetura Híbrida Mautic Visual + Despachante Determinístico de Campanhas
- **Status:** CONCLUÍDO (Commit `2598127`)
- **Descrição:** Implementação da ponte bidirecional entre o construtor visual de campanhas do **Mautic** e o executor determinístico do RevNault (`src/features/campaigns/mautic_bridge.py`), permitindo que árvores de decisão no Mautic disparem mensagens de WhatsApp pela instância exata do consultor responsável.
- **Como Implementar (Detalhes Técnicos):**
  1. Criar endpoint receptor `POST /api/v1/webhooks/mautic/campaign-action` com validação de assinatura HMAC.
  2. Quando o Mautic acionar um passo de WhatsApp ou atualização de CRM, o endpoint enfileira no stream `stream:marketing` do Redis.
  3. O worker resolve o consultor dono da carteira do dentista (`field_owner_id` ou `inside_owner_id`), renderiza as variáveis dinâmicas (`{{contact.name}}`, `{{contact.cro}}`, `{{consultant.name}}`) e despacha pela instância correspondente na Evolution API v2.
- **DoD:** Processamento de webhook do Mautic em $< 15\text{ ms}$; roteamento automático para o chip do consultor titular da conta ou linha corporativa de fallback.
- **TDD:** Simular payload de webhook de campanha do Mautic para um dentista da carteira do Consultor A; verificar que o job foi enfileirado apontando para a instância de WhatsApp do Consultor A.
- **Target Files:** `src/features/campaigns/mautic_bridge.py`, `src/features/campaigns/service.py`, `src/features/webhooks/router.py`, `tests/test_mautic_hybrid_dispatch.py`
- **Validation Command:** `python -m pytest tests/test_mautic_hybrid_dispatch.py -q`
- **Blocked by:** TICKET-02, TICKET-04


#### [x] [TICKET-09] Motor de Disparo em Massa de Alta Velocidade com Listmonk Engine
- **Status:** CONCLUÍDO (Commit `9fc4cfa`)
- **Descrição:** Integração do motor open-source **Listmonk** (`src/features/campaigns/listmonk_adapter.py`) para envios transacionais e newsletters técnicas em alta escala (catálogos PDF, alertas de lotes, convites de congressos) para bases de 50.000+ cirurgiões sem sobrecarregar o banco principal.
- **Como Implementar (Detalhes Técnicos):**
  1. Implementar cliente REST assíncrono para a API do Listmonk (`/api/subscribers`, `/api/campaigns`, `/api/tx`).
  2. Sincronizar segmentos dinâmicos do RevNault (ex.: *"Todos os Implantodontistas Cone Morse da Região Sul"*) como listas no Listmonk.
  3. Configurar receptor de webhooks de bounce, abertura e clique do Listmonk para retroalimentar o score de engajamento do contato no RevNault.
- **DoD:** Sincronização de lotes de 10.000 contatos em menos de $5\text{ s}$; atualização automática de status `email_bounced` e cliques na timeline do contato.
- **TDD:** Criar campanha segmentada por especialidade `Implantodontia`, disparar via adaptador Listmonk e simular evento de clique no catálogo técnico.
- **Target Files:** `src/features/campaigns/listmonk_adapter.py`, `src/features/campaigns/router.py`, `docker-stack.yml`, `tests/test_listmonk_campaigns.py`
- **Validation Command:** `python -m pytest tests/test_listmonk_campaigns.py -q`
- **Blocked by:** TICKET-08


#### [TICKET-10] [x] DONE - Motor Preditivo de Lead Scoring Odontológico, ICP Fit e Handoff Automático
- **Descrição:** Evolução de `src/features/scoring/` para calcular em tempo real o **Score Comportamental + Técnico Odontológico ($0\text{ a }100$)**, atualizando o vetor de afinidade do cirurgião no `pgvector` e executando o handoff automático para o Kanban de Vendas ao atingir o limiar de corte ($\ge 75\text{ pontos}$).
- **Como Implementar (Detalhes Técnicos):**
  1. Calcular o score combinando **Fit de ICP ($60\%$)** (Volume de implantes/mês, uso de fluxo digital/scanner, especialidade alvo, porte da clínica) e **Engajamento ($40\%$)** (Cliques em tabela de compatibilidade, abertura de catálogo, resposta no WhatsApp, presença em imersão).
  2. Quando `total_score >= threshold` (padrão $75$) e não houver deal aberto nos últimos 30 dias, criar automaticamente o card no estágio inicial do funil de vendas atribuído ao consultor da região, injetando o briefing técnico gerado no card.
- **DoD:** Cálculo determinístico e auditável; criação automática do Deal sem duplicação (idempotente); histórico de variação de score salvo em `scoring_history` e renderizado em `frontend/src/features/scoring/IcpScoringDashboard.tsx`.
- **TDD:** Simular lead que começa com 50 pontos (Fit ICP), clica na tabela de torque (+15 pts) e baixa catálogo de cirurgia guiada (+15 pts), totalizando 80 pontos; validar criação imediata do Deal no Kanban do consultor responsável.
- **Target Files:** `src/features/scoring/schemas.py`, `src/features/scoring/service.py`, `src/features/scoring/router.py`, `frontend/src/features/scoring/IcpScoringDashboard.tsx`, `tests/test_lead_scoring_auto_handoff.py`
- **Validation Command:** `python -m pytest tests/test_lead_scoring_auto_handoff.py -q`
- **Blocked by:** TICKET-03, TICKET-09

---

### FASE 2: Camada de Vendas, Copiloto de IA ("Granola-like"), VoIP/Meet LiveKit & Documenso

#### [TICKET-11] [x] DONE - Infraestrutura de Salas WebRTC e Telefonia VoIP com LiveKit SFU & LiveKit SIP
- **Descrição:** Implementação do módulo de comunicações em tempo real (`src/features/communications/livekit_service.py`) integrando o servidor **LiveKit SFU** para videoconferências embutidas em React (`@livekit/components-react`) e **LiveKit SIP** para discagem/recebimento de chamadas telefônicas normais (VoIP) diretamente no navegador do consultor, com gravação automática de faixas de áudio separadas (*Track Egress*) no Cloudflare R2.
- **Como Implementar (Detalhes Técnicos):**
  1. Implementar gerador de tokens de acesso LiveKit (`AccessToken` JWT assinado com `LIVEKIT_API_KEY` e `LIVEKIT_API_SECRET`) vinculado ao `deal_id` ou `ticket_id`.
  2. Configurar regras de `RoomCompositeEgress` e `TrackEgress` para exportar automaticamente o arquivo `.ogg`/`.wav` do canal do consultor e do canal do cliente diretamente para o bucket do Cloudflare R2 ao encerrar a sala.
  3. Configurar endpoint de discagem SIP (`POST /api/v1/communications/voip/dial`) e o componente `<LiveKitDealRoomModal />` em React.
- **DoD:** Salas de vídeo e chamadas VoIP iniciadas em 1 clique dentro da tela do Deal; gravação salva automaticamente no R2 disparando webhook `room_finished`.
- **TDD:** Gerar token de sala para um Deal, simular chamadas de início de Egress e webhook de encerramento do LiveKit, validando registro da gravação vinculada ao Deal.
- **Target Files:** `src/features/communications/livekit_service.py`, `src/features/communications/router.py`, `frontend/src/features/communications/LiveKitDealRoomModal.tsx`, `docs/reconstruct_revnault/05_reconstructed_app/js/modules/livekit-room.js`, `docker-stack.yml`, `tests/test_livekit_webrtc_sip.py`
- **Validation Command:** `python -m pytest tests/test_livekit_webrtc_sip.py -q`
- **Blocked by:** TICKET-01, TICKET-02

#### [TICKET-12] [x] DONE - Pipeline STT de Alta Performance com faster-whisper e Diarização pyannote.audio
- **Descrição:** Criação do worker de transcrição e diarização (`src/features/intelligence/transcription_worker.py`) que consome os áudios salvos no Cloudflare R2, executa transcrição acelerada com `faster-whisper` (CTranslate2 `int8`) e separa os interlocutores (`SPEAKER_CONSULTANT` vs. `SPEAKER_SURGEON`) via `pyannote.audio` ou canais estéreo isolados do LiveKit.
- **Como Implementar (Detalhes Técnicos):**
  1. Escutar o evento `call.recording_ready` no Redis Streams.
  2. Baixar o stream de áudio via URL assinada do R2, processar através do motor `faster-whisper` (com fallback configurável para API Whisper/Groq em ambientes sem GPU dedicada) e alinhar os timestamps de fala de cada participante.
  3. Salvar a transcrição diarizada na tabela `call_transcriptions` e vetorizar os blocos da conversa no `pgvector` (`entity_type = 'call_transcript'`).
- **DoD:** Transcrição com timestamps precisos por frase e identificação clara de quem é o consultor e quem é o cirurgião/cliente; indexação vetorial imediata.
- **TDD:** Processar fixture de diálogo comercial odontológico, validar estrutura de segmentos diarizados e confirmar indexação no `VectorStoreService`.
- **Target Files:** `src/features/intelligence/transcription_worker.py`, `src/features/intelligence/schemas.py`, `src/features/intelligence/service.py`, `tests/test_faster_whisper_diarization.py`
- **Validation Command:** `python -m pytest tests/test_faster_whisper_diarization.py -q`
- **Blocked by:** TICKET-03, TICKET-11

#### [TICKET-13] [x] DONE - Copiloto Comercial "Granola-like" via LiteLLM e Auto-Preenchimento Zero-Touch do Deal
- **Descrição:** Implementação do extrator cognitivo estruturado (`src/features/intelligence/granola_copilot.py`) utilizando **LiteLLM** (suportando Ollama/vLLM local ou modelos cloud) para transformar a transcrição da reunião ou áudio de pós-operatório do consultor em notas estruturadas, mapeamento de objeções, criação automática de tarefas de follow-up e atualização de campos do Deal (*Zero-Touch CRM*).
- **Como Implementar (Detalhes Técnicos):**
  1. Submeter a transcrição diarizada a um schema Pydantic estrito (`MeetingIntelligenceExtraction`): `executive_summary`, `implant_systems_mentioned`, `competitors_cited`, `objections_raised`, `next_steps_tasks`, `suggested_deal_value`, `suggested_probability`.
  2. Atualizar automaticamente o card do Deal em `src/features/deals/service.py` com o resumo, registrar as objeções em `deal_objections` e criar as tarefas operacionais em `src/features/tasks/service.py` com data de vencimento calculada.
  3. Suportar também "Notas de Voz Rápidas de Campo": o consultor externo envia um áudio de 30s no WhatsApp após sair do consultório e o Copiloto atualiza o Deal e o estoque consignado.
- **DoD:** Zero necessidade de digitação manual pós-reunião; tarefas criadas automaticamente para o consultor interno e externo; log de auditoria da sugestão da IA exibido em `frontend/src/features/deals/components/GranolaCopilotCard.tsx`.
- **TDD:** Alimentar o Copiloto com uma transcrição onde o Dr. Roberto pede *"proposta de 20 implantes Cone Morse com prazo de 60 dias até sexta-feira"*; validar que o Deal teve valor atualizado, objeção de prazo registrada e tarefa criada para sexta-feira.
- **Target Files:** `src/features/intelligence/granola_copilot.py`, `src/features/intelligence/router.py`, `src/features/deals/service.py`, `src/features/tasks/service.py`, `frontend/src/features/deals/components/GranolaCopilotCard.tsx`, `tests/test_granola_copilot_zerotouch.py`
- **Validation Command:** `python -m pytest tests/test_granola_copilot_zerotouch.py -q`
- **Blocked by:** TICKET-12

#### [TICKET-14] [x] DONE - Motor Dinâmico de Catálogo Odontológico, Multi-Tabela de Preços e Alçadas de Desconto
- **Descrição:** Implementação do motor de catálogo técnico e precificação (`src/features/deals/catalog_pricing.py`) com taxonomia odontológica (Implantes, Componentes Protéticos, Biomateriais, Kits Cirúrgicos, Motores/Scanners), tabelas diferenciadas por perfil de comprador e trava de alçada de desconto por nível hierárquico RBAC.
- **Como Implementar (Detalhes Técnicos):**
  1. Criar tabelas `products_catalog` (com SKU, registro ANVISA, plataforma protética, diâmetro, comprimento, torque recomendado) e `price_tables` (`BALCAO`, `FRANQUIA`, `DISTRIBUIDOR`, `UNIVERSIDADE_ENSINO`, `KOL_PARCEIRO`).
  2. Implementar motor de cálculo de proposta que valida o desconto solicitado contra o limite do cargo no RBAC (ex.: Consultor até $5\%$, Supervisor até $12\%$, Diretor até $25\%$).
  3. Caso o desconto exceda a alçada do vendedor, bloquear a geração do contrato e criar solicitação de aprovação instantânea para o gestor imediato.
- **DoD:** Precificação exata por categoria de cliente; bloqueio determinístico de descontos fora da alçada; aprovação em 1 clique pelo gestor liberando a proposta.
- **TDD:** Simular consultor tentando aplicar $15\%$ de desconto (limite $5\%$); validar que o Deal entra em `PENDING_DISCOUNT_APPROVAL`; simular aprovação pelo gerente e validar desbloqueio.
- **Target Files:** `src/features/deals/catalog_pricing.py`, `src/features/deals/schemas.py`, `src/features/deals/service.py`, `src/features/deals/router.py`, `tests/test_catalog_pricing_approval.py`
- **Validation Command:** `python -m pytest tests/test_catalog_pricing_approval.py -q`
- **Blocked by:** TICKET-04

#### [TICKET-15] [x] DONE - Fechamento de Propostas e Contratos com Documenso Headless e Assinatura via WhatsApp
- **Descrição:** Integração do motor open-source **Documenso** (`src/features/deals/documenso_service.py`) para geração dinâmica de PDFs de propostas comerciais, contratos de fornecimento e termos de responsabilidade de consignação, enviando o link de assinatura diretamente no WhatsApp do cirurgião e movendo o Deal para `WON` após o webhook de rubrica.
- **Como Implementar (Detalhes Técnicos):**
  1. Gerar o PDF do pedido/termo a partir dos itens do Deal, arquivar a versão original no Cloudflare R2 e enviar via API REST do Documenso (`/api/v1/documents`) posicionando as tags de assinatura do cirurgião, consultor e testemunha.
  2. Disparar o link de assinatura via Evolution API para o WhatsApp do dentista.
  3. Receber o webhook `DOCUMENT_COMPLETED` do Documenso, baixar o PDF assinado com manifesto criptográfico (IP, timestamp, hash SHA-256) para o Cloudflare R2, atualizar o Deal para `GANHO` e publicar `deal.won` no Redis Streams.
- **DoD:** Geração e envio do contrato em 1 clique no card do Kanban; transição automática de estágio após assinatura; guarda jurídica do PDF assinado no R2.
- **TDD:** Gerar contrato para um Deal aprovado, simular webhook `DOCUMENT_COMPLETED` do Documenso e verificar transição do Deal para `WON`, armazenamento da chave R2 e disparo de comissão.
- **Target Files:** `src/features/deals/documenso_service.py`, `src/features/deals/router.py`, `src/features/webhooks/router.py`, `docker-stack.yml`, `tests/test_documenso_contract_flow.py`
- **Validation Command:** `python -m pytest tests/test_documenso_contract_flow.py -q`
- **Blocked by:** TICKET-01, TICKET-14

---

### FASE 3: Integração Integral do Motor Proprietário KEYPARTNERS (Consignação Cirúrgica & Parcerias)

#### [TICKET-16] [x] DONE - Incorporação do Domínio Core KeyPartners: Custódia de Kits, Lotes ANVISA e Saldos
- **Descrição:** Implementação nativa completa do motor **KeyPartners** (`src/features/keypartners/`) no backend e banco de dados do RevNault, controlando o razão de custódia de estoque em posse de cada clínica/cirurgião com rastreabilidade estrita de lote, número de série, data de esterilização e validade ANVISA.
- **Como Implementar (Detalhes Técnicos):**
  1. Criar esquema relacional completo do KeyPartners via migration Alembic:
     * `kp_partner_agreements`: Contrato de parceria (Nível Silver, Gold, Black/KOL, limite de crédito consignado em R\$, piso mínimo de faturamento mensal, prazo máximo de giro em dias).
     * `kp_consignment_kits`: Caixas e kits cirúrgicos/protéticos seriados (QR Code único, composição padrão de brocas, chaves e catracas).
     * `kp_custody_ledger`: Razão imutável de movimentações (`REMESSA`, `CONSUMO_CIRURGICO`, `DEVOLUCAO_INTACTA`, `TROCA_GARANTIA`, `EXTRAVIO`) com `product_id`, `anvisa_reg`, `batch_number`, `serial_number`, `sterilization_expiry_date`.
  2. Implementar serviço `KeyPartnersCustodyService` garantindo que nenhuma remessa ultrapasse o limite de crédito consignado disponível do parceiro nem envie lotes com validade inferior a 30 dias.
- **DoD:** Rastreabilidade de $100\%$ dos implantes e kits em posse de terceiros por lote e validade; bloqueio automático de remessa de lote vencido ou parceiro sem limite.
- **TDD:** Criar acordo de parceria com limite de R\$ 15.000, remeter kit + 10 implantes (total R\$ 12.000), tentar remeter mais R\$ 5.000 (validar bloqueio por limite) e testar bloqueio de implante com lote vencido.
- **Target Files:** `src/features/keypartners/__init__.py`, `src/features/keypartners/schemas.py`, `src/features/keypartners/service.py`, `src/features/keypartners/router.py`, `src/main.py`, `tests/test_keypartners_custody_ledger.py`
- **Validation Command:** `python -m pytest tests/test_keypartners_custody_ledger.py -q`
- **Blocked by:** TICKET-04, TICKET-14

#### [TICKET-17] [x] DONE - Fluxo Operacional de Remessa, Conferência de Lacre e Baixa Pós-Cirúrgica (Inside + Field)
- **Descrição:** Implementação da máquina de estados do ciclo cirúrgico consignado no KeyPartners (`SOLICITADO_FIELD` $\rightarrow$ `APROVADO_INSIDE` $\rightarrow$ `TERMO_ASSINADO` $\rightarrow$ `EM_TRANSITO` $\rightarrow$ `EM_POSSE_CLINICA` $\rightarrow$ `CONCILIACAO_POS_OP` $\rightarrow$ `FATURADO_E_REPOSTO`), integrando o consultor de campo e o analista interno em `frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx`.
- **Como Implementar (Detalhes Técnicos):**
  1. O Consultor Externo solicita a remessa pelo app móvel informando a data da cirurgia e a grade de implantes desejada.
  2. O Analista Interno aprova no backoffice, bipa os lotes enviados, gera o Termo de Custódia via **Documenso** (TICKET-15) e despacha.
  3. Após a cirurgia, o Consultor Externo ou a clínica realiza o **Reporte Pós-Operatório** (via tela ou comando de voz no Copiloto Granola) informando quais lotes foram implantados no paciente e anexando a foto do lacre dos itens não utilizados (salva no Cloudflare R2).
  4. O sistema converte automaticamente os itens consumidos em Pedido de Venda Faturável (`CFOP 5.113/6.113`) e agenda a reposição/devolução dos excedentes.
- **DoD:** Conciliação exata entre itens remetidos, consumidos e devolvidos; geração automática do pedido de venda apenas sobre o que foi utilizado na cirurgia.
- **TDD:** Simular ciclo completo: remessa de 10 implantes, reporte pós-cirúrgico de 3 implantes usados (lotes A1, A2, A3) e 7 intactos; validar que o saldo em custódia caiu para 7 e que um pedido faturável de 3 unidades foi gerado para o Inside Sales.
- **Target Files:** `src/features/keypartners/surgical_cycle.py`, `src/features/keypartners/service.py`, `src/features/keypartners/router.py`, `frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx`, `docs/reconstruct_revnault/05_reconstructed_app/js/modules/consignments.js`, `tests/test_keypartners_surgical_postop.py`
- **Validation Command:** `python -m pytest tests/test_keypartners_surgical_postop.py -q`
- **Blocked by:** TICKET-13, TICKET-15, TICKET-16

#### [TICKET-18] [x] DONE - Gestão de Key Opinion Leaders (KOLs), Embaixadores e Metas de Comodato
- **Descrição:** Implementação do submódulo de gestão de cirurgiões embaixadores, professores e grandes clínicas parceiras (`src/features/keypartners/kol_management.py`), monitorando contrapartidas de comodato de equipamentos (motores cirúrgicos, scanners intraorais, kits permanentes) versus consumo mensal de implantes e entregas de aulas/casos clínicos.
- **Como Implementar (Detalhes Técnicos):**
  1. Criar tabela `kp_kol_contracts` vinculando equipamentos cedidos em comodato (com número de patrimônio) à meta mensal de consumo de consumíveis e cotas de palestras/publicações clínicas.
  2. Implementar auditoria automática mensal que verifica a adimplência da meta do KOL e armazena os casos clínicos e vídeos submetidos pelo embaixador no Cloudflare R2.
- **DoD:** Painel completo de ativos em comodato por KOL; cálculo automático de atingimento de contrapartida contratual.
- **TDD:** Cadastrar KOL com motor cirúrgico em comodato exigindo consumo mínimo de 20 implantes/mês; simular consumo de 22 implantes e validar status `COMPLIANT`; simular consumo de 8 implantes e validar geração de alerta para a gerência regional.
- **Target Files:** `src/features/keypartners/kol_management.py`, `src/features/keypartners/schemas.py`, `src/features/keypartners/router.py`, `tests/test_keypartners_kol_contracts.py`
- **Validation Command:** `python -m pytest tests/test_keypartners_kol_contracts.py -q`
- **Blocked by:** TICKET-17

---

### FASE 4: Integração Integral do Motor Proprietário DENTGO (Marketplace B2B & Logística Express)

#### [TICKET-19] [x] DONE - Incorporação do Domínio Core DENTGO: Hubs Logísticos, Estoque Regional e Catálogo de Urgência
- **Descrição:** Implementação nativa do motor **DENTGO** (`src/features/dentgo/`) dentro do ecossistema RevNault, permitindo que indústrias, filiais e dentais parceiras operem como *Hubs Logísticos Urbanos (Sellers)* oferecendo entregas cirúrgicas expressas ($45\text{ a }90\text{ min}$) e entregas agendadas (*Same-Day*) para cirurgiões habilitados.
- **Como Implementar (Detalhes Técnicos):**
  1. Criar tabelas `dentgo_hubs` (CNPJ, coordenadas geográficas `lat`/`lng`, raio de atuação em km, horário de plantão cirúrgico), `dentgo_hub_inventory` (saldo disponível para pronta-entrega por lote e validade) e `dentgo_orders`.
  2. Implementar algoritmo de geolocalização (fórmula de Haversine) que, diante da busca de um cirurgião por um componente de emergência (ex.: *"Implante Cone Morse $4.3 \times 11.5\text{ mm}$ + Membrana de Colágeno"*), localiza o Hub ativo mais próximo com estoque válido e calcula o ETA (tempo estimado de chegada) e a taxa de urgência cirúrgica.
  3. Exigir validação ativa de CRO (`cro_verified = True` do TICKET-06) antes de liberar o checkout de dispositivos implantáveis.
- **DoD:** Busca geolocalizada retornando hubs em raio de até $30\text{ km}$ ordenados por menor ETA; bloqueio estrito de venda de implantes para usuários sem CRO ativo.
- **TDD:** Cadastrar 2 Hubs (Hub A a $3\text{ km}$ sem estoque do lote; Hub B a $7\text{ km}$ com estoque válido); simular pedido de emergência de uma clínica e confirmar roteamento automático para o Hub B com cálculo de ETA.
- **Target Files:** `src/features/dentgo/__init__.py`, `src/features/dentgo/schemas.py`, `src/features/dentgo/service.py`, `src/features/dentgo/router.py`, `src/main.py`, `tests/test_dentgo_marketplace_routing.py`
- **Validation Command:** `python -m pytest tests/test_dentgo_marketplace_routing.py -q`
- **Blocked by:** TICKET-06, TICKET-16

#### [TICKET-20] [x] DONE - Máquina de Despacho Last-Mile, Custódia por Lacre Térmico e Comprovante no R2
- **Descrição:** Implementação do módulo de logística sanitária e controle de entregadores (`src/features/dentgo/logistics_dispatch.py` e `frontend/src/features/dentgo/DentgoExpressCockpit.tsx`), gerenciando a bipagem no CD, o código de lacre inviolável da maleta térmica, o rastreamento em tempo real e a prova de entrega (POD - *Proof of Delivery*) com foto e assinatura salvas no Cloudflare R2.
- **Como Implementar (Detalhes Técnicos):**
  1. Criar estados logísticos: `ORDER_PLACED` $\rightarrow$ `PICKING_BIPADO` $\rightarrow$ `SEALED_READY` $\rightarrow$ `COURIER_ASSIGNED` $\rightarrow$ `IN_TRANSIT_LIVE` $\rightarrow$ `DELIVERED_VERIFIED`.
  2. Exigir que o operador do Hub informe o `seal_code` (número do lacre físico) e bipe o DataMatrix/lote ANVISA na saída; na chegada à clínica, o recepcionista/cirurgião valida o `seal_code` ou fornece o `delivery_pin` de 4 dígitos, enquanto o entregador sobe a foto do pacote entregue no Cloudflare R2.
  3. Publicar cada mudança de coordenada/status no Redis Streams para notificação via WhatsApp da clínica.
- **DoD:** Nenhuma entrega cirúrgica é concluída sem validação do código de lacre/PIN e upload da evidência fotográfica no R2; rastreabilidade sanitária completa do transporte.
- **TDD:** Executar fluxo de despacho completo; tentar finalizar entrega com PIN incorreto (validar erro 400); finalizar com PIN correto e foto no R2, confirmando publicação do evento `dentgo.delivered`.
- **Target Files:** `src/features/dentgo/logistics_dispatch.py`, `src/features/dentgo/service.py`, `src/features/dentgo/router.py`, `frontend/src/features/dentgo/DentgoExpressCockpit.tsx`, `docs/reconstruct_revnault/05_reconstructed_app/js/modules/dentgo-dispatch.js`, `tests/test_dentgo_lastmile_custody.py`
- **Validation Command:** `python -m pytest tests/test_dentgo_lastmile_custody.py -q`
- **Blocked by:** TICKET-01, TICKET-19

#### [TICKET-21] [x] DONE - Sinergia Automática KeyPartners $\leftrightarrow$ DENTGO (Reposição On-Demand e Resgate de Ociosos)
- **Descrição:** Integração direta entre os motores **KeyPartners** e **DENTGO** (`src/features/dentgo/keypartners_synergy.py`) para que baixas pós-cirúrgicas disparem ordens automáticas de reposição de estoque consignado via courier, e alertas de kits ociosos gerem ordens de coleta reversa para realocação em outro cirurgião da mesma cidade.
- **Como Implementar (Detalhes Técnicos):**
  1. Escutar o evento `keypartners.postop_reported` no Redis Streams: quando um cirurgião consome $N$ implantes de sua caixa consignada fixa, gerar automaticamente uma ordem de reposição `REPLENISHMENT_ORDER` no DENTGO apontando para o Hub mais próximo.
  2. Implementar endpoint `POST /api/v1/keypartners/consignments/{id}/trigger-dentgo-pickup` que cria uma ordem de **Logística Reversa** no DENTGO para um courier retirar um kit cirúrgico ocioso na Clínica A e entregá-lo (após conferência/esterilização no Hub) na Clínica B.
- **DoD:** Reposição de kits consignados gerada sem intervenção manual; ciclo completo de logística reversa atualizado no `kp_custody_ledger`.
- **TDD:** Simular baixa pós-cirúrgica de 2 implantes no KeyPartners e verificar criação automática da ordem de reposição no DENTGO; simular ordem de coleta reversa de kit ocioso e verificar transferência de custódia após entrega.
- **Target Files:** `src/features/dentgo/keypartners_synergy.py`, `src/features/keypartners/service.py`, `src/features/dentgo/service.py`, `tests/test_keypartners_dentgo_synergy.py`
- **Validation Command:** `python -m pytest tests/test_keypartners_dentgo_synergy.py -q`
- **Blocked by:** TICKET-17, TICKET-20

#### [TICKET-22] [x] DONE - Motor de Monetização do Marketplace: Take-Rate, Frete Cirúrgico e Split de Pagamentos
- **Descrição:** Implementação do motor financeiro do DENTGO (`src/features/dentgo/financial_split.py`) calculando e segregando na fonte as três receitas transacionais: valor líquido do fornecedor (Indústria/Dental), remuneração do entregador especializado (*Express Surgical Delivery Fee*) e comissão da plataforma RevNault (*Take-Rate* de $3\%$ a $7\%$).
- **Como Implementar (Detalhes Técnicos):**
  1. Criar tabela `dentgo_financial_splits` registrando para cada pedido: `gross_amount`, `platform_take_rate_pct`, `platform_fee_amount`, `delivery_fee_total`, `courier_net_payout`, `seller_net_payout`, `settlement_status`.
  2. Suportar modalidade **"Faturar no Convênio/Crédito Corporativo KeyPartners"** (para clínicas parceiras aprovadas que pagam quinzenalmente) e **"Pagamento Instantâneo Pix/Cartão com Split na Fonte"**.
- **DoD:** Conciliação centavo a centavo ($V_{\text{bruto}} = V_{\text{seller}} + V_{\text{courier}} + V_{\text{revnault}}$); extrato transparente para indústria, courier e administradora.
- **TDD:** Simular pedido de urgência de R\$ 2.000,00 em implantes + R\$ 45,00 de frete express com Take-Rate de $5\%$; validar que `platform_fee_amount` = R\$ 100,00 + margem de frete, `seller_net_payout` = R\$ 1.900,00 e `courier_net_payout` calculado sem erro de arredondamento.
- **Target Files:** `src/features/dentgo/financial_split.py`, `src/features/dentgo/schemas.py`, `src/features/dentgo/router.py`, `tests/test_dentgo_financial_split.py`
- **Validation Command:** `python -m pytest tests/test_dentgo_financial_split.py -q`
- **Blocked by:** TICKET-20

---

### FASE 5: Camada de Customer Experience - CX (Chatwoot, Evolution Cluster, Vídeo SOS & ANVISA)

#### [TICKET-23] [x] DONE - Orquestrador de Sharding da Evolution API v2 (100 a 1.000 Instâncias) e Espelhamento em Tempo Real
- **Descrição:** Evolução de `src/features/integrations/omnichannel/` para gerenciar um cluster distribuído de **Evolution API v2** (suportando de 100 a 1.000 números de WhatsApp de consultores com balanceamento por *consistent hashing*), descarregando todas as mídias no Cloudflare R2 e espelhando conversas e contatos em tempo real no RevNault.
- **Como Implementar (Detalhes Técnicos):**
  1. Criar tabela `whatsapp_instances` (`instance_name`, `consultant_user_id`, `shard_node_url`, `phone_number`, `status`, `qr_code_base64`).
  2. Implementar roteador de sharding que aloca novas instâncias de consultores no nó da Evolution API com menor carga (`shard-a`, `shard-b`, `shard-c`), configurando a instância para salvar mídias diretamente no bucket do Cloudflare R2.
  3. Processar os webhooks `MESSAGES_UPSERT`, `CONTACTS_UPSERT` e `CALL_OFFER` via Redis Streams: quando um cliente tentar ligar por chamada de voz normal do WhatsApp (`CALL_OFFER`), responder automaticamente com o link instantâneo da sala WebRTC do LiveKit para gravação e suporte com IA.
- **DoD:** Pareamento via QR Code direto no painel do consultor; espelhamento bidirecional de mensagens enviadas pelo celular físico; interceptação elegante de chamadas do WhatsApp convertendo para link LiveKit.
- **TDD:** Provisionar 3 instâncias distribuídas em 3 shards simulados; enviar evento `MESSAGES_UPSERT` e validar persistência na timeline do contato; enviar evento `CALL_OFFER` e validar resposta automática com link de sala LiveKit.
- **Target Files:** `src/features/integrations/omnichannel/evolution_cluster.py`, `src/features/integrations/omnichannel/service.py`, `src/features/integrations/omnichannel/router.py`, `tests/test_evolution_sharding_mirror.py`
- **Validation Command:** `python -m pytest tests/test_evolution_sharding_mirror.py -q`
- **Blocked by:** TICKET-01, TICKET-02, TICKET-11

#### [TICKET-24] [x] DONE - Integração Profunda Chatwoot Omnichannel + Sidebar Contextual 360° (KeyPartners + DENTGO)
- **Descrição:** Integração bidirecional com o **Chatwoot** (`src/features/integrations/omnichannel/chatwoot_bridge.py`) e construção do Dashboard App em React (`frontend/src/features/inbox/OmnichannelContextSidebar.tsx`) exibindo em tela única: CRO do dentista, kits consignados em posse dele no **KeyPartners**, entregas em andamento no **DENTGO** e situação financeira.
- **Como Implementar (Detalhes Técnicos):**
  1. Sincronizar contatos, caixas de entrada e agentes do RevNault com o Chatwoot via API Platform/Application.
  2. Criar o endpoint e a view do *Chatwoot Dashboard App* (`GET /api/v1/omnichannel/chatwoot-context-panel?contact_phone=...`) que retorna em tempo real o resumo consolidado da conta (Deals abertos, Saldo Consignado KeyPartners, Pedidos DENTGO em trânsito e Score de Saúde).
- **DoD:** Atendente ou consultor enxerga toda a vida cirúrgica, logística e financeira do cliente ao lado do chat sem trocar de aba.
- **TDD:** Consultar endpoint do painel contextual para um cirurgião com 1 kit consignado e 1 entrega DENTGO em trânsito; validar que o JSON/HTML retorna ambos os ativos com precisão.
- **Target Files:** `src/features/integrations/omnichannel/chatwoot_bridge.py`, `src/features/integrations/omnichannel/router.py`, `frontend/src/features/inbox/OmnichannelContextSidebar.tsx`, `docs/reconstruct_revnault/05_reconstructed_app/js/modules/inbox-context-sidebar.js`, `tests/test_chatwoot_context_sidebar.py`
- **Validation Command:** `python -m pytest tests/test_chatwoot_context_sidebar.py -q`
- **Blocked by:** TICKET-17, TICKET-20, TICKET-23

#### [TICKET-25] [x] DONE - Vídeo Suporte Cirúrgico Crítico em 1 Clique ("SOS Mesa Cirúrgica" via LiveKit)
- **Descrição:** Implementação do fluxo de emergência clínica em `src/features/tickets/surgical_sos.py`: quando um cirurgião em procedimento aciona suporte urgente (dúvida de sequência de fresagem, estabilidade primária ou componente protético), o sistema cria um ticket crítico `P0_SURGICAL_TABLE`, gera uma sala de vídeo instantânea no **LiveKit** e conecta a câmera do celular da clínica ao assessor técnico de plantão em menos de $10\text{ segundos}$.
- **Como Implementar (Detalhes Técnicos):**
  1. Detectar gatilho de urgência no WhatsApp/DENTGO ou botão "SOS Cirurgia" no app.
  2. Criar sala LiveKit com perfil de baixa latência e enviar o link mágico no WhatsApp do cirurgião/instrumentadora (que abre direto no navegador mobile sem exigir instalação de app).
  3. Disparar alerta sonoro na fila de assessores clínicos do Chatwoot/RevNault e, caso falte algum componente físico identificado na chamada de vídeo, permitir que o assessor despache o item via **DENTGO** com 1 clique de dentro da própria chamada.
- **DoD:** Geração da sala e envio do link em $< 2\text{ s}$; gravação da orientação técnica arquivada no ticket; botão de despacho rápido DENTGO acoplado à tela de suporte.
- **TDD:** Acionar endpoint `POST /api/v1/tickets/surgical-sos`, validar criação de ticket `P0`, geração de URL WebRTC LiveKit e conversão de necessidade identificada em pedido de urgência no DENTGO.
- **Target Files:** `src/features/tickets/surgical_sos.py`, `src/features/tickets/service.py`, `src/features/tickets/router.py`, `tests/test_surgical_sos_livekit.py`
- **Validation Command:** `python -m pytest tests/test_surgical_sos_livekit.py -q`
- **Blocked by:** TICKET-11, TICKET-20, TICKET-24

#### [TICKET-26] [x] DONE - Copiloto RAG de Catálogos Técnicos, Torques e Sequência de Fresagem (pgvector)
- **Descrição:** Implementação do assistente técnico baseado em RAG (`src/features/intelligence/surgical_rag.py`) que indexa manuais cirúrgicos, tabelas de torque de inserção, sequências de brocas por densidade óssea (Tipo I a IV) e compatibilidade protética no `pgvector`, sugerindo respostas técnicas exatas com citação de página para o consultor/atendente no Chatwoot.
- **Como Implementar (Detalhes Técnicos):**
  1. Criar pipeline de ingestão de catálogos técnicos (`POST /api/v1/intelligence/catalog-rag/ingest`) que divide manuais em chunks semânticos por linha de implante e grava os embeddings no `pgvector`.
  2. A cada pergunta técnica recebida no chat (ex.: *"Qual a sequência de brocas para o implante Cone Morse $3.5 \times 13\text{ mm}$ em osso tipo II e qual o torque máximo do minipilar?"*), buscar os chunks mais relevantes e gerar a resposta técnica sugerida com aviso de página/referência do manual.
- **DoD:** Zero alucinação de medidas ou torques (respostas estritamente ancoradas nos documentos oficiais da fábrica com score de similaridade $\ge 0.78$); tempo de resposta $< 1.5\text{ s}$.
- **TDD:** Ingerir especificações oficiais de torque de implantes e componentes; realizar consulta sobre torque de minipilar cônico e validar que a resposta traz o valor exato em $\text{N}\cdot\text{cm}$ e a referência do documento.
- **Target Files:** `src/features/intelligence/surgical_rag.py`, `src/features/intelligence/router.py`, `tests/test_surgical_catalog_rag.py`
- **Validation Command:** `python -m pytest tests/test_surgical_catalog_rag.py -q`
- **Blocked by:** TICKET-03, TICKET-24

#### [TICKET-27] [x] DONE - Módulo de Cosmovigilância, Tecnovigilância ANVISA e Garantia de Osseointegração (RMA)
- **Descrição:** Implementação da esteira regulatória de queixas técnicas e reposição em garantia de implantes perdidos/não-osseointegrados (`src/features/tickets/anvisa_technovigilance.py`), coletando obrigatoriamente lote, série, torque aplicado, região anatômica (dente FDI), data da cirurgia, data do explante e radiografia periapical/tomografia no Cloudflare R2.
- **Como Implementar (Detalhes Técnicos):**
  1. Criar tabela `anvisa_rma_claims` vinculada a `tickets` e ao `kp_custody_ledger` (validando se o lote informado realmente foi vendido ou consignado para aquele cirurgião).
  2. Armazenar o exame radiográfico de comprovação da falha no Cloudflare R2.
  3. Calcular a taxa acumulada de perda por lote fabril: se um lote apresentar índice de falha $> 2.5\%$, disparar alerta crítico de **Recall / Bloqueio Preventivo de Lote** no KeyPartners e no DENTGO para impedir novas remessas daquele lote.
- **DoD:** Validação cruzada do lote reclamado com a nota/consignação original; geração automática da remessa de reposição em garantia; trava sanitária automática de lote defeituoso.
- **TDD:** Registrar 3 queixas técnicas de perda de implante para o lote `LOTE-9988` (ultrapassando o teto de $2.5\%$ das unidades distribuídas); validar que o lote entra imediatamente em status `QUARANTINE_BLOCKED` no KeyPartners e no DENTGO.
- **Target Files:** `src/features/tickets/anvisa_technovigilance.py`, `src/features/tickets/schemas.py`, `src/features/tickets/router.py`, `tests/test_anvisa_technovigilance_rma.py`
- **Validation Command:** `python -m pytest tests/test_anvisa_technovigilance_rma.py -q`
- **Blocked by:** TICKET-01, TICKET-16, TICKET-20

#### [TICKET-28] [x] DONE - Réguas Automatizadas de Acompanhamento Pós-Operatório Clínico B2C (24h / 48h / 72h / 7d)
- **Descrição:** Para clínicas, franquias e consultórios particulares que utilizam o RevNault, implementar a régua ativa de cuidado pós-cirúrgico do paciente (`src/features/automations/postop_patient_care.py`), monitorando sinais de dor, edema, sangramento e adesão medicamentosa via WhatsApp após cirurgias de implante ou enxerto.
- **Como Implementar (Detalhes Técnicos):**
  1. Ao registrar a conclusão de uma cirurgia clínica, agendar disparos automáticos via Redis/Evolution API em $+24\text{ h}$, $+48\text{ h}$, $+72\text{ h}$ e $+7\text{ dias}$ (remoção de sutura).
  2. Analisar a resposta do paciente (texto ou áudio transcrito pelo `faster-whisper`): se detectar sinais de alerta (*"sangramento intenso"*, *"febre"*, *"muita dor"*, *"parafuso soltou"*), abrir imediatamente um ticket urgente para o cirurgião responsável e notificar a recepção da clínica.
- **DoD:** Disparos humanizados em nome do cirurgião; triagem automática de intercorrências pós-operatórias reduzindo complicações clínicas e aumentando o CSAT do consultório.
- **TDD:** Iniciar régua pós-operatória para um paciente; simular resposta de áudio/texto relatando *"estou com sangramento forte e inchaço"* no marco de 24h; validar abertura imediata de alerta vermelho para o dentista.
- **Target Files:** `src/features/automations/postop_patient_care.py`, `src/features/automations/router.py`, `tests/test_postop_patient_care_b2c.py`
- **Validation Command:** `python -m pytest tests/test_postop_patient_care_b2c.py -q`
- **Blocked by:** TICKET-12, TICKET-23

---

### FASE 6: Camada de Business Intelligence - BI (Apache Superset, Text-to-SQL & Predição SOK/PR)

#### [TICKET-29] [x] DONE - Integração do Apache Superset Embedded com Guest Tokens JWT e Row-Level Security (RLS)
- **Descrição:** Implementação do módulo de BI embarcado (`src/features/intelligence/superset_embedded.py` e `frontend/src/features/bi/SupersetEmbeddedDashboard.tsx`) gerando *Guest Tokens JWT* assinados para renderizar dashboards do **Apache Superset** dentro do RevNault, aplicando filtros automáticos de **Row-Level Security (RLS)** baseados na árvore de RBAC do usuário logado.
- **Como Implementar (Detalhes Técnicos):**
  1. Implementar endpoint `POST /api/v1/intelligence/bi/guest-token` que consulta `get_scoped_user_ids(current_user)` no RBAC e monta a cláusula RLS determinística (ex.: `tenant_id = 10 AND (field_owner_id IN (4, 5) OR inside_owner_id IN (4, 5))`).
  2. Assinar o token JWT compatível com o `@superset-ui/embedded-sdk` e implementar o componente React `<SupersetEmbeddedDashboard />` exibindo os painéis de Indústria (Giro de Consignado, Ranking Regional, Taxa de Perda ANVISA) e Clínica (Margem Líquida por Procedimento, Ocupação de Cadeira).
  3. Adicionar suporte à exportação de datasets analíticos pesados em formato `.parquet`/`.csv` direto para o Cloudflare R2.
- **DoD:** Dashboards renderizados sem exigir segundo login; isolamento hermético de dados por regional/consultor via cláusula SQL injetada no token JWT.
- **TDD:** Gerar Guest Token para um Consultor Regional do Paraná e outro para o Diretor Nacional; decodificar os tokens JWT e validar que as regras `rls` do consultor restringem estritamente aos IDs de sua carteira.
- **Target Files:** `src/features/intelligence/superset_embedded.py`, `src/features/intelligence/router.py`, `frontend/src/features/bi/SupersetEmbeddedDashboard.tsx`, `docs/reconstruct_revnault/05_reconstructed_app/js/modules/bi-superset.js`, `docker-stack.yml`, `tests/test_superset_rls_embedded.py`
- **Validation Command:** `python -m pytest tests/test_superset_rls_embedded.py -q`
- **Blocked by:** TICKET-03, TICKET-04

#### [TICKET-30] [x] DONE - Agente Analítico Conversacional Text-to-SQL (Web & WhatsApp da Diretoria)
- **Descrição:** Criação do motor **Text-to-SQL** (`src/features/intelligence/text_to_sql_agent.py`) que permite a diretores, gerentes e donos de clínicas fazerem perguntas analíticas por texto ou áudio no WhatsApp/Web, convertendo a pergunta em SQL seguro (somente leitura na réplica OLAP com filtro de RBAC obrigatório) e devolvendo tabelas e gráficos.
- **Como Implementar (Detalhes Técnicos):**
  1. Indexar o dicionário de metadados das tabelas analíticas (`deals`, `kp_custody_ledger`, `dentgo_orders`, `anvisa_rma_claims`) no `pgvector`.
  2. Implementar validador AST de SQL que bloqueia qualquer comando de mutação (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `GRANT`, `TRUNCATE`), aceitando exclusivamente `SELECT` e injetando obrigatoriamente o filtro `tenant_id` e o escopo RBAC do solicitante.
  3. Executar na conexão de leitura (`get_read_db`), formatar o resumo executivo via LiteLLM e retornar a série de dados pronta para gráfico.
- **DoD:** Consultas em linguagem natural respondidas em $< 3\text{ s}$; proteção $100\%$ determinística contra SQL Injection e comandos destrutivos; respeito absoluto ao escopo hierárquico.
- **TDD:** Testar pergunta legítima (*"Qual o total faturado em implantes Cone Morse por regional?"*); testar tentativa maliciosa de prompt injection pedindo `SELECT * FROM users; DROP TABLE deals;` e validar bloqueio imediato pelo parser AST.
- **Target Files:** `src/features/intelligence/text_to_sql_agent.py`, `src/features/intelligence/router.py`, `tests/test_text_to_sql_security.py`
- **Validation Command:** `python -m pytest tests/test_text_to_sql_security.py -q`
- **Blocked by:** TICKET-03, TICKET-29

#### [TICKET-31] [x] DONE - Motor Matemático de Score de Ociosidade de Kit Consignado ($SOK$) e Ponto de Reposição ($PR$)
- **Descrição:** Implementação dos algoritmos preditivos de estoque e consignação (`src/features/intelligence/predictive_inventory.py`) que calculam diariamente o **Score de Ociosidade de Kit ($SOK$)** e o **Ponto de Reposição ($PR$)** para cada parceiro, gerando ações automáticas no Kanban, no KeyPartners e no DENTGO.
- **Como Implementar (Detalhes Técnicos):**
  1. Implementar a equação determinística do Score de Ociosidade de Kit Consignado ($SOK$):
     $$SOK = \left( \frac{D_{\text{sem\_cirurgia}}}{D_{\text{limite\_contratual}}} \right) \times 0.6 + \left( \frac{V_{\text{kit\_imobilizado}}}{V_{\text{faturamento\_medio\_mensal}}} \right) \times 0.4$$
     Quando $SOK \ge 1.0$, abrir tarefa crítica para o consultor externo e sugerir ordem de coleta reversa no **DENTGO**.
  2. Implementar a equação do Ponto de Reposição ($PR$):
     $$PR = (C_{\text{medio\_diario}} \times T_{\text{entrega\_dentgo}}) + ES$$
     Quando o saldo do cirurgião no `kp_custody_ledger` atingir $PR$, criar Deal pré-preenchido no funil de *Recompra Ativa* e enviar mensagem de aprovação em 1 clique no WhatsApp da clínica.
- **DoD:** Execução exata das fórmulas matemáticas; geração autônoma de oportunidades de reabastecimento e ordens de recolhimento de kits ociosos.
- **TDD:** Testar cálculo de $SOK$ para clínica com 60 dias sem cirurgia (limite 30 dias) e kit de R\$ 20.000 com faturamento médio de R\$ 5.000 ($SOK = 1.2 + 1.6 = 2.8 \ge 1.0$), validando disparo da sugestão de coleta no DENTGO; testar cálculo de $PR$ e criação automática do Deal de recompra.
- **Target Files:** `src/features/intelligence/predictive_inventory.py`, `src/features/intelligence/service.py`, `src/features/intelligence/router.py`, `tests/test_predictive_sok_pr_math.py`
- **Validation Command:** `python -m pytest tests/test_predictive_sok_pr_math.py -q`
- **Blocked by:** TICKET-17, TICKET-21

#### [TICKET-32] [x] DONE - Calculadora de Margem Líquida Real por Procedimento Clínico (Módulo para Clínicas e Franquias)
- **Descrição:** Implementação do motor de engenharia financeira clínica (`src/features/intelligence/clinical_margin.py`) para que consultórios e redes de franquias calculem o lucro líquido real de cada cirurgia realizada:
  $$\text{Margem Líquida} = V_{\text{procedimento}} - (C_{\text{insumos\_keypartners\_dentgo}} + C_{\text{honorario\_cirurgiao}} + C_{\text{hora\_cadeira}} + C_{\text{imposto}})$$
- **Como Implementar (Detalhes Técnicos):**
  1. Cruzar automaticamente o custo real dos implantes e biomateriais baixados no KeyPartners/DENTGO naquela cirurgia com o valor cobrado do paciente, os honorários do implantodontista, o custo fixo de hora-clínica da cadeira e a alíquota de imposto.
  2. Exibir alerta no dashboard quando um procedimento ou convênio apresentar margem líquida $< 15\%$.
- **DoD:** Visão exata da rentabilidade por cirurgia e por cadeira clínica; integração automática com o custo dos lotes consumidos.
- **TDD:** Registrar cirurgia de protocolo cobrada a R\$ 12.000 com consumo de 4 implantes + 4 minipilares (R\$ 1.800), prótese laboratorial (R\$ 2.200), honorário (R\$ 2.500), 4 horas de cadeira (R\$ 800) e imposto de $10\%$ (R\$ 1.200); validar margem líquida exata de R\$ 3.500,00 ($29.17\%$).
- **Target Files:** `src/features/intelligence/clinical_margin.py`, `src/features/intelligence/router.py`, `tests/test_clinical_procedure_margin.py`
- **Validation Command:** `python -m pytest tests/test_clinical_procedure_margin.py -q`
- **Blocked by:** TICKET-17, TICKET-29

---

### FASE 7: Camada de Growth & RevNault (Health Score HSC, Moeda Cirúrgica, MGM & Reativação Cal.com)

#### [TICKET-33] [x] DONE - Motor Determinístico de Health Score Cirúrgico ($HSC$) e Prevenção Ativa de Churn
- **Descrição:** Implementação do motor de saúde da conta (`src/features/intelligence/health_score_hsc.py`) calculando continuamente o **Health Score Cirúrgico ($HSC$)** de cada cirurgião/clínica parceira:
  $$HSC = 0.4 \cdot F_{\text{cirurgica}} + 0.3 \cdot G_{\text{consignado}} + 0.2 \cdot S_{\text{atendimento}} + 0.1 \cdot E_{\text{canal}}$$
- **Como Implementar (Detalhes Técnicos):**
  1. Calcular $F_{\text{cirurgica}}$ penalizando desvios padrão $> +1.5\sigma$ no intervalo entre cirurgias; $G_{\text{consignado}}$ pelo giro do estoque KeyPartners; $S_{\text{atendimento}}$ pelas notas CSAT e ausência de RMAs no CX; e $E_{\text{canal}}$ pelo tempo de resposta no WhatsApp.
  2. Disparar playbook autônomo por faixa:
     * $HSC < 40$ (**Risco Crítico**): Cria tarefa presencial urgente para o consultor externo, notifica o gerente regional e gera um voucher de **Frete Express Grátis no DENTGO** enviado no WhatsApp para destravar a próxima cirurgia.
     * $HSC > 75$ (**Conta Promotora**): Habilita elegibilidade para *upsell* de fluxo digital (scanners/kits guiados) e convite do programa de indicação MGM.
- **DoD:** Atualização automática do $HSC$ a cada evento cirúrgico ou via worker diário; execução comprovada dos playbooks de retenção e expansão.
- **TDD:** Simular cirurgião cujo intervalo entre cirurgias subiu de 7 para 35 dias e abriu 2 queixas técnicas ($HSC = 28$); validar geração automática da tarefa de resgate e emissão do voucher no DENTGO.
- **Target Files:** `src/features/intelligence/health_score_hsc.py`, `src/features/intelligence/service.py`, `src/features/intelligence/router.py`, `tests/test_surgical_health_score_hsc.py`
- **Validation Command:** `python -m pytest tests/test_surgical_health_score_hsc.py -q`
- **Blocked by:** TICKET-21, TICKET-27, TICKET-31

#### [TICKET-34] [x] DONE - Programa de Fidelidade "Moeda Cirúrgica" (KeyPartners Loyalty Engine)
- **Descrição:** Implementação do razão de pontos e recompensas técnicas (`src/features/keypartners/loyalty_engine.py`) onde cada implante faturado, lote consignado conciliado no prazo ou caso clínico publicado gera **Moedas Cirúrgicas** resgatáveis por abatimento na locação de motores, kits de cirurgia guiada, créditos de entrega expressa no **DENTGO** e inscrições em imersões.
- **Como Implementar (Detalhes Técnicos):**
  1. Criar tabelas `kp_loyalty_wallets`, `kp_loyalty_transactions` e `kp_loyalty_rewards_catalog`.
  2. Creditar pontos automaticamente ao receber os eventos `deal.won` e `keypartners.postop_reported`, classificando automaticamente o parceiro nos tiers `SILVER`, `GOLD` e `BLACK_KOL`.
  3. Permitir resgate direto no checkout do DENTGO ou na tela do Deal.
- **DoD:** Razão de pontos auditável e livre de saldo negativo; progressão automática de tier; resgate abatendo valores de frete express ou equipamentos.
- **TDD:** Faturar 30 implantes para um cirurgião, validar progressão de `SILVER` para `GOLD`, acumular pontos e executar resgate de 1 voucher de frete express no DENTGO.
- **Target Files:** `src/features/keypartners/loyalty_engine.py`, `src/features/keypartners/schemas.py`, `src/features/keypartners/router.py`, `tests/test_surgical_loyalty_engine.py`
- **Validation Command:** `python -m pytest tests/test_surgical_loyalty_engine.py -q`
- **Blocked by:** TICKET-18, TICKET-22, TICKET-33

#### [TICKET-35] [x] DONE - Loop Viral de Indicação B2B (Member-Get-Member Cirúrgico entre Colegas de Pós/CRO)
- **Descrição:** Implementação do motor de indicação estruturada (`src/features/campaigns/referral_mgm.py`) que transforma cirurgiões com $HSC > 75$ e CSAT alto em recrutadores ativos de novos colegas implantodontistas, recompensando ambos com créditos em implantes/insumos após a positivação da primeira cirurgia do indicado.
- **Como Implementar (Detalhes Técnicos):**
  1. Gerar links únicos rastreáveis (`/r/{referral_code}`) para cirurgiões promotores e disparar convite personalizado no WhatsApp assinado pelo consultor da conta.
  2. Quando o colega indicado preenche o formulário validando seu CRO/UF (TICKET-06), criar o Lead no Mautic/RevNault com score acelerado (+40 pts) e tag `origem_indicacao_kol`.
  3. Escutar o evento `deal.won` do primeiro pedido do indicado e creditar automaticamente o bônus em **Moedas Cirúrgicas / Crédito de Implantes** para o indicador e para o indicado.
- **DoD:** Rastreamento de ponta a ponta do indicador ao indicado; prevenção contra auto-indicação (mesmo CPF/CRO/CNPJ); liberação condicional do bônus somente após faturamento real.
- **TDD:** Gerar código MGM para o Dr. Marcos (CRO-SP 11111); cadastrar Dr. Lucas (CRO-SP 22222) usando o código; fechar o primeiro Deal do Dr. Lucas e validar crédito automático de R\$ 600 em bonificação para ambos.
- **Target Files:** `src/features/campaigns/referral_mgm.py`, `src/features/campaigns/router.py`, `tests/test_b2b_referral_mgm_loop.py`
- **Validation Command:** `python -m pytest tests/test_b2b_referral_mgm_loop.py -q`
- **Blocked by:** TICKET-06, TICKET-33, TICKET-34

#### [TICKET-36] [x] DONE Motor de Agendamento Inteligente Cal.com e Loop de Reativação Preventiva de Pacientes (6/12/18m)
- **Status:** [x] CONCLUIDO (222/222 testes aprovados, cobertura 100% dos fluxos de reativação 180/365/540d, webhook BOOKING_CREATED e LiveKit room generation).
- **Descrição:** Integração do motor open-source **Cal.com** (`src/features/automations/calcom_reactivation.py`) para agendamento sem fricção de consultorias técnicas B2B (visitas de representantes/demonstração de scanners) e **Loops de Reativação B2C** de pacientes que instalaram próteses sobre implante há 6, 12 ou 18 meses para profilaxia e manutenção da garantia peri-implantar.
- **Como Implementar (Detalhes Técnicos):**
  1. Implementar adaptador para a API do Cal.com sincronizando agendas dos consultores e cadeiras das clínicas, gerando links dinâmicos de sala do **LiveKit** quando o agendamento for teleconsulta/reunião online.
  2. Criar worker diário que identifica procedimentos cirúrgicos que completaram $180$, $365$ ou $540\text{ dias}$, dispara mensagem humanizada via WhatsApp (Evolution API) em nome do cirurgião e envia o link de agendamento direto do Cal.com.
  3. Processar o webhook `BOOKING_CREATED` do Cal.com criando a tarefa/compromisso no RevNault e confirmando via WhatsApp.
- **DoD:** Sincronização bidirecional de horários; conversão automática de pacientes dormentes em agendamentos confirmados na agenda da clínica.
- **TDD:** Simular paciente cuja cirurgia de protocolo completou 180 dias hoje; validar disparo da mensagem de manutenção preventiva com link Cal.com; simular webhook `BOOKING_CREATED` e confirmar criação do agendamento e Deal de manutenção.
- **Target Files:** `src/features/automations/calcom_reactivation.py`, `src/features/automations/router.py`, `src/features/webhooks/router.py`, `docker-stack.yml`, `tests/test_calcom_patient_reactivation.py`
- **Validation Command:** `python -m pytest tests/test_calcom_patient_reactivation.py -q`
- **Blocked by:** TICKET-11, TICKET-23, TICKET-28

#### [TICKET-37] [x] DONE Liquidação Inteligente FEFO de Lotes com Validade Curta via Flash Deals no DENTGO
- **Status:** [x] CONCLUIDO (226/226 testes aprovados, cobertura 100% do motor FEFO 6-9 meses, segmentação geolocalizada Haversine 50km, disparo WhatsApp 1-clique e reserva atômica de lotes). **(FASE 7 100% Concluída)**.
- **Descrição:** Implementação do motor anti-perda de estoque (`src/features/dentgo/fefo_flash_deals.py`) que monitora lotes de implantes e biomateriais nos Hubs/CDs com validade esterilizante residual entre $6$ e $9\text{ meses}$ (*First-Expired, First-Out - FEFO*) e dispara ofertas relâmpago segmentadas no WhatsApp e no topo do app **DENTGO** para cirurgiões de alto giro daquela exata conexão protética.
- **Como Implementar (Detalhes Técnicos):**
  1. Varredura automática no `dentgo_hub_inventory` e `kp_custody_ledger` identificando lotes na janela de alerta FEFO.
  2. Cruzar no `pgvector`/PostgreSQL os 50 cirurgiões num raio de $50\text{ km}$ que mais consomem aquela medida de implante/biomaterial e disparar campanha *Flash Deal* via Mautic/Evolution API com link de checkout em 1 clique no DENTGO.
- **DoD:** Transformação de potenciais descartes contábeis de lotes prestes a vencer em liquidez imediata; reserva atômica do lote no momento do clique.
- **TDD:** Inserir lote de 20 membranas de colágeno vencendo em 7 meses no Hub Campinas; rodar motor FEFO e validar geração da oferta promocional direcionada apenas aos cirurgiões de Campinas que consomem biomateriais.
- **Target Files:** `src/features/dentgo/fefo_flash_deals.py`, `src/features/dentgo/router.py`, `tests/test_dentgo_fefo_flash_deals.py`
- **Validation Command:** `python -m pytest tests/test_dentgo_fefo_flash_deals.py -q`
- **Blocked by:** TICKET-08, TICKET-19

---

### FASE 8: Camada de Desenvolvimento, Plataforma & Conectores Plug-and-Play (Windmill, Orthanc DICOM & ERPs)

#### [TICKET-38] [x] DONE Hub de Orquestração Windmill e Conector Fiscal ERP (TOTVS Protheus, SAP B1 & Sankhya) para Consignação
- **Status:** [x] CONCLUIDO (231/231 testes aprovados, cobertura 100% do conector fiscal ERP polimórfico TOTVS Protheus, SAP B1 e Sankhya, emissão determinística CFOP 5.917/6.917 remessa, 1.918/2.918 retorno simbólico, 5.113/6.113 venda consignada, guarda XML/DANFE PDF no R2 e rotas de auditoria).
- **Descrição:** Integração do motor open-source **Windmill** (Rust/Go) em `src/features/integrations/totvs/` e `src/features/integrations/erp_hub/` para orquestrar os fluxos fiscais e contábeis de consignação cirúrgica com ERPs industriais: emissão automática de **NF-e de Remessa em Consignação (CFOP 5.917 / 6.917)**, **Retorno Simbólico (CFOP 1.918 / 2.918)** e **NF-e de Venda de Material Consignado (CFOP 5.113 / 6.113)**.
- **Como Implementar (Detalhes Técnicos):**
  1. Expandir `src/features/integrations/totvs/adapter.py` e criar interface padrão `BaseERPConnector` suportando TOTVS Protheus, SAP Business One e Sankhya acionados via workers do Windmill.
  2. Quando uma remessa é aprovada no KeyPartners (TICKET-17), disparar job no Windmill que emite a NF-e de Remessa (`CFOP 5.917/6.917`), salva o XML e o DANFE em PDF no **Cloudflare R2** e anexa ao pedido do DENTGO/KeyPartners.
  3. Quando o reporte pós-cirúrgico é concluído, disparar job que emite o retorno simbólico e fatura a NF-e de Venda (`CFOP 5.113/6.113`) exclusivamente sobre os lotes implantados.
- **DoD:** Emissão e conciliação fiscal $100\%$ automatizada de remessa, retorno e venda consignada; guarda de XML/DANFE no R2 por 5 anos fiscais; re-tentativas automáticas via Windmill se a SEFAZ ou o ERP oscilar.
- **TDD:** Simular aprovação de remessa no KeyPartners e validar payload fiscal `CFOP 5917` enviado ao conector ERP e armazenamento do XML/PDF no R2; simular baixa pós-cirúrgica e validar emissão do `CFOP 5113`.
- **Target Files:** `src/features/integrations/totvs/adapter.py`, `src/features/integrations/totvs/service.py`, `src/features/integrations/totvs/router.py`, `src/features/integrations/erp_hub/windmill_client.py`, `docker-stack.yml`, `tests/test_erp_consignment_cfop_flow.py`
- **Validation Command:** `python -m pytest tests/test_erp_consignment_cfop_flow.py -q`
- **Blocked by:** TICKET-01, TICKET-05, TICKET-17

#### [TICKET-39] [x] DONE Servidor de Imagiologia Médica Orthanc DICOM e Visualizador 3D de Tomografias / STL no R2
- **Status:** [x] CONCLUIDO (236/236 testes aprovados, cobertura 100% do Orthanc DICOM, presigned URLs R2, anonimização LGPD, tokens temporários HMAC-SHA256, medição óssea anatômica e componente DicomStl3DViewer sem emojis).
- **Descrição:** Implementação do módulo de imagiologia odontológica (`src/features/intelligence/orthanc_dicom.py` e `frontend/src/features/imaging/DicomStl3DViewer.tsx`) integrando o **Orthanc DICOM Server** conectado ao **Cloudflare R2** para upload, indexação e visualização 3D no navegador de Tomografias Computadorizadas Cone Beam (`.dcm`) e escaneamentos intraorais (`.stl`/`.ply`) diretamente na ficha do Deal, do Planejamento de Cirurgia Guiada ou do Ticket de Suporte Cirúrgico.
- **Como Implementar (Detalhes Técnicos):**
  1. Configurar serviço Orthanc no `docker-stack.yml` com plugin S3 apontando para o bucket do Cloudflare R2 (evitando ocupar disco local da VPS com exames de $300\text{ MB}+$).
  2. Implementar endpoints `POST /api/v1/imaging/studies/upload-presign` e `GET /api/v1/imaging/studies/{study_id}/viewer-token` com anonimização opcional de tags DICOM sensíveis (LGPD).
  3. Implementar o componente React `<DicomStl3DViewer />` (Cornerstone3D / Three.js) e manter paridade em `dicom-stl-viewer.js` para que o consultor técnico e o cirurgião meçam espessura óssea em milímetros e planejem o diâmetro do implante juntos.
- **DoD:** Upload direto de arquivos DICOM e STL para o R2; renderização fluida no navegador autenticada por token temporário; vínculo direto do exame com o Deal ou Ticket de Cosmovigilância ANVISA.
- **TDD:** Registrar estudo DICOM/STL vinculado a um caso de cirurgia guiada, validar geração de URL assinada no R2, verificar metadados anatômicos da arcada e testar bloqueio de acesso por usuário de outro tenant.
- **Target Files:** `src/features/intelligence/orthanc_dicom.py`, `src/features/intelligence/router.py`, `frontend/src/features/imaging/DicomStl3DViewer.tsx`, `docs/reconstruct_revnault/05_reconstructed_app/js/modules/dicom-stl-viewer.js`, `docker-stack.yml`, `tests/test_orthanc_dicom_stl_r2.py`
- **Validation Command:** `python -m pytest tests/test_orthanc_dicom_stl_r2.py -q`
- **Blocked by:** TICKET-01, TICKET-27

#### [TICKET-40] [x] DONE Motor de Webhooks Outbound Plug-and-Play com Assinatura Criptográfica HMAC-SHA256
- **Status:** [x] CONCLUIDO (241/241 testes aprovados, cobertura 100% de assinaturas HMAC-SHA256, proteção estrita anti-SSRF, circuit breaker após 15 falhas consecutivas, persistência de logs de auditoria e schemas Pydantic tipados).
- **Descrição:** Evolução de `src/features/webhooks/` para oferecer um **Portal de Desenvolvedores & Webhooks Outbound** onde indústrias, laboratórios de prótese e clínicas cadastram URLs externas para receber eventos em tempo real do ecossistema (`deal.won`, `keypartners.custody_changed`, `dentgo.order_delivered`, `cx.surgical_sos_triggered`, `growth.hsc_critical`) assinados com cabeçalho `X-RevNault-Signature: sha256=...`.
- **Como Implementar (Detalhes Técnicos):**
  1. Criar tabelas `webhook_subscriptions` (`id`, `tenant_id`, `target_url`, `subscribed_events_json`, `signing_secret_encrypted`, `is_active`) e `webhook_delivery_logs`.
  2. Consumir todos os eventos do Redis Streams (TICKET-02), assinar o payload JSON com `hmac.new(secret, payload_bytes, hashlib.sha256).hexdigest()` e despachar com timeout de $5\text{ s}$ e retentativas automáticas com *circuit breaker* (desativando a assinatura após 15 falhas consecutivas e avisando o administrador).
- **DoD:** Assinatura HMAC-SHA256 verificável; log completo de status HTTP, latência em ms e payload de resposta; proteção contra SSRF (bloqueando chamadas para IPs internos `127.0.0.1`, `10.x.x.x`, `192.168.x.x`).
- **TDD:** Cadastrar webhook para `dentgo.order_delivered`, disparar evento, validar que o cabeçalho `X-RevNault-Signature` bate exatamente com o cálculo HMAC-SHA256 e testar bloqueio de URL apontando para `http://127.0.0.1:8000` (prevenção SSRF).
- **Target Files:** `src/features/webhooks/outbound_dispatcher.py`, `src/features/webhooks/schemas.py`, `src/features/webhooks/router.py`, `tests/test_outbound_webhooks_hmac.py`
- **Validation Command:** `python -m pytest tests/test_outbound_webhooks_hmac.py -q`
- **Blocked by:** TICKET-02, TICKET-05

#### [TICKET-41] [x] DONE Unificação do Cockpit Odontológico 360° (React 19 + TypeScript SPA) e Sincronia Estrita de Contratos
- **Status:** [x] CONCLUIDO (AppRouter integrado no React 19 com as 6 suítes verticais, api_contracts.ts sincronizado 1:1 com FastAPI, 3/3 testes de sincronia de contratos aprovados, conformidade estrita com a Lei #14).
- **Descrição:** Consolidação de todas as features em fatias verticais na aplicação principal **React 19 + TypeScript + TanStack Query + shadcn/ui** (`frontend/src/App.tsx`), garantindo paridade visual nos ativos de auditoria (`docs/reconstruct_revnault/05_reconstructed_app/`) e sincronização $1:1$ dos contratos tipados em `api_contracts.ts`.
- **Como Implementar (Detalhes Técnicos):**
  1. Integrar no roteador tipado do React (`frontend/src/router.tsx`) todas as 6 suítes (Marketing GrapesJS/Mautic, Vendas + Copiloto Granola, KeyPartners Consignados, DENTGO Express, CX Chatwoot/SOS LiveKit e BI Superset/DICOM 3D) utilizando os primitivos do Design System e respeitando o RBAC Dual.
  2. Atualizar `docs/reconstruct_revnault/02_decompiled/api_contracts.ts` e `frontend/src/types/api_contracts.ts` com todas as interfaces e rotas criadas nos Tickets 00 a 40 para manter paridade estrita exigida pelo `test_api_contracts_sync.py`.
- **DoD:** Interface com estética definitiva de produção (Desktop Multi-Monitor para Inside Sales/Diretoria e Mobile-First PWA para Consultores de Campo/Cirurgiões/Couriers DENTGO); $100\%$ de sincronia entre rotas FastAPI e `api_contracts.ts`.
- **TDD:** Executar a suíte de sincronia de contratos (`test_api_contracts_sync.py`) e validar que todas as rotas do backend possuem definição correspondente e tipada.
- **Target Files:** `frontend/src/App.tsx`, `frontend/src/router.tsx`, `frontend/src/types/api_contracts.ts`, `docs/reconstruct_revnault/02_decompiled/api_contracts.ts`, `docs/reconstruct_revnault/05_reconstructed_app/index.html`, `docs/reconstruct_revnault/05_reconstructed_app/js/app.js`, `tests/test_api_contracts_sync.py`
- **Validation Command:** `python -m pytest tests/test_api_contracts_sync.py -q`
- **Blocked by:** TICKET-00, TICKET-07, TICKET-11, TICKET-17, TICKET-20, TICKET-24, TICKET-29, TICKET-39, TICKET-40

#### [TICKET-42] [x] DONE Orquestração do Cluster Docker Swarm (100 a 1.000 Consultores), Manuais e Auditoria Final dos 11 Gates AIDD
- **Status:** [x] CONCLUIDO (Cluster multi-serviço Docker Swarm/Compose completo com limites de CPU/RAM, redes segregadas edge/app/data, healthchecks, snapshot e streaming WAL com retenção para Cloudflare R2, 245/245 testes aprovados e 100% de aprovação nos 14 Quality Gates).
- **Descrição:** Atualização completa do `docker-stack.yml` para suportar a topologia de produção multi-nó (Contabo VPS/VDS + Cloudflare R2), atualização dos manuais operacionais em `docs/manuais/` para refletir todas as novas rotas e aprovação limpa nos 11 Gates de Qualidade e Segurança do repositório.
- **Como Implementar (Detalhes Técnicos):**
  1. Estruturar o `docker-stack.yml` com limites explícitos de CPU/RAM (`deploy.resources.limits`), healthchecks e redes overlay segregadas (`revnault_edge`, `revnault_app`, `revnault_data`) para Traefik, Frontend React/Nginx, FastAPI Core Async, Workers Redis, Evolution API Shards, Chatwoot, Mautic, Listmonk, LiveKit, Documenso, Superset, Cal.com, Windmill, Orthanc, PostgreSQL 16 (Primary + Read Replica) e Redis 7.
  2. Atualizar os manuais em `docs/manuais/` e o índice `docs/manuais/README.md` documentando as novas rotas de KeyPartners, DENTGO, Copiloto Granola, Storage R2, Superset e Orthanc para passar no gate `G_MANUAIS_ROTAS.py`.
  3. Executar a bateria completa de testes `pytest` e todos os scripts em `gates/G_*.py`.
- **DoD:** `pytest` $100\%$ verde em toda a suíte do sistema; aprovação binária (`PASS`) nos 11 gates de auditoria (`G_BLOQUEAR_SEGREDOS`, `G_CONTRACTS`, `G_CYBERSECURITY_OWASP`, `G_DETERMINISMO_LEI_1`, `G_ESTRUTURA_AST`, `G_HARNESS_COMPAT`, `G_INJECT`, `G_MANUAIS_ROTAS`, `G_PERFORMANCE`, `G_QUARTETO_SINE_QUA_NON`, `G_STACK_PADRAO_OURO`, `G_TESTES_REAIS`).
- **TDD:** Rodar suíte global de testes e script verificador de todos os gates determinísticos sem nenhum warning ou violação arquitetural.
- **Target Files:** `docker-stack.yml`, `.env.example`, `docs/manuais/README.md`, `scripts/audit_rotas_manuais.py`, `gates/G_MANUAIS_ROTAS.py`, `gates/G_CONTRACTS.py`
- **Validation Command:** `python -m pytest -q && python gates/G_SAIDA_BINARIA.py`
- **Blocked by:** TICKET-41

---

## PARTE 6: Mapa de Dependências de Execução (Ordem Crítica)

```
[FASE 0: EVOLUÇÃO DA STACK & FUNDAÇÃO]
  TICKET-00 (SQLAlchemy 2.0 Async + Alembic + React 19/TS/shadcn + tokens.css)
      │
      └──> TICKET-01 (Cloudflare R2) ──┬──> TICKET-02 (Redis Streams) ──> TICKET-04 (RBAC Dual Field/Inside)
                                       ├──> TICKET-03 (Postgres 16 + pgvector)
                                       └──> TICKET-05 (Traefik + Vault AES-256)
                                                       │
[FASE 1: MARKETING]                                    ▼
  TICKET-06 (CRO/CFO) ──> TICKET-07 (GrapesJS LP) ──> TICKET-08 (Mautic Bridge) ──> TICKET-09 (Listmonk) ──> TICKET-10 (Lead Scoring)
                                                       │
[FASE 2: VENDAS & IA]                                  ▼
  TICKET-11 (LiveKit VoIP/Meet) ──> TICKET-12 (faster-whisper + PyAnnote) ──> TICKET-13 (Copiloto Granola)
  TICKET-14 (Catálogo & Alçadas) ──> TICKET-15 (Documenso WhatsApp)
                                                       │
[FASE 3: KEYPARTNERS]                                  ▼
  TICKET-16 (Custódia & Lotes ANVISA) ──> TICKET-17 (Ciclo Pós-Cirúrgico) ──> TICKET-18 (Gestão KOLs)
                                                       │
[FASE 4: DENTGO]                                       ▼
  TICKET-19 (Hubs & Geolocalização) ──> TICKET-20 (Despacho & Lacre R2) ──> TICKET-21 (Sinergia KeyPartners) ──> TICKET-22 (Split Financeiro)
                                                       │
[FASE 5: CX & SUPORTE]                                 ▼
  TICKET-23 (Evolution Cluster) ──> TICKET-24 (Chatwoot 360°) ──> TICKET-25 (Vídeo SOS Cirúrgico)
                                                              ├──> TICKET-26 (RAG Catálogo Técnico)
                                                              ├──> TICKET-27 (Cosmovigilância ANVISA)
                                                              └──> TICKET-28 (Régua Pós-Op B2C)
                                                       │
[FASE 6: BI & ANALYTICS]                               ▼
  TICKET-29 (Superset Embedded RLS) ──> TICKET-30 (Agente Text-to-SQL)
  TICKET-31 (Predição SOK e PR)     ──> TICKET-32 (Margem Líquida Clínica)
                                                       │
[FASE 7: GROWTH & RevNault]                              ▼
  TICKET-33 (Health Score HSC) ──> TICKET-34 (Moeda Cirúrgica) ──> TICKET-35 (Loop Indicação MGM)
  TICKET-36 (Cal.com Reativação) & TICKET-37 (Flash Deals FEFO no DENTGO)
                                                       │
[FASE 8: PLATAFORMA & GATES]                           ▼
  TICKET-38 (Windmill ERP TOTVS/SAP) ──> TICKET-39 (Orthanc DICOM 3D) ──> TICKET-40 (Webhooks HMAC) ──> TICKET-41 (Cockpit React 19 Sync) ──> TICKET-42 (Cluster & Gates)
```