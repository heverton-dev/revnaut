# SKILL (interno) — Fase 1: Pesquisador

Este não é um skill top-level invocável por `/nome` — é a especificação de comportamento da Fase 1 dentro do skill guarda-chuva `aidd-project-generator`. A forma de rodar manualmente esta fase isolada é via o comando em `COMMANDS.md` (`/aidd-pesquisador`), não por um skill próprio, pra não poluir o namespace global de skills com uma entrada por fase.

## Comportamento esperado
Recebe `ideia` (texto) → consulta GitHub/HuggingFace/Replit → filtra pelos gates R1-R4 (`RULES.md`) → grava `_phase_01_index.json` (`SPEC.md`) → devolve `status: COMPLETO|FALHA` pro `orquestrador.py`.

## Quando esta fase é chamada
Só pelo `OrquestradorAIDD._executar_phase()` (`scripts/orquestrador.py:115`), como subprocess:
```
python scripts/phases/01_pesquisador.py <pasta_saida>
```
Hoje esse arquivo não existe — ver `config.json` (`status: "spec_only"`).

## Relação com as outras fases
Produz o insumo que a Fase 2 (Analisador) consome para não alucinar contra referências inexistentes (gate A2 da Fase 2 exige mínimo 2 referências citadas).
