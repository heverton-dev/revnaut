Aqui está a **Auditoria Técnica Linha-a-Linha** dos artefatos reais anexados e o **Plano de Ação Faseado em Micro-Tickets Cirúrgicos** para execução no **Antigravity**, desenhado para convergir o **Caminho A** (maturidade imediata do Monólito Modular VSA sem peso local) com o **Caminho B** (acoplamento tipado fim-a-fim e orquestração *Headless Open-Source* de alta performance), elevando o **RevNault Dental Ops** acima de HubSpot, Salesforce e RD Station no nicho industrial odontológico.

# PARTE 1: Auditoria Linha-a-Linha (Sem Filtros)

## 1. `backend/main.py` — Proxy de Retrocompatibilidade VSA

- **Linhas 1–9:** `from src.main import app` e `from src.core.database import get_connection, init_db`.  
- **Diagnóstico Técnico:** Excelente decisão arquitetural. Você já iniciou a transição para **Vertical Slice Architecture (VSA)** em `src/main.py` e `src/features/auth/`, mantendo `backend/main.py` apenas como *shim* de retrocompatibilidade para não quebrar scripts de deploy ou testes legados.   
- **Gap Detectado:** Apesar de `backend/main.py` apontar para `src.core.database`, o arquivo `backend/database.py` ainda contém DDL e seeds próprios apontando para `data/revnault.db`, enquanto o `STATUS_RETOMADA_PROXIMA_SESSAO.md` cita `data/revnault.db` / `data/revnault.db`. Essa dualidade de bancos (`revnault.db` vs `revnault.db`) e de módulos (`backend/database.py` vs `src/core/database.py`) é uma armadilha clássica para agentes de IA editarem o arquivo errado.   

## 2. `backend/database.py` — Motor SQLite WAL vs. Especificação RBAC

- **Linhas 12–21 (**`get_connection`**):** Configuração de `PRAGMA journal_mode=WAL;`, `PRAGMA synchronous=NORMAL;` e `PRAGMA foreign_keys=ON;` com `timeout=10.0`.  
  - **Ponto Forte:** Para um ambiente de desenvolvimento no **Antigravity** e até mesmo para um monólito em VPS única, o SQLite em modo WAL é **extremamente rápido** (leituras concorrentes em microssegundos sem latência de rede TCP e 0MB de overhead de container de banco).
  - **Bug Silencioso de Concorrência (Linha 17):** Falta `check_same_thread=False` ou um pool/context manager por request com `PRAGMA busy_timeout = 5000;` explícito no nível do SQLite. Sob disparos simultâneos de webhooks (Evolution API + Mautic), threads do Uvicorn podem colidir se uma transação de escrita demorar.   
- **Linhas 24–129 (DDL Legado vs.** `SPEC_RBAC_DATA_SCOPING_HIERARQUICO.md`**):**
  - **Conflito de Schema #1 (**`users`**):** Na linha 33 de `database.py`, `users` tem apenas `(id, account_id, name, email, role, created_at)`. Já a sua `SPEC_RBAC` (Linhas 78–93) exige `(team_id, role_id, phone, custom_data_scope, is_active, is_superadmin)`.   
  - **Conflito de Schema #2 (**`contacts` **e** `deals`**):** Nas linhas 58–86 de `database.py`, nem `contacts` nem `deals` possuem as colunas `owner_id`, `team_id` e os metadados odontológicos (`cro`, `uf`, `specialty`, `clinic_name`, `monthly_implant_volume`). Sem `owner_id` e `team_id` indexados nas tabelas `deals`, `contacts` e `conversations`, **a Invariante #4 e #5 da sua** `SPEC_RBAC` **(Linhas 126–128) não consegue filtrar dados por equipe ou subárvore (**`WITH RECURSIVE`**)**.   
  - **Conflito de Seed (Linhas 135–143):** O seed de `database.py` ainda injeta `'Sales Rocket'` / `'Thiago Hortolan'` e deals genéricos de AgroTech/Fintech, enquanto o `STATUS_RETOMADA` estabelece a **Invariante Inviolável** de que apenas `hevertoneduardoperes@gmail.com` é o Super Admin (`is_superadmin = 1`) e o domínio é 100% **Dental Ops**.   

## 3. `SPEC_RBAC_DATA_SCOPING_HIERARQUICO.md` — Engenharia de Permissão

