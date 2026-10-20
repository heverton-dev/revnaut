# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: scheduling

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Disparar Campanha de Manutenção** | Interação direta | Envia convites de agendamento preventivo para pacientes | Ação reativa | Suporte operacional | **100% Funcional** |
| **Sincronizar com Cal.com** | Interação direta | Importa horários vagos e consultas marcadas | Ação reativa | Suporte operacional | **100% Funcional** |
| **Editar Template de Reativação** | Interação direta | Personaliza mensagem de revisão periódica de implante | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta complexidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Confirmação Automática por Botão 1-Clique** | Barra de ações da rota | Link para paciente confirmar ou remarcar pelo WhatsApp | Lacuna identificada no fluxo | `TICKET-SCHED-01` |
| **Bloqueio de Agenda por Falta de Material** | Barra de ações da rota | Trava horário se o kit de implante não estiver na clínica | Lacuna identificada no fluxo | `TICKET-SCHED-02` |
