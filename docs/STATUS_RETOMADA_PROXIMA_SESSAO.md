# Status de Retomada — Próxima Sessão (Revnaut Dental Ops)

**Data do Ponto de Restauração:** 16/10/2026 08:35 BRT  
**ID da Conversa:** `f1bbcd99-64df-4a50-a2e8-1a221672f2dd`  
**Repositório GitHub:** `https://github.com/heverton-dev/revnaut` (Privado)  
**Ambiente Ativo:** Local Monolith / VPS Swarm (`https://revnaut.vpsconexao.org`)  
**Backend:** FastAPI + SQLite WAL (`data/revops.db`)  
**Frontend:** `docs/reconstruct_rvops/05_reconstructed_app/index.html` (Servido na raiz `/`)  
**Testes Automatizados:** 44/44 passaram com 100% de sucesso (`pytest -q`)  
**Quality Gates AIDD:** 12/12 gates aprovados em exit code 0 (`G_TESTES_REAIS`, `G_BLOQUEAR_SEGREDOS`, `G_CYBERSECURITY_OWASP`, `G_QUARTETO_SINE_QUA_NON`, `G_CONTRACTS`, `G_STACK_PADRAO_OURO`, `G_SAIDA_BINARIA`, `G_DETERMINISMO_LEI_1`, `G_ESTRUTURA_AST`, `G_HARNESS_COMPAT`, `G_INJECT`, `G_PERFORMANCE`)

---

## 1. O que foi Entregue e Homologado (RevOps Puro: RBAC, Data Scoping, Funis & Hierarquia)

- [x] **Expurgo e Blindagem Arquitetural de Escopo (Alinhamento Key Partners):**
  - Remoção de todo o código e tabelas de estoque físico consignado (`consignments`, `consignment_items`, `surgery_replacements`).
  - O projeto `proj_revops` foca estritamente em **Revenue Operations (CRM B2B, Funis Comerciais, Hierarquia de Vendas e RBAC)**.
  - As operações cirúrgicas físicas, bipagem e devolução permanecem 100% sob responsabilidade do **`proj_portal_ka`** (Key Partners).

- [x] **Modelagem Relacional DDL no SQLite WAL (TICKET-01):**
  - Criação das tabelas `business_units`, `teams`, `roles`, `role_permissions`.
  - Injeção das colunas `team_id`, `role_id`, `custom_data_scope`, `is_superadmin` na tabela `users`.
  - Injeção das colunas de isolamento `owner_id` e `team_id` em `deals`, `contacts`, `institutions`.
  - Testes: `tests/test_hierarchy_ddl.py` (3/3 aprovados).

- [x] **Motor de Presets Plug & Play e CRUD de Hierarquia (TICKET-02):**
  - Fatia vertical modular `src/features/hierarchy/` (`schemas.py`, `service.py`, `router.py`).
  - Implementação idempotente dos **4 Presets Progressivos Setoriais**:
    1. *Fábrica Enxuta / Distribuidor* (1 camada: Diretoria -> Consultores).
    2. *Nacional em Expansão* (2 camadas: Diretoria -> Regionais -> Consultores).
    3. *Multidivisão de Produtos* (3 camadas: BUs Cirurgia/Biomateriais/Prótese -> Regionais -> Consultores).
    4. *Multinacional Enterprise (Padrão Neodent / Straumann)* (4-5 camadas: C-Level -> 4 BUs Cirúrgico/CAD-CAM/Ensino/Key Accounts -> Distritos -> Regionais -> Consultores).
  - Algoritmo de validação anti-loop de hierarquia acíclica (DAG).
  - Testes: `tests/test_hierarchy_presets.py` (4/4 aprovados).

- [x] **Motor Central de Data Scoping no Backend (TICKET-03):**
  - Módulo `src/core/security.py` com resolução SQL determinística via CTE recursiva nativa do SQLite WAL.
  - Suporte tipado aos 5 escopos de isolamento de dados: `self`, `team`, `subtree`, `business_unit`, `tenant_global` e `superadmin`.
  - Testes: `tests/test_data_scoping.py` (4/4 aprovados) e `tests/test_deals_contacts_scoping.py` (4/4 aprovados).

- [x] **Interface Visual de Organograma e Seletor de Escopo (TICKET-04):**
  - Aba e view `#hierarchy-view` no frontend dark enterprise (`index.html`).
  - Cards interativos dos 4 Presets Plug & Play com provisionamento em 1 clique.
  - Painel com lista de Business Units e árvore de equipes (DAG) aninhada.
  - Seletor de simulação de escopo na topbar (`#user-scope-select`) persistido em `localStorage`, injetando `X-User-Id` nas requisições.

- [x] **Matriz Granular de Permissionamento RBAC (VER & REALIZAR):**
  - Catálogo formal de recursos odontológicos (`deals`, `contacts`, `institutions`, `hierarchy`, `campaigns`) em `src/features/hierarchy/service.py`.
  - Suporte total ao Tenant Admin para personalizar permissões por cargo em runtime sem tocar no código fonte.
  - Portão Inviolável Lei #13: Verificação de `enforce_user_permission` em endpoints críticos (`deals:write`, `contacts:write`) retornando 403 Forbidden para usuários não autorizados.
  - Aba interativa "Matriz Granular de Permissões (RBAC)" no frontend em `#hierarchy-view` com seletor de cargo, badge de escopo RLS e tabela de checkboxes por recurso.
  - Testes dedicados: `tests/test_rbac_permissions_matrix.py` (4/4 aprovados).

- [x] **Auditoria Completa dos Quality Gates AIDD (TICKET-05):**
  - Suíte completa de 44 testes reais passando em 100% GREEN.
  - 12 Quality Gates executados com exit code 0.

---

## 2. O que Iniciar Imediatamente a Seguir

1. **Sincronização em Produção VPS Swarm:**
   - Realizar git commit/push e acionar webhook de deploy contínuo em `https://revnaut.vpsconexao.org`.
2. **Construtor de Fluxos de Automação Cirúrgica (Campaign Engine):**
   - Disparo automático de ordem de reposição para o consultor de campo assim que a baixa cirúrgica for efetuada na caixa consignada.

---

## 3. Prompt de Retomada Rápida

Basta colar o comando abaixo na nova sessão:

```text
Continuar o projeto Revnaut Dental Ops a partir de docs/STATUS_RETOMADA_PROXIMA_SESSAO.md. O motor de RBAC e Data Scoping Hierárquico cobre Consignações, Deals e Contatos, com 41 testes e 12 Quality Gates em exit 0. Sincronizar em produção no VPS Swarm ou implementar as automações de reposição cirúrgica no Campaign Engine.
```
