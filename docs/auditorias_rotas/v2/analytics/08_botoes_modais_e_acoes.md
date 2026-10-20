# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: analytics (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Carregar Dashboard Superset** | Interação direta | Gera token de autenticação e injeta iframe seguro | Ação reativa | Suporte operacional | **100% Funcional** |
| **Executar Pergunta Text-to-SQL** | Interação direta | Traduz pergunta natural em SQL auditado por AST parser | Ação reativa | Suporte operacional | **100% Funcional** |
| **Exportar Resultados SQL em CSV** | Interação direta | Download instantâneo da tabela de dados resultante | Ação reativa | Suporte operacional | **100% Funcional** |
| **Alternar Filtros de Tempo (7d, 30d, 90d)** | Interação direta | Atualiza parâmetros das visualizações analíticas | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Salvar Consulta no Favoritos** | Barra de ações da rota | Botão para favoritar queries frequentes de Text-to-SQL | Lacuna identificada no fluxo | `TICKET-ANA-01` |
| **Agendamento de Envio por E-mail** | Barra de ações da rota | Disparo automático do relatório consolidado semanal | Lacuna identificada no fluxo | `TICKET-ANA-02` |
