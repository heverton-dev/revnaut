---
name: aidd-reconstruct
description: Pipeline autônomo de engenharia reversa profunda e reconstrução de alta fidelidade (Clone-to-Craft). Orquestra Playwright (acesso/interação/HAR), REA (desofuscação/decompilação/contratos de API), Mobbin (correção anatômica de UX/heurísticas) e Impeccable (Design System/Craft/produção de código limpo funcional). Suporta Web/SPA, Electron/Desktop e Android APK.
commands:
  - "/aidd-reconstruct"
  - "/reconstruct"
  - "/reverse-craft"
  - "/clone-forge"
---

# AIDD-RECONSTRUCT • Engenharia Reversa Profunda & Reconstrução Factual (Clone-to-Craft)

> **Padrão de Governança AIDD:** Determinismo Estrito (Lei #1), Qualidade Binária (Lei #2), Persistência Estruturada (Lei #3), Zero Stubs (Lei #5) e Honestidade de Rótulo (Lei #8).  
> **Propósito:** Entregar a desconstrução e reconstrução **COMPLETA e PROFUNDA** de qualquer alvo (Web, SPA, Electron, APK ou Binário), gerando não apenas a casca visual, mas a **lógica de negócio, contratos de API, árvore de estado, design tokens e código executável polido**.

---

## 1. Princípio da Profundidade Total (Zero Superficialidade)

A engenharia reversa não para no HTML/CSS visível. Uma execução só é considerada **PROFUNDA** quando extrai e reconstitui as 4 camadas da aplicação:

1. **Camada de Tráfego & Contratos (API & Network):** Endpoints, payloads JSON, query params, headers de autorização e esquemas OpenAPI/TypeScript dos serviços consumidos.
2. **Camada Lógica & Estado (Business Logic & Stores):** Desofuscação de bundles JS/TS, descompilação de classes/métodos (Java/Kotlin/Smali para APK), extração de regras de validação, mapeamento de stores (Redux, Pinia, Zustand, Room/SQLite).
3. **Camada Anatômica & Heurística (UX Benchmarking via Mobbin):** Auditoria das falhas e anti-patterns do app original, corrigindo fluxos truncados, formulários desajeitados e inconsistências contra padrões de elite do mercado.
4. **Camada de Craft & Design System (Impeccable):** Criação da Single Source of Truth (`tokens.css`, `tokens.json`), tipografia escalada, acessibilidade (WCAG AAA) e código limpo, modular e autônomo.

---

## 2. A Esteira Operacional em 5 Fases

```mermaid
graph TD
    Alvo[Alvo: Web / SPA / Electron / APK] --> F1[Fase 1: Ingestão Ativa & Captura Factual (Playwright / REA)]
    F1 --> F2[Fase 2: Decompilação & Extração Semântica (REA Engine)]
    F2 --> F3[Fase 3: Auditoria Anatômica & Correção Heurística (Mobbin MCP)]
    F3 --> F4[Fase 4: Reconstrução de Código & Design System (Impeccable)]
    F4 --> F5[Fase 5: Quality Gate & Validação Factual (Linter + DevTools)]
```

---

### Fase 1 — Ingestão Ativa & Captura Factual (`Playwright / Driver`)
* **Navegação & Crawl:** Percorre deterministamente todas as rotas públicas e autenticadas do alvo.
* **Network Dump:** Grava o log de tráfego completo em formato HAR (`network.har`), capturando todas as requisições XHR/Fetch, WebSockets e Server-Sent Events.
* **Capturas Retina 2x:** Registra cada tela e modal em Desktop (`1440x900 @2x`) e Mobile (`393x852 @3x`).
* **Dump de Sessão:** Salva cookies, LocalStorage, SessionStorage e IndexedDB para reconstituição de estado.

### Fase 2 — Engenharia Reversa Profunda & Desofuscação (`REA Engine`)
* **Aplicações Web / SPA / Electron:**
  * Executa `recover_javascript_sources` e `analyze_web_bundle` para extrair os módulos originais do Webpack/Vite/Rollup.
  * Se for Electron, desempacota o ASAR via `analyze_javascript_application`, mapeia IPC bridges (`preload.js`, `contextBridge`) e processos Main/Renderer.
  * Reconstrói as interfaces TypeScript e esquemas de dados a partir dos payloads capturados no HAR.
* **Aplicativos Android (APK / AAB):**
  * Executa `inspect_android_package`, `inspect_android_class` e `inspect_android_method`.
  * Extrai `AndroidManifest.xml`, permissões, services, broadcast receivers e activities.
  * Mapeia modelos de banco local (SQLite / Room) e endpoints hardcoded ou compilados.
* **Binários Nativos / CLI:**
  * Utiliza `open_binary`, `binary_overview`, `list_strings` e `procedure_pseudo_code` para mapear rotinas críticas.

### Fase 3 — Auditoria Anatômica & Correção de UX (`Mobbin MCP`)
* **Detecção de Anti-Patterns do Original:**
  * Identifica telas densas demais, fluxos com excesso de cliques, formulários sem feedback e ausência de estados vazios (*empty states*).
* **Benchmarking Setorial:**
  * Consulta o `mobbin-mcp` para obter a anatomia de referência do segmento (Fintech, Health, B2B SaaS, E-commerce).
* **Matriz de Correção:**
  * Registra o que foi corrigido no design original (ex: substituição de dropdown obsoleto por combobox pesquisável, melhoria no checkout, responsividade real).

### Fase 4 — Reconstrução de Código & Design System (`Impeccable`)
* **Design Tokens (SSOT):**
  * Gera `tokens.json` e `tokens.css` com paleta HSL balanceada, espaçamentos em escala base-4/8px, tipografia proporcional e elevações/sombras.
* **Geração do Projeto Reconstruído:**
  * Cria o código-fonte limpo, componentizado e desacoplado na pasta `reconstructed_app/`.
  * **Zero Stubs:** Todos os formulários possuem validação, estados de loading, feedback visual e dados mockados realistas baseados no HAR capturado.
  * Código modular (HTML/Vanilla CSS, React/Vite, Vue ou Next.js conforme o alvo).

### Fase 5 — Quality Gate & Homologação Factual (`Linter + Runtime`)
* Executa o `aidd-linter-design` para garantir zero cores hardcoded e conformidade com os tokens.
* Carrega o app reconstruído no navegador ou emulador e valida se a paridade funcional e visual com o original atinge `>= 98%`.

---

## 3. Estrutura Canônica de Saída do Projeto

Todos os artefatos são persistidos de forma determinística na pasta:  
`docs/reconstruct_{target_name}/`

```
docs/reconstruct_{target_name}/
├── DOSSIE_REVERSA.md               # Relatório executivo completo da engenharia reversa
├── 01_evidence/                    # Evidências brutas factuais
│   ├── network.har                 # Tráfego completo interceptado
│   ├── storage_dump.json           # Cookies, LocalStorage e SessionStorage
│   └── screens/                    # Screenshots Retina 2x de todos os fluxos
├── 02_decompiled/                  # Código desofuscado e recuperado
│   ├── api_contracts.ts            # Tipagens TS e schemas OpenAPI de todos os endpoints
│   ├── business_rules.md           # Lógica de validações e regras de negócio
│   └── recovered_sources/          # Módulos JS/TS/Java recuperados pelo REA
├── 03_mobbin_benchmark/            # Referências de mercado e correções de UX
│   ├── audit_heuristica.md         # Anti-patterns encontrados e solucionados
│   └── benchmark_references.json   # Telas e fluxos de referência consultados
├── 04_design_system/               # Single Source of Truth
│   ├── tokens.json                 # Tokens semânticos
│   └── tokens.css                  # Variáveis CSS prontas para reuso
└── 05_reconstructed_app/           # APLICAÇÃO FINAL RECONSTRUÍDA E FUNCIONAL
    ├── src/                        # Código-fonte limpo sem ofuscação
    ├── public/                     # Assets e ícones otimizados
    ├── mock_server/                # Mock dos endpoints capturados para rodar 100% offline
    └── package.json / index.html   # Projeto pronto para execução (npm run dev / preview)
```

---

## 4. Comandos e Uso

* `/reconstruct run [alvo_url_ou_arquivo]` — Executa as 5 fases ponta a ponta.
  * *Exemplo Web:* `/reconstruct run https://app.exemplo.com/dashboard`
  * *Exemplo APK:* `/reconstruct run ./binaries/aplicativo.apk`
  * *Exemplo Electron:* `/reconstruct run ./resources/app.asar`
* `/reconstruct api [alvo]` — Executa apenas a engenharia reversa de rede, contratos e esquemas de dados.
* `/reconstruct ui [alvo]` — Executa a extração visual, auditoria Mobbin e geração do Design System.

---

## 5. Critérios de Homologação (Quality Gate Binário)

A reconstrução só é considerada CONCLUÍDA se:
1. `DOSSIE_REVERSA.md` documentar todos os endpoints, fluxos e regras mapeadas.
2. Os contratos em `api_contracts.ts` refletirem com fidelidade os dados do `network.har`.
3. O app reconstruído em `05_reconstructed_app/` rodar localmente sem erros de compilação ou console.
4. O `aidd-linter-design` aprovar o código sem ocorrências de valores hardcoded arbitrários.
