# 01. Visão Geral e Jornada do Usuário — Rota: rbac

## 1. Identificação e Roteamento
- **Identificador / Slug:** `rbac`
- **Título Visual no Sistema:** Equipes e Acessos (Árvore Hierárquica & Comissões)
- **Classificação:** Frontend SPA View (Single Page Application com Hashbang Router)
- **URL de Produção:** `https://revnault.vpsconexao.org/#!/rbac`
- **Componente React Raiz:** `frontend/src/features/rbac/RbacHierarchyTree.tsx`

---

## 2. Propósito e Objetivo de Negócio
A rota `rbac` atua no ecossistema RevNault proporcionando aos operadores clínicos e comerciais:
1. Controle determinístico dos fluxos de equipes e acessos (árvore hierárquica & comissões).
2. Redução do tempo de atendimento e eliminação de processos analógicos na operação.
3. Rastreabilidade ponta a ponta com persistência auditável no SQLite WAL.

---

## 3. Abas e Sub-rotas Mapeadas
- **Aba `tree`:** Árvore Hierárquica Nacional / Regional / Consultor
- **Aba `permissions`:** Matriz de Permissões Granulares
- **Aba `targets`:** Gestor de Metas Comerciais por Equipe
- **Aba `commissions`:** Regras de Cálculo de Comissionamento

---

## 4. Jornada e Fluxo Operacional
O usuário acessa `#!/rbac`, o sistema valida as permissões de RBAC do perfil ativo e carrega os dados específicos da fatia vertical. O operador interage através dos controles dedicados sem recarregar a aplicação.
