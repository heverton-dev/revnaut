# 01. Visão Geral e Jornada do Usuário — Rota: video_sos

## 1. Identificação e Roteamento
- **Identificador / Slug:** `video_sos`
- **Título Visual no Sistema:** Chamadas e Vídeo SOS (Mesa Cirúrgica)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/video_sos`
- **Componente React Raiz:** `frontend/src/features/communications/LiveKitDealRoomModal.tsx`

---

## 2. Propósito e Objetivo de Negócio
A rota `video_sos` atua no ecossistema RevOps proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de chamadas e vídeo sos (mesa cirúrgica).
2. Redução do tempo de atendimento e eliminação de processos analógicos na operação.
3. Rastreabilidade ponta a ponta com persistência auditável no SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba `video`:** Videoconferência WebRTC LiveKit
- **Aba `voip`:** Telefonia SIP Direta com Especialista
- **Aba `recording`:** Histórico de Gravações & Transcrições

---

## 4. Jornada e Fluxo Operacional
O usuário acessa `#!/video_sos`, o sistema valida as permissões de RBAC do perfil ativo e carrega os dados específicos da fatia vertical. O operador interage através dos controles dedicados sem recarregar a aplicação.
