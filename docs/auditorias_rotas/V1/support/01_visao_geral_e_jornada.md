# 01. Visão Geral e Jornada do Usuário — Rota: support

## 1. Identificação e Roteamento
- **Identificador / Slug:** `support`
- **Título Visual no Sistema:** Suporte Clínico e Garantias (ANVISA & Pós-Op)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/support`
- **Componente React Raiz:** `frontend/src/features/support/SupportAnvisaWorkspace.tsx`

---

## 2. Propósito e Objetivo de Negócio
A rota `support` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de suporte clínico e garantias (anvisa & pós-op).
2. Redução do tempo de atendimento e eliminação de processos analógicos na operação.
3. Rastreabilidade ponta a ponta com persistência auditável no SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba `anvisa_rma`:** Quarentena & Laudos de Tecnovigilância RMA
- **Aba `surgical_sos`:** Chamados de Emergência SOS Cirurgia
- **Aba `postop_b2c`:** Acompanhamento Pós-Operatório do Paciente

---

## 4. Jornada e Fluxo Operacional
O usuário acessa `#!/support`, o sistema valida as permissões de RBAC do perfil ativo e carrega os dados específicos da fatia vertical. O operador interage através dos controles dedicados sem recarregar a aplicação.
