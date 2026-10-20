# Estado - ciclo completo rota dashboard (V4)
- P1, P2 aprovados (todos os tickets DASH4-01 a 09).
- Estagio 4 executado, nada commitado; aguardando P4 (revisao do diff e decisao de commit).
- Decisoes: parquet rejeitado (422 no backend; aviso no front) em vez de implementado; seletor de personas removido do front; superadmin mantem impersonacao via user_id/X-User-Id; datasets account-wide negados (403) para escopo que nao seja tenant global/superadmin.
- Validacao: pytest completo 681 passed, 0 failed; tsc exit 0. Sem teste E2E em navegador para as mudancas de front.
