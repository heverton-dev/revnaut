# 01. Visão Geral e Jornada do Usuário — Rota: rbac (Auditoria V3)

## 1. Identificação Técnica
- **Rota Visual:** `https://revnault.vpsconexao.org/#!/rbac`
- **Título Oficial:** Equipes, Metas & Comissionamento (RBAC)
- **Componente Front-end:** `frontend/src/features/rbac/RbacHierarchyTree.tsx`
- **Motores Backend:** `src/features/rbac/router.py`, `src/features/hierarchy/router.py`
- **Suíte de Testes:** `tests/test_hierarchy_ddl.py`, `tests/test_hierarchy_presets.py`, `tests/test_rbac_permissions_matrix.py`, `tests/test_targets_and_commissions.py`

---

## 2. Jornada do Usuário Real
O usuário acessa o módulo para executar operações cirúrgicas e comerciais sem atrito:
1. **Entrada na Tela:** Carregamento otimizado com dados reais via SQLite WAL.
2. **Navegação por Abas:** Alternância fluida entre as visões do módulo.
3. **Ações Primárias:** Interação com botões de alta densidade sem stubs ou toasts vazios.

---

## 3. Abas e Sub-Rotas Mapeadas
- **Aba `tree`:** Árvore Hierárquica Nacional / Regional / Consultor
- **Aba `permissions`:** Matriz de Permissões Granulares por Papel
- **Aba `targets`:** Gestor de Metas Comerciais por Equipe
- **Aba `commissions`:** Regras e Cálculos de Comissionamento