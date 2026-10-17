# SPEC — Fase 7: Autocrítica

**Status:** ⚠️ NÃO IMPLEMENTADO. **Correção crítica dupla:**
1. O `orquestrador.py` original chamava esta fase de `07_analisador.py` — mesmo nome do arquivo da Fase 2 (`02_analisador.py`). Renomeada aqui para `07_autocritica.py` (ver mudança em `scripts/orquestrador.py`).
2. A versão anterior (`DEMO-7-PHASES.md`) descrevia esta fase gerando `score: 60/100`, roadmap de "590 horas, $88k, 8 meses" e classificações como "TRANSCENDENTE" — o próprio `PLANO-REAL-8-FASES.md:4` confirma que essa narrativa **era fabricada** (auditoria de 29/08/2026). Este SPEC não reproduz nada disso.

## Objetivo
Rodar uma checklist de fatos verificáveis sobre o projeto recém-criado — não opinião de LLM, não roadmap especulativo.

## Comportamento real
```python
checks = {
    'readme_existe': os.path.exists(f'{pasta}/README.md'),
    'git_inicializado': os.path.exists(f'{pasta}/.git'),
    'sqlite_criado': os.path.exists(f'{pasta}/estado_projeto.db'),
    'todos_gates_logados': len(gates_executados) == len(gates_esperados),
    'sem_gate_falho': all(g['status'] == 'PASS' for g in gates_executados),
}
score = sum(checks.values()) / len(checks) * 100  # nota real 0-100, baseada em fatos
```
Zero LLM. Zero estimativa de horas/custo/roadmap — se o usuário quiser isso no futuro, precisa vir de dados reais de execuções acumuladas (ver nota em `RULES.md`), nunca de tabela fixa.

## Output
`.aidd/cache/_phase_07_index.json`:
```json
{
  "fase": 7,
  "status": "COMPLETO",
  "checks": {"readme_existe": true, "git_inicializado": true, "sqlite_criado": true, "todos_gates_logados": true, "sem_gate_falho": true},
  "score": 100.0
}
```

## Gate
| Gate | Regra |
|---|---|
| **A7** | `score` é literalmente `sum(checks.values()) / len(checks) * 100` — recalculável e conferível por qualquer pessoa lendo o JSON, sem precisar confiar em texto narrativo |

## Teste anti-alucinação
Apagar de propósito um arquivo que a Fase 5 deveria ter criado, rodar a Fase 7 de novo — `score` tem que cair e o check correspondente tem que aparecer `false`, apontando especificamente aquele arquivo.
