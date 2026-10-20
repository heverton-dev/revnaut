---
name: aidd-route-analyze
description: Orquestrador filarmonico deterministico para auditoria profunda de rotas e sub-rotas (SPA, Backend API, Webhook e Hibridas). Executa analise de codigo factual, engenharia reversa de contratos (REA), diagnostico de UI/UX Impeccable, subprodutizacao de motores, cyber-seguranca e RLS, arquitetura VSA, especificacao BDD/TDD/SDD, geracao de micro-tickets cirurgicos e compilacao final em PDF corporativo diagramado, com Quality Gates inquebraveis (exit 0 / exit 1).
---

# AIDD Route Analyze — Orquestrador Filarmônico de Auditoria de Rotas

## 1. Visão Geral & Finalidade
A skill `aidd-route-analyze` orquestra a auditoria técnica mais profunda, cadenciada e determinística do ecossistema AIDD. Operando como um maestro regendo uma orquestra de ferramentas especializadas, cada rota ou sub-rota submetida passa por uma FSM (Máquina de Estados Finitos) sequencial, com validação factual no código-fonte, inspeção de tokens e contratos de rede, verificação de subprodutização do motor, geração de dossiê em Markdown (`docs/auditorias_rotas/<slug_rota>/`) e compilação final em **PDF diagramado em nível executivo/corporativo**.

---

## 2. Invariantes Inegociáveis (Leis Canônicas)
1. **Lei #14 (Zero Emojis):** É terminantemente proibido o uso de qualquer caractere de emoji nos artefatos da auditoria, nos relatórios ou nas telas inspecionadas. Apenas ícones vetoriais SVG (Lucide/shadcn) são tolerados.
2. **Lei #5 (Zero Stubs / Zero Mocks):** Todo gap identificado deve resultar em micro-tickets cirúrgicos com código real e critérios binários de teste. Sem placeholders ou mocks de fachada.
3. **Todo Portão Deve Morder (Lei #13):** Cada transição de fase é protegida por um Quality Gate em script Python (`exit 0` = aprovação, `exit 1` = bloqueio).
4. **Isolamento Cirúrgico & Token Economy:** O grafo de conhecimento (`codebase-memory-mcp`) deve ser consultado antes de varreduras extensivas de disco. Todos os artefatos intermediários ficam isolados no escopo da rota.

---

## 3. As 8 Fases da Orquestração Filarmônica

```
[Entrada: Rota / Sub-rota / URL]
       │
       ▼
[FASE 00: Roteamento & Dispatch] ➔ python .agents/skills/aidd-route-analyze/scripts/dispatcher.py "<alvo>"
       │   GATE: G_ROUTE_DISPATCH.py (exit 0/1)
       ▼
[FASE 01: Cartografia via Grafo] ➔ codebase-memory-mcp (search_graph / detect_changes)
       │   Mapeia routers, views, tabelas, schemas e dependencias.
       ▼
[FASE 02: REA Runtime & Contratos] ➔ REA (reverse-engineer-anything)
       │   Analisa endpoints no DOM, chamadas de fetch/API, contratos de rede e payloads.
       ▼
[FASE 03: UI/UX Impeccable] ➔ Impeccable Flags (visual-hierarchy, breathing-room, overflow, tokens)
       │   GATE: G_UI_IMPECCABLE.py (Valida zero emojis e consistencia de tokens)
       ▼
[FASE 04: Motores & Subprodutização] ➔ Motor vs Tela
       │   Cruza funcoes e filtros do backend com o que a interface consome (recursos ociosos).
       ▼
[FASE 05: Cyber-Segurança, RBAC & RLS] ➔ Seguranca de Fato
       │   GATE: G_SECURITY_RLS.py (Verifica tenant isolation, IDOR, sanitizacao)
       ▼
[FASE 06: Tríade DD (TDD, BDD, SDD)] ➔ Engenharia com Prova Real
       │   Cenarios Gherkin (BDD) + Contratos de Testes Red-Green (TDD) + Rastreabilidade (SDD).
       ▼
[FASE 07: Emissão do Dossiê & Micro-Tickets] ➔ python .agents/skills/aidd-route-analyze/scripts/dossier_generator.py
       │   GATE: G_DOSSIER_COMPLETE.py (Garante 8 arquivos Markdown preenchidos e integros)
       ▼
[FASE 08: Compilação de PDF Corporativo] ➔ python .agents/skills/aidd-route-analyze/scripts/pdf_compiler.py "<slug>"
       │   GATE: G_PDF_GENERATED.py (Valida compilacao e integridade do PDF final)
```

---

## 4. Estrutura do Dossiê Canônico (`docs/auditorias_rotas/<slug_rota>/`)

Todo ciclo gera rigorosamente 8 arquivos estruturados e 1 PDF consolidado:

1. `01_visao_geral_e_jornada.md`: Propósito funcional, taxonomia da rota e mapeamento da jornada do usuário.
2. `02_ui_ux_impeccable.md`: Diagnóstico heurístico Impeccable (hierarquia visual, respiro, transbordo/overflow, acessibilidade e conformidade Lei #14).
3. `03_motores_e_subprodutizacao.md`: Catálogo dos motores acionados, capacidades existentes no backend e lista de subprodutização (recursos ociosos não expostos).
4. `04_cyber_seguranca_e_rls.md`: Matriz RBAC, isolamento multi-tenant, vetores de IDOR e telemetria segura (PII).
5. `05_arquitetura_e_engenharia.md`: Aderência VSA, complexidade, integridade de transações SQLite WAL e acoplamento.
6. `06_especificacao_dd.md`: Especificação BDD Gherkin, plano de testes TDD Red-Green e invariantes SDD.
7. `07_plano_micro_tickets.md`: Decomposição atômica de melhorias em micro-tickets (O Quê, Como, Onde com arquivo e linha, Critério Binário de Aceitação).
8. `RELATORIO_CONSOLIDADO.md`: Resumo executivo com veredito dos Quality Gates e plano imediato.
9. `RELATORIO_AUDITORIA_<slug>.pdf`: Documento executivo unificado diagramado em A4 com tipografia Inter, capa, metadados e rodapé paginado.

---

## 5. Como Invocar e Executar

Ao receber o comando `/aidd-route-analyze <rota_ou_url>`, execute os passos em sequência:

```bash
# 1. Roteamento Inteligente
python .agents/skills/aidd-route-analyze/scripts/dispatcher.py "<rota_ou_url>"
python .agents/skills/aidd-route-analyze/gates/G_ROUTE_DISPATCH.py

# 2. Inicializar Scaffold do Dossiê
python .agents/skills/aidd-route-analyze/scripts/dossier_generator.py "<slug>"

# 3. Executar as fases de analise factual no codigo-fonte e preencher os 8 arquivos

# 4. Validar os Quality Gates dos Dossiês
python .agents/skills/aidd-route-analyze/gates/G_UI_IMPECCABLE.py "<slug>"
python .agents/skills/aidd-route-analyze/gates/G_SECURITY_RLS.py "<slug>"
python .agents/skills/aidd-route-analyze/gates/G_DOSSIER_COMPLETE.py "<slug>"

# 5. Compilar Dossiê em PDF Corporativo e Validar
python .agents/skills/aidd-route-analyze/scripts/pdf_compiler.py "<slug>"
python .agents/skills/aidd-route-analyze/gates/G_PDF_GENERATED.py "<slug>"
```
