# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: deals (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Novo Negócio** | Interação direta | Abre modal Dialog para criação rápida de oportunidade | Ação reativa | Suporte operacional | **100% Funcional** |
| **Alternar Tabela / Kanban** | Interação direta | Altera modo visual de renderização com persistência de estado | Ação reativa | Suporte operacional | **100% Funcional** |
| **Filtrar por Pipeline** | Interação direta | Dropdown seletor de funis comerciais cadastrados | Ação reativa | Suporte operacional | **100% Funcional** |
| **Buscar Negociação** | Interação direta | Filtro em tempo real por nome de cirurgião, clínica ou valor | Ação reativa | Suporte operacional | **100% Funcional** |
| **Exportar CSV** | Interação direta | Download instantâneo da listagem de oportunidades | Ação reativa | Suporte operacional | **100% Funcional** |
| **Abrir Gaveta do Negócio** | Interação direta | Drawer lateral com timeline, copilot Granola e contratos | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Aprovação Rápida de Desconto** | Barra de ações da rota | Ação de aprovação em 1 clique para descontos acima da alçada | Lacuna identificada no fluxo | `TICKET-DEALS-01` |
| **Reordenar Estágios do Funil** | Barra de ações da rota | Drag and drop de colunas de estágio para gestores | Lacuna identificada no fluxo | `TICKET-DEALS-02` |
