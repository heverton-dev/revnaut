# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: omnichannel (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/inbox/OmnichannelWorkspace.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_chatwoot_omnichannel_context_sidebar.py`
  - `tests/test_evolution_signed_call_offer.py`
  - `tests/test_omnichannel_webhooks.py`