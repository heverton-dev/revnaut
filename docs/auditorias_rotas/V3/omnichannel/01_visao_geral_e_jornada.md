# 01. Visão Geral e Jornada do Usuário — Rota: omnichannel (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/omnichannel`
- **Título Oficial:** Atendimento Clínico WhatsApp (Omnichannel)
- **Componente Front-end:** `frontend/src/features/inbox/OmnichannelWorkspace.tsx`
- **Motores Backend:** `src/features/integrations/omnichannel/router.py`, `src/features/communications/router.py`
- **Suíte de Testes:** `tests/test_chatwoot_omnichannel_context_sidebar.py`, `tests/test_evolution_signed_call_offer.py`, `tests/test_omnichannel_webhooks.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `inbox`:** Fila de Conversas Inbox (Chatwoot)
- **Aba `chat`:** Chat em Tempo Real e Envio de Mídia
- **Aba `context`:** Barra Lateral de Contexto do Cirurgião
- **Aba `sos_call`:** Disparador de Chamada SOS Mesa Cirúrgica