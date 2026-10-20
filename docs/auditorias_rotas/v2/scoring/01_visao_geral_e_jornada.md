# 01. Visão Geral e Jornada do Usuário — Rota: scoring (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `scoring`
- **Título Visual no Sistema:** Qualificação de Clientes (ICP Scoring)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/scoring`
- **Componente React Raiz:** `frontend/src/features/scoring/IcpScoringDashboard.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `scoring` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de qualificação de clientes (icp scoring).
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `overview`:** Score Geral da Carteira
- **Aba / Sub-aba `matrix`:** Matriz ICP Odontológico
- **Aba / Sub-aba `rules`:** Critérios e Pesos de Enquadramento

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/scoring`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
