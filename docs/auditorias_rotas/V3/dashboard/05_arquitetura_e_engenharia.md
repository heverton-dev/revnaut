# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: dashboard (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/dashboard/ExecutiveCockpitView.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_predictive_sok_pr_math.py`
  - `tests/test_clinical_graph_churn.py`
  - `tests/test_revenue_triggers.py`