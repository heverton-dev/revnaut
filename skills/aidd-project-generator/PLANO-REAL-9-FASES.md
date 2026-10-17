# PLANO REAL v2 — 10 Fases (Decisão + Núcleo + 8 Dimensões)

**Substitui integralmente a v1** (`PLANO-REAL-9-FASES.md` anterior), corrigida após auditoria de `proj_yt-list/scripts/phases/*.py` e re-auditoria deste próprio plano.

**Regra de ouro:** nenhuma fase é "concluída" por eu dizer que está. Só é concluída quando VOCÊ roda o comando de verificação listado e vê o resultado com seus próprios olhos.

**Teto de custo por fase:** nenhuma fase de desenvolvimento deve gastar mais que **$3 em chamadas de API** sem eu parar e avisar antes de continuar.

**Princípio de economia de tokens (estabelecido pelo usuário em 29/08/2026):**
- O que é **determinístico** (01_pesquisador, 05_criador, gates, utils_modelo) deve custar zero tokens de LLM **por design correto**, nunca por acidente (import quebrado, como estava antes da correção).
- O que é **probabilístico** (chamadas reais de LLM em 02, 03, 04-swarm, 06) pode e deve usar técnicas de economia (rtk, caveman, headroom, lean-ctx) para reduzir custo **sem reduzir qualidade do material entregue** — economia de token não é desculpa para entregar pior.
- Check-in de cota via `ccusage status` antes de cada fase (ver `~/.claude/skills/implementacao/SKILL.md`).

---

## FASE -1 — DECISÃO OBRIGATÓRIA (não é código, é uma escolha sua)

### O problema real
`proj_yt-list/scripts/phases/*.py` não é o gerador genérico "aidd-project-generator" que você pediu (rodar com qualquer ideia, qualquer harness, qualquer LLM). É um script que rodou **uma vez**, para gerar o próprio `proj_yt-list`, e ficou com YouTube hardcoded dentro (`yt_videos_processados` em `05_criador.py`).

### As duas opções reais
**Opção A — Genericizar este núcleo de verdade:** parametrizar `05_criador.py` (nome de tabela vira `f"{dominio}_processados"` derivado da ideia, não fixo), remover o hardcode YouTube, e ele vira o motor real do skill global. Reaproveita 100% do trabalho já feito (3.366 linhas, `05_criador` e `utils_modelo` já são 8/10).

**Opção B — Manter como está:** `scripts/phases/` continua sendo o pipeline **próprio e específico** do `proj_yt-list` (faz sentido ter YouTube hardcoded, já que é este projeto). O gerador genérico (`aidd-project-generator`) é construído do zero, separadamente, no skill global — sem reaproveitar estes arquivos.

**Recomendação: Opção A.** É objetivamente menos trabalho (genericizar 1 tabela + extrair 2 constantes é menos esforço que reescrever 3.366 linhas do zero), e o resultado serve aos dois propósitos.

### Comando de verificação desta fase
Nenhum — é uma decisão em texto. A prova de que foi tomada é você escolher A ou B antes de eu tocar em qualquer arquivo da Fase 0.

---

## FASE 0 — CORREÇÃO DO NÚCLEO (5 correções cirúrgicas, não reescrita)

Assumindo Opção A aprovada. Se for Opção B, esta fase muda de "corrigir" para "escrever do zero" (ver estimativa de esforço alternativa no fim).

### Correção 1/5 — Matar o import morto (`02_analisador.py`, `03_designer.py`)
**Problema real:** `from agent import agent` falha sempre (confirmado: `python -c "from agent import agent"` retorna `ImportError`). O "caminho real" nunca executa.
**O que muda:** substituir por `litellm.completion(model=os.getenv('LLM_MODEL', 'anthropic/claude-haiku-4-5'), messages=[...])` — biblioteca real (`pip install litellm`), funciona com Anthropic, OpenAI, Google, Ollama, etc. via 1 variável de ambiente.
**Comando de verificação:**
```bash
pip install litellm
LLM_MODEL="anthropic/claude-haiku-4-5" python scripts/phases/02_analisador.py "CLI para validar JSON" --cache-dir /tmp/teste1
LLM_MODEL="ollama/llama3" python scripts/phases/02_analisador.py "CLI para validar JSON" --cache-dir /tmp/teste2
```
**O que você DEVE VER:** os dois comandos rodam com **modelos diferentes** trocando só a variável de ambiente, sem editar nenhum código. `cat /tmp/teste1/_phase_02_index.json` e `/tmp/teste2/...` mostram análises com texto diferente (LLMs diferentes respondem diferente).
**Teste anti-alucinação:** rodar sem `LLM_MODEL` e sem internet — tem que falhar com erro de conexão real, não cair silenciosamente no mock.

