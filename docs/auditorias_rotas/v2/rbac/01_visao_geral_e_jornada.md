# 01. Visão Geral e Jornada do Usuário — Rota: rbac (Auditoria v2)

## 1. Identificação e Roteamento
- **Identificador / Slug:** `rbac`
- **Título Visual no Sistema:** Equipes, Metas & Comissionamento (RBAC)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL Canônica:** `https://revnault.vpsconexao.org/#!/rbac`
- **Componente React Raiz:** `frontend/src/features/rbac/RbacHierarchyTree.tsx`
- **Ciclo de Auditoria:** v2 (Pós-implementação de gaps e tickets de produção)

---

## 2. Propósito e Objetivo de Negócio
A rota `rbac` atua no ecossistema RevOps proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de equipes, metas & comissionamento (rbac).
2. Redução do tempo de atendimento operacional e eliminação de processos analógicos em campo.
3. Rastreabilidade regulatória ponta a ponta com persistência auditável em SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba / Sub-aba `tree`:** Árvore Hierárquica Nacional / Regional / Consultor
- **Aba / Sub-aba `permissions`:** Matriz de Permissões Granulares por Papel
- **Aba / Sub-aba `targets`:** Gestor de Metas Comerciais por Equipe
- **Aba / Sub-aba `commissions`:** Regras e Cálculos de Comissionamento

---

## 4. Jornada e Fluxo Operacional
O usuário autenticado acessa a rota `#!/rbac`. O sistema valida os privilégios do papel ativo no RBAC e carrega os dados específicos da fatia vertical de backend de forma reativa. O operador interage através dos controles dedicados sem recarregar a aplicação.
