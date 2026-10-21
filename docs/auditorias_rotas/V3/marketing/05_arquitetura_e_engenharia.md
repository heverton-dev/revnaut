# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: marketing (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/campaigns/LandingPageBuilder.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_landing_pages_grapesjs.py`
  - `tests/test_b2b_referral_mgm_loop.py`
  - `tests/test_listmonk_campaigns.py`