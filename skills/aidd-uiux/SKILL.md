---
name: aidd-uiux
description: Orquestrador autônomo do pipeline de UI/UX de alta fidelidade (Craft Floor). Encadeia benchmarking no Mobbin MCP, compilação de design system pela skill Impeccable, inspeção visual factual no Chrome DevTools MCP e homologação Human-in-the-Loop (HITL) via Quality Gates.
commands:
  - "/aidd-uiux"
  - "/uiux"
  - "/craft"
  - "/impeccable-flow"
---

# AIDD-UIUX • Orquestrador Autônomo de UI/UX de Alta Fidelidade

> **Governança Canônica AIDD:** Determinismo Estrito (Lei #1), Qualidade Binária (Lei #2), Persistência Estruturada (Lei #3), Zero Stubs (Lei #5) e Desenvolvedor no Controle / HITL (Lei #7).  
> **Propósito:** Automatizar o ciclo completo de modernização e elevação de craft visual de interfaces web e mobile sem quebrar a consistência da marca.

---

## 1. Princípio de Ouro: Anatomia vs. Identidade

Para garantir harmonia estética inabalável e evitar o efeito "colcha de retalhos":
1. **Do Mobbin MCP:** Extrai-se **apenas** anatomia, arquitetura de informação, densidade de componentes e fluxos de interação comprovados pelo mercado.
2. **Do Motor Impeccable:** Compila-se e impõe-se **estritamente** o Design System local (tokens semânticos, paleta da marca, escala base-4/8px, tipografia instrumental e regras de contraste WCAG AA/AAA).
3. **Do DevTools MCP:** Coleta-se **prova factual em runtime** (zero especulação visual; captura de viewport real e detecção de refluxos/quebras de layout).

---

## 2. Gatilhos & Comandos

A skill é acionada por comando explícito ou intenção de melhoria de interface:
* `/aidd-uiux run [alvo] [termo_mobbin]` — Executa a esteira completa ponta a ponta.
* `/aidd-uiux audit [alvo]` — Audita anti-patterns, contraste e captura screenshot do estado inicial via DevTools.
* `/aidd-uiux bench [termo] [plataforma]` — Consulta referências no Mobbin MCP e extrai padrões anatômicos.
* `/aidd-uiux refactor [componente]` — Aplica os 7 pilares do Impeccable (Layout, Typeset, Colorize, Optimize, Animate, Polish, Tokens).
* `/aidd-uiux verify [url]` — Recarrega o navegador real, valida contenção de layout e gera evidência comparativa.

Também responde a linguagem natural:
* *"refatore a tela de estoque com o fluxo aidd-uiux"*
* *"melhore o kanban de consumo usando referências do mobbin e padrão impecável"*

---

## 3. Protocolo de Execução Encadeado (As 5 Fases)

Ao ser acionada no modo completo (`run`), o agente DEVE seguir sequencialmente:

### Fase 1 — Diagnóstico Inicial em Runtime (DevTools MCP)
1. Verificar se o servidor local está ativo na porta do projeto. Se offline, iniciá-lo em segundo plano (`IsDaemon: true`).
2. Conectar via `chrome-devtools-mcp` (ou `playwright`), navegar até a URL do componente e executar `take_screenshot` para estabelecer o **marco zero visual**.
3. Diagnosticar anti-patterns no DOM: quebras indesejadas de linha (`white-space`), reflows, alinhamentos caóticos e ausência de contenção (`contain`).

### Fase 2 — Benchmarking Estrutural (Mobbin MCP)
1. Invocar a tool `mobbin_buscar_telas` passando a `query` de domínio (ex: `"dental clinic inventory"`, `"medical kanban"`, `"b2b data table"`).
2. Analisar as telas retornadas para identificar a melhor distribuição espacial de filtros, paginação, cards e micro-ações.
3. Se aplicável, invocar `mobbin_extrair_tokens` para mapear espaçamentos e ritmos visuais líderes.

### Fase 3 — Compilação Normativa e Refatoração (Motor Impeccable)
1. **Tradução Mandatória:** Descartar cores e fontes literais do Mobbin; aplicar exclusivamente os tokens do CSS do projeto (`--brand-*`, `--space-*`, `--radius-*`).
2. **Tipografia Instrumental:** Aplicar fontes semânticas (ex: `Plus Jakarta Sans`) e `tabular-nums` em todas as colunas com números, lotes, códigos de barras ou valores monetários.
3. **Escala de Espaçamento Base-4/8px:** Substituir margens e paddings arbitrários por tokens harmonizados.
4. **Resolução de Anti-Patterns:**
   * Garantir `white-space: nowrap` e `flex-shrink: 0` em botões, tags e menus de cabeçalho.
   * Garantir aceleração por GPU (`will-change: transform`) em modais e gavetas laterais.
   * Adicionar suporte estrito a `@media (prefers-reduced-motion: reduce)`.
   * Configurar `:focus-visible` cirúrgico e scrollbars médicas sutis.
5. **Zero Placeholders:** Se faltar imagens ou ícones, gerar assets autorais via `generate_image` ou SVGs puros inline.

### Fase 4 — Prova Factual de Runtime (DevTools MCP)
1. Forçar reload do navegador real via `navigate_page` ou script de navegação.
2. Inspecionar o console do navegador (`list_console_messages`) garantindo zero erros de JavaScript ou quebra de recursos.
3. Executar `take_screenshot` no mesmo viewport exato da Fase 1 para gerar o par comparativo **Antes vs. Depois**.

### Fase 5 — Registro HITL e Quality Gate (Human-in-the-Loop & Git)
1. Registrar todas as alterações no arquivo de governança do projeto (ex: `DECISOES_IMPECCABLE.md` ou equivalente), estruturado por ID (`DEC-01`, `DEC-02`), Racional Técnico e Impacto.
2. Atualizar o painel web de homologação rápida (se existente no workspace).
3. **Ponto de Parada HITL:** Apresentar o resumo comparativo ao desenvolvedor com links para os arquivos e screenshots.
4. Sob confirmação do desenvolvedor, efetivar o commit atômico no Git com mensagem semântica (ex: `feat(uiux): refatora esteira kanban sob protocolo aidd-uiux`).

---

## 4. Checklist do Quality Gate (Qualidade Binária)

Antes de considerar qualquer entrega finalizada, a skill exige verificação factual dos seguintes critérios:

- [ ] Servidor de aplicação rodando e respondendo HTTP 200.
- [ ] Zero quebras de linha acidentais em cabeçalhos, botões ou chips de status.
- [ ] Números, lotes e valores com alinhamento tabular (`tabular-nums`).
- [ ] Cores literais fora de variáveis CSS: **Zero**.
- [ ] Console do navegador sem erros de runtime (`list_console_messages`).
- [ ] Screenshot de validação capturada e acessível em disco.
- [ ] Registro documental HITL persistido para auditoria.

---

## 5. Formato de Resposta ao Usuário (Rule 10 & Lei #4)

Ao concluir uma execução da skill, responda estritamente neste padrão:
1. **Primeira linha:** O que foi executado e transformado na interface.
2. **Tabela de Decisões:** Tópicos factuais com *ID ➔ O que mudou ➔ Por que mudou ➔ Impacto visual*.
3. **Evidência Visual:** Links diretos para os arquivos alterados e caminho da screenshot gerada.
4. **Ação HITL:** Pergunta direta para homologação do desenvolvedor (`Deseja aprovar e commitar estas alterações?`).
