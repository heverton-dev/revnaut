# 01. Visão Geral e Jornada do Usuário — Rota: video_sos (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/video_sos`
- **Título Oficial:** Chamadas e Vídeo SOS Mesa Cirúrgica (LiveKit)
- **Componente Front-end:** `frontend/src/features/communications/LiveKitDealRoomModal.tsx`
- **Motores Backend:** `src/features/communications/router.py`, `src/features/intelligence/router.py`
- **Suíte de Testes:** `tests/test_surgical_sos_livekit.py`, `tests/test_livekit_webrtc_sip.py`, `tests/test_faster_whisper_diarization.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `video`:** Videoconferência WebRTC LiveKit em Tempo Real
- **Aba `voip`:** Telefonia SIP Direta com Especialista
- **Aba `recording`:** Histórico de Gravações & Transcrições Whisper