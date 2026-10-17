# RULES — Fase 5: Criador

1. **Toda verificação de gate usa `os.path.exists()`/consulta SQL real** — nunca "assumir que deu certo porque o comando anterior não lançou exceção".
2. **`estado_projeto.db` precisa ter dado real, não schema vazio.** Gate E3 falha se a tabela existir mas estiver vazia depois da execução — senão o gate é fachada.
3. **Git commit tem que existir de verdade** (`git log --oneline` não vazio) — `git init` sozinho não satisfaz E2.
4. **S1 é inegociável.** Nenhum projeto sai desta fase com `.env`/credenciais sem estar no `.gitignore`, nem com secret literal no código gerado.