### Correção 2/5 — Modal real (`04_decisor.py`)
**Problema real:** `_apresentar_modal_mock()` retorna dict fixo sempre. Gate C2 (`symlinks >= 0`) é sempre verdadeiro por construção — gate de fachada.
**O que muda:** `input()` real perguntando cada decisão (ou flag `--nao-interativo` para CI/CD, que aí usa uma heurística real baseada no design da Phase 3, não um dict fixo). Gate C2 vira: "todo symlink declarado aponta para um arquivo que existe" (`Path(destino).resolve().exists()`), que pode falhar de verdade.
**Comando de verificação:**
```bash
python scripts/phases/04_decisor.py --design '{"...": "..."}'
# Deve perguntar interativamente, não imprimir direto um resultado fixo
```
**O que você DEVE VER:** o terminal para e espera sua resposta antes de continuar. Se você responder diferente em 2 execuções, o JSON de saída é diferente.
**Teste anti-alucinação:** declarar um symlink para um arquivo que não existe de propósito — Gate C2 tem que reportar `FALHOU`.

### Correção 3/5 — Documentos reais (`06_documentador.py`)
**Problema real:** `_renderizar_formatos()` retorna `{'html_valido': True, 'pdf_gerado': True, ...}` sem nunca escrever nenhum arquivo. "PROJETO PRONTO!" é fabricado.
**O que muda:** escrever de fato o HTML (template Jinja2), o Markdown (montagem de string), e tentar o PDF via `typst` (se instalado) ou `weasyprint` como alternativa mais simples de instalar. Se o PDF falhar por falta de dependência, Gate F2 **reporta falha de verdade**, não `True` fixo.
**Comando de verificação:**
```bash
python scripts/phases/06_documentador.py "MeuProjeto" --cache-dir /tmp/teste3
ls /tmp/teste3/docs/
cat /tmp/teste3/docs/MeuProjeto-arquitetura.md
```
**O que você DEVE VER:** arquivos `.html`, `.md` e (se a dependência estiver instalada) `.pdf` **existindo de fato** na pasta `docs/`, com conteúdo lido do design real da Phase 3 (não texto genérico fixo).
**Teste anti-alucinação:** desinstalar a lib de PDF de propósito (`pip uninstall weasyprint`) e rodar de novo — Gate F2 tem que reportar `FALHOU: dependência não encontrada`, não `True`.

### Correção 4/5 — Auto-crítica de verdade (`07_analisador.py`)
**Problema real:** `_calcular_score` retorna `base_score = 54` fixo. Pontos fortes/fracos são listas hardcoded, iguais para qualquer projeto.
**O que muda:** calcular o score a partir de `dados` (o dict real coletado de `_phase_01` a `_phase_06`): contar gates que realmente passaram/falharam, checar se os arquivos que Phase 5/6 alegam ter criado **existem de fato no disco** (reaproveitando a lógica do Gate E1), e gerar pontos fortes/fracos derivados dessas contagens reais.
**Comando de verificação:**
```bash
python scripts/phases/07_analisador.py /tmp/projeto-A
python scripts/phases/07_analisador.py /tmp/projeto-B
diff /tmp/projeto-A/AVALIACAO-AUTO-CRITICA.md /tmp/projeto-B/AVALIACAO-AUTO-CRITICA.md
```
**O que você DEVE VER:** se `projeto-A` teve 1 gate falho e `projeto-B` teve todos passando, os scores e as listas de pontos fracos **têm que ser diferentes** entre os dois. Hoje seriam idênticos.
**Teste anti-alucinação:** apagar um arquivo que Phase 5 deveria ter criado, rodar Phase 7 de novo — o score tem que cair e o "ponto fraco" correspondente tem que aparecer mencionando especificamente aquele arquivo.

