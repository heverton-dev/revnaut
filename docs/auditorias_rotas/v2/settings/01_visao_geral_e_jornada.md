# 01. Visão Geral e Jornada do Usuário — Rota: settings (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `settings`
- **Título Visual no Sistema:** Configurações, Vault & Conexão TOTVS ERP
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/settings`
- **Componente React Raiz:** `frontend/src/features/settings/CredentialsVaultPage.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `settings` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de configurações, vault & conexão totvs erp.
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `vault`:** Cofre Seguro de Chaves de API e Segredos
- **Aba / Sub-aba `erp`:** Conexão TOTVS Protheus & Sincronização de Notas
- **Aba / Sub-aba `webhooks`:** Webhooks Studio & Assinaturas HMAC
- **Aba / Sub-aba `users`:** Gestão de Usuários e Perfis de Acesso

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/settings`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
