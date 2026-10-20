# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: video_sos (Auditoria v2)

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Iniciar Chamada de Vídeo** | Interação direta | Cria sala WebRTC segura com codec VP8/Opus | Ação reativa | Suporte operacional | **100% Funcional** |
| **Alternar Microfone / Câmera** | Interação direta | Controles de mídia locais do operador | Ação reativa | Suporte operacional | **100% Funcional** |
| **Compartilhar Tela de Tomografia** | Interação direta | Transmite corte DICOM 3D para suporte remoto | Ação reativa | Suporte operacional | **100% Funcional** |
| **Encerrar Chamada** | Interação direta | Fecha a sala e dispara transcrição automática Faster-Whisper | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta densidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Adicionar 2º Cirurgião Especialista** | Barra de ações da rota | Botão para incluir médico consultor adicional na chamada | Lacuna identificada no fluxo | `TICKET-SOS-01` |
| **Anotação Visual sobre o Vídeo** | Barra de ações da rota | Ferramenta de desenho e setas sobre o fluxo de vídeo | Lacuna identificada no fluxo | `TICKET-SOS-02` |
