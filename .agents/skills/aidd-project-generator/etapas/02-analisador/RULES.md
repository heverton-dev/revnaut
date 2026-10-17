# RULES — Fase 2: Analisador

1. **Nunca usar `from agent import agent`.** Import conhecido por falhar (`ImportError` confirmado em auditoria anterior). Usar `litellm.completion(...)` real.
2. **Modelo só via env var (`LLM_MODEL`).** Proibido hardcodar provedor/modelo no código — quebra a promessa de "funciona com qualquer harness/LLM".
3. **`usage.input_tokens`/`output_tokens` tem que vir da resposta real da API.** Nunca estimar com `len(texto)/4` ou fórmula parecida e apresentar como "tokens reais".
4. **Gate A2 é anti-alucinação de verdade.** As URLs citadas em `referencias_citadas` precisam existir literalmente (comparação de string exata) em `_phase_01_index.json` — não vale o LLM "lembrar" de um projeto que soa plausível.
5. **Gate A4 (qualidade textual) é o elo fraco desta fase — documentar isso, não esconder.** É o único gate aqui que depende de julgamento, não de fato verificável em código. Se possível, implementar como checagem mecânica auxiliar (ex: tamanho mínimo de texto, ausência de campos vazios) em vez de "parece bom".
6. **Teste anti-alucinação obrigatório antes de considerar a fase pronta:** rodar com 2 ideias bem diferentes; os dois `_phase_02_index.json` têm que ter `resposta_bruta_llm` visivelmente diferente. Se rodar sem `LLM_MODEL` e sem internet, tem que falhar com erro de conexão real — nunca cair num mock silencioso.
