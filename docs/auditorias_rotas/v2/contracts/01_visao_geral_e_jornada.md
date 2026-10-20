# 01. Visão Geral e Jornada do Usuário — Rota: contracts (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `contracts`
- **Título Visual no Sistema:** Propostas e Contratos (Documenso & ANVISA)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/contracts`
- **Componente React Raiz:** `frontend/src/features/contracts/ContractsDocumensoWorkspace.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `contracts` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de propostas e contratos (documenso & anvisa).
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `documenso_list`:** Contratos e Assinaturas Eletrônicas
- **Aba / Sub-aba `anvisa_catalog`:** Catálogo Regulatório ANVISA e Lotes
- **Aba / Sub-aba `r2_custody`:** Custódia Segura no Cloudflare R2

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/contracts`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
