# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: keypartners (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/keypartners/ConsignmentSurgicalBoard.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_erp_consignment_cfop_flow.py`
  - `tests/test_keypartners_dispatch_custody_route.py`
  - `tests/test_keypartners_kol_contracts.py`