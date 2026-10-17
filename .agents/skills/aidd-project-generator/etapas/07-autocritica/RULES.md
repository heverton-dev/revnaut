# RULES — Fase 7: Autocrítica

1. **Proibido reintroduzir a narrativa fabricada anterior.** Nada de score "60/100" com classificação textual ("Prototipo", "TRANSCENDENTE"), nada de "590 horas / $88k / 8 meses" de investimento hardcoded, nada de "Roadmap v3.0 → v6.0" com horas chutadas. Isso já foi auditado e identificado como fabricação — não repetir.
2. **`score` é sempre recalculável por fora.** Qualquer pessoa deve poder pegar o `checks{}` do JSON e recalcular o `score` manualmente com a fórmula — se o número não bater, a implementação está mentindo.
3. **Se algum dia quisermos estimativa de esforço/roadmap real:** só pode vir de `estado_projeto.db` com dados de execuções que de fato aconteceram (ver `PLANO-REAL-8-FASES.md`, Fase 6 "Predictive Gates" — que exige 20+ execuções reais antes de escrever uma linha de código disso). Nunca de tabela estática no código.
4. **Nome do arquivo é `07_autocritica.py`, não `07_analisador.py`.** Evita colisão de nome com `02_analisador.py` e deixa claro que a fase é distinta.
