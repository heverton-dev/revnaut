# Permissionamento Granular — Cargos, Rotas e Subrotas

> **Status:** Especificação + schema (fase 1)  
> **Fonte de verdade do catálogo:** `frontend/src/components/layout/navConfig.ts`  
> **Papéis canônicos seed:** `src/core/database.py` + `scripts/seed_multinational_enterprise.py`  
> **Data:** 2026-10-20

---

## 1. Princípios invioláveis

1. **Menu esconder ≠ autorizar.** Toda rota/facility precisa de guard no frontend **e** na API.
2. **role_id é a chave canônica** do workspace (não string livre de cargo).
3. **Super Admin** (`is_superadmin=1` / `role-ceo`) enxerga o catálogo completo.
4. **Admin de Acesso** edita apenas cargos **operacionais** — nunca o próprio Super Admin nem outro Admin de Acesso.
5. **Defaults de seed** são o estado inicial do banco após a migração `0005`; alterações posteriores são sobrescritas por edição no módulo, não por re-seed cego.
6. **Facility** = subrota navegável no hash (`#!/dentgo?f=hubs`). Abas de contexto interno (ex.: colunas do omnichannel) podem ou não ser expostas como facility — ver §4.

---

## 2. Hierarquia de quem administra

| Papel | role_id | Acessa módulo de permissões | Escopo de edição |
|-------|---------|-----------------------------|------------------|
| Super Admin | `role-ceo` + `is_superadmin` | Sim | Tudo, incluindo Super Admin e Admin de Acesso |
| **Admin de Acesso** | `role-access-admin` | Sim | Apenas cargos operacionais (field, inside, logistics, clinical, manager) |
| Gerente Comercial | `role-manager` | Não | — |
| Cargos operacionais | `role-field` … `role-clinical` | Não | — |
| TI / suporte de infra | *(sem role canônico)* | Não | Operação de sistema; permissão de UI é papel de negócio, não de TI |

**Regra de ouro do Admin de Acesso:**

- Pode criar/editar permissões de `role-field`, `role-inside`, `role-logistics`, `role-clinical`, `role-manager`.
- Pode criar **novos cargos operacionais** (filhos de operação).
- **Não** pode alterar grants de `role-ceo` nem de `role-access-admin`.
- **Não** pode promover usuários a `is_superadmin`.
- Qualquer tentativa de auto-elevação → HTTP 403 + auditoria.

---

## 3. Matriz canônica de cargos × rotas (defaults de seed)

Legenda: `●` = liberado no modo focado · `—` = bloqueado · URL = `#!/{rota}[?f={facility}]`

### 3.1 Consultor Externo (Campo) — `role-field`

| Rota | Subrotas / facilities | Prioridade menu |
|------|----------------------|-----------------|
| `deals` | *(sem submenu — workspace único)* | 1 |
| `dentgo` | — *(sem submenu no cargo campo)* | 2 |
| `contacts` | — | 3 |
| `keypartners` | — | 4 |
| `video_sos` | — | 5 |
| `intelligence` | — | 6 |
| `market_intel` | — | 7 |

**Bloqueadas:** dashboard, omnichannel, contracts, scoring, marketing, imaging, scheduling, support, analytics, rbac, settings.

### 3.2 Consultor Interno (Atendimento) — `role-inside`

| Rota | Subrotas / facilities | Prioridade |
|------|----------------------|------------|
| `omnichannel` | `chats` · `contacts` · `instances` | 1 |
| `scheduling` | — | 2 |
| `deals` | — | 3 |
| `scoring` | — | 4 |
| `contacts` | — | 5 |
| `contracts` | — | 6 |
| `market_intel` | — | 7 |

**Landing:** `#!/omnichannel?f=chats`  
**Bloqueadas:** dashboard, dentgo, keypartners, video_sos, imaging, marketing, intelligence, analytics, support, rbac, settings.

### 3.3 Logística e Estoque — `role-logistics`

| Rota | Subrotas / facilities | Prioridade |
|------|----------------------|------------|
| `dentgo` | `orders` · `hubs` · `fefo` · `split` | 1 |
| `keypartners` | `board` · `agreements` · `kol` · `loyalty` | 2 |
| `support` | `anvisa_rma` · `surgical_sos` · `postop_b2c` | 3 |
| `settings` | `vault` · `erp` · `webhooks` · `users` | 4 |

**Landing:** `#!/dentgo?f=orders`  
**Perfis com submenus:** sim  
**Bloqueadas:** dashboard, deals, contacts, omnichannel, scoring, marketing, contracts, video_sos, imaging, intelligence, market_intel, analytics, scheduling, rbac.

### 3.4 Suporte Clínico e Pós-Venda — `role-clinical`

| Rota | Subrotas / facilities | Prioridade |
|------|----------------------|------------|
| `support` | `anvisa_rma` · `surgical_sos` · `postop_b2c` | 1 |
| `video_sos` | — | 2 |
| `imaging` | — | 3 |
| `scheduling` | — | 4 |
| `omnichannel` | — | 5 |