### Correção 5/5 — Testes reais para as 6 fases
**Problema real:** `tests/` coleta 0 testes via pytest, apesar do `CLAUDE.md` do projeto marcar isso como concluído.
**O que muda:** criar `tests/test_phase_02.py` até `test_phase_07.py`, com asserts reais (não `pytest.skip`) cobrindo pelo menos: 1 caso de sucesso, 1 caso de gate falho de propósito.
**Comando de verificação:**
```bash
python -m pytest tests/ -v
```
**O que você DEVE VER:** `collected N items` com N > 0, e uma lista de `PASSED`/`FAILED` reais — não `SKIPPED`.

### Esforço real (Opção A — corrigir)
30-40 horas. Custo: ~$5-8 em API (testes com litellm real).

### Esforço alternativo (Opção B — construir do zero, ignorando o que existe)
70-90 horas (equivalente à Fase 0 original da v1 do plano, que assumia partir do zero).

---

## FASE 1 — v9.0 External Learning (paralelo, independente)

Sem mudanças da v1, exceto: `01_pesquisador.py` **já existe e já tem chamadas reais** (`requests`) — confirmado por grep. Esta fase deixa de ser "criar do zero" e vira "adicionar mais fontes" (Hacker News + arXiv) ao que já existe.

### Comando de verificação
```bash
python scripts/phases/01_pesquisador.py "CLI para validar JSON"
```
### O que você DEVE VER
Resultados reais de busca no GitHub (nomes de repositório, estrelas) específicos à sua frase — rode com uma ideia bem diferente e os resultados têm que mudar.

### Esforço real
4-6 horas (só adicionar HN/arXiv, GitHub já funciona).

---

## FASE 2 — v11.0 Neuro-Symbolic / Verificação Formal (paralelo)

### Correção da v1: usar as regras REAIS, não inventadas
`gate_g0_qualidade.py` já tem regras reais e específicas: 17 canais na whitelist, 6 palavras proibidas, título entre 5-200 caracteres. `scripts/gates/regras.json` deve ser **extraído desse arquivo existente**, não inventado do zero.

```json
{
  "G0_canal": {"exige": ["canal_na_whitelist_17_itens"], "proibe": []},
  "G0_titulo": {"exige": ["titulo_entre_5_e_200_chars"], "proibe": ["titulo_contem_palavra_proibida"]},
  "G0_descricao": {"exige": ["descricao_min_20_chars"], "proibe": ["descricao_contem_palavra_proibida"]}
}
```

### Comando de verificação
```bash
pip install z3-solver
python scripts/gates/verificador_z3.py
```
### O que você DEVE VER
`sat` ou `unsat` impresso pelo Z3. Editar `regras.json` inserindo contradição de propósito → vira `unsat` com `unsat_core()` apontando a regra conflitante.

### Esforço real
8-10 horas (menor que a v1 porque as regras já existem, só precisam ser extraídas).

---

## FASE 3 — v6.0 Maestro (decisão real via LLM) — depende da Fase 0/Correção 2

Já é a implementação real de `04_decisor.py` corrigido (Correção 2 da Fase 0). Sem trabalho adicional aqui — mantido como item separado só para rastreabilidade de escopo.

---

## FASE 4 — v7.0 Swarm (3 LLMs reais, personas diferentes) — depende da Fase 3

Sem mudança de conteúdo da v1, exceto: usar `litellm` (não `anthropic.Anthropic()` direto), para as 3 personas poderem, inclusive, rodar em **3 provedores diferentes** se você quiser (ex.: 1 chamada Anthropic, 1 OpenAI, 1 local) — universalidade aplicada literalmente na diversidade do swarm.

### Comando de verificação
```bash
python scripts/phases/04b_decisor_swarm.py --ideia "Bot que modera conteúdo 24/7"
cat .aidd/cache/_phase_04b_swarm.json | jq '.respostas_brutas'
```
### O que você DEVE VER
3 textos diferentes entre si, cada um refletindo sua persona.

### Esforço real
15-20 horas. Custo: 3x por decisão — aprovar antes de automatizar.

---

## FASE 5 — v8.0 Self-Modifying REDEFINIDO: Sugestão de Patch — depende da Fase 0

Sem mudança da v1. `patches/` + `git apply --check` como prova.

### Esforço real
10-12 horas.

---

## FASE 6 — v10.0 Predictive Gates — CORRIGIDA: hoje são 0 execuções, não "quase 20"

