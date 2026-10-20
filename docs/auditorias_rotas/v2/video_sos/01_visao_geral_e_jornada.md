# 01. Visão Geral e Jornada do Usuário — Rota: video_sos (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `video_sos`
- **Título Visual no Sistema:** Chamadas e Vídeo SOS Mesa Cirúrgica (LiveKit)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/video_sos`
- **Componente React Raiz:** `frontend/src/features/communications/LiveKitDealRoomModal.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `video_sos` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de chamadas e vídeo sos mesa cirúrgica (livekit).
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `video`:** Videoconferência WebRTC LiveKit em Tempo Real
- **Aba / Sub-aba `voip`:** Telefonia SIP Direta com Especialista
- **Aba / Sub-aba `recording`:** Histórico de Gravações & Transcrições Whisper

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/video_sos`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
