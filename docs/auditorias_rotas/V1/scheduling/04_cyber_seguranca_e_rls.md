# 04. Cyber-Segurança, RBAC e Isolamento Multi-tenant — Rota: scheduling

## 1. Matriz de Autenticação e RBAC
- **Acesso Autorizado:** Controlado pelas políticas de perfil configuradas no AppShell e validadas por dependências de autorização no FastAPI.
- **Segregação de Funções:** Ações críticas exigem papéis compatíveis (ex: Diretor ou Gerente para aprovações e cadastros sensíveis).

---

## 2. Isolamento Multi-tenant e RLS
- **Blindagem de Tenant:** Proteção de dados de contato e prontuário de pacientes em conformidade com sigilo profissional odontológico.
- **Prevenção de IDOR:** Toda busca ou mutação valida explicitamente se o registro alvo pertence ao `organization_id` do usuário conectado.
