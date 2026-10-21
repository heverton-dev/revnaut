# 01. Visão Geral e Jornada do Usuário — Rota: settings (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/settings`
- **Título Oficial:** Configurações, Vault & Conexão TOTVS ERP
- **Componente Front-end:** `frontend/src/features/settings/CredentialsVaultPage.tsx`
- **Motores Backend:** `src/features/settings/router.py`, `src/features/integrations/totvs/router.py`, `src/features/integrations/omnichannel/router.py`
- **Suíte de Testes:** `tests/test_credentials_vault.py`, `tests/test_totvs_integration.py`, `tests/test_outbound_webhooks_hmac.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `vault`:** Cofre Seguro de Chaves de API e Segredos
- **Aba `erp`:** Conexão TOTVS Protheus & Sincronização de Notas
- **Aba `webhooks`:** Webhooks Studio & Assinaturas HMAC
- **Aba `users`:** Gestão de Usuários e Perfis de Acesso