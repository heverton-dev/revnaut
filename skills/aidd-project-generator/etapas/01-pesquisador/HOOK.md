# HOOK — Fase 1: Pesquisador

**N/A por enquanto.**

Esta fase roda sob demanda, disparada explicitamente pelo `orquestrador.py` — não precisa reagir a nenhum evento do harness (não é o tipo "toda vez que um arquivo X é editado, valide Y").

**Quando isso mudaria:** se quisermos que os gates R1-R4 sejam re-verificados automaticamente sempre que `_phase_01_index.json` for editado manualmente (proteção contra alguém "arrumar" o índice à mão pra passar no gate), aí um hook `PostToolUse` no matcher `Edit`/`Write` filtrando esse path faria sentido — reexecutando a validação dos gates sem reprocessar a fase inteira.