- **Linhas 31–76 (**`business_units`**,** `teams`**,** `roles`**,** `role_permissions`**):** Modelagem limpa, enxuta e sem dependência de libs pesadas (Casbin/OPA).   
- **Ponto Crítico de Performance (Linha 126 —** `WITH RECURSIVE team_tree`**):** A resolução de subárvore via CTE recursiva no SQLite é instantânea (< 0.2ms), **desde que** existam índices compostos:
  - Falta no DDL da Spec: `CREATE INDEX IF NOT EXISTS idx_teams_parent ON teams(account_id, parent_id);` e `CREATE INDEX IF NOT EXISTS idx_deals_scoping ON deals(account_id, team_id, owner_id);`. Sem esses índices, cada listagem de Kanban fará *Full Table Scan*.

## 4. `api_contracts.ts` — Contratos Descompilados vs. Domínio Odontológico

- **Linhas 6–170:** Os contratos estão muito bem tipados, mas refletem o legado genérico da RevNault (`UserRole` matricial fixa nas linhas 26–51, `Contact` sem CRO/Especialidade nas linhas 60–73).   
- **Oportunidade Caminho B:** Atualizar `api_contracts.ts` para ser a **Fonte Única de Verdade (Single Source of Truth)** sincronizada com os schemas Pydantic de `src/features/`, gerando validação automática para o Frontend sem precisar de um build pesado de Next.js.

## 5. `open_source_architecture.md` — A Estratégia "Under the Hood"

- **Diagnóstico Realista de Recursos (Ambiente Antigravity vs. VPS):**
  - Subir **Mautic 5 (PHP-FPM + MySQL/MariaDB) + Chatwoot (Rails + Sidekiq + Postgres + Redis) + Evolution API (Node/Baileys)** juntos no ambiente de desenvolvimento local vai consumir **4.5 GB a 6 GB de RAM** e travar a fluidez do Antigravity.   
  - **Como grandes empresas resolvem isso (e como faremos):** No código do **RevNault (**`src/features/integrations/`**)**, aplicamos o padrão **Ports & Adapters (Hexagonal) com Strategy Pattern**.
    - **Em Dev/Test no Antigravity (**`ENV=local`**):** O RevNault usa `LocalMockAdapter` (em memória/SQLite WAL), respondendo em **1ms**, gastando **0MB de RAM extra** e permitindo rodar os 59+ testes do `pytest` em menos de 2 segundos.   
    - **Em Produção na VPS (**`ENV=production` **no Swarm):** As variáveis de ambiente apontam para as URLs reais do Chatwoot, Evolution API, Mautic e TOTVS Protheus via HTTP assíncrono (`httpx` + Webhooks).   

# PARTE 2: Posicionamento "Enterprise Dental Ops" (Superando HubSpot, RD e Salesforce)

Por que uma indústria como **Conexão Implantes, Neodent, Straumann, SIN ou Plenum** pagaria caro pelo **RevNault** em vez do HubSpot ou Salesforce? Porque implementaremos nativamente no core da aplicação as **5 Features Matadoras do Setor Industrial Odontológico**:   

1. **Grafo de Relacionamento Clínico ("O Ecossistema do Implante"):** Diferente de um CRM comum onde 1 Contato = 1 Empresa, na odontologia **1 Cirurgião-Dentista (CRO)** opera em **N Clínicas/Hospitais**, indica pacientes para **M Radiologias** e trabalha com **K Laboratórios de Prótese (CAD/CAM)**, além de lecionar em **Instituições de Ensino (Pós-Graduação/ABO/APCD)**. Mapear essa rede dá visibilidade de *Key Opinion Leaders (KOLs / Speakers)*.
2. **Motor de Inteligência de Carteira & Previsão de Churn (RFM Odontológico):** Algoritmo determinístico em SQL/Python que calcula a frequência de compra de componentes protéticos/implantes de cada clínica e dispara um alerta automático no Kanban/WhatsApp do Assessor Comercial quando um cirurgião que comprava a cada 20 dias passa de 30 dias sem faturar.
3. **Automação de Fluxo Digital (CAD/CAM & Scanner Intraoral SLA):** Funil e tickets dedicados para recebimento de arquivos `.STL` / `.PLY`, aprovação de desenho protético e SLA de fresagem em minutos.
4. **Governança do "Quarteto" & Comissionamento em Cascata:** Divisão nativa de metas e comissões entre *SDR (Qualificação) + Closer Interno + Assessor Técnico Externo (Campo) + Especialista Digital*, respeitando o `SPEC_RBAC_DATA_SCOPING_HIERARQUICO.md`.   

