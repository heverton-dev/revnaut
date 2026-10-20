# Tickets V4 - dashboard (ordem de execucao)

| ID | Sev | Titulo | Bloqueado por | Criterio binario (prova) | Arquivos |
|---|---|---|---|---|---|
| DASH4-01 | CRITICO | Identidade vem da sessao no guest-token | - | Teste RED/GREEN: usuario comum com `user_id=superadmin` recebe 403 ou RLS do proprio usuario; superadmin pode agir como outro | `intelligence/router.py`, `schemas.py`, `tests/test_superset_rls_embedded.py` |
| DASH4-02 | CRITICO | Mesma regra em export-dataset e text-to-sql, `account_id` sempre `current_user.account_id` | DASH4-01 | Teste: usuario comum com `account_id` alheio ou `user_id` alheio recebe 403; contagem de linhas = escopo proprio | `router.py`, `schemas.py`, testes |
| DASH4-03 | ALTO | RLS por tabela (sem fallback para o tenant inteiro) | DASH4-02 | Teste: consultor SELF exporta `consignment_turnover`/`dentgo_deliveries`/`anvisa_rma` e nao ve linhas de outro dono | `superset_embedded.py`, `text_to_sql_agent.py` |
| DASH4-04 | ALTO | Clausula RLS parametrizada / ids validados | DASH4-03 | Teste: `user_id` com aspas (`x' OR '1'='1`) nao altera SQL (400 ou parametro) | `superset_embedded.py` |
| DASH4-05 | MEDIO | Remover seletor de personas e `user_id`/`account_id` do payload no front | DASH4-01,02 | `grep USER_RLS_OPTIONS` = 0; tsc exit 0; guest-token chamado sem `user_id` | `SupersetEmbeddedDashboard.tsx`, `api_contracts.ts` |
| DASH4-06 | MEDIO | `parquet` real ou rejeitar formato | - | Teste: `format=parquet` gera parquet valido ou retorna 422 | `superset_embedded.py`, `schemas.py` |
| DASH4-07 | MEDIO | Cockpit mostra erro/estado parcial por fonte | - | Teste de componente ou E2E: 401/500 em `/metrics` exibe aviso visivel | `SupersetEmbeddedDashboard.tsx` |
| DASH4-08 | BAIXO | Mensagem 500 generica + log interno | - | Teste: excecao forcada nao devolve texto interno | `router.py` |
| DASH4-09 | INFO | Sincronizar `api_contracts.ts` com rotas `access` | - | `test_api_contracts_sync` verde | `frontend/src/types/api_contracts.ts` (resolver junto do trabalho de access) |

Sugestao P2: DASH4-01 a DASH4-04 (criticos e altos) + DASH4-09 para destravar o gate.
