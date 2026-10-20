# 04. Cyber-Segurança, RBAC e Isolamento Multi-tenant — Rota: dashboard

## 1. Matriz de Autenticação e RBAC

A rota do Dashboard atua sob políticas hierárquicas de controle de acesso (RBAC):

| Perfil do Usuário | Escopo de Visibilidade Permitido | Política RLS no Backend | Acesso ao Cockpit |
| :--- | :--- | :--- | :--- |
| **Super Admin Global** | Acesso irrestrito a todos os tenants e carteiras (`1=1`) | Sem cláusula restritiva de tenant | Permitido (Auditoria Total) |
| **Diretor Nacional** | Visão agregada de faturamento e carteira do tenant atual | `organization_id = :tenant_id` | Permitido (Cockpit Completo) |
| **Gerente Regional** | Visão filtrada restrita à sua regional geográfica (ex: Sul/PR) | `organization_id = :tenant_id AND regional = :regional` | Permitido (Escopo de Equipe) |
| **Consultor Comercial** | Apenas seus próprios negócios e carteira de cirurgiões | `organization_id = :tenant_id AND owner_id = :user_id` | Permitido (Carteira Individual) |
| **Usuário Não Autenticado** | Bloqueio total com redirecionamento para login | Retorno HTTP 401 Unauthorized | Bloqueado |

---

## 2. Isolamento Multi-tenant e Prevenção de IDOR

- **Mecanismo de Escopo de Tenant:**
  - No backend (`src/features/intelligence/router.py`), as rotas recebem o parâmetro `account_id: str = "0f14ffff"`.
  - **Vulnerabilidade / Ponto de Atenção Identificado:** Em endpoints legados, se o `account_id` for aceito como query parameter arbitrário sem sobreposição estrita pelo `user.account_id` extraído do Bearer JWT validado, há risco potencial de **IDOR** (Insecure Direct Object Reference), permitindo a um usuário malicioso inspecionar carteiras de outros tenants alterando o parâmetro na requisição.
  - **Ação Obrigatória:** Garantir que a dependência FastAPI `get_current_active_user` force a sobreposição do `account_id` do payload pelo tenant real autenticado.

---

## 3. Blindagem Analítica Text-to-SQL (Proteção AST)

O módulo analítico associado à rota (`src/features/intelligence/router.py`) possui um dos mecanismos de segurança mais rigorosos da aplicação:
1. **Parser Sintático AST (Abstract Syntax Tree):** Toda consulta SQL gerada é inspecionada antes da execução.
2. **Bloqueio Categórico de Mutações (DDL/DML):** Rejeita imediatamente comandos `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE` com erro `HTTP 400 Bad Request`.
3. **Bloqueio de Extração de Credenciais:** Impede consultas direcionadas às tabelas sensíveis de autenticação (`users`, `credentials`, `passwords`, `password_hash`).
4. **Injeção Forçada de RLS:** A AST injeta dinamicamente o filtro de escopo do usuário autenticado antes de submeter a query ao SQLite WAL, impedindo vazamento vertical ou horizontal de dados.

---

## 4. Higiene de Logs e Proteção de PII

- **Dados Sensíveis de Cirurgiões (LGPD / Sigilo Clínico):**
  - O radar anti-churn trafega apenas identificadores necessários (Nome, CRO, UF, dias sem pedido). Não trafega dados fiscais confidenciais ou prontuários médicos de pacientes no payload do dashboard.
- **Auditoria de Requisições:**
  - Erros e telemetria de exportação registram apenas a chave anonimizada de storage no Cloudflare R2 (`r2_storage_key`), sem expor credenciais S3/R2 nos headers de resposta.
