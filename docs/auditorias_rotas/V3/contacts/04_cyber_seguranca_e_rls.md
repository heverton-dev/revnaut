# 04. Cyber-Segurança, RBAC & Isolamento de Dados — Rota: contacts (Auditoria V3)

## 1. Modelo de Segurança e Isolamento Multi-Tenant
- **Tenant Isolation:** Isolamento estrito por organization_id no SQLite WAL, sanitização contra SQLi e validação de CRO e CPF.
- **Mitigação de IDOR:** Toda consulta e mutação de recursos valida estritamente a posse do objeto (`account_id` e `organization_id`) prevenindo vulnerabilidades de Insecure Direct Object References (IDOR).

---

## 2. Proteção de Dados e Controles RBAC
- **Autenticação:** Sessão assinada via token HMAC-SHA256 com TTL e renovação determinística.
- **Autorização Granular (RBAC):** Validação dupla no backend FastAPI (`get_current_active_user`) e AppShell frontend garantindo que privilégios de acesso sejam respeitados por papel.
- **Privacidade Sanitária (LGPD / ANVISA):** Dados de pacientes e cirurgiões isolados por tenant com auditoria contínua.
