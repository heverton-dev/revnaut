# SKILL (interno) — Fase 2: Analisador

Comportamento: recebe `ideia` + saída da Fase 1 → 1 chamada real de LLM via `litellm` → grava `_phase_02_index.json` → devolve `status` pro `orquestrador.py`.

Chamada apenas via `OrquestradorAIDD._executar_phase()` ou manualmente via `/aidd-analisador` (ver `COMMANDS.md`). Hoje não existe script real — ver `config.json`.
