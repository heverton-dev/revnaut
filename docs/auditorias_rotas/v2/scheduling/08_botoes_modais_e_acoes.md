# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: scheduling (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Criar Campanha de Retorno** | Interação direta | Define intervalo de retorno e lista de pacientes | Ação reativa | Suporte operacional | **100% Funcional** |
| **Sincronizar Agenda Cal.com** | Interação direta | Consulta compromissos e status de confirmação | Ação reativa | Suporte operacional | **100% Funcional** |
| **Enviar Link de Agendamento** | Interação direta | Dispara link direto para o paciente selecionar horário | Ação reativa | Suporte operacional | **100% Funcional** |
| **Editar Modelo de Mensagem** | Interação direta | Customiza texto com variáveis dinâmicas de nome e data | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Confirmação em 1 Clique (Sim/Não)** | Barra de ações da rota | Webhook para confirmar presença automaticamente por mensagem | Lacuna identificada no fluxo | `TICKET-SCH-01` |
| **Reagendamento de Faltosos** | Barra de ações da rota | Fila prioritária para remarcar pacientes que não compareceram | Lacuna identificada no fluxo | `TICKET-SCH-02` |
