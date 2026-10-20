# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: rbac (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Adicionar Nó na Hierarquia** | Interação direta | Cria regional, gerente ou consultor na estrutura | Ação reativa | Suporte operacional | **100% Funcional** |
| **Salvar Matriz de Permissões** | Interação direta | Persiste escopos de leitura/escrita por perfil no SQLite | Ação reativa | Suporte operacional | **100% Funcional** |
| **Definir Meta de Vendas** | Interação direta | Configura cota mensal de faturamento para o consultor | Ação reativa | Suporte operacional | **100% Funcional** |
| **Calcular Comissões do Mês** | Interação direta | Executa motor de cálculo com faixas progressivas e aceleradores | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Simulador de Comissões para o Vendedor** | Barra de ações da rota | Calculadora interativa na tela do consultor comercial | Lacuna identificada no fluxo | `TICKET-RBAC-01` |
| **Histórico de Alterações de Cargo** | Barra de ações da rota | Timeline de promoções e transferências de região | Lacuna identificada no fluxo | `TICKET-RBAC-02` |
