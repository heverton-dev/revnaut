# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: rbac

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Novo Membro na Equipe** | Interação direta | Cadastra usuário com papel (Diretor, Gerente, Consultor) | Ação reativa | Suporte operacional | **100% Funcional** |
| **Definir Meta de Faturamento** | Interação direta | Atribui cota mensal em R$ e volume de implantes | Ação reativa | Suporte operacional | **100% Funcional** |
| **Ajustar Percentual de Comissão** | Interação direta | Regula gatilhos de comissionamento por faturamento | Ação reativa | Suporte operacional | **100% Funcional** |
| **Simular Visão do Usuário** | Interação direta | Testa a árvore de permissões e RLS daquele perfil | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta complexidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Bloqueio Temporário de Usuário** | Barra de ações da rota | Desativa credenciais de consultor desligado com 1 clique | Lacuna identificada no fluxo | `TICKET-RBAC-01` |
| **Exportar Folha de Comissões para ERP** | Barra de ações da rota | Gera arquivo de fechamento de comissão para folha TOTVS | Lacuna identificada no fluxo | `TICKET-RBAC-02` |
