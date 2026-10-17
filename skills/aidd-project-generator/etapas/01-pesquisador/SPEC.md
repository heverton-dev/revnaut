# SPEC — Fase 1: Pesquisador de Referências

**Status:** ⚠️ NÃO IMPLEMENTADO — este SPEC existe, `scripts/phases/01_pesquisador.py` não existe ainda no skill `aidd-project-generator`. Ver `config.json` (`status: "spec_only"`).

## Objetivo
Dada a ideia de projeto do usuário, buscar referências reais e similares em repositórios públicos (GitHub, HuggingFace, Replit) para embasar a Fase 2 (Analisador) com exemplos concretos — não com suposição do modelo.

## Input
| Campo | Tipo | Origem |
|---|---|---|
| `ideia` | string | Texto livre do usuário, vindo do `orquestrador.py --ideia "..."` |
| `cache_dir` | path | Default `.aidd/cache` |

## Output
Arquivo `.aidd/cache/_phase_01_index.json`:
```json
{
  "fase": 1,
  "status": "COMPLETO",
  "referencias": [
    {"nome": "string", "url": "string", "fonte": "github|huggingface|replit",
     "stars": 0, "ultimo_commit": "ISO-8601", "match_score": 0.0}
  ],
  "total_encontrado": 0
}
```

## Gates (critério de aceite — mecânicos, não opinião do LLM)
| Gate | Regra |
|---|---|
| **R1** | Toda `url` em `referencias[]` responde HTTP 200 |
| **R2** | ≥90% das referências têm atividade (commit) nos últimos 12 meses |
| **R3** | Estrutura do repositório é válida (tem README, não é fork vazio) |
| **R4** | Mínimo de 5 referências encontradas — abaixo disso, gate falha e Fase 1 retorna `status: FALHA` |

Falha em qualquer gate → `orquestrador.py` interrompe o pipeline na Fase 1 (ver `_executar_phase` em `scripts/orquestrador.py:115`).

## Custo
0k tokens de LLM — 100% Python + chamadas de API (GitHub Search API, etc). Determinismo total.

## Erros esperados
- Rate limit da API do GitHub sem token configurado → deve degradar avisando, não travar silenciosamente.
- Zero resultados para ideia muito nichada → falha R4 é esperada e correta, não é bug.