**Landing:** `#!/support?f=anvisa_rma`

### 3.5 Gerente Comercial — `role-manager`

| Rota | Subrotas / facilities | Prioridade |
|------|----------------------|------------|
| `dashboard` | — | 1 |
| `deals` | — | 2 |
| `market_intel` | `signals` · `competitors` · `opportunities` · `campaigns` | 3 |
| `contacts` | `crm_surgeons` · `institutions_links` · `cfo_compliance` · `icp_scoring` | 4 |
| `keypartners` | `board` · `agreements` · `kol` · `loyalty` | 5 |
| `contracts` | `documenso_lifecycle` · `anvisa_catalog_pricing` · `r2_custody` | 6 |
| `marketing` | — | 7 |
| `rbac` | `tree` · `permissions` · `targets` · `commissions` | 8 |

> **Nota:** `rbac` no gerente é limitado na UI de produto (área de equipes). No permissionamento granular da API, grants de `role-access-admin`/`role-ceo` permanecem proibidos.

### 3.6 Diretoria / Super Admin — `role-ceo`

| Rota | Subrotas / facilities |
|------|----------------------|
| `dashboard` | — |
| `omnichannel` | `chats` · `contacts` · `instances` |
| `scheduling` | — |
| `scoring` | — |
| `contacts` | `crm_surgeons` · `institutions_links` · `cfo_compliance` · `icp_scoring` |
| `deals` | — |
| `contracts` | `documenso_lifecycle` · `anvisa_catalog_pricing` · `r2_custody` |
| `imaging` | — |
| `marketing` | — |
| `dentgo` | `orders` · `hubs` · `fefo` · `split` |
| `keypartners` | `board` · `agreements` · `kol` · `loyalty` |
| `video_sos` | — |
| `support` | `anvisa_rma` · `surgical_sos` · `postop_b2c` |
| `intelligence` | `copilot` · `rag` · `inventory` · `margin` · `health_score` |
| `market_intel` | `signals` · `competitors` · `opportunities` · `campaigns` |
| `analytics` | `rls_studio` · `text_to_sql` |
| `rbac` | `tree` · `permissions` · `targets` · `commissions` |
| `settings` | `vault` · `erp` · `webhooks` · `users` |

**Perfis com submenus:** sim  
**Toggle “visão completa”:** somente este papel no frontend atual.

### 3.7 Admin de Acesso — `role-access-admin` (novo, dia 1)

| Rota | Subrotas / facilities | Por quê |
|------|----------------------|---------|
| `dashboard` | — | Visão do dia (opcional; default: liberado) |
| `rbac` | `tree` · **`permissions`** · `targets` · `commissions` | **Módulo principal** = `permissions` |
| `settings` | `users` | Vincular usuários a cargos |
| `analytics` | `rls_studio` | Auditoria de acesso (opcional, default: liberado) |

**Landing:** `#!/rbac?f=permissions`  
**Não recebe:** funil de vendas operacional, dentgo despacho, etc. — foco em governança.

---

## 4. Catálogo completo de rotas e facilities

| Rota (id) | Label menu | Facilities navegáveis (`?f=`) | Abas de contexto (não grantáveis como rota) |
|-----------|------------|-------------------------------|--------------------------------------------|
| `dashboard` | Visão do Dia | — | cortes de cockpit |
| `omnichannel` | Atendimento | `chats`, `contacts`, `instances` | coluna de contexto 360° |
| `scheduling` | Agenda e Retornos | — | varredura / ações em linha |
| `scoring` | Qualificação (ICP) | — | pesos de score |
| `contacts` | Dentistas e Clínicas | `crm_surgeons`, `institutions_links`, `cfo_compliance`, `icp_scoring` | filtros de UF/especialidade |
| `deals` | Funil de Negociações | — | lista/kanban, estágios |
| `contracts` | Propostas e Contratos | `documenso_lifecycle`, `anvisa_catalog_pricing`, `r2_custody` | — |
| `imaging` | Exames e Diagnóstico 3D | — | visualizador |
| `marketing` | Campanhas e Indicações | — | builder de landing |
| `dentgo` | Entregas Expressas | `orders`, `hubs`, `fefo`, `split` | — |
| `keypartners` | Consignação (Maletas) | `board`, `agreements`, `kol`, `loyalty` | — |
| `video_sos` | Chamadas e Vídeo | — | abas do modal LiveKit |
| `support` | Suporte e Garantias | `anvisa_rma`, `surgical_sos`, `postop_b2c` | — |
| `intelligence` | Assistente Comercial | `copilot`, `rag`, `inventory`, `margin`, `health_score` | — |
| `market_intel` | Radar de Mercado | `signals`, `competitors`, `opportunities`, `campaigns` | filtros de escopo |
| `analytics` | Relatórios e Metas | `rls_studio`, `text_to_sql` | dashboards embutidos |
| `rbac` | Equipes e Acessos | `tree`, `permissions`, `targets`, `commissions` | — |
| `settings` | Configurações | `vault`, `erp`, `webhooks`, `users` | — |

