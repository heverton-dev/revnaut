# 04. Cyber-Segurança, RBAC e Isolamento Multi-tenant — Rota: imaging (Auditoria v2)

## 1. Matriz de Autenticação e RBAC
- **Acesso Autorizado:** Controlado pelas políticas de perfil configuradas no AppShell e validadas por dependências de autorização no FastAPI.
- **Segregação de Funções:** Ações críticas exigem papéis compatíveis (ex: Diretor ou Gerente para aprovações e cadastros sensíveis).

---

## 2. Isolamento Multi-tenant e RLS
- **Blindagem de Tenant:** Anonimização de tags DICOM sensíveis do paciente (LGPD) e URLs pré-assinadas com expiração.
- **Prevenção de IDOR:** Toda busca ou mutação valida explicitamente se o registro alvo pertence ao `organization_id` do usuário conectado.
- **Sanitização de Entradas:** Proteção contra SQLi, XSS e validação rigorosa de schemas com Pydantic.
