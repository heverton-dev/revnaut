# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: dashboard (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Visualizar por Estágio** | Interação direta | Alterna o gráfico central para visão por estágio de funil | Ação reativa | Suporte operacional | **100% Funcional** |
| **Visualizar por Tendência** | Interação direta | Alterna o gráfico central para série temporal de MRR | Ação reativa | Suporte operacional | **100% Funcional** |
| **Visualizar Consignação** | Interação direta | Alterna o gráfico central para giro de maletas e CFOP 5.113 | Ação reativa | Suporte operacional | **100% Funcional** |
| **Card Pipeline Total** | Interação direta | Exibe valor total negociado e taxa de conversão | Ação reativa | Suporte operacional | **100% Funcional** |
| **Card MRR / Fechado Ganho** | Interação direta | Exibe receita recorrente e novos contratos | Ação reativa | Suporte operacional | **100% Funcional** |
| **Card Performance Mídia** | Interação direta | Exibe ROAS consolidado e CAC médio | Ação reativa | Suporte operacional | **100% Funcional** |
| **Card Alertas de Churn** | Interação direta | Exibe contagem de cirurgiões em risco crítico | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Exportar Relatório Executivo PDF** | Barra de ações da rota | Disparo direto de download do snapshot do cockpit | Lacuna identificada no fluxo | `TICKET-DASH-01` |
| **Filtro Global por Regional** | Barra de ações da rota | Dropdown para filtrar KPIs por divisão geográfica | Lacuna identificada no fluxo | `TICKET-DASH-02` |
