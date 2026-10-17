# SPEC — Fase 3: Designer

**Status:** ⚠️ NÃO IMPLEMENTADO. **Correção importante:** o `SKILL.md` antigo descrevia esta fase como "5 subagentes LLM paralelos" (30k tokens) — isso é a versão fabricada/não auditada. O desenho honesto (`PLANO-REAL-8-FASES.md`) é bem mais simples.

## Objetivo
Desenhar a estrutura AIDD 5-camadas para o projeto e nomear os arquivos específicos ao domínio da ideia.

## Comportamento real
1. **Determinístico, zero LLM:** gera a estrutura de camadas como dicionário Python fixo (as 5 camadas AIDD são sempre as mesmas — não precisam de LLM pra existir).
2. **1 chamada real de LLM** (não 5 subagentes) só para decidir os *nomes* de arquivo específicos ao domínio (ex: para uma ideia de "CLI de validação de schema JSON", sugerir `validador.py`, não `main.py` genérico).

## Input
- `ideia` (string)
- `.aidd/cache/_phase_02_index.json` (análise da Fase 2)

## Output
`.aidd/cache/_phase_03_index.json`:
```json
{
  "fase": 3,
  "status": "COMPLETO",
  "camadas": {"core": [], "shared": [], "modules": [], "static": [], "tests": []},
  "nomes_sugeridos": {"arquivo_principal": "", "justificativa": ""},
  "usage": {"input_tokens": 0, "output_tokens": 0}
}
```

## Gates
| Gate | Regra |
|---|---|
| **D1** | 5 camadas AIDD presentes no dict de saída (checagem mecânica de chaves) |
| **D2** | Nomes sugeridos contêm palavra-chave literal da `ideia` — se o nome serviria pra qualquer projeto genérico, gate falha |
| **D3** | Economia de tokens medida de verdade: `usage` real desta fase comparado ao orçamento declarado em `config.json`, não estimativa |

## Custo
~2-3k tokens (1 chamada real, não 30k de 5 subagentes).
