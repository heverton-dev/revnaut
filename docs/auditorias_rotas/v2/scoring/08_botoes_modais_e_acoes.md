# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: scoring (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Recalcular Scores** | Interação direta | Dispara recálculo determinístico em lote de toda a base | Ação reativa | Suporte operacional | **100% Funcional** |
| **Filtrar por Tier (A/B/C)** | Interação direta | Filtra cards de cirurgiões pelo potencial cirúrgico | Ação reativa | Suporte operacional | **100% Funcional** |
| **Exportar Matriz** | Interação direta | Gera snapshot das regras e clientes classificados | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Ajuste Interativo de Pesos (Sliders)** | Barra de ações da rota | Calibração dinâmica de pesos na UI pelo gestor | Lacuna identificada no fluxo | `TICKET-SCORING-01` |
| **Handoff Automático para Vendedor** | Barra de ações da rota | Botão para atribuição automática de leads Tier A a consultores seniores | Lacuna identificada no fluxo | `TICKET-SCORING-02` |
