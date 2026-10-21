# 08. Auditoria Anatômica de Botões, Modais & Ações — Rota: video_sos (Auditoria V3)

## 1. Inventário Factual de Botões Existentes

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- |
| **Iniciar Chamada de Vídeo** | Interação direta | Cria sala WebRTC segura com codec VP8/Opus | **100% Funcional** |
| **Alternar Microfone / Câmera** | Interação direta | Controles de mídia locais do operador | **100% Funcional** |
| **Compartilhar Tela de Tomografia** | Interação direta | Transmite corte DICOM 3D para suporte remoto | **100% Funcional** |
| **Encerrar Chamada** | Interação direta | Fecha a sala e dispara transcrição automática Faster-Whisper | **100% Funcional** |

---

## 2. Gaps de Interação & Botões Sugeridos
- **Adicionar 2º Cirurgião Especialista** (`TICKET-SOS-01`): Botão para incluir médico consultor adicional na chamada
- **Anotação Visual sobre o Vídeo** (`TICKET-SOS-02`): Ferramenta de desenho e setas sobre o fluxo de vídeo