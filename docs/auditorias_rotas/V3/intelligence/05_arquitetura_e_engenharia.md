# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: intelligence (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/intelligence/IntelligenceSuiteWorkspace.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_clinical_graph_churn.py`
  - `tests/test_surgical_catalog_rag.py`
  - `tests/test_pgvector_store.py`