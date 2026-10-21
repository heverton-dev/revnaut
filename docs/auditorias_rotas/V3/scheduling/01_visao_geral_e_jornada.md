# 01. Visão Geral e Jornada do Usuário — Rota: scheduling (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/scheduling`
- **Título Oficial:** Reativação de Pacientes (Cal.com)
- **Componente Front-end:** `frontend/src/features/scheduling/CalcomReactivationWorkspace.tsx`
- **Motores Backend:** `src/features/scheduling/router.py`, `src/features/integrations/omnichannel/router.py`
- **Suíte de Testes:** `tests/test_calcom_patient_reactivation.py`, `tests/test_outbound_webhooks_hmac.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `campaigns`:** Campanhas de Reativação Cal.com
- **Aba `appointments`:** Agenda de Consultas Confirmadas
- **Aba `templates`:** Modelos de Mensagens WhatsApp / SMS