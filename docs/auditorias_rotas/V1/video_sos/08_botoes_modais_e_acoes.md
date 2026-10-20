# 08. Auditoria Anatômica de Botões, Modais & Ações de Interface — Rota: video_sos

## 1. Inventário Factual de Botões Existentes na Rota

| Elemento / Rótulo Visual | Gatilho Técnico | O Que Faz | O Que Abre / Dispara | Por Que Existe (Propósito de Negócio) | Status Factual de Funcionamento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Entrar na Sala SOS** | Interação direta | Gera token de sala LiveKit e ativa áudio/vídeo | Ação reativa | Suporte operacional | **100% Funcional** |
| **Compartilhar Tomografia / Exame** | Interação direta | Transmite tela ou janela DICOM para o consultor | Ação reativa | Suporte operacional | **100% Funcional** |
| **Iniciar Gravação Clínica** | Interação direta | Grava a chamada para arquivo de tecnovigilância | Ação reativa | Suporte operacional | **100% Funcional** |
| **Desligar / Encerrar Chamada** | Interação direta | Desconecta WebRTC e finaliza sala | Ação reativa | Suporte operacional | **100% Funcional** |

---

## 2. Modais e Gavetas (Drawers) na Rota
As ações de alta complexidade disparam formulários em modais Dialog centralizados ou gavetas laterais Sheet, garantindo que o operador não perca o contexto de navegação.

---

## 3. Catálogo de Botões Faltantes (Gaps de Interação & UX)

| Botão Faltante | Localização Sugerida na Tela | O Que Deveria Abrir / Fazer | Por Que Está Faltando (Impacto na Jornada) | Micro-Ticket Vinculado |
| :--- | :--- | :--- | :--- | :--- |
| **Snapshot / Foto da Tela com Anotações** | Barra de ações da rota | Captura frame do vídeo para desenhar na tomografia ao vivo | Lacuna identificada no fluxo | `TICKET-SOS-01` |
| **Troca Rápida de Câmera (Endoscópio)** | Barra de ações da rota | Seletor de fonte de vídeo médica | Lacuna identificada no fluxo | `TICKET-SOS-02` |
