# PLANO DE MICRO-TICKETS CIRÚRGICOS DE HOMOLOGAÇÃO E2E, EXPOSIÇÃO TOTAL DOS MOTORES (100%) & REDESIGN UI/UX CORPORATIVO B2B — REVNAULT

> **Objetivo:** Erradicar 100% das "Cascas Cosméticas", elevar a **Taxa de Aproveitamento dos Motores do Backend de `12,11%` para `100%`** (expondo todos os 38 sub-domínios na UI), eliminar os 15/17 overflows mobile (`375x812`) e entregar uma experiência B2B Enterprise Tier-1 (padrão Linear / Stripe / Salesforce Health Cloud) com conformidade estrita às Leis Invioláveis (#5 Zero Stubs, #11 Stack Canônica, #14 Zero Emojis / Tokens CSS Estritos).
> **Referência Forense:** [`RELATORIO_HOMOLOGACAO_PROFUNDA_E2E_REVNAULT.md`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/RELATORIO_HOMOLOGACAO_PROFUNDA_E2E_REVNAULT.md) e [`docs/homolog_e2e_playwright_report.json`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/docs/homolog_e2e_playwright_report.json).

---

## PADRÃO ARQUITETURAL DE UI/UX CORPORATIVA B2B EXIGIDO EM TODOS OS TICKETS

1. **AppShell Responsivo Multi-Viewport (`375px` / `768px` / `1366px` / `1920px`):**
   - Em `< 1024px` (`Mobile 375px` e `Tablet 768px`), a `<aside>` lateral recolhe automaticamente para uma gaveta (`Sheet` / Drawer mobile acionado por botão Hamburger no `header`), liberando **100% da largura da viewport (`375px` / `768px`)** para o `<main>`.
   - Em `>= 1024px`, a sidebar suporta modo expandido (`w-64`) e modo compacto (`w-16` com tooltips de ícone).
2. **Roteamento URL Sincronizado + Fim das Rotas Órfãs:**
   - Sincronizar `activeNav` com `window.location.hash` / History API (`/#!/deals`, `/#!/contacts`, etc.) e expor na sidebar todas as 17 rotas (incluindo `scoring`, `marketing` e `imaging`).
3. **Sub-Navegação Estruturada por Módulo (`Tabs`):**
   - Cada módulo multi-motor utiliza o componente [`Tabs.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/components/ui/Tabs.tsx) no topo da página, acompanhado de **KPI Summary Cards** (3 a 4 indicadores executivos), **DataTables** com busca/filtro/paginação e **Modais/Drawers (`Dialog`/`Sheet`)** para ações de criação e mutação.
4. **Zero Hardcoded IDs:**
   - Todo componente que opera sobre uma entidade (`dealId`, `contactId`, `studyId`, `agreementId`, `orderId`, `partnerId`) busca a lista real do backend e oferece um `<Select />` dinâmico no cabeçalho do componente.

---

## SEQUÊNCIA EXECUTÁVEL DE MICRO-TICKETS (`[HOMOLOG-01]` A `[HOMOLOG-20]`)

---

### `[HOMOLOG-01]` — AppShell Responsivo Multi-Viewport, Navegação Completa (17 Rotas), URL Sync & Command Palette Funcional (`Cmd+K`)

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - Em `375x812`, `<aside className="w-64 shrink-0">` ocupa `256px` fixos (68% da tela), esmagando `<main>` para `119px` e causando clipping em 15/17 rotas.
  - As rotas `scoring`, `marketing` e `imaging` estão declaradas em [`router.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/router.tsx), mas não existem no menu lateral de [`AppShell.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/components/layout/AppShell.tsx).
  - O Command Palette (`Cmd+K`) possui itens estáticos sem `onClick` e a busca não filtra rotas nem executa comandos.
  - O seletor de usuário/tenant no rodapé da sidebar é estático e não consulta `/api/v1/auth/me` ou `/api/v1/auth/users`.
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `GET /api/v1/health` (status real do banco e contas online no badge da topbar)
  - `GET /api/v1/auth/me` e `GET /api/v1/auth/users` (context switcher de consultor Field/Inside/Director)
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Transformar a sidebar em `hidden lg:flex lg:w-64` no desktop e adicionar drawer deslizante mobile/tablet (`< 1024px`) com botão Hamburger no `header`.
  - Incluir as 17 rotas organizadas nas 3 seções da sidebar (`scoring`, `marketing` e `imaging` visíveis e clicáveis).
  - Sincronizar rota ativa com URL (`window.location.hash` / `popstate`) para permitir deep-linking e F5 sem perda de contexto.
  - Tornar o `Cmd+K` 100% funcional: filtrar todas as 17 rotas e ações rápidas em tempo real e navegar ao clicar ou pressionar `Enter`.
- **DoD (Definition of Done):**
  - Em `375x812` e `768x1024`, `mainWidth == clientWidth` (`375px` e `768px`), zero overflow horizontal no `header` e 100% das 17 rotas navegáveis pela sidebar e pelo `Cmd+K`.
- **Target Files:**
  - [`frontend/src/components/layout/AppShell.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/components/layout/AppShell.tsx)
  - [`frontend/src/App.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/App.tsx)
  - [`frontend/src/router.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/router.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && python scripts/homolog_playwright_e2e.py`

---

### `[HOMOLOG-02]` — Cockpit Executivo Real (`dashboard`) & BI Superset Studio (`analytics`) com Text-to-SQL e KPIs Nativos

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - As rotas `dashboard` e `analytics` renderizam exatamente a mesma instância de `<SupersetEmbeddedDashboard />` que aponta um `<iframe>` para `https://superset.revnault.local/...` (domínio inexistente localmente), deixando uma caixa em branco de `640px`.
  - O motor Text-to-SQL (`POST /api/v1/intelligence/bi/text-to-sql`) e as métricas executivas (`/api/v1/metrics`, `/api/v1/campaigns/metrics`, `/api/v1/intelligence/churn-risk`, `/api/v1/intelligence/clinical-graph`) estão 100% ocultos.
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `GET /api/v1/metrics`
  - `GET /api/v1/campaigns/metrics`
  - `GET /api/v1/intelligence/churn-risk`
  - `GET /api/v1/intelligence/clinical-graph`
  - `POST /api/v1/intelligence/bi/guest-token`
  - `POST /api/v1/intelligence/bi/export-dataset`
  - `POST /api/v1/intelligence/bi/text-to-sql`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Diferenciar `dashboard` (Cockpit Executivo Operacional com KPIs consolidados de Pipeline, Consignação, Radares de Churn e Grafo Clínico) de `analytics` (Estúdio BI Superset RLS + Console Analítico Text-to-SQL interativo + Exportador Parquet/CSV R2).
  - No `SupersetEmbeddedDashboard`, substituir o iframe quebrado por uma visualização híbrida: **Gráficos Analíticos SVG Nativos + Tabela de Dados RLS Auditável + Seletor Dinâmico de Dashboard (`industry_consignment`, `clinic_chair`, `dentgo_sla`, `anvisa_quality_gate`) + Console Text-to-SQL** (`POST /api/v1/intelligence/bi/text-to-sql`).
- **DoD (Definition of Done):**
  - `dashboard` e `analytics` exibem visões distintas, carregam dados reais do SQLite, permitem executar perguntas em linguagem natural via Text-to-SQL e exportar datasets para o R2.
- **Target Files:**
  - [`frontend/src/features/bi/SupersetEmbeddedDashboard.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/bi/SupersetEmbeddedDashboard.tsx)
  - [`frontend/src/router.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/router.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_superset_bi.py -q`

---

### `[HOMOLOG-03]` — Pipeline & Deals (`deals`): Paginação, Busca, Filtro por Funil, Visão Kanban, Criação de Deal, Edição Inline, Aprovação de Crédito, Timeline e Tarefas

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - A rota `deals` em [`App.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/App.tsx) despeja 1.190 linhas de uma só vez no DOM (causando lentidão e overflow em tablet/mobile), o botão `"Novo Negócio"` não tem `onClick`, o componente [`KanbanBoard.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/components/ui/KanbanBoard.tsx) está órfão e 11 endpoints de `deals` e `tasks` estão ocultos.
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `GET /api/v1/pipelines`
  - `GET /api/v1/deals` e `POST /api/v1/deals`
  - `PUT /api/v1/deals/{deal_id}` (Edição inline de valor/título/prazo)
  - `PUT /api/v1/deals/{deal_id}/stage` (Movimentação de estágio com trava de crédito)
  - `GET /api/v1/deals/{deal_id}/timeline`
  - `POST /api/v1/deals/{deal_id}/approve-credit`
  - `GET /api/v1/deals/export/csv`
  - `PATCH /api/v1/tasks/{task_id}/toggle`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Barra superior com: Seletor de Pipeline (`GET /api/v1/pipelines`), Input de Busca Instantânea, Toggle de Visualização (`Tabela Paginada` vs. `Quadro Kanban`), Botão `Exportar CSV` (`GET /api/v1/deals/export/csv`) e Botão `Novo Negócio` abrindo modal `Dialog` conectado a `POST /api/v1/deals`.
  - Paginação determinística na `DataTable` (25/50 itens por página) e scroll horizontal responsivo (`overflow-x-auto`).
  - Drawer lateral (`Sheet`) ao clicar em um Deal exibindo: Edição Inline (`PUT /api/v1/deals/{id}`), Seletor de Mudança de Estágio (`PUT .../stage`), Botão `Aprovar Limite de Crédito` (`POST .../approve-credit`), Checklist de Tarefas (`PATCH /api/v1/tasks/{id}/toggle`) e Timeline de Auditoria (`GET .../timeline`).
- **DoD (Definition of Done):**
  - Criar negócio, mover estágio, aprovar crédito, alternar tarefa, consultar timeline, exportar CSV e alternar entre Tabela Paginada e Kanban funcionando E2E sem overflow em `375px` e `768px`.
- **Target Files:**
  - [`frontend/src/App.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/App.tsx)
  - [`frontend/src/components/ui/DataTable.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/components/ui/DataTable.tsx)
  - [`frontend/src/components/ui/KanbanBoard.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/components/ui/KanbanBoard.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_e2e_api.py -q`

---

### `[HOMOLOG-04]` — CRM de Cirurgiões-Dentistas, Clínicas, Dossiê 360°, Importação CSV & Compliance Ético CFO (`contacts`)

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - A rota `contacts` exibe apenas o input isolado `<CroVerifiedInput />` (sem salvar nada) e o `<IcpScoringDashboard />`. Não existe tabela de cirurgiões, nem cadastro de contato, nem importação CSV, nem dossiê 360°, nem validador de copy CFO 196/2019, nem gestão de clínicas/instituições.
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `GET /api/v1/contacts` e `POST /api/v1/contacts`
  - `POST /api/v1/contacts/import`
  - `GET /api/v1/contacts/{contact_id}/profile`
  - `GET /api/v1/contacts/{contact_id}/timeline` e `POST /api/v1/contacts/{contact_id}/timeline/comments`
  - `POST /api/v1/contacts/validate-cro`
  - `POST /api/v1/contacts/validate-cfo-compliance`
  - `GET /api/v1/institutions` e `POST /api/v1/institutions`
  - `POST /api/v1/intelligence/links`, `GET /api/v1/intelligence/links/contact/{contact_id}`, `DELETE /api/v1/intelligence/links/{link_id}`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Estruturar o módulo `contacts` em 4 sub-abas (`Tabs`):
    1. **Base de Cirurgiões (CRM):** Tabela paginada com busca, filtro por UF/Especialidade, botão `Novo Cirurgião` (integrando `CroVerifiedInput` + `POST /api/v1/contacts`), botão `Importar CSV` (`POST /api/v1/contacts/import`) e Drawer de **Dossiê 360° & Timeline** (`GET .../profile`, `GET/POST .../timeline`).
    2. **Clínicas, Hospitais & Vínculos Societários:** Listagem e criação de Instituições (`GET/POST /api/v1/institutions`) + vinculação multi-clínica (`POST/GET/DELETE /api/v1/intelligence/links`).
    3. **Auditor Ético CFO 196/2019:** Validador interativo de peças publicitárias odontológicas (`POST /api/v1/contacts/validate-cfo-compliance`).
    4. **Qualificação & Score ICP:** Incorporação organizada do `IcpScoringDashboard`.
- **DoD (Definition of Done):**
  - Todos os 8 endpoints de `contacts`, 2 de `institutions` e 3 de `intelligence/links` operacionais via UI, com validação CRO obrigatória no cadastro e Drawer 360° funcional.
- **Target Files:**
  - `frontend/src/features/contacts/ContactsCrmWorkspace.tsx` *(novo)*
  - [`frontend/src/features/contacts/components/CroVerifiedInput.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/contacts/components/CroVerifiedInput.tsx)
  - [`frontend/src/router.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/router.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_cro_cfo_compliance.py -q`

---

### `[HOMOLOG-05]` — Central de Contratos Digitais Documenso, Catálogo ANVISA & Alçadas de Desconto (`contracts`)

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - A rota `contracts` é hoje uma **Casca Cosmética** que renderiza apenas `<R2DirectUploader module="contracts" />`.
  - O motor de Catálogo de Implantes ANVISA, Tabelas de Preço, Simulador de Proposta Comercial com Alçada de Desconto e Geração de Contratos Documenso com Hash SHA-256 (7 endpoints em `deals/router.py`) está 0% exposto na UI.
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `GET /api/v1/deals/catalog/products`
  - `GET /api/v1/deals/catalog/price-tables`
  - `POST /api/v1/deals/catalog/calculate-proposal`
  - `POST /api/v1/deals/catalog/approve-discount`
  - `POST /api/v1/deals/{deal_id}/generate-contract`
  - `GET /api/v1/deals/{deal_id}/contracts`
  - `POST /api/v1/webhooks/documenso/document-completed` (Simulador de assinatura concluída com carimbo SHA-256)
  - `POST /api/v1/storage/presign-upload` e `GET /api/v1/storage/presign-download`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Substituir a casca cosmética de `contracts` por uma **Central de Propostas, Alçadas & Contratos Documenso** com 3 sub-abas:
    1. **Ciclo de Vida de Contratos Documenso:** Seletor dinâmico de Deal (`GET /api/v1/deals`), listagem de contratos do Deal (`GET .../contracts`), botão `Gerar Contrato de Comodato / Fornecimento` (`POST .../generate-contract`) e botão de homologação `Simular Assinatura ICP/Documenso SHA-256` (`POST /api/v1/webhooks/documenso/document-completed`).
    2. **Catálogo ANVISA & Simulador de Proposta Comercial:** Tabela de produtos com registro ANVISA (`GET .../catalog/products`), seletor de tabela de preços (`GET .../catalog/price-tables`), calculadora de proposta (`POST .../calculate-proposal`) e fluxo de aprovação de alçada de desconto (`POST .../approve-discount`).
    3. **Custódia de Minutas PDF no Cloudflare R2:** Mantém o `<R2DirectUploader module="contracts" />` acompanhado de download pré-assinado (`GET /api/v1/storage/presign-download`).
- **DoD (Definition of Done):**
  - Zero casca cosmética: o usuário calcula proposta, aprova desconto, emite contrato Documenso para qualquer Deal real, consulta o hash SHA-256 e faz upload/download no R2.
- **Target Files:**
  - `frontend/src/features/contracts/ContractsDocumensoWorkspace.tsx` *(novo)*
  - [`frontend/src/router.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/router.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_documenso_contracts.py tests/test_catalog_pricing.py -q`

---

### `[HOMOLOG-06]` — Tecnovigilância ANVISA, Quarentena de Lote, SOS Mesa Cirúrgica & Linha de Cuidado Pós-Op B2C (`support`)

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - A rota `support` é a segunda **Casca Cosmética** crítica: renderiza apenas `<R2DirectUploader module="dicom" />`.
  - Esconde 100% dos motores de RMA de Tecnovigilância ANVISA (`tickets/anvisa_rma.py`), Quarentena Automática de Lote (`QUARANTINE_BLOCKED`), Ticket SOS de Mesa Operatória (`tickets/surgical_sos.py`) e Régua Pós-Operatória B2C 24h/48h/72h/7d (`automations/postop_b2c.py`).
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `POST /api/v1/tickets/anvisa-rma` e `GET /api/v1/tickets/anvisa-rma`
  - `GET /api/v1/tickets/anvisa-rma/quarantine/{batch_number}`
  - `GET /api/v1/tickets/anvisa-rma/{claim_id}`
  - `PATCH /api/v1/tickets/{ticket_id}/status`
  - `POST /api/v1/tickets/surgical-sos`, `GET /api/v1/tickets/surgical-sos/{ticket_id}`, `POST /api/v1/tickets/surgical-sos/{ticket_id}/dispatch-dentgo`
  - `POST /api/v1/automations/postop-care/start`, `GET /api/v1/automations/postop-care`, `GET /api/v1/automations/postop-care/{schedule_id}`, `POST /api/v1/automations/postop-care/{schedule_id}/feedback`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Substituir a casca cosmética de `support` pela **Central de Tecnovigilância ANVISA, SOS Cirúrgico & Pós-Operatório B2C** com 3 sub-abas:
    1. **Tecnovigilância ANVISA & Quarentena de Lotes (RMA):** Tabela de ocorrências RMA (`GET /api/v1/tickets/anvisa-rma`), formulário de abertura de garantia de osseointegração com upload de laudo R2 (`POST /api/v1/tickets/anvisa-rma`) e Verificador de Quarentena de Lote (`GET .../quarantine/{batch_number}`) exibindo alerta vermelho quando `QUARANTINE_BLOCKED`.
    2. **SOS Mesa Cirúrgica & Despacho de Emergência:** Abertura de chamado crítico de centro cirúrgico (`POST /api/v1/tickets/surgical-sos`) com botão de 1 clique `Acionar Coleta/Entrega DENTGO Express` (`POST .../{id}/dispatch-dentgo`).
    3. **Linha de Cuidado Pós-Operatória B2C (24h / 48h / 72h / 7d):** Painel de monitoramento de pacientes pós-implante (`GET /api/v1/automations/postop-care`), início de régua (`POST .../start`) e registro de feedback clínico de dor/edema/sangramento (`POST .../{id}/feedback`) com disparo de Alerta Vermelho ao cirurgião.
- **DoD (Definition of Done):**
  - Todos os 12 endpoints de RMA ANVISA, SOS Mesa e Pós-Op B2C conectados e testados E2E na rota `support`.
- **Target Files:**
  - `frontend/src/features/support/SupportAnvisaWorkspace.tsx` *(novo)*
  - [`frontend/src/router.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/router.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_anvisa_rma.py tests/test_surgical_sos.py tests/test_postop_b2c.py -q`

---

### `[HOMOLOG-07]` — Motor Cal.com de Reativação Preventiva de Pacientes 6/12/18 Meses & Agenda de Retornos (`scheduling`)

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - A rota `scheduling` é a terceira **Casca Cosmética**: renderiza `<SupersetEmbeddedDashboard />` em vez do motor Cal.com (`src/features/automations/calcom_service.py`).
  - Os 5 endpoints de agendamento profilático de retorno (6, 12 e 18 meses), disparo de convites WhatsApp e bookings confirmados com kit peri-implantar estão 0% expostos na UI.
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `GET /api/v1/automations/calcom/schedules`
  - `GET /api/v1/automations/calcom/bookings`
  - `POST /api/v1/automations/calcom/schedule-reactivation`
  - `POST /api/v1/automations/calcom/scan-dispatches`
  - `POST /api/v1/automations/calcom/webhook`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Criar o componente dedicado `CalcomReactivationWorkspace.tsx` para a rota `scheduling` contendo:
    - KPIs de Retorno Profilático (Ciclos Agendados 6m/12m/18m, Convites Disparados, Consultas Confirmadas, Kits Peri-Implantares Sugeridos).
    - Formulário/Modal `Programar Ciclo de Reativação (6/12/18m)` (`POST .../schedule-reactivation`).
    - Botão de ação `Executar Varredura de Disparos Pendentes` (`POST .../scan-dispatches`).
    - Tabela de Agendamentos Preventivos (`GET .../schedules`) e Tabela de Consultas Confirmadas (`GET .../bookings`) com botão para simular/confirmar booking via webhook Cal.com (`POST .../webhook`).
- **DoD (Definition of Done):**
  - Rota `scheduling` 100% desvinculada do `SupersetEmbeddedDashboard` e operando os 5 endpoints do motor Cal.com.
- **Target Files:**
  - `frontend/src/features/scheduling/CalcomReactivationWorkspace.tsx` *(novo)*
  - [`frontend/src/router.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/router.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_calcom_reactivation.py -q`

---

### `[HOMOLOG-08]` — Hub de Inteligência Artificial & Ciência de Dados (`intelligence` — 1/2): Seletor Dinâmico Granola, Pipeline Whisper PTT & Assistente RAG Cirúrgico

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - A rota `intelligence` exibe apenas `<GranolaCopilotCard dealId="d-101" />` com ID hardcoded `d-101`, escondendo o pipeline de Transcrição de Áudio PTT Whisper (`transcriptions/*`) e o Assistente RAG Cirúrgico de Sequência de Fresagem e Torque (`catalog-rag/*`).
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `POST /api/v1/intelligence/copilot/extract-and-apply` (com seletor dinâmico de `deal_id` real de `GET /api/v1/deals`)
  - `POST /api/v1/intelligence/transcriptions/process`
  - `GET /api/v1/intelligence/transcriptions/{transcription_id}`
  - `GET /api/v1/intelligence/transcriptions/deal/{deal_id}`
  - `POST /api/v1/intelligence/catalog-rag/ingest`
  - `POST /api/v1/intelligence/catalog-rag/query`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Transformar a rota `intelligence` em uma **Suíte de Inteligência Comercial & Clínica** com navegação por abas (`Tabs`):
    - **Aba 1 — Copiloto Comercial Granola & Transcrição PTT Whisper:** Seletor dinâmico de Oportunidade (`GET /api/v1/deals`), processamento de áudio/nota de voz PTT (`POST .../transcriptions/process`), histórico de transcrições do Deal (`GET .../transcriptions/deal/{deal_id}`) e extração estruturada Zero-Touch (`GranolaCopilotCard`).
    - **Aba 2 — Assistente RAG Cirúrgico (Protocolos de Fresagem & Torque):** Console de consulta técnica sobre osso Tipo I/II/III/IV, RPM, irrigação e torque de inserção (`POST .../catalog-rag/query`) + botão de ingestão de bulas/manuais técnicos (`POST .../catalog-rag/ingest`).
- **DoD (Definition of Done):**
  - Fim do `dealId="d-101"` hardcoded; transcrição Whisper PTT e RAG Cirúrgico de Fresagem/Torque 100% funcionais na UI.
- **Target Files:**
  - [`frontend/src/features/deals/components/GranolaCopilotCard.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/deals/components/GranolaCopilotCard.tsx)
  - `frontend/src/features/intelligence/IntelligenceSuiteWorkspace.tsx` *(novo)*
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_granola_copilot.py tests/test_whisper_transcription.py tests/test_surgical_rag.py -q`

---

### `[HOMOLOG-09]` — Hub de Inteligência Artificial & Ciência de Dados (`intelligence` — 2/2): Estoque Preditivo ($SOK$/$PR$), Margem Líquida Clínica & Health Score Cirúrgico ($HSC$)

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - Os três motores matemáticos preditivos de `src/features/intelligence/` — Estoque Mínimo $SOK$ / Ponto de Reposição $PR$, Calculadora de Margem Líquida Clínica por Hora de Cadeira e Health Score Cirúrgico $HSC$ — estão 0% expostos no frontend (7 endpoints órfãos).
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `POST /api/v1/intelligence/inventory/sok`
  - `POST /api/v1/intelligence/inventory/pr`
  - `GET /api/v1/intelligence/inventory/report/{agreement_id}`
  - `POST /api/v1/intelligence/margin/calculate`
  - `GET /api/v1/intelligence/margin/summary/{clinic_id}`
  - `POST /api/v1/intelligence/health-score/calculate`
  - `GET /api/v1/intelligence/health-score/history/{partner_id}`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Adicionar 3 sub-abas analíticas ao `IntelligenceSuiteWorkspace.tsx`:
    - **Aba 3 — Estoque Mínimo Preditivo ($SOK$) & Ponto de Reposição ($PR$):** Simulador estatístico ($Z \cdot \sigma_d \cdot \sqrt{LT}$) com alerta de ruptura e geração automática de sugestão de remessa (`POST .../inventory/sok`, `POST .../inventory/pr`, `GET .../inventory/report/{agreement_id}`).
    - **Aba 4 — Calculadora de Margem Líquida Clínica (ROI por Hora de Cadeira):** Simulador de rentabilidade de procedimentos cirúrgicos (All-on-4, Implante Unitário, Prótese Protocolo) cruzando custo de componentes, honorários e tempo de cadeira (`POST .../margin/calculate`, `GET .../margin/summary/{clinic_id}`).
    - **Aba 5 — Health Score Cirúrgico ($HSC$) & Previsão de Churn:** Avaliação ponderada de giro de implantes, pontualidade financeira, engajamento e SLA logístico (`POST .../health-score/calculate`, `GET .../health-score/history/{partner_id}`).
- **DoD (Definition of Done):**
  - 100% dos 7 motores do módulo `intelligence` acessíveis e operacionais com dados reais na rota `intelligence`.
- **Target Files:**
  - `frontend/src/features/intelligence/IntelligenceSuiteWorkspace.tsx`
  - [`frontend/src/router.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/router.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_predictive_inventory.py tests/test_clinical_margin.py tests/test_health_score_hsc.py -q`

---

### `[HOMOLOG-10]` — KeyPartners Consignação (`keypartners` — 1/2): Acordos de Consignação, Maletas Seriais, Nova Ordem Cirúrgica & Conciliação Pós-Op CFOP 5.113

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - Em [`ConsignmentSurgicalBoard.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx), não existe botão para criar Ordem Cirúrgica (`POST /api/v1/keypartners/surgical-orders`), nem para registrar o Apontamento Pós-Operatório na coluna `EM_POSSE_CLINICA` (`POST .../{id}/postop-report`), nem para cadastrar Acordos de Consignação (`POST/GET /api/v1/keypartners/agreements`), Maletas Seriais (`POST /api/v1/keypartners/kits`) ou acionar Coleta Reversa via DENTGO (`POST /api/v1/keypartners/consignments/{kit_serial}/trigger-dentgo-pickup`).
  - Além disso, o componente tem `min-h-screen p-6` aninhado dentro do `<main>` do `AppShell`, gerando padding duplicado.
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `POST /api/v1/keypartners/agreements` e `GET /api/v1/keypartners/agreements`
  - `POST /api/v1/keypartners/kits`
  - `POST /api/v1/keypartners/agreements/{agreement_id}/dispatch`
  - `GET /api/v1/keypartners/agreements/{agreement_id}/custody-summary`
  - `POST /api/v1/keypartners/surgical-orders` e `GET /api/v1/keypartners/surgical-orders/{order_id}`
  - `POST /api/v1/keypartners/surgical-orders/{order_id}/postop-report`
  - `POST /api/v1/keypartners/consignments/{kit_serial}/trigger-dentgo-pickup`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Remover o `min-h-screen p-6` duplicado e organizar `ConsignmentSurgicalBoard.tsx` com sub-abas:
    - **Aba 1 — Quadro Cirúrgico 4 Estágios (Kanban):** Botão primário `+ Nova Ordem Cirúrgica` (`POST .../surgical-orders`), botões de transição nos cards para todas as fases: `Aprovar Remessa` (`SOLICITADO_FIELD` -> `APROVADO_INSIDE`), `Despachar Maleta` (`APROVADO_INSIDE` -> `EM_POSSE_CLINICA`) e `Conciliar Pós-Op & Faturar CFOP 5.113` (`EM_POSSE_CLINICA` -> `FATURADO_E_REPOSTO` via `POST .../{id}/postop-report`).
    - **Aba 2 — Acordos de Consignação, Custódia de Maletas & Coleta Reversa:** Listagem e criação de Acordos (`GET/POST .../agreements`), cadastro de Maletas Seriais ANVISA (`POST .../kits`), despacho de kit (`POST .../agreements/{id}/dispatch`), resumo de custódia (`GET .../custody-summary`) e botão `Acionar Coleta Reversa DENTGO` (`POST .../consignments/{kit_serial}/trigger-dentgo-pickup`).
- **DoD (Definition of Done):**
  - Ciclo completo de 4 estágios cirúrgicos + custódia de maletas executável do início ao fim pela UI sem ficar preso em EmptyState.
- **Target Files:**
  - [`frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_keypartners_custody.py tests/test_keypartners_surgical_cycle.py -q`

---

### `[HOMOLOG-11]` — KeyPartners Ecossistema Clínico (`keypartners` — 2/2): Gestão de Contratos KOL (Speakers) & Carteira de Fidelidade Surgical Currency

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - Os motores de Gestão de Speakers/KOLs (`keypartners/kol_service.py` — 5 endpoints + `GET /api/v1/intelligence/kol-speakers`) e de Fidelidade B2B por Moeda Cirúrgica (`keypartners/loyalty_service.py` — 4 endpoints) estão 0% expostos na UI.
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `GET /api/v1/keypartners/kol-contracts` e `POST /api/v1/keypartners/kol-contracts`
  - `GET /api/v1/keypartners/kol-contracts/{contract_id}`
  - `POST /api/v1/keypartners/kol-contracts/{contract_id}/record-consumption`
  - `POST /api/v1/keypartners/kol-contracts/{contract_id}/evidence`
  - `GET /api/v1/intelligence/kol-speakers`
  - `GET /api/v1/keypartners/loyalty/wallet/{partner_id}`
  - `GET /api/v1/keypartners/loyalty/rewards`
  - `POST /api/v1/keypartners/loyalty/credit`
  - `POST /api/v1/keypartners/loyalty/redeem`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Adicionar mais 2 sub-abas ao workspace `keypartners`:
    - **Aba 3 — Contratos KOL & Speakers Científicos:** Tabela de líderes de opinião e contratos de patrocínio (`GET .../kol-contracts` e `GET /api/v1/intelligence/kol-speakers`), modal `Novo Contrato KOL` (`POST .../kol-contracts`), botão `Apontar Consumo de Cota` (`POST .../{id}/record-consumption`) e `Registrar Evidência Científica/Aula` (`POST .../{id}/evidence`).
    - **Aba 4 — Programa de Fidelidade (Surgical Currency Wallet):** Consulta de saldo e tier (`BRONZE`, `SILVER`, `GOLD`, `BLACK_DIAMOND`) da carteira (`GET .../loyalty/wallet/{partner_id}`), catálogo de prêmios (`GET .../loyalty/rewards`), lançamento de pontos (`POST .../loyalty/credit`) e resgate imediato (`POST .../loyalty/redeem`).
- **DoD (Definition of Done):**
  - 100% dos 21 endpoints do domínio KeyPartners operacionais em 4 abas estruturadas.
- **Target Files:**
  - [`frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_keypartners_kol.py tests/test_keypartners_loyalty.py -q`

---

### `[HOMOLOG-12]` — DENTGO Express (`dentgo` — 1/2): Hubs Regionais, Busca Emergencial Haversine, Checkout Same-Day & Esteira de 6 Estágios com Lacre e PIN

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - [`DentgoExpressCockpit.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/dentgo/DentgoExpressCockpit.tsx) apenas consulta `GET /api/v1/dentgo/orders` e cai num `EmptyState` sem botão para criar pedidos, sem gestão de Hubs Regionais e sem botões para avançar os 6 estágios da entrega (`ORDER_PLACED` -> `PICKING_BIPADO` -> `SEALED_READY` -> `COURIER_ASSIGNED` -> `IN_TRANSIT_LIVE` -> `DELIVERED_VERIFIED`).
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `GET /api/v1/dentgo/hubs` e `POST /api/v1/dentgo/hubs`
  - `POST /api/v1/dentgo/hubs/{hub_id}/inventory`
  - `POST /api/v1/dentgo/hubs/search-emergency`
  - `POST /api/v1/dentgo/orders/checkout`
  - `GET /api/v1/dentgo/orders` e `GET /api/v1/dentgo/orders/{order_id}`
  - `POST /api/v1/dentgo/orders/{order_id}/picking`
  - `POST /api/v1/dentgo/orders/{order_id}/seal`
  - `POST /api/v1/dentgo/orders/{order_id}/assign-courier`
  - `POST /api/v1/dentgo/orders/{order_id}/start-transit`
  - `POST /api/v1/dentgo/orders/{order_id}/verify-delivery`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Remover o `min-h-screen p-6` duplicado de `DentgoExpressCockpit.tsx` e estruturar as sub-abas:
    - **Aba 1 — Despacho Same-Day & Rastreio Last-Mile (SLA 45 min):** Botão `+ Novo Despacho Emergencial` (`POST .../orders/checkout`), lista de entregas em andamento e painel lateral de **Inspeção de Custódia e Lacre** com botões interativos de transição para cada uma das 5 etapas (`Bipar Picking ANVISA`, `Lacrar Embalagem Térmica`, `Designar Motoboy/Courier`, `Iniciar Trânsito Live`, `Confirmar Entrega com PIN Sanitário & POD R2`).
    - **Aba 2 — Rede de Micro-Hubs Regionais & Radar Haversine:** Cadastro e listagem de Hubs (`GET/POST .../hubs`), abastecimento de lote ANVISA no Hub (`POST .../hubs/{id}/inventory`) e Simulador de Busca Geográfica de Emergência (`POST .../hubs/search-emergency`).
- **DoD (Definition of Done):**
  - O operador consegue cadastrar um Hub, disparar um pedido express e conduzi-lo pelos 6 estágios até `DELIVERED_VERIFIED` com validação de PIN pela interface.
- **Target Files:**
  - [`frontend/src/features/dentgo/DentgoExpressCockpit.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/dentgo/DentgoExpressCockpit.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_dentgo_hubs.py tests/test_dentgo_logistics.py -q`

---

### `[HOMOLOG-13]` — DENTGO Liquidação & Finanças (`dentgo` — 2/2): Motor de Ofertas Relâmpago FEFO (<180 dias) & Ledger de Split Financeiro Automático

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - Os motores de Liquidação Preventiva FEFO (`dentgo/fefo_service.py` — 4 endpoints) e de Split Financeiro Tripartido 80% Indústria / 12% Hub / 8% Entregador (`dentgo/financial_split.py` — 3 endpoints) estão 0% expostos na UI.
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `POST /api/v1/dentgo/fefo/scan`
  - `GET /api/v1/dentgo/fefo/deals` e `GET /api/v1/dentgo/fefo/deals/{deal_id}`
  - `POST /api/v1/dentgo/fefo/deals/{deal_id}/reserve`
  - `POST /api/v1/dentgo/orders/{order_id}/split`
  - `GET /api/v1/dentgo/orders/{order_id}/split`
  - `GET /api/v1/dentgo/splits`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Adicionar mais 2 sub-abas ao `DentgoExpressCockpit.tsx`:
    - **Aba 3 — Liquidação Preventiva FEFO (Flash Deals ANVISA):** Botão `Escanear Lotes Próximos do Vencimento (<180d)` (`POST .../fefo/scan`), vitrine de ofertas com desconto progressivo (`15%`, `30%`, `45%` ou bloqueio `<30d`) (`GET .../fefo/deals`) e botão `Reservar Lote Promocional` (`POST .../fefo/deals/{id}/reserve`).
    - **Aba 4 — Split Financeiro & Liquidação (80% Indústria / 12% Hub / 8% Courier):** Tabela de conciliação financeira das entregas (`GET .../splits`), cálculo individual de split (`POST .../orders/{id}/split`) e detalhamento de repasses.
- **DoD (Definition of Done):**
  - 100% dos 19 endpoints do domínio DENTGO operacionais em 4 abas estruturadas.
- **Target Files:**
  - [`frontend/src/features/dentgo/DentgoExpressCockpit.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/dentgo/DentgoExpressCockpit.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_dentgo_fefo_flash_deals.py tests/test_dentgo_financial_split.py -q`

---

### `[HOMOLOG-14]` — Central Omnichannel Completa (`omnichannel`): Chat WhatsApp em Tempo Real, Seletor de Cirurgião 360°, Instâncias Evolution API & Correção do 404 PACS

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - Na rota `omnichannel`, não existe janela de conversa/chat! Há apenas a sidebar `OmnichannelContextSidebar` chumbada em `contactIdentifier="cnt-01"` (que não existe no banco) ao lado do `DicomStl3DViewer` chumbado em `studyId="study-demo-01"` (que falha com **HTTP 404** no Playwright!).
  - Os endpoints de conversas/mensagens (`GET /api/v1/chat/conversations`, `GET/POST .../messages`) e de gestão de instâncias WhatsApp Evolution API (`GET/POST /api/v1/omnichannel/whatsapp/instances`) estão 0% expostos.
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `GET /api/v1/chat/conversations`
  - `GET /api/v1/chat/{chat_id}/messages`
  - `POST /api/v1/chat/messages` e `POST /api/v1/conversations/{chat_id}/messages`
  - `GET /api/v1/omnichannel/context/{contact_identifier}` (com contato real selecionado)
  - `GET /api/v1/omnichannel/chatwoot-context-panel`
  - `POST /api/v1/omnichannel/chatwoot/sync-contact/{contact_id}`
  - `GET /api/v1/omnichannel/whatsapp/instances`, `POST /api/v1/omnichannel/whatsapp/instances`, `GET /api/v1/omnichannel/whatsapp/instances/{instance_name}`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Remover o `DicomStl3DViewer` (que pertence à rota `imaging`) de dentro de `omnichannel`, eliminando o HTTP 404.
  - Construir o layout canônico de 3 colunas da **Central Omnichannel & Evolution API**:
    1. **Coluna 1 (Lista de Conversas & Instâncias WhatsApp):** Lista de conversas ativas (`GET /api/v1/chat/conversations`), seletor de cirurgião (`GET /api/v1/contacts`) e aba/modal de **Instâncias Evolution API** (`GET/POST /api/v1/omnichannel/whatsapp/instances`).
    2. **Coluna 2 (Janela de Chat em Tempo Real):** Histórico de mensagens (`GET /api/v1/chat/{chat_id}/messages`) + barra de envio de mensagem (`POST /api/v1/chat/messages`).
    3. **Coluna 3 (Contexto 360° KeyPartners + DENTGO):** `OmnichannelContextSidebar` recebendo dinamicamente o contato selecionado (com `onOpenSosVideo` navegando para `video_sos`).
- **DoD (Definition of Done):**
  - Zero HTTP 404 ao abrir `omnichannel`; envio e leitura de mensagens funcionando E2E; contexto 360° carregando cirurgião real; gestão de instâncias WhatsApp Evolution API acessível.
- **Target Files:**
  - [`frontend/src/features/inbox/OmnichannelContextSidebar.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/inbox/OmnichannelContextSidebar.tsx)
  - [`frontend/src/router.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/router.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_omnichannel_evolution_chatwoot.py -q`

---

### `[HOMOLOG-15]` — PACS 3D DICOM/STL (`imaging`) & Vídeo Suporte SOS (`video_sos`): Seed/Lista de Estudos 3D, Upload R2 Funcional e Seletor Dinâmico de Sala/Gravações

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - `DicomStl3DViewer.tsx` busca `studyId="study-demo-01"`, que retorna **HTTP 404** caso não haja estudo cadastrado; não lista os estudos disponíveis (`GET /api/v1/imaging/studies`); e o botão `"Upload DICOM/STL no R2"` (linha 175) tem `onClick={() => {}}` (botão morto).
  - `LiveKitDealRoomModal.tsx` na rota `video_sos` está preso a `dealId="sos-mesa-01"` hardcoded e não exibe a lista de gravações Egress salvas no R2 (`GET /api/v1/communications/deals/{deal_id}/recordings`).
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `GET /api/v1/imaging/studies` e `GET /api/v1/imaging/studies/{study_id}`
  - `POST /api/v1/imaging/studies/upload-presign`
  - `GET /api/v1/imaging/studies/{study_id}/viewer-token`
  - `POST /api/v1/communications/rooms/token`
  - `POST /api/v1/communications/voip/dial`
  - `GET /api/v1/communications/deals/{deal_id}/recordings`
  - `POST /api/v1/communications/livekit/webhook`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Em `DicomStl3DViewer.tsx`: carregar a lista de exames (`GET /api/v1/imaging/studies`); se a lista estiver vazia ou `study-demo-01` não existir, oferecer botão funcional `Registrar & Carregar Tomografia Cone Beam (.dcm / .stl)` que chama `POST /api/v1/imaging/studies/upload-presign` e abre imediatamente o visualizador 3D sem erro 404! Adicionar barra superior com seletor de exame (`<Select />`) e uploader R2 real.
  - Em `LiveKitDealRoomModal.tsx`: adicionar seletor dinâmico de Deal (`GET /api/v1/deals`), aba/painel de **Gravações de Sala Cirúrgica no R2** (`GET /api/v1/communications/deals/{deal_id}/recordings`) e botão para simular finalização de gravação Egress (`POST /api/v1/communications/livekit/webhook`).
- **DoD (Definition of Done):**
  - Zero HTTP 404 no visualizador 3D; botão de upload DICOM/STL 100% funcional; seletor de Deal e listagem de gravações R2 ativos no `LiveKitDealRoomModal`.
- **Target Files:**
  - [`frontend/src/features/imaging/DicomStl3DViewer.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/imaging/DicomStl3DViewer.tsx)
  - [`frontend/src/features/communications/LiveKitDealRoomModal.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/communications/LiveKitDealRoomModal.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_orthanc_dicom_viewer.py tests/test_livekit_communications.py -q`

---

### `[HOMOLOG-16]` — Suíte de Marketing Odontológico (`marketing`): Builder GrapesJS, Disparos Listmonk, Automações Mautic & Programa de Indicação MGM B2B

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - A rota `marketing` estava **órfã fora da sidebar** e exibia apenas o `<LandingPageBuilder campaignId="camp-allon4-sp" />` sem listar as páginas já criadas (`GET /api/v1/campaigns/landing-pages`) e sem expor os motores Listmonk (`POST /api/v1/campaigns/broadcast-listmonk`), Mautic (`POST /api/v1/webhooks/mautic/campaign-action`), Fluxos de Automação (`GET/PUT/POST /api/v1/automations/flows/*`) e Programa de Indicação B2B Member-Get-Member (`POST /api/v1/campaigns/referral/*`).
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `GET /api/v1/campaigns/landing-pages`, `GET /api/v1/campaigns/landing-pages/{page_id}`, `GET /api/v1/campaigns/landing-pages/templates`, `POST /api/v1/campaigns/landing-pages`, `PUT /api/v1/campaigns/landing-pages/{page_id}`, `PUT /api/v1/campaigns/landing-pages/{page_id}/publish`, `POST /api/v1/campaigns/public/lp/{slug}/submit`
  - `POST /api/v1/campaigns/broadcast-listmonk`
  - `POST /api/v1/webhooks/mautic/campaign-action`
  - `POST /api/v1/campaigns/referral/generate-link`, `POST /api/v1/campaigns/referral/register`, `POST /api/v1/campaigns/referral/qualify`, `GET /api/v1/campaigns/referral/dashboard/{referrer_id}`
  - `GET /api/v1/automations/flows`, `PUT /api/v1/automations/flows/{flow_id}/toggle`, `POST /api/v1/automations/flows/{flow_id}/test`, `GET /api/v1/automations/logs`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Expandir `LandingPageBuilder.tsx` com 3 abas completas:
    1. **Construtor GrapesJS & Páginas Publicadas no R2:** Seletor de Landing Pages salvas (`GET .../landing-pages`), editor visual com templates CFO e botão de teste de captura de lead (`POST .../public/lp/{slug}/submit`).
    2. **Campanhas Listmonk & Cadências Mautic:** Disparador de campanha transacional/newsletter Listmonk (`POST .../broadcast-listmonk`) + gerenciamento de réguas de automação Mautic (`GET/PUT/POST /api/v1/automations/flows/*` e `POST /api/v1/webhooks/mautic/campaign-action`).
    3. **Programa de Indicação B2B (Member-Get-Member — MGM):** Gerador de link de indicação para cirurgiões embaixadores (`POST .../referral/generate-link`), registro/qualificação de indicado (`POST .../register`, `POST .../qualify`) e painel de recompensas do indicador (`GET .../referral/dashboard/{referrer_id}`).
- **DoD (Definition of Done):**
  - Rota `marketing` acessível na sidebar e operando LPs, Listmonk, Mautic e Referral MGM E2E.
- **Target Files:**
  - [`frontend/src/features/campaigns/LandingPageBuilder.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/campaigns/LandingPageBuilder.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_grapesjs_landing_pages.py tests/test_mautic_listmonk_campaigns.py tests/test_referral_mgm.py -q`

---

### `[HOMOLOG-17]` — Motor Preditivo de Lead Scoring ICP (`scoring`): CRUD Completo de Regras, Aplicação de Presets & Simulador de Handoff Automático

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - [`IcpScoringDashboard.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/scoring/IcpScoringDashboard.tsx) apenas lê regras e presets (`GET /rules`, `GET /presets`) e recalcula (`POST /recalculate`), mas não permite **aplicar um preset** (`POST /api/v1/scoring/presets/apply`), **criar/editar/excluir regras** (`POST/PUT/DELETE /api/v1/scoring/rules`) nem **avaliar handoff automático** (`POST /api/v1/scoring/evaluate-handoff` / `POST /api/v1/automations/evaluate-hot-lead/{contact_id}`).
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `GET /api/v1/scoring/presets` e `POST /api/v1/scoring/presets/apply`
  - `GET /api/v1/scoring/rules`, `POST /api/v1/scoring/rules`, `PUT /api/v1/scoring/rules/{rule_id}`, `DELETE /api/v1/scoring/rules/{rule_id}`
  - `POST /api/v1/scoring/recalculate`
  - `POST /api/v1/scoring/evaluate-handoff`
  - `POST /api/v1/automations/evaluate-hot-lead/{contact_id}`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Adicionar botão `Aplicar Preset` em cada card de Preset (`POST /api/v1/scoring/presets/apply`).
  - Adicionar formulário/modal `+ Nova Regra de Pontuação` (`POST /api/v1/scoring/rules`), edição inline de pontos (`PUT .../rules/{id}`) e botão de exclusão (`DELETE .../rules/{id}`).
  - Adicionar card **Simulador de Qualificação & Handoff Automático (Tier A >= 80 pts)** conectando `POST /api/v1/scoring/evaluate-handoff`.
- **DoD (Definition of Done):**
  - 100% dos 8 endpoints de `scoring` conectados e operacionais via interface.
- **Target Files:**
  - [`frontend/src/features/scoring/IcpScoringDashboard.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/scoring/IcpScoringDashboard.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_icp_scoring.py -q`

---

### `[HOMOLOG-18]` — Governança RBAC Dual Tree (`rbac`): Gestão de Unidades, Equipes, Matriz de Permissões, Metas & Comissionamento Bipartido (70/30)

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - [`RbacHierarchyTree.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/rbac/RbacHierarchyTree.tsx) consome apenas 1 dos 18 endpoints (`GET /api/v1/hierarchy/tree`, ou seja, **5,6% de aproveitamento**). Os 17 endpoints de presets organizacionais, unidades de negócio, equipes, matriz de permissões por cargo, metas financeiras e regras/extratos de comissão bipartida (70% Field Sales / 30% Inside Sales) estão invisíveis.
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `GET /api/v1/hierarchy/tree` e `POST /api/v1/hierarchy/presets/apply`
  - `GET /api/v1/hierarchy/business-units` e `POST /api/v1/hierarchy/business-units`
  - `GET /api/v1/hierarchy/teams`, `POST /api/v1/hierarchy/teams`, `PUT /api/v1/hierarchy/teams/{team_id}/parent`
  - `GET /api/v1/hierarchy/roles`, `POST /api/v1/hierarchy/roles`, `GET /api/v1/hierarchy/catalog`, `GET /api/v1/hierarchy/roles/{role_id}/permissions`, `PUT /api/v1/hierarchy/roles/{role_id}/permissions`
  - `GET /api/v1/hierarchy/targets`, `POST /api/v1/hierarchy/targets`, `GET /api/v1/hierarchy/targets/suggestion`
  - `GET /api/v1/hierarchy/commissions/rules`, `POST /api/v1/hierarchy/commissions/rules`, `GET /api/v1/hierarchy/commissions/statement`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Evoluir `RbacHierarchyTree.tsx` para uma **Central de Governança RBAC, Metas & Comissionamento Dual** com 4 abas:
    1. **Organograma DAG Dual Tree (Field & Inside):** Árvore interativa + botões `Aplicar Preset Corporativo` (`POST .../presets/apply`), `+ Nova Unidade de Negócio` (`POST .../business-units`) e `+ Nova Equipe Regional` (`POST .../teams`).
    2. **Cargos & Matriz de Permissões Granulares:** Lista de cargos (`GET/POST .../roles`), catálogo de escopos (`GET .../catalog`) e checkboxes para atualizar permissões (`PUT .../roles/{id}/permissions`).
    3. **Metas Comerciais & Sugestão Inteligente:** Painel de metas por equipe/consultor (`GET/POST .../targets`) com botão `Sugerir Meta Preditiva` (`GET .../targets/suggestion`).
    4. **Comissionamento Bipartido (70% Field / 30% Inside):** Regras de comissão (`GET/POST .../commissions/rules`) e Extrato Auditável de Comissões (`GET .../commissions/statement`).
- **DoD (Definition of Done):**
  - Aproveitamento do motor `hierarchy` elevado de `5,6%` para `100%` (18/18 endpoints expostos).
- **Target Files:**
  - [`frontend/src/features/rbac/RbacHierarchyTree.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/rbac/RbacHierarchyTree.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_rbac_dual_tree.py -q`

---

### `[HOMOLOG-19]` — Configurações Enterprise, Hub Fiscal ERP Windmill/TOTVS (CFOP 5917/1918/5113), Webhooks Outbound & Quarteto Dinâmico (`settings`)

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - O item do menu lateral chama-se `"Configurações & ERP"`, mas [`CredentialsVaultPage.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/settings/CredentialsVaultPage.tsx) mostra apenas o Cofre de Credenciais AES-256-GCM.
  - O Hub Fiscal ERP Windmill/TOTVS (7 endpoints de emissão NF-e CFOP 5917/1918/5113 e sincronização Protheus), o Gerenciador de Webhooks Outbound com Circuit Breaker (8 endpoints), a Gestão de Usuários (`GET/POST/PUT /api/v1/auth/users`) e os atalhos para o Quarteto Dinâmico (`/docs`, `/webhooks`, `/mcp`, `/docs/guia`) estão ocultos.
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - `GET/POST/DELETE /api/v1/auth/credentials`
  - `GET /api/v1/auth/users`, `POST /api/v1/auth/users`, `PUT /api/v1/auth/users/{user_id}/status`, `POST /api/v1/auth/users/{user_id}/reset-password`
  - `POST /api/v1/integrations/erp/remittance/emit` (NF-e Remessa Consignação CFOP 5917/6917)
  - `POST /api/v1/integrations/erp/settlement/emit` (NF-e Retorno Simbólico 1918 + Venda 5113)
  - `GET /api/v1/integrations/erp/invoices` e `GET /api/v1/integrations/erp/invoices/{invoice_id}`
  - `POST /api/v1/integrations/totvs/customers/sync`, `POST /api/v1/integrations/totvs/orders`, `GET /api/v1/integrations/totvs/outbox`
  - `GET/POST /api/v1/webhooks/subscriptions`, `DELETE /api/v1/webhooks/subscriptions/{id}`, `PATCH /api/v1/webhooks/subscriptions/{id}/reset-circuit`, `POST /api/v1/webhooks/test-dispatch`, `GET /api/v1/webhooks/logs`
  - `GET /api/v1/quarteto/manuais`
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Expandir `CredentialsVaultPage.tsx` com 4 abas:
    1. **Cofre Cifrado AES-256-GCM:** Gestão de chaves e certificados A1.
    2. **Hub Fiscal ERP Windmill & TOTVS Protheus:** Emissão de NF-e de Remessa em Consignação (CFOP 5917/6917), Liquidação/Faturamento Cirúrgico (CFOP 1918 + 5113), tabela de Notas Fiscais emitidas (`GET .../erp/invoices`) e fila Outbox TOTVS (`GET .../totvs/outbox`).
    3. **Webhooks Outbound & Circuit Breaker:** Cadastro de endpoints de destino, disparo de teste HMAC-SHA256 (`POST .../test-dispatch`), reset de circuit breaker (`PATCH .../reset-circuit`) e logs de entrega (`GET .../logs`).
    4. **Usuários, Segurança & Quarteto Canônico:** Gestão de usuários (`GET/POST/PUT /api/v1/auth/users`) e links diretos para `/docs` (Swagger), `/webhooks`, `/mcp` e `/docs/guia` (Manuais Canônicos).
- **DoD (Definition of Done):**
  - 100% dos motores de ERP Fiscal, TOTVS, Webhooks Outbound e Usuários operacionais dentro da rota `settings`.
- **Target Files:**
  - [`frontend/src/features/settings/CredentialsVaultPage.tsx`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/frontend/src/features/settings/CredentialsVaultPage.tsx)
- **Validation Command:**
  - `npm --prefix frontend run build && pytest tests/test_windmill_erp_hub.py tests/test_vault_security.py -q`

---

### `[HOMOLOG-20]` — Bateria Final de Homologação E2E Playwright nas 4 Viewports & Quality Gate Inquebrável (Lei #13 & Lei #14)

- **Diagnóstico do Gap (Motor vs. Tela / UX):**
  - Garantir que após a implementação dos tickets `[HOMOLOG-01]` a `[HOMOLOG-19]`, o bundle de produção `frontend/dist` esteja atualizado, `src/main.py` sirva prioritariamente `frontend/dist`, o Design Linter (Lei #14) passe com 0 violações e o harness Playwright E2E comprove:
    - **0 overflows horizontais / 0 elementos esmagados** em `375x812`, `768x1024`, `1366x768` e `1920x1080`.
    - **0 erros de rede (`status >= 400`) e 0 erros de console** nas 17 rotas.
    - **100% dos 38 sub-domínios de negócio expostos na UI**.
- **Endpoints do Motor a Plugar (100% do Potencial):**
  - Verificação automatizada de todos os 38 sub-domínios no relatório `docs/homolog_e2e_playwright_report.json`.
- **Especificação de UI/UX Corporativa & Responsividade:**
  - Atualizar `scripts/homolog_playwright_e2e.py` com asserções binárias (Quality Gate exit 0 / exit 1 conforme Lei #2 e Lei #13).
- **DoD (Definition of Done):**
  - `npm --prefix frontend run build` compila com zero erros TypeScript.
  - `python scripts/homolog_playwright_e2e.py` retorna `exit 0` com 17/17 rotas navegáveis na sidebar, 0 falhas HTTP e 0 overflows nas 4 viewports.
  - `pytest` passa 100% da suíte de testes automatizados.
- **Target Files:**
  - [`scripts/homolog_playwright_e2e.py`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/scripts/homolog_playwright_e2e.py)
  - [`docs/homolog_e2e_playwright_report.json`](file:///C:/Users/trcnologia/Desktop/_inbox/proj_revops/docs/homolog_e2e_playwright_report.json)
- **Validation Command:**
  - `npm --prefix frontend run build && python scripts/homolog_playwright_e2e.py && python .agents/skills/aidd-linter-design/scripts/design_linter.py --path frontend/src && pytest -q`
