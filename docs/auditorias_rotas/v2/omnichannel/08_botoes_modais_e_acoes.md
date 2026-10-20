# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: omnichannel (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Enviar Mensagem** | Interação direta | Dispara payload de texto via Evolution API / WhatsApp | Ação reativa | Suporte operacional | **100% Funcional** |
| **Reproduzir Áudio** | Interação direta | Player de áudio para voice notes recebidas de cirurgiões | Ação reativa | Suporte operacional | **100% Funcional** |
| **Criar Negócio do Chat** | Interação direta | Converte diálogo em oportunidade no funil comercial | Ação reativa | Suporte operacional | **100% Funcional** |
| **Transferir Conversa** | Interação direta | Transfere atendimento para consultor ou especialista técnico | Ação reativa | Suporte operacional | **100% Funcional** |
| **SOS Mesa Cirúrgica** | Interação direta | Abre modal de videoconferência LiveKit instantânea | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Modelos de Resposta Rápida** | Barra de ações da rota | Botão para inserir templates aprovados pela ANVISA | Lacuna identificada no fluxo | `TICKET-OMNI-01` |
| **Anexar Exame 3D ao Chat** | Barra de ações da rota | Atalho para enviar tomografia DICOM direto na conversa | Lacuna identificada no fluxo | `TICKET-OMNI-02` |
