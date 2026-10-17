# SPEC — Fase 2: Analisador

**Status:** ⚠️ NÃO IMPLEMENTADO. Baseado no desenho honesto de `PLANO-REAL-9-FASES.md` (Correção 1/5), não na versão antiga do `SKILL.md`.

## Objetivo
Cruzar a ideia do usuário com as referências reais da Fase 1 e produzir uma especificação estruturada (objetivo, público, constraints, stack, arquitetura sugerida).

## Input
- `ideia` (string)
- `.aidd/cache/_phase_01_index.json` (referências da Fase 1)

## Comportamento
1 chamada real de LLM via `litellm` (não `from agent import agent` — esse import é conhecido por falhar sempre, `ImportError` confirmado; nunca usar).
```python
import litellm
resposta = litellm.completion(
    model=os.getenv("LLM_MODEL", "anthropic/claude-haiku-4-5"),
    messages=[...ideia + referencias...],
)
```
Modelo trocável só por variável de ambiente `LLM_MODEL` — sem editar código pra trocar de provedor (Anthropic/OpenAI/Google/Ollama).

## Output
`.aidd/cache/_phase_02_index.json`:
```json
{
  "fase": 2,
  "status": "COMPLETO",
  "analise": {"objetivo": "", "publico": "", "constraints": [], "stack": [], "arquitetura": ""},
  "referencias_citadas": ["url1", "url2"],
  "resposta_bruta_llm": "...",
  "usage": {"input_tokens": 0, "output_tokens": 0}
}
```
`usage` tem que vir do campo real retornado pela API (`resposta.usage`), nunca estimado/inventado.

## Gates
| Gate | Regra |
|---|---|
| **A1** | Schema válido — os 4 campos obrigatórios presentes |
| **A2** | Zero-alucinação — mínimo 2 URLs de `referencias_citadas` existem literalmente em `_phase_01_index.json` |
| **A3** | 5 aspectos cobertos (objetivo, público, constraints, stack, arquitetura) |
| **A4** | Coerência textual — nota de qualidade; **é o único gate desta fase que não é 100% mecânico** (ver `RULES.md` sobre esse risco) |

## Custo
~5k tokens por execução (1 chamada real de LLM). Rastreável via `usage` real, não estimativa.
