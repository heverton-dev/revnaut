# 01. Visão Geral e Jornada do Usuário — Rota: contacts (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `contacts`
- **Título Visual no Sistema:** Dentistas e Clínicas (CRM Cirúrgico)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/contacts`
- **Componente React Raiz:** `frontend/src/features/contacts/ContactsCrmWorkspace.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `contacts` atua no ecossistema RevOps proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de dentistas e clínicas (crm cirúrgico).
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `crm_surgeons`:** Cirurgiões Dentistas Cadastrados
- **Aba / Sub-aba `institutions`:** Clínicas, Hospitais e Polos
- **Aba / Sub-aba `cfo_compliance`:** Validação de Registro CFO / CRO Ativo
- **Aba / Sub-aba `icp_scoring`:** Qualificação e Enriquecimento ICP

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/contacts`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
