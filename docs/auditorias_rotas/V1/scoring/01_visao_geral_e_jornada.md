# 01. Visão Geral e Jornada do Usuário — Rota: scoring

## 1. Identificação e Roteamento
- **Identificador / Slug:** `scoring`
- **Título Visual no Sistema:** Qualificação de Clientes (ICP Scoring)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/scoring`
- **Componente React Raiz:** `frontend/src/features/scoring/IcpScoringDashboard.tsx`

---

## 2. Propósito e Objetivo de Negócio
A rota `scoring` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de qualificação de clientes (icp scoring).
2. Redução do tempo de atendimento e eliminação de processos analógicos na operação.
3. Rastreabilidade ponta a ponta com persistência auditável no SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba `overview`:** Score Geral da Carteira
- **Aba `matrix`:** Matriz ICP Odontológico
- **Aba `rules`:** Critérios e Pesos de Enquadramento

---

## 4. Jornada e Fluxo Operacional
O usuário acessa `#!/scoring`, o sistema valida as permissões de RBAC do perfil ativo e carrega os dados específicos da fatia vertical. O operador interage através dos controles dedicados sem recarregar a aplicação.
