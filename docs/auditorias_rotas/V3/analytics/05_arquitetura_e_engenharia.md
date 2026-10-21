# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: analytics (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/bi/SupersetEmbeddedDashboard.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_superset_rls_embedded.py`
  - `tests/test_text_to_sql_dynamic.py`
  - `tests/test_text_to_sql_security.py`