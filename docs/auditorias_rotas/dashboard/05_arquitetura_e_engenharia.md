# 05. Arquitetura e Engenharia de Software — Rota: dashboard

## 1. Aderência à Arquitetura VSA (Vertical Slice Architecture)

A rota do Dashboard consome funcionalidades distribuídas em fatias verticais autônomas:

- **Frontend:**
  - O componente raiz reside em `frontend/src/features/bi/SupersetEmbeddedDashboard.tsx`.
  - Atualmente, o arquivo agrega tanto o **Cockpit Executivo** (rota `/#!/dashboard`) quanto o **Estúdio BI Superset + Text-to-SQL** (rota `/#!/analytics`) em um único arquivo de mais de 1.000 linhas.
  - **Recomendação VSA:** Desacoplar a rota `/#!/dashboard` em um componente específico `ExecutiveCockpitView.tsx`, mantendo `SupersetEmbeddedDashboard.tsx` focado estritamente na integração do Apache Superset e Text-to-SQL da rota `/#!/analytics`.

- **Backend:**
  - As fatias verticais em `src/features/intelligence/`, `src/features/deals/` e `src/features/campaigns/` respeitam o padrão VSA, mantendo seus próprios routers, schemas e lógicas de domínio bem encapsulados.

---

## 2. Desempenho e Concorrência

### 2.1. Eliminação de Waterfalls no Frontend
- A carga inicial do Cockpit Executivo utiliza `Promise.all` para disparar em paralelo as 5 requisições de backend:
  ```typescript
  const [mRes, cRes, chRes, cgRes, dRes] = await Promise.all([
    fetch("/api/v1/metrics"),
    fetch("/api/v1/campaigns/metrics"),
    fetch("/api/v1/intelligence/churn-risk"),
    fetch("/api/v1/intelligence/clinical-graph"),
    fetch("/api/v1/deals"),
  ]);
  ```
- **Impacto Prático:** Redução drástica do First Contentful Paint (FCP) de métricas, permitindo renderização imediata sem bloqueio sequencial em cascata.

### 2.2. Persistência em SQLite WAL
- O banco de dados opera com o modo de journal **WAL (Write-Ahead Logging)** ativado (`PRAGMA journal_mode=WAL;`).
- Isso garante que consultas analíticas pesadas disparadas pelo Dashboard (como agregação de deals ou contagem de nós) não travem as operações de escrita transacional (ex: fechamento de vendas, criação de leads).

---

## 3. Gestão de Estado e Re-renderizações

- **Memoização Eficiente:** O cálculo das barras do gráfico analítico é protegido por `React.useMemo` dependendo apenas de `[chartViewMode, dealsData, pipelineMetrics]`, prevenindo re-computações desnecessárias durante alterações de abas ou digitação.
- **Isolamento de Erros:** O componente utiliza tratamento gracioso com fallbacks para evitar a quebra total da tela caso um dos 5 microsserviços responda com erro HTTP 500.
