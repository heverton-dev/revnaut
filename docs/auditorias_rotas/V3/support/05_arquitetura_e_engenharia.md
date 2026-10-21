# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: support (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/support/SupportAnvisaWorkspace.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_anvisa_technovigilance_rma.py`
  - `tests/test_postop_patient_care_b2c.py`