# PARTE 3: Plano de Ação Faseado (Micro-Tickets Cirúrgicos para o Antigravity)

Cada ticket abaixo segue rigorosamente a estrutura de `.agents/skills/aidd-tickets` e `aidd-tdd`: **escopo atômico, rápida execução pelo agente, zero peso no ambiente e validação binária (**`pytest` **exit code 0)**.   

## FASE 1: Saneamento do Core, Unificação SQLite WAL e RBAC Hierárquico (Caminho A)

*Objetivo: Eliminar a dualidade de bancos, implementar 100% da* `SPEC_RBAC_DATA_SCOPING_HIERARQUICO.md` *e blindar o isolamento multi-tenant/hierárquico com performance de sub-milissegundo.*

### `TICKET-01`: Unificação Canônica do Banco SQLite WAL e Tuning de Alta Concorrência

- **Contexto:** Eliminar qualquer divergência entre `backend/database.py` (`revnault.db`) e `src/core/database.py` (`revnault.db`).   
- **Ação Cirúrgica:**
  1. Transformar `backend/database.py` em um simples reexportador (`from src.core.database import get_connection, init_db, DB_PATH`), exatamente como já foi feito em `backend/main.py`.   
  2. Em `src/core/database.py`, configurar a conexão SQLite com `check_same_thread=False` e injetar os pragmas de alta performance:
    - `PRAGMA journal_mode=WAL;`
    - `PRAGMA synchronous=NORMAL;`
    - `PRAGMA busy_timeout=5000;`
    - `PRAGMA temp_store=MEMORY;`
    - `PRAGMA cache_size=-32000;` (32MB de cache em RAM, zero peso na máquina).
- **Critério de Aceite Binário:** `pytest -v` passa 100% e `backend/database.py` possui menos de 15 linhas.

### `TICKET-02`: Migração Idempotente do Schema RBAC Hierárquico & Índices de Performance

- **Contexto:** Materializar as tabelas de `SPEC_RBAC_DATA_SCOPING_HIERARQUICO.md` e adicionar as colunas de posse (`owner_id`, `team_id`) nas entidades de negócio sem perder dados existentes.   
- **Ação Cirúrgica:**
  1. Garantir no `init_db()` a criação de `business_units`, `teams`, `roles`, `role_permissions`.   
  2. Executar migração segura (`ALTER TABLE ... ADD COLUMN` verificando `PRAGMA table_info`) em `deals`, `contacts`, `conversations` para garantir `owner_id TEXT`, `team_id TEXT`, `business_unit_id TEXT`.
  3. Criar os índices compostos obrigatórios: `idx_teams_hierarchy (account_id, parent_id)`, `idx_deals_scope (account_id, team_id, owner_id)` e `idx_contacts_scope (account_id, team_id, owner_id)`.
- **Critério de Aceite Binário:** `pytest tests/test_data_scoping.py -q` retorna exit code 0.   

### `TICKET-03`: Engine de Resolução de Escopo (`WITH RECURSIVE`) e Validador Anti-Ciclo (DAG)

- **Contexto:** Atender às Invariantes #3 e #4 da `SPEC_RBAC`.   
- **Ação Cirúrgica:**
  1. Criar/refinar em `src/features/rbac/service.py` a função `build_scope_filter_sql(user_ctx: UserContext, table_alias: str) -> tuple[str, list]` que injeta automaticamente a cláusula `WHERE` correta (`self`, `team`, `subtree` via CTE recursiva, `business_unit` ou `tenant_global`).   
  2. Implementar validador de ciclo em `POST/PUT /api/v1/teams` que percorre os ancestrais de `parent_id` e retorna `HTTP 422` caso detecte parentesco circular.   
  3. Implementar o endpoint `POST /api/v1/hierarchy/presets/apply` com os 4 presets odontológicos (`fabrica_enxuta`, `nacional_expansao`, `multidivisao_produtos`, `multinacional_enterprise`) em transação atômica.   
