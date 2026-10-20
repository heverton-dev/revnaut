# 01. Visão Geral e Jornada do Usuário — Rota: settings

## 1. Identificação e Roteamento
- **Identificador / Slug:** `settings`
- **Título Visual no Sistema:** Configurações e Notas Fiscais (Cofre & ERP TOTVS)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/settings`
- **Componente React Raiz:** `frontend/src/features/settings/CredentialsVaultPage.tsx`

---

## 2. Propósito e Objetivo de Negócio
A rota `settings` atua no ecossistema RevOps proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de configurações e notas fiscais (cofre & erp totvs).
2. Redução do tempo de atendimento e eliminação de processos analógicos na operação.
3. Rastreabilidade ponta a ponta com persistência auditável no SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba `vault`:** Cofre Seguro de Chaves de API e Segredos
- **Aba `erp`:** Conexão TOTVS Protheus & Sincronização Fiscal
- **Aba `webhooks`:** Webhooks Studio & Assinaturas HMAC
- **Aba `users`:** Gestão de Usuários e Perfis

---

## 4. Jornada e Fluxo Operacional
O usuário acessa `#!/settings`, o sistema valida as permissões de RBAC do perfil ativo e carrega os dados específicos da fatia vertical. O operador interage através dos controles dedicados sem recarregar a aplicação.
