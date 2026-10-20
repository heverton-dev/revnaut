# Auditoria V4 - rota `dashboard` (Cockpit Executivo)

Data: 2026-10-20. Escopo: leitura + PoC em banco temporario. Nenhum codigo de producao alterado.

## Artefatos
- Front: `frontend/src/features/dashboard/ExecutiveCockpitView.tsx` (wrapper) -> `frontend/src/features/bi/SupersetEmbeddedDashboard.tsx` (2717 linhas, 50 useState, `mode="executive_cockpit"`), `router.tsx:76`.
- Back: `src/features/intelligence/{router,superset_embedded,text_to_sql_agent,schemas}.py`; RBAC em `src/features/access/service.py`.
- Testes: `tests/test_superset_rls_embedded.py`, `test_api_auth_enforcement.py`, `test_api_contracts_sync.py`.

## Baseline
pytest (3 arquivos): 266 ok, 1 falha (`test_api_contracts_sync`: rotas `/api/v1/access/matrix` e `/access/roles/{role_id}/grants` ausentes em `api_contracts.ts`, origem: trabalho nao commitado em `access/*`, fora do dashboard). `tsc --noEmit`: exit 0.

## Achados (ordenados por severidade)

| # | Sev | Achado | Evidencia |
|---|---|---|---|
| F1 | CRITICO | `/bi/guest-token` usa `payload.user_id` do corpo (campo obrigatorio no schema); qualquer usuario autenticado emite token com RLS de outro usuario, inclusive superadmin (`1=1`). | `router.py:213`, `schemas.py:239`. PoC: usuario `usr-lowpriv` -> 200, `rls_clause = 1=1` |
| F2 | CRITICO | `/bi/export-dataset` e `/bi/text-to-sql` confiam em `user_id` e `account_id` do corpo. Exigem login (401 sem token), mas nao comparam com `current_user`. | `router.py:227-251`. PoC: lowpriv como superadmin exporta 17 deals e le `SELECT title FROM deals` sem filtro. `account_id` do corpo tambem permite troca de tenant (por leitura de codigo, nao executado) |
| F3 | ALTO | RLS alargado para o tenant inteiro: se a clausula contem `owner_id`, `kp_custody_ledger`, `dentgo_orders` e `anvisa_rma_claims` usam so `account_id`. Consultor (SELF) e gestor (TEAM) veem o tenant todo nesses datasets. Padrao igual em `text_to_sql_agent.py:391`. | `superset_embedded.py:170-179` |
| F4 | ALTO | Clausula RLS montada por f-string com `user_id`/`account_id`/`team_id` e injetada em SQL e no JWT. Hoje explorável via F1/F2 (ids vem do cliente). | `superset_embedded.py:27-83,166-182` |
| F5 | MEDIO | UI embute seletor de personas (`usr-superadmin-god` "Full Audit 1=1") e envia `user_id` e `account_id` hardcoded `0f14ffff`; e a origem do vetor de F1/F2. | `SupersetEmbeddedDashboard.tsx:171-175,194,196,321,371` |
| F6 | MEDIO | Formato `parquet` aceito, mas o conteudo e CSV com mime parquet (Lei 8, honestidade de rotulo). | `superset_embedded.py:189-204` |
| F7 | MEDIO | `fetchExecutiveCockpit` engole todo erro e ignora respostas nao-ok: 401/500 viram painel vazio sem aviso. Componente monolitico (2717 linhas) mistura 4 modos. | `SupersetEmbeddedDashboard.tsx:~350-362` |
| F8 | BAIXO | Handlers devolvem `detail=str(e)` em 500 (vazamento de detalhe interno). | `router.py:198,219,236,255` |
| F9 | INFO | Teste de contrato vermelho (baseline) bloqueia gate de entrega. | ver Baseline |

Nao verificado nesta rodada: botao "Reativar no WhatsApp" aninhado em card clicavel (apontado na V3); acessibilidade e responsivo em navegador real; performance.

## Contestacao (doubt-driven)
- F1/F2: impersonacao legitima existe so para superadmin via `X-User-Id` em `get_current_user`; correto e permitir `user_id` diferente apenas se `current_user.is_superadmin`. Reproduzido por execucao, nao e suposicao.
- F3: nao e falso positivo por design; a tabela pode nao ter `owner_id`, mas a correcao e mapear RLS por tabela, nao ampliar para o tenant.
- Teste existente `test_superset_bi_api_endpoints` envia `user_id` arbitrario e passa, ou seja, codifica o comportamento vulneravel; precisara mudar.
