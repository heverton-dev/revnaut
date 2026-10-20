# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: support (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Abrir Protocolo RMA** | Interação direta | Registra intercorrência técnica com recolhimento de implante | Ação reativa | Suporte operacional | **100% Funcional** |
| **Emitir Laudo de Quarentena** | Interação direta | Gera documento técnico para submissão à ANVISA | Ação reativa | Suporte operacional | **100% Funcional** |
| **Reposição Imediata via DENTGO** | Interação direta | Dispara envio de peça de reposição em garantia | Ação reativa | Suporte operacional | **100% Funcional** |
| **Questionário Pós-Operatório B2C** | Interação direta | Envia formulário de cicatrização para o paciente | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Upload de Radiografia Periapical de Falha** | Barra de ações da rota | Formulário específico para anexar imagem da falha | Lacuna identificada no fluxo | `TICKET-SUP-01` |
| **Notificação Direta para Engenharia de Produto** | Barra de ações da rota | Botão de escalonamento para fábrica de implantes | Lacuna identificada no fluxo | `TICKET-SUP-02` |
