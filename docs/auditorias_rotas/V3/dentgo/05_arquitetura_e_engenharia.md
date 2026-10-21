# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: dentgo (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/dentgo/DentgoExpressCockpit.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_dentgo_express_route.py`
  - `tests/test_dentgo_fefo_flash_deals.py`
  - `tests/test_dentgo_financial_split.py`