# RULES — Fase 3: Designer

1. **Não reintroduzir os "5 subagentes paralelos".** Essa descrição existiu no `SKILL.md` antigo e nunca foi implementada nem auditada como real — é 1 chamada de LLM, ponto.
2. **Camadas AIDD são um dict fixo no código, não decisão do LLM.** Não gastar tokens perguntando ao modelo algo que é sempre a mesma resposta.
3. **Gate D2 é o anti-alucinação desta fase:** se os nomes de arquivo sugeridos para "CLI de schema JSON" e "dashboard de métricas" saírem intercambiáveis, a chamada de LLM não está considerando a ideia de verdade — é prompt genérico disfarçado.
4. **D3 usa `usage` real da API**, igual à Fase 2 — nunca estimar.
