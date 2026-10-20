# 01. Visão Geral e Jornada do Usuário — Rota: contracts

## 1. Identificação e Roteamento
- **Identificador / Slug:** `contracts`
- **Título Visual no Sistema:** Propostas e Contratos (Documenso & ANVISA)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/contracts`
- **Componente React Raiz:** `frontend/src/features/contracts/ContractsDocumensoWorkspace.tsx`

---

## 2. Propósito e Objetivo de Negócio
A rota `contracts` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de propostas e contratos (documenso & anvisa).
2. Redução do tempo de atendimento e eliminação de processos analógicos na operação.
3. Rastreabilidade ponta a ponta com persistência auditável no SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba `documenso_list`:** Contratos & Assinaturas Digitais
- **Aba `anvisa_catalog`:** Catálogo Regulatório & Lotes
- **Aba `r2_custody`:** Custódia de Documentos no Cloudflare R2

---

## 4. Jornada e Fluxo Operacional
O usuário acessa `#!/contracts`, o sistema valida as permissões de RBAC do perfil ativo e carrega os dados específicos da fatia vertical. O operador interage através dos controles dedicados sem recarregar a aplicação.
