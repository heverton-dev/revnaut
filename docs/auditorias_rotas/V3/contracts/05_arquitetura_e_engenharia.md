# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: contracts (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/contracts/ContractsDocumensoWorkspace.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_documenso_contract_flow.py`
  - `tests/test_r2_storage.py`
  - `tests/test_catalog_pricing_approval.py`