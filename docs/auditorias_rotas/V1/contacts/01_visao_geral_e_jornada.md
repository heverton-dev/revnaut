# 01. Visão Geral e Jornada do Usuário — Rota: contacts

## 1. Identificação e Roteamento
- **Identificador / Slug:** `contacts`
- **Título Visual no Sistema:** Dentistas e Clínicas (CRM Cirúrgico)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/contacts`
- **Componente React Raiz:** `frontend/src/features/contacts/ContactsCrmWorkspace.tsx`

---

## 2. Propósito e Objetivo de Negócio
A rota `contacts` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de dentistas e clínicas (crm cirúrgico).
2. Redução do tempo de atendimento e eliminação de processos analógicos na operação.
3. Rastreabilidade ponta a ponta com persistência auditável no SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba `crm_surgeons`:** Cirurgiões Dentistas Cadastrados
- **Aba `institutions`:** Clínicas, Hospitais e Polos
- **Aba `cfo_compliance`:** Validação de Registro CFO / CRO Ativo
- **Aba `icp_scoring`:** Qualificação e Enriquecimento ICP

---

## 4. Jornada e Fluxo Operacional
O usuário acessa `#!/contacts`, o sistema valida as permissões de RBAC do perfil ativo e carrega os dados específicos da fatia vertical. O operador interage através dos controles dedicados sem recarregar a aplicação.
