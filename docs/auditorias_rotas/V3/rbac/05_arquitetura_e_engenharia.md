# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: rbac (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/rbac/RbacHierarchyTree.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_hierarchy_ddl.py`
  - `tests/test_hierarchy_presets.py`
  - `tests/test_rbac_permissions_matrix.py`
  - `tests/test_targets_and_commissions.py`