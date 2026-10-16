# Auditoria Heurística & Anatomia de UX — Rvops CRM

> **Metodologia:** Benchmarking via Mobbin MCP (Unify, Square, Gumloop) e Heurísticas de Nielsen aplicadas a B2B RevOps SaaS.

---

## 1. Mapeamento de Anti-Patterns do Original (Rvops)

| # | Módulo | Anti-Pattern Detectado | Impacto no Usuário | Solução de Elite (Mobbin/AIDD) |
|---|---|---|---|---|
| **01** | **Autenticação & MFA** | Modal de MFA invasivo no primeiro acesso sem explicação do valor de segurança. | Fricção e abandono no login de novos colaboradores. | Banner contextual não bloqueante ou fluxo guiado com opção persistente de adiamento seguro. |
| **02** | **Funil de Negócios** | Kanban com scroll horizontal desbalanceado e cabeçalho poluído por dropdowns aninhados. | Fadiga visual, dificuldade de arrasto e perda de contexto sobre o total de negócios. | Colunas com contadores de valor/quantidade no topo, drag-and-drop suave com Ghost preview e visual switcher claro (Lista / Kanban). |
| **03** | **Contatos & Leads** | Filtros em múltiplos menus dropdowns lentos com renderização no backend. | Fricção na busca diária de leads e segmentação de base. | Filtros facetados em formato de *Pills* (Tags com contadores ativos), busca instantânea debounced e seleção em massa. |
| **04** | **Caixa de Entrada / Chat** | Falta de distinção clara entre WhatsApp Oficial, Webchat e SMS na listagem de mensagens. | Erro humano no tom da conversa ou atraso no atendimento urgente. | Badges de status de canal (WhatsApp verde com ícone, Webchat azul, etc.), indicador de digitação e atalho para criar negócio inline. |
| **05** | **Dashboards & Relatórios** | Gráficos sem granularidade temporal dinâmica (apenas filtros fixos). | O decisor de RevOps não consegue navegar de mês para semana com 1 clique. | Time-range selector com atalhos rápidos (Hoje, Últimos 7d, Mês Atual) e cartões com delta percentual comparativo (+12% vs. mês anterior). |

---

## 2. Princípios de Craft Adotados na Reconstrução

1. **Hierarchy First:** As métricas financeiras (MRR, Pipeline Total, Taxa de Conversão) sempre ocupam a primeira linha visual.
2. **Micro-interações Suaves:** Hover states em linhas de tabela, feedback otimista em transições de status no Kanban e skeletons durante carregamentos.
3. **Ergonomia e Densidade B2B:** Modo compacto para operadores avançados (SDRs/BDRs) com suporte completo a atalhos de teclado.
