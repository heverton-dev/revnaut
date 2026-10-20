# 01. Visão Geral e Jornada do Usuário — Rota: omnichannel (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `omnichannel`
- **Título Visual no Sistema:** Atendimento Clínico WhatsApp (Omnichannel)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/omnichannel`
- **Componente React Raiz:** `frontend/src/features/inbox/OmnichannelWorkspace.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `omnichannel` atua no ecossistema RevOps proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de atendimento clínico whatsapp (omnichannel).
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `inbox`:** Fila de Conversas Inbox (Chatwoot)
- **Aba / Sub-aba `chat`:** Chat em Tempo Real e Envio de Mídia
- **Aba / Sub-aba `context`:** Barra Lateral de Contexto do Cirurgião
- **Aba / Sub-aba `sos_call`:** Disparador de Chamada SOS Mesa Cirúrgica

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/omnichannel`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
