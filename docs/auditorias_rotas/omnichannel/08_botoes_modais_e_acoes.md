# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: omnichannel

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Enviar Mensagem de Texto** | Interação direta | Transmite via Evolution API para o WhatsApp | Ação reativa | Suporte operacional | **100% Funcional** |
| **Anexar Documento / Exame 3D** | Interação direta | Upload e envio de PDF/DICOM para a conversa | Ação reativa | Suporte operacional | **100% Funcional** |
| **Botão SOS Mesa Cirúrgica** | Interação direta | Inicia chamada de emergência e alerta consultor | Ação reativa | Suporte operacional | **100% Funcional** |
| **Transferir Conversa** | Interação direta | Repassa o atendimento para outro consultor ou técnico | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta complexidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Gravar Áudio Direto do Navegador** | Barra de ações da rota | Botão de microfone para enviar PTT no WhatsApp | Lacuna identificada no fluxo | `TICKET-OMNI-01` |
| **Criar Oportunidade a Partir do Chat** | Barra de ações da rota | Atalho para converter cirurgião interessado em deal | Lacuna identificada no fluxo | `TICKET-OMNI-02` |
