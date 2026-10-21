# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: scoring (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/scoring/IcpScoringDashboard.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_lead_scoring_handoff.py`
  - `tests/test_lead_scoring_auto_handoff.py`