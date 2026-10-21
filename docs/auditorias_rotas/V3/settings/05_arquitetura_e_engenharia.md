# 05. Arquitetura de Software & Vertical Slice Architecture — Rota: settings (Auditoria V3)

## 1. Organização em Fatias Verticais (VSA)
- O módulo reside em `frontend/src/features/settings/CredentialsVaultPage.tsx` mantendo separação clara entre camada de apresentação, estado e contratos de API.

---

## 2. Acoplamento e Reusabilidade
- Componentes reutilizáveis importados de `@/components/ui/` (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`).
- Ausência de dependências circulares com testes automatizados dedicados:
  - `tests/test_credentials_vault.py`
  - `tests/test_totvs_integration.py`
  - `tests/test_outbound_webhooks_hmac.py`