- **Critério de Aceite Binário:** Todos os 7 Critérios Binários de Aceite de `SPEC_RBAC_DATA_SCOPING_HIERARQUICO.md` passando em `tests/test_data_scoping.py`.   

## FASE 2: Blindagem Tipada Fim-a-Fim e Zero-Bloat no Frontend (Caminho B Leve)

*Objetivo: Ter a segurança do Caminho B (TypeScript + Contratos) sem transformar o projeto num monstro lento de* `node_modules` *que trava o Antigravity.*

### `TICKET-04`: Sincronizador Automático de Contratos (`Pydantic -> api_contracts.ts` + JSDoc TypeCheck)

- **Contexto:** Como o frontend atual (`docs/reconstruct_revnault/05_reconstructed_app/js/app.js`) roda direto no navegador sem *build step* pesado, podemos ativar **100% da checagem de tipos do TypeScript** usando `// @ts-check` + JSDoc apontando para `api_contracts.ts`, ou um script Python de 50 linhas que exporta o `openapi.json` do FastAPI para atualizar `api_contracts.ts`.   
- **Ação Cirúrgica:**
  1. Atualizar `docs/reconstruct_revnault/02_decompiled/api_contracts.ts` com os novos contratos reais do RevNault Dental Ops (`UserContext`, `DataScopeEnum`, `DentalContact`, `ConsignmentBox`, `TotvsOrderPayload`, `HierarchyPreset`).   
  2. Criar um teste de contrato (`tests/test_api_contracts_sync.py`) que verifica se todas as rotas `/api/v1/*` do FastAPI possuem `response_model` tipado em Pydantic (nenhum endpoint retornando `dict` solto sem schema).
- **Critério de Aceite Binário:** `pytest tests/test_api_contracts_sync.py -q` passa com exit code 0 e o Quality Gate `G_CONTRACTS` valida 100% das rotas.   

### `TICKET-05`: Modularização ES Modules Nativa do Frontend (`js/app.js`)

- **Contexto:** Evitar que `js/app.js` vire um arquivo monolítico gigante que estoure a janela de contexto dos agentes no Antigravity.   
- **Ação Cirúrgica:**
  1. Usar **ES Modules nativos do navegador** (`<script type="module" src="/js/app.js"></script>`), que **não exigem Webpack nem Node.js rodando em background**, mantendo o ambiente instantâneo.
  2. Extrair de `js/app.js` módulos limpos sob `js/modules/`: `api-client.js` (wrapper centralizado com injeção automática do Bearer Token e tratamento de 401/403), `rbac-tree.js`, `kanban-deals.js` e `consignments.js`.
- **Critério de Aceite Binário:** Carregamento da raiz `/` em < 50ms, zero erros de console e todos os testes de UI/API verdes.

## FASE 3: Integrações "Open-Source Under the Hood" & ERP Adapter (Ports & Adapters)

*Objetivo: Conectar TOTVS Protheus, Evolution API, Chatwoot e Mautic mantendo execução local em 1ms (Mock Determinístico) e execução real em Produção.*

### `TICKET-06`: Conector Plug & Play TOTVS Protheus (`src/features/integrations/totvs/`)

- **Contexto:** Item #1 da fila imediata em `STATUS_RETOMADA_PROXIMA_SESSAO.md`.   
- **Ação Cirúrgica:**
  1. Criar a fatia vertical `src/features/integrations/totvs/` (`schemas.py`, `adapter.py`, `service.py`, `router.py`).
  2. Modelar os contratos REST padrão do Protheus:
    - **Clientes (**`SA1`**):** Sincronização bidirecional mapeando `A1_COD`, `A1_LOJA`, `A1_CGC` (CNPJ/CPF da Clínica/Cirurgião), `A1_X_CRO` (CRO/UF) e limite de crédito (`A1_LC`).
    - **Pedidos de Venda (**`SC5` **Cabeçalho /** `SC6` **Itens):** Geração automática de pedido de venda quando um Deal vai para o estágio `"Fechado & Ganho"` ou quando há consumo de kit em consignação.   
  3. Implementar fila de retentativa local no SQLite WAL (`integration_outbox`) com chave de idempotência (`idempotency_key`) para que, se o ERP da fábrica estiver em manutenção, nenhum pedido se perca.
- **Critério de Aceite Binário:** `pytest tests/test_totvs_integration.py -q` validando sincronização `SA1`, emissão `SC5/SC6` e idempotência contra duplicidade.

### `TICKET-07`: Gateway Unificado Omnichannel & Marketing (`Evolution API` + `Chatwoot` + `Mautic`)

- **Contexto:** Materializar a topologia do `open_source_architecture.md` com zero peso no ambiente de desenvolvimento.   
- **Ação Cirúrgica:**
  1. Criar `src/features/integrations/omnichannel/` com suporte a webhooks de entrada (`/api/v1/webhooks/evolution`, `/api/v1/webhooks/chatwoot`, `/api/v1/webhooks/mautic`) validados por assinatura HMAC (`secret`).   
  2. Quando o `mautic` dispara um evento de aumento de pontos (`lead.changepoints`) ou `evolution-api` registra resposta do cirurgião, o RevNault atualiza o `score` do contato e registra na timeline unificada.   
- **Critério de Aceite Binário:** `pytest tests/test_omnichannel_webhooks.py -q` simulando payloads reais do Evolution API v2, Chatwoot e Mautic 5 com exit code 0.

## FASE 4: Features "HubSpot/Salesforce Killer" para Indústria Odontológica

*Objetivo: Implementar os diferenciais competitivos exclusivos do setor odontológico.*

### `TICKET-08`: Motor de Transbordo Automático de Leads Hot (Tier A) & Gatilhos de Receita

- **Contexto:** Item #2 da fila imediata em `STATUS_RETOMADA_PROXIMA_SESSAO.md`.   
- **Ação Cirúrgica:**
  1. Criar `src/features/automations/revenue_triggers.py`.
  2. Quando um Cirurgião-Dentista atinge **Tier A (Hot Lead)** no Lead Scoring ICP Odontológico (ex: Volume >= 30 implantes/mês + interação ativa):   
    - O motor localiza automaticamente o **Closer Regional** responsável pelo território (`UF` / `team_id`) respeitando a árvore RBAC.   
    - Cria automaticamente o Deal prioritário no Kanban, gera uma Task com SLA de 15 minutos para contato e dispara alerta via Webhook/WhatsApp para o Closer.   
- **Critério de Aceite Binário:** `pytest tests/test_revenue_triggers.py -q` comprovando transbordo automático de Lead Tier A para o Closer do respectivo território/UF.

### `TICKET-09`: Grafo Clínico KOL (Cirurgião <-> Clínicas <-> Laboratórios CAD/CAM <-> Faculdades) & Radar Anti-Churn

- **Contexto:** Superar os CRMs generalistas com inteligência de recência de compra (RFM Odontológico).
- **Ação Cirúrgica:**
  1. Criar vínculo N:N (`contact_institutions`) ligando o Cirurgião (CRO) às múltiplas clínicas onde opera, laboratórios de prótese parceiros e instituições onde dá aula (identificando *Speakers / KOLs*).
  2. Implementar endpoint `GET /api/v1/intelligence/churn-risk` que cruza o ciclo médio de recompra de implantes de cada clínica com a data do último pedido, destacando na UI os clientes em risco de migrar para o concorrente.
- **Critério de Aceite Binário:** `pytest tests/test_clinical_graph_churn.py -q` passando 100%.
  &nbsp;

## Resumo da Arquitetura de Execução (Antigravity vs. VPS Swarm)


| **Camada**                                                | **Ambiente Dev/Test (Antigravity)**                                   | **Ambiente Produção (revnaut.vpsconexao.org)**              |
| --------------------------------------------------------- | --------------------------------------------------------------------- | ----------------------------------------------------------- |
| **Runtime Backend**                                       | Python FastAPI (Uvicorn local) — *Boot em 0.4s*                       | Container `revnault-core` no Docker Swarm + Traefik      |
| **Banco de Dados**                                        | SQLite WAL unificado (`data/revnault.db`) — *0MB RAM extra*       | SQLite WAL com backup contínuo (Litestream) ou Postgres     |
| **Frontend**                                              | HTML5 + CSS Tokens + ES Modules nativos + TypeCheck TS                | Servido estaticamente com cache agressivo + Gzip/Brotli     |
| **Motores Externos (Mautic, Chatwoot, Evolution, TOTVS)** | `InMemoryMockAdapters` determinísticos (Testes rodam em < 2s offline) | Containers dedicados no Swarm + Webhooks HMAC reais   |


 

&nbsp;
