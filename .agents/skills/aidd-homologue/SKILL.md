---
name: aidd-homologue
description: Orquestrador autônomo de homologação profunda Full-Stack E2E com Playwright, auditoria de aproveitamento de motores de backend vs. exposição na UI, verificação multi-viewport e crítica de UI/UX corporativa B2B com geração de micro-tickets cirúrgicos. Use quando o usuário solicitar '/aidd-homologue', '/homologue', '/homologar', 'homologar aplicação', 'auditar motores vs tela' ou 'homologação profunda E2E'.
commands:
  - "/aidd-homologue"
  - "/homologue"
  - "/homologar"
---

# AIDD-HOMOLOGUE • Homologação Profunda Full-Stack E2E, Auditoria de Motores & Crítica de UI/UX Corporativa

> **Governança Canônica AIDD:** Determinismo Estrito (Lei #1), Qualidade Binária (Lei #2), Persistência Estruturada (Lei #3), Zero Stubs / Zero Mocks (Lei #5), Quarteto Sine Qua Non (Lei #10), Todo Portão Deve Provar que Morde (Lei #13) e Zero Emojis (Lei #14).  
> **Papel Operacional:** Arquiteto Principal de Automação de QA, Auditor de Design de Produto e Engenheiro de Sistemas Full-Stack.

---

## 1. Missão & Princípios Inegociáveis

Executar uma homologação ponta a ponta (E2E) sem filtros em todas as camadas da aplicação: **Aproveitamento de Motores de Backend vs. Exposição na UI**, **Verificação Funcional Rota a Rota e Sub-rota a Sub-rota via Playwright**, **Responsividade Multi-Viewport** e **Qualidade de Design UI/UX Corporativo B2B**.

**Proibições Estritas:**
* **NÃO** escreva resumos superficiais de código estático.
* **VOCÊ DEVE** iniciar a aplicação real, executar verificações automatizadas em navegador headless com Playwright combinadas com inspeção de AST/DOM e expor **todas** as lacunas onde:
  1. *"O motor debaixo do capô faz X, mas a UI limita, esconde ou falha em expor X"* (**Subutilização de Motor / Capacidades de Backend Órfãs**).
  2. *"A UI alega ou finge fazer Y (casca cosmética, card estático, placeholder genérico, estado mockado ou ID de demonstração chumbado), mas não executa o fluxo completo ponta a ponta"* (**Casca Cosmética / Propaganda Enganosa**).
  3. *"O design da UI é poluído, não intuitivo, não corporativo, não responsivo ou visualmente quebrado entre viewports."*

---

## 2. Gatilhos & Comandos

A skill é acionada por comando explícito ou linguagem natural:
* `/aidd-homologue` ou `/homologue` — Executa os 4 estágios completos ponta a ponta, roda o script Playwright e gera os 2 relatórios mandatórios na raiz do repositório.
* `/aidd-homologue stage1` — Executa apenas a autodescoberta e matriz de aproveitamento Backend vs. Frontend.
* `/aidd-homologue stage2` — Cria e executa o harness Playwright E2E nas 4 viewports.
* `/aidd-homologue tickets` — Atualiza ou regenera `PLANO_MICRO_TICKETS_HOMOLOGACAO_UX_MOTORES.md` a partir das falhas detectadas.

---

## 3. Protocolo de Execução nos 4 Estágios Obrigatórios

### ESTÁGIO 1 — Autodescoberta de Motores de Backend vs. Rotas de Frontend

1. **Introspecção Programática do Backend:** Analisar toda a base de código de backend (routers, controllers, schema OpenAPI/Swagger, workers em background, serviços de domínio e scripts CLI) para construir um inventário de **100% dos endpoints disponíveis, regras de negócio e motores de background**.
2. **Introspecção Programática do Frontend:** Analisar toda a base de código de frontend (configuração de rotas, páginas, views, modais, abas e clientes de API / hooks de fetch) e verificar o que é efetivamente servido no ponto de entrada principal (`/`).
3. **Cruzamento e Cálculo da Taxa de Aproveitamento dos Motores (%):** Calcular a razão exata por módulo, classificando cada capacidade do backend em uma das 4 categorias canônicas:
   * `[100% INTEGRATED]`: Exposto na UI com formulários/ações interativas reais, chamadas reais de API e mutações persistentes no banco de dados refletidas no DOM.
   * `[UNDERUTILIZED / ORPHANED ENGINE]`: Implementado no backend, mas sem tela, aba, formulário ou gatilho correspondente na UI.
   * `[COSMETIC SHELL / FALSE ADVERTISING]`: Visível no menu ou na tela, porém sustentado por widget genérico, componente repetido, array estático mockado ou ID de entidade chumbado (`id="demo-01"`) sem seleção dinâmica.
   * `[DEAD BUTTON / VISUAL STUB]`: Renderiza um botão/controle no DOM que não faz nada, apenas altera estado em memória local sem chamar a API, ou dispara erro de console/rede.

---

### ESTÁGIO 2 — Harness Automatizado Playwright E2E & Multi-Viewport

Criar e executar um script automatizado do Playwright (`scripts/homolog_playwright_e2e.py` ou `scripts/homolog_playwright_e2e.spec.ts`) que:

1. **Subida da Stack Real:** Inicia a aplicação completa (ou conecta à instância ativa) e navega por **100% das rotas, sub-rotas, abas e modais descobertos**.
2. **Auditoria nas 4 Viewports Mandatórias:**
   * **Mobile:** `375x812`
   * **Tablet:** `768x1024`
   * **Corporate Laptop:** `1366x768`
   * **Desktop Full HD:** `1920x1080`
3. **Captura e Asserção Programática em Cada Rota/Viewport:**
   * **Erros de Runtime e Rede:** Erros de console (`page.on("console")`), exceções não tratadas (`page.on("pageerror")`) e respostas HTTP com falha (`HTTP >= 400`).
   * **Bugs de Layout e Geometria:** Overflow horizontal (`scrollWidth > clientWidth`), sobreposição de bounding boxes (`getBoundingClientRect()`), botões de ação cortados (clipped), tabelas espremidas sem container de scroll e alvos de toque/clique `< 36px`.
   * **Presença dos 4 Estados Obrigatórios de UI (alimentados por API real):**
     1. *Loading State* (Skeleton / Spinner estruturado)
     2. *Empty State* (com CTA claro)
     3. *Error State* (com ação de retry)
     4. *Success State* (dados reais renderizados)
   * **Interação E2E Real:** Clica em botões, submete formulários e verifica se as requisições de rede atingem o backend e atualizam a UI de forma persistente.

---

### ESTÁGIO 3 — Crítica de UI/UX Corporativa B2B, Usabilidade & Arquitetura da Informação

Avaliar cada tela contra os padrões Tier-1 de UX Corporativa B2B (**Linear / Stripe / HubSpot**) e as regras do Design System (Zero Emojis — Lei #14):

1. **Identificação de Anti-Patterns Visuais e Ergonômicos:**
   * Ausência de sub-abas de navegação dentro de módulos complexos.
   * Falta de cabeçalhos de KPIs executivos.
   * Tabelas de dados sem busca, filtros ou paginação.
   * Fluxos de criação/edição sem gavetas deslizantes (*slide-over drawers*) ou modais estruturados.
   * Exibição de IDs técnicos brutos (UUIDs/hashes) para o usuário final.
   * Espaçamento ou tipografia inconsistentes, ausência de `tabular-nums` em dados numéricos, ou cores hardcoded fora do sistema de Design Tokens.
   * Presença de emojis Unicode na interface (violação da Lei #14).
2. **Proposta de Reestruturação de Arquitetura da Informação & Componentes:**
   * Especificar para cada módulo a composição exata: `AppShell + Sub-Tabs + Dynamic Entity Selectors + Master-Detail Tables + Slide-over Action Drawers`.

---

### ESTÁGIO 4 — Entregáveis Mandatórios (Prontos para Execução de Micro-Tickets)

Gerar **dois arquivos Markdown completos e sem filtros** na raiz do repositório (redigidos em Português):

#### 1. `RELATORIO_HOMOLOGACAO_PROFUNDA_E2E.md`
Deve conter obrigatoriamente as 4 seções:
* **Seção 1 — Veredito Executivo e Taxa Global de Aproveitamento dos Motores:** Percentual exato do backend exposto na UI vs. subutilizado/oculto, com resumo executivo da saúde E2E.
* **Seção 2 — Matriz Forense "Motor Debaixo do Capô vs. Casca na Tela":** Tabela módulo a módulo contendo:
  `| Módulo | O que o motor faz no backend | O que a tela mostra hoje | Classificação & Diagnóstico (Casca / Propaganda Enganosa / Subutilização) |`
* **Seção 3 — Resultado da Execução Playwright Rota a Rota e Botão a Botão:** Listagem factual de erros de console/rede, botões mortos, IDs chumbados e estados de UI ausentes.
* **Seção 4 — Auditoria de UI/UX Corporativa, Usabilidade e Responsividade nas 4 Viewports (`375px`, `768px`, `1366px`, `1920px`):** Tabela de quebras geométricas, overflows, alvos `< 36px` e anti-patterns B2B por rota.

#### 2. `PLANO_MICRO_TICKETS_HOMOLOGACAO_UX_MOTORES.md`
Converter **100% dos gaps descobertos** em Micro-Tickets sequenciais e cirúrgicos (`[HOMOLOG-01]` até `[HOMOLOG-NN]`). Cada ticket DEVE conter:
* **Diagnóstico do Gap (Motor vs. Tela / UX):** Funcionalidade exata atualmente oculta, mockada, chumbada ou visualmente quebrada.
* **Endpoints do Motor a Conectar (Potencial Máximo):** Rotas e serviços exatos do backend que serão conectados à UI.
* **Especificação de UI/UX Corporativa & Responsividade:** Sub-abas, tabelas, formulários, gavetas (*drawers*), seletores dinâmicos e regras de Design Tokens.
* **DoD (Definition of Done):** Critérios binários e mensuráveis de aceitação E2E.
* **Target Files:** Arquivos exatos de frontend e backend a criar ou modificar.
* **Validation Command:** Comando exato do Playwright + Quality Gate que comprova a conclusão do ticket (`exit 0`).

---

## 4. Checklist Binário de Conclusão da Skill (Quality Gate)

A execução da skill `aidd-homologue` só é considerada concluída quando:
- [ ] O inventário AST/código de Backend vs. Frontend foi cruzado com cálculo percentual real.
- [ ] O script `scripts/homolog_playwright_e2e.py` (ou `.spec.ts`) foi criado e executado contra a aplicação viva nas 4 viewports (`375x812`, `768x1024`, `1366x768`, `1920x1080`).
- [ ] O arquivo `RELATORIO_HOMOLOGACAO_PROFUNDA_E2E.md` foi gravado na raiz do projeto com as 4 seções obrigatórias e zero emojis.
- [ ] O arquivo `PLANO_MICRO_TICKETS_HOMOLOGACAO_UX_MOTORES.md` foi gravado na raiz do projeto com todos os tickets `[HOMOLOG-01..NN]` detalhados e prontos para execução.
