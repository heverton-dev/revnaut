# SPEC — Fase 6: Documentador

**Status:** ⚠️ NÃO IMPLEMENTADO. **Correção crítica:** em código real auditado anteriormente, `_renderizar_formatos()` retornava `{'html_valido': True, 'pdf_gerado': True, ...}` **sem nunca escrever nenhum arquivo**. Esta fase existe pra nunca repetir isso.

## Objetivo
Gerar documentação tripartite (HTML + Markdown + PDF) a partir dos dados reais das fases 1-5. Zero LLM — é montagem de template, não geração criativa.

## Comportamento real
1. **HTML:** template Jinja2 real, preenchido com dados reais de `_phase_0{1..5}_index.json`.
2. **Markdown:** montagem de string (não chamada de LLM) com os mesmos dados.
3. **PDF:** tentar via `typst` (padrão deste projeto, ver `templates/template-book.typ` do `transcption-to-book` como referência) ou `weasyprint` como alternativa mais simples de instalar. **Se a dependência não estiver instalada, a fase reporta falha de verdade — nunca `pdf_gerado: True` fixo.**

## Output
```
docs/
├── arquitetura.html
├── arquitetura.md
└── arquitetura.pdf   (só se a geração realmente funcionou)
```

## Gates
| Gate | Regra |
|---|---|
| **F1** | `arquitetura.html` existe no disco E não está vazio |
| **F2** | `arquitetura.pdf` existe no disco — **se a lib de PDF não estiver instalada, este gate FALHA de verdade**, não reporta sucesso |
| **F3** | `arquitetura.md` é Markdown válido (lint básico: headers bem formados, sem tag HTML quebrada) |

## Custo
0 tokens de LLM.