### Correção da v1
`estado_projeto.db` tem **0 linhas em todas as 5 tabelas**, confirmado. A única execução real (a que gerou o proj_yt-list) nem gravou telemetria no banco — só nos JSONs de `.aidd/cache/`. Antes desta fase começar, é preciso:
1. Conectar a Correção 4 (Phase 7 real) para também escrever em `estado_projeto.db`, não só em JSON.
2. Rodar o pipeline completo pelo menos 20 vezes com ideias reais e variadas (uso normal ao longo de semanas).

### Comando de verificação (só depois do pré-requisito acima)
```bash
python -c "
import sqlite3
conn = sqlite3.connect('estado_projeto.db')
print(conn.execute('SELECT COUNT(*) FROM yt_telemetria_execucao').fetchone())
"
```
### O que você DEVE VER
Um número **maior que 0** antes de qualquer código de predição ser escrito. Se ainda for 0, esta fase não começa — ponto final, não é negociável.

### Esforço real
6-8 horas de código + semanas de uso real antes de ser possível começar.

---

## FASE 7 — v12.0 REDEFINIDO: Reaproveitamento de Templates — depende de 2+ execuções reais

### Correção da v1
Hoje existe **exatamente 1** execução real (a do proj_yt-list). Falta pelo menos mais 1 execução real e distinta antes de testar reaproveitamento.

### Comando de verificação
```bash
python scripts/orquestrador.py /pasta-A --ideia "CLI Python para validar JSON"
python scripts/orquestrador.py /pasta-B --ideia "CLI Python para validar YAML"
cat pasta-B/.aidd/cache/_phase_04_decisao.json | jq '.reaproveitado_de'
```
### O que você DEVE VER
`"reaproveitado_de": "pasta-A"` e zero chamadas de LLM logadas na segunda execução.

### Esforço real
8-10 horas.

---

## FASE 8 — v13.0 Orchestrator: integração final — CORRIGIDA

### Correção da v1
`scripts/orquestrador.py` **já existe** (363 linhas) e responde `--help` com um menu real (`--modo interativo|batch|teste`). Esta fase não é "construir do zero" — é **verificar se ele de fato chama as 6 fases corrigidas na ordem certa** e ler o restante das 363 linhas (não lidas ainda nesta auditoria) para confirmar se há mais teatro escondido ali.

### Comando de verificação final
```bash
python scripts/orquestrador.py --modo teste
python scripts/orquestrador.py /pasta-final --ideia "API REST para gerenciar tarefas" --modo completo
cat pasta-final/AVALIACAO-AUTO-CRITICA.md
```
### O que você DEVE VER
Um relatório com linhas de checklist objetiva (arquivo existe, gate passou/falhou com número real), sem nenhuma linha "Score: 450/100" ou "Confiança: 87%" sem cálculo real por trás.

---

## RESUMO DE ORDEM E ESFORÇO TOTAL (v2, corrigido)

| Ordem | Fase | Pré-requisito | Horas reais | Custo API |
|---|---|---|---|---|
| 1 | Fase -1 (Decisão A/B) | — | 0h (decisão sua) | — |
| 2 | Fase 0 (5 correções) | Fase -1 = Opção A | 30-40h | ~$5-8 |
| 3 | Fase 1 (v9.0) | Nenhum, paralelo | 4-6h | $0 |
| 4 | Fase 2 (v11.0) | Nenhum, paralelo | 8-10h | $0 |
| 5 | Fase 3 (v6.0) | Fase 0 | incluso | — |
| 6 | Fase 4 (v7.0) | Fase 3 | 15-20h | 3x/decisão |
| 7 | Fase 5 (v8.0) | Fase 0 | 10-12h | ~$2 |
| 8 | Fase 7 (v12.0) | 2+ execuções reais | 8-10h | $0 |
| 9 | Fase 6 (v10.0) | 20+ execuções reais (hoje: 0) | 6-8h | $0 |
| 10 | Fase 8 (integração) | Todas anteriores | 8-10h | — |

**Total real: ~80-110 horas, ~$10-20 em API para desenvolvimento** (igual à v1 — a correção não aumentou o esforço total, só a ordem e a precisão de onde ele se aplica).

**Nenhuma fase começa sem sua aprovação explícita — e a Fase -1 (decisão A/B) precisa ser respondida antes de qualquer coisa, inclusive antes da Fase 0.**
