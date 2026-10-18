# AIDD-Tickets — Plano de Decomposição Atômica: RBAC e Data Scoping Hierárquico

> **Documento:** `docs/planos/TICKETS_RBAC_DATA_SCOPING.md`  
> **Status:** 100% Concluído (5/5 Tickets Homologados)  
> **Autor:** AIDD Core Architecture  
> **Data:** 16/10/2026  

---

### [TICKET-01] Migração DDL e Modelagem Relacional no SQLite WAL
- **Descrição:** Criação das tabelas relacionais `business_units`, `teams`, `roles`, `role_permissions`, `users` e injeção de colunas `owner_id` e `team_id` em `consignments`, `deals` e `contacts`.
- **Target Files:** `src/core/database.py`, `tests/test_hierarchy_ddl.py`
- **Validation Command:** `python -m pytest tests/test_hierarchy_ddl.py -q`
- **Blocked by:** none

---

### [TICKET-02] Motor de Presets Plug & Play Odontológicos e CRUD de Hierarquia
- **Descrição:** Implementação de `src/features/hierarchy/` com os 4 presets progressivos setoriais, validação anti-loop de hierarquia (DAG acíclica) e CRUD de Business Units e Equipes.
- **Target Files:** `src/features/hierarchy/schemas.py`, `src/features/hierarchy/service.py`, `src/features/hierarchy/router.py`, `src/main.py`, `tests/test_hierarchy_presets.py`
- **Validation Command:** `python -m pytest tests/test_hierarchy_presets.py -q`
- **Blocked by:** TICKET-01

---

### [TICKET-03] Motor Central de Data Scoping no Backend (FastAPI Dependency)
- **Descrição:** Criação do resolvedor de escopo hierárquico `get_data_scope_filter` em `src/core/security.py`, com CTE recursiva no SQLite WAL e injeção em rotas de Consignações, Negócios e Contatos.
- **Target Files:** `src/core/security.py`, `src/features/consignments/service.py`, `src/features/consignments/router.py`, `tests/test_data_scoping.py`
- **Validation Command:** `python -m pytest tests/test_data_scoping.py -q`
- **Blocked by:** TICKET-02

---

### [TICKET-04] Interface Visual de Organograma e Seletor de Visão de Equipe (UI)
- **Descrição:** Adição da view `#hierarchy-view` no frontend (`index.html`), permitindo ao Tenant Admin visualizar a árvore corporativa e ao gestor alternar entre visão própria e de subordinados.
- **Target Files:** `docs/reconstruct_rvops/05_reconstructed_app/index.html`, `tests/test_backend.py`
- **Validation Command:** `python -m pytest tests/test_backend.py -q`
- **Blocked by:** TICKET-03

---

### [TICKET-05] Homologação Geral, Quality Gates AIDD e Documentação de Retomada
- **Descrição:** Execução de todos os Quality Gates AIDD em exit code 0 e atualização de `docs/STATUS_RETOMADA_PROXIMA_SESSAO.md`.
- **Target Files:** `docs/STATUS_RETOMADA_PROXIMA_SESSAO.md`
- **Validation Command:** `python gates/G_TESTES_REAIS.py`
- **Blocked by:** TICKET-04
