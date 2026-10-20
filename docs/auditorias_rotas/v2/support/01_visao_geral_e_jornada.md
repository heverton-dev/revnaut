# 01. Visão Geral e Jornada do Usuário — Rota: support (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `support`
- **Título Visual no Sistema:** Suporte Clínico, RMA & Tecnovigilância ANVISA
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/support`
- **Componente React Raiz:** `frontend/src/features/support/SupportAnvisaWorkspace.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `support` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de suporte clínico, rma & tecnovigilância anvisa.
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `anvisa_rma`:** Quarentena & Laudos de Tecnovigilância ANVISA
- **Aba / Sub-aba `surgical_sos`:** Chamados de Emergência SOS Cirurgia
- **Aba / Sub-aba `postop_b2c`:** Acompanhamento Pós-Operatório do Paciente

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/support`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
