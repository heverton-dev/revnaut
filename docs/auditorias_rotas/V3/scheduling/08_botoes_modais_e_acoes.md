# 08. Auditoria Anatômica de Botões, Modais & Ações — Rota: scheduling (Auditoria V3)

## 1. Inventário Factual de Botões Existentes

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- |
| **Criar Campanha de Retorno** | Interação direta | Define intervalo de retorno e lista de pacientes | **100% Funcional** |
| **Sincronizar Agenda Cal.com** | Interação direta | Consulta compromissos e status de confirmação | **100% Funcional** |
| **Enviar Link de Agendamento** | Interação direta | Dispara link direto para o paciente selecionar horário | **100% Funcional** |
| **Editar Modelo de Mensagem** | Interação direta | Customiza texto com variáveis dinâmicas de nome e data | **100% Funcional** |

---

## 2. Gaps de Interação & Botões Sugeridos
- **Confirmação em 1 Clique (Sim/Não)** (`TICKET-SCH-01`): Webhook para confirmar presença automaticamente por mensagem
- **Reagendamento de Faltosos** (`TICKET-SCH-02`): Fila prioritária para remarcar pacientes que não compareceram