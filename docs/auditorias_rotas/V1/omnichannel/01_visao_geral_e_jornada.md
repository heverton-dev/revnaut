# 01. Visão Geral e Jornada do Usuário — Rota: omnichannel

## 1. Identificação e Roteamento
- **Identificador / Slug:** `omnichannel`
- **Título Visual no Sistema:** Atendimento WhatsApp & Comunicações
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/omnichannel`
- **Componente React Raiz:** `frontend/src/features/inbox/OmnichannelWorkspace.tsx`

---

## 2. Propósito e Objetivo de Negócio
A rota `omnichannel` atua no ecossistema RevOps proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de atendimento whatsapp & comunicações.
2. Redução do tempo de atendimento e eliminação de processos analógicos na operação.
3. Rastreabilidade ponta a ponta com persistência auditável no SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba `inbox`:** Fila de Conversas e Mensagens
- **Aba `chat_view`:** Área de Mensagens & Envio
- **Aba `context_sidebar`:** Contexto Clínico do Cirurgião
- **Aba `quick_replies`:** Respostas Rápidas e Protocolos

---

## 4. Jornada e Fluxo Operacional
O usuário acessa `#!/omnichannel`, o sistema valida as permissões de RBAC do perfil ativo e carrega os dados específicos da fatia vertical. O operador interage através dos controles dedicados sem recarregar a aplicação.
