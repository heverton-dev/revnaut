# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: market_intel (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/market_intel/MarketIntelRadarWorkspace.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_market_intel_service.py`
  - `tests/test_market_intel_api.py`
  - `tests/test_market_intel_concurrency.py`