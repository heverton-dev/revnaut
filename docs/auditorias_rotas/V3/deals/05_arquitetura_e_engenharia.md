# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: deals (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/deals/DealsWorkspace.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_deals_advanced_features.py`
  - `tests/test_deals_contacts_scoping.py`
  - `tests/test_granola_copilot_zerotouch.py`