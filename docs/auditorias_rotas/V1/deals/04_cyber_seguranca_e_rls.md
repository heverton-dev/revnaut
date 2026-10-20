# 04. Cyber-Segurança, RBAC e Isolamento Multi-tenant — Rota: deals

## 1. Matriz de Autenticação e RBAC

A rota de Negociações aplica regras estritas de escopo hierárquico (*Hierarchical Scoping*):

| Perfil do Usuário | Escopo de Visibilidade de Negócios | Bloqueio / Permissão de Ações |
| :--- | :--- | :--- |
| **Super Admin** | Acesso irrestrito a todos os funis, regiões e contas (`1=1`) | Leitura, criação, edição e aprovação de crédito irrestritas |
| **Diretor Nacional** | Visão agregada de todas as regionais do tenant | Leitura, edição e aprovação de exceções de crédito |
| **Gerente Regional** | Restrito aos negócios pertencentes aos consultores de sua regional | Leitura e edição da equipe; aprovação de crédito limitada |
| **Consultor Comercial** | Estritamente os negócios onde é o proprietário (`owner_id = user_id`) | Leitura e edição restrita à sua própria carteira; **não pode aprovar próprio crédito** |
| **Não Autenticado** | Redirecionamento forçado para `/#!/login` | Bloqueio total (HTTP 401) |

---

## 2. Isolamento Multi-tenant e Prevenção de IDOR

- **Mecanismo de Escopo de Tenant:**
  - O cabeçalho `X-User-Id` e o token de contexto são inspecionados para determinar a organização e o perfil do usuário.
  - Queries de negócios filtram explicitamente por `organization_id` no repositório SQLite WAL, prevenindo qualquer vazamento horizontal de dados entre clínicas concorrentes.
- **Prevenção de IDOR em Mutações:**
  - Ao executar `PUT /api/v1/deals/{deal_id}` ou `POST /api/v1/deals/{deal_id}/approve-credit`, o backend verifica se o `deal_id` pertence à organização e ao escopo hierárquico do usuário antes de aplicar as alterações, retornando HTTP 403 Forbidden para tentativas de manipulação indevida.

---

## 3. Trilha de Auditoria e Imutabilidade

- **Auditoria Automática de Alterações:**
  - Cada mutação de valor, prioridade ou mudança de estágio grava um registro na tabela `deal_timeline` com:
    - Identificador do usuário que realizou a ação (`author_id`).
    - Timestamp UTC preciso com microssegundos.
    - Descrição da alteração (ex: "Estágio alterado de Qualificação para Proposta").
  - Essa trilha é imutável: não existem endpoints de exclusão ou edição retroativa na timeline de auditoria.
