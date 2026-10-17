# RULES — Fase 1: Pesquisador

Regras determinísticas que o script (ou quem o implementar) deve seguir. Não são sugestões — são os gates R1-R4 do `SPEC.md` traduzidos em obrigação de código.

1. **Nunca inventar referência.** Toda entrada em `referencias[]` vem de uma resposta real de API — proibido o LLM (se algum subagente for usado aqui no futuro) alucinar nome/URL de projeto.
2. **HTTP 200 obrigatório (R1).** Antes de gravar uma referência no índice, fazer request de verificação na URL. Timeout curto (ex: 5s) — se der timeout, descartar a referência, não assumir que existe.
3. **Atividade recente (R2).** Calcular `dias_desde_ultimo_commit`; referência entra na conta de "ativa" só se ≤365 dias.
4. **Estrutura válida (R3).** Repositório precisa ter pelo meno um arquivo de documentação raiz (`README*`) e não ser um fork sem commits próprios.
5. **Mínimo 5 (R4).** Se após aplicar R1-R3 sobrarem menos de 5 referências, a fase falha (`status: FALHA`) — não é permitido "completar com menos" silenciosamente.
6. **Zero tokens de LLM nesta fase.** Qualquer decisão aqui é código determinístico. Se no futuro precisar de ranking semântico (match_score), isso é Fase 2, não Fase 1.