**Regra de grant:**

- Liberar a rota **sem** facilities ⇒ usuário entra no default da rota.
- Liberar rota **com** facilities ⇒ usuário só entra nas facilities listadas; deep-link a facility não listada → redirect para a primeira facility do grant.

---

## 5. Modelo de dados (banco)

### 5.1 Tabelas novas (migração `0005`)

```
access_catalog_routes
  route_id          TEXT PK          -- 'dentgo'
  label             TEXT
  journey_group     TEXT             -- 'Operação do Dia' | ...
  default_facility  TEXT NULL

access_catalog_facilities
  facility_id       TEXT PK          -- 'orders'
  route_id          TEXT FK
  label             TEXT
  sort_order        INTEGER

role_route_grants
  id                INTEGER PK
  account_id        TEXT
  role_id           TEXT FK roles
  route_id          TEXT FK access_catalog_routes
  is_visible_menu   INTEGER DEFAULT 1
  menu_priority     INTEGER DEFAULT 999
  allow_submenus    INTEGER DEFAULT 0
  UNIQUE(account_id, role_id, route_id)

role_facility_grants
  id                INTEGER PK
  account_id        TEXT
  role_id           TEXT FK roles
  route_id          TEXT
  facility_id       TEXT FK access_catalog_facilities
  sort_order        INTEGER DEFAULT 999
  UNIQUE(account_id, role_id, route_id, facility_id)

access_admin_scopes
  id                INTEGER PK
  account_id        TEXT
  admin_role_id     TEXT             -- role-access-admin
  editable_role_id  TEXT             -- role-field | ... | NOVO cargo operacional
  UNIQUE(account_id, admin_role_id, editable_role_id)

access_audit_log
  id                INTEGER PK
  account_id        TEXT
  actor_user_id     TEXT
  action            TEXT             -- grant.create | grant.update | role.create | ...
  target_role_id    TEXT
  payload_json      TEXT
  created_at        TIMESTAMP
```

### 5.2 Papel novo no catálogo `roles`

| id | name | is_admin | default_data_scope |
|----|------|----------|--------------------|
| `role-access-admin` | Admin de Acesso (Permissões) | 1 | team |

`users.is_superadmin` permanece **apenas** para Super Admin de plataforma (`role-ceo`).

---

## 6. Plano de migração (fases)

### Fase 1 — Schema + seed (esta entrega)
- [x] Doc neste arquivo  
- [ ] Alembic `0005_granular_rbac` (tabelas + catálogo + grants default + `role-access-admin`)  
- [ ] Seed idempotente em `database.py` para hosts que não rodam Alembic no boot  

### Fase 2 — API de leitura
- [ ] `GET /api/v1/access/me` → `{ role_id, routes[], facilities[], landing }` (efetivo, com impersonation)  
- [ ] Middleware de rota no backend: 403 se facility/route fora do grant (além do guard atual de UI)  

### Fase 3 — Frontend consome banco
- [ ] `navConfig` deixa de ser fonte de grants; vira **catálogo estático de labels/icons**  
- [ ] AppShell/App carregam grants via `/access/me` (cache + fallback seed em offline dev)  
- [ ] Guard de URL usa o mesmo payload  

### Fase 4 — Módulo Admin de Acesso (UI)
- [ ] Rota `#!/rbac?f=permissions` evolui para matriz (cargos × rotas × facilities)  
- [ ] CRUD restrito: Super Admin e Admin de Acesso (escopo `access_admin_scopes`)  
- [ ] Auditoria em `access_audit_log`  

### Fase 5 — Hardening
- [ ] Testes: deep-link bloqueado por facility, impersonation, 403 API, auto-elevação negada  
- [ ] Gate de quality: seed vs catálogo divergente → exit 1  

---

## 7. Decisões de produto já tomadas

| Decisão | Valor |
|---------|--------|
| Quem administra o módulo | Super Admin + Admin de Acesso |
| TI | Fora do permissionamento de negócio |
| Admin de Acesso no seed dia 1 | Sim (`role-access-admin`) |
| Fonte de grants | Banco (após fase 3), não memória React |
| Menu + URL + API | Três camadas de enforcement |

---

## 8. Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Frontend e API divergem | Fase 2/3: API authoritativa; frontend só espelha |
| Re-seed sobrescreve customizações | Seed idempotente: só insere grants se tabela vazia ou flag `seed_version` |
| Admin de Acesso edita a si mesmo | Bloqueio por `editable_role_id` ∈ scopes + check server-side de self-escalation |
| Facility órfã no hash | Redirect para primeira facility do grant da rota |

---

## 9. Referência de implementação atual (pré-banco)

Enquanto a fase 3 não roda, a matriz viva está em:

- `ROLE_WORKSPACES` / `ROLE_ID_TO_WORKSPACE` / `rawNavSections` — `navConfig.ts`  
- Guard de rota — `AppShell.tsx`  
- Hash `?f=` — `lib/navHash.ts`  

A migração `0005` **espelha** esses defaults para não quebrar o app existente.
