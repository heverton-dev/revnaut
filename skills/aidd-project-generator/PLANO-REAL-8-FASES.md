# PLANO REAL — 9 Fases (Núcleo + 8 Dimensões)

**Status:** Plano técnico de reconstrução, pós-auditoria de 29/08/2026.
**Substitui:** toda a narrativa de score (60→450) das versões v6.0-v13.0 anteriores, que era fabricada (ver AUDITORIA na conversa que originou este documento).
**Regra de ouro deste documento:** nenhuma fase é "concluída" por eu dizer que está. Só é concluída quando VOCÊ roda o comando de verificação listado e vê o resultado com seus próprios olhos.

Decisões já tomadas por você:
- v8.0 → redefinido como sugestão de patch (seguro), não auto-modificação.
- v12.0 → redefinido como reaproveitamento de templates, não ecossistema fictício.
- Escopo → skill global `~/.claude/skills/aidd-project-generator`, não feature do proj_yt-list.

---

## FASE 0 — O NÚCLEO (pré-requisito absoluto de tudo mais)

### O que será criado
```
scripts/phases/
├── 01_pesquisador.py       (~150 linhas)
├── 02_analisador.py        (~200 linhas)
├── 03_designer.py          (~250 linhas)
├── 04_decisor.py           (~150 linhas)
├── 05_criador.py           (~200 linhas)
├── 06_documentador.py      (~200 linhas)
├── 07_analisador_critico.py (~250 linhas — o real "Phase 7", nunca escrito até hoje)
└── utils_modelo.py         (~80 linhas)
```

### O que cada arquivo faz de verdade (sem LLM decorativo)
- **01_pesquisador.py**: recebe a ideia (string), chama a API do GitHub Search (`https://api.github.com/search/repositories?q=<ideia>`) via `requests`, salva os 5 resultados reais (nome, estrelas, url) em `.aidd/cache/_phase_01_pesquisa.json`. Zero LLM aqui — é 100% determinístico.
- **02_analisador.py**: 1 chamada real de LLM (Anthropic API, `anthropic` SDK) comparando a ideia com as referências da fase 1. Salva a resposta bruta da API em `.aidd/cache/_phase_02_analise.json`, incluindo o `usage.input_tokens`/`output_tokens` reais retornados pela API (não estimados).
- **03_designer.py**: gera a estrutura de pastas AIDD 5-camadas como dicionário Python determinístico (sem LLM) + 1 chamada de LLM só para decidir nomes de arquivos específicos ao domínio da ideia.
- **04_decisor.py**: decisão Global vs Local (Skill/MCP/Hook/CLAUDE.md) — 1 chamada real de LLM com schema JSON forçado (`tool_choice` obrigatório), retornando decisão + justificativa + confiança auto-reportada.
- **05_criador.py**: `os.makedirs`, `subprocess.run(['git', 'init'])`, `sqlite3.connect()` criando `estado_projeto.db` de verdade com uma tabela `execucoes(id, timestamp, ideia, gates_json)`. 100% determinístico, zero LLM.
- **06_documentador.py**: gera README.md real a partir de um template Jinja2 preenchido com dados reais das fases anteriores. Zero LLM (é montagem de string, não geração criativa).
- **07_analisador_critico.py**: o Phase 7 real. Roda uma checklist de **verificações objetivas via código** (não opinião de LLM):
  ```python
  checks = {
      'readme_existe': os.path.exists(f'{pasta}/README.md'),
      'git_inicializado': os.path.exists(f'{pasta}/.git'),
      'sqlite_criado': os.path.exists(f'{pasta}/estado_projeto.db'),
      'todos_gates_logados': len(gates_executados) == len(gates_esperados),
      'sem_gate_falho': all(g['status'] == 'PASS' for g in gates_executados),
  }
  score = sum(checks.values()) / len(checks) * 100  # nota real 0-100, baseada em fatos, não em vibe
  ```

### Dependências reais a instalar
```bash
pip install anthropic requests jinja2
```
Requer `ANTHROPIC_API_KEY` real configurada como variável de ambiente.

### Comando de verificação (o que VOCÊ roda)
```bash
cd ~/.claude/skills/aidd-project-generator
python scripts/orquestrador.py /caminho/para/pasta-teste --modo completo
echo "Exit code: $?"
```

### O que você DEVE VER
1. `echo $?` retorna **0** (sucesso real de processo, não impresso por print — é o exit code do SO).
2. A pasta `pasta-teste/` contém arquivos que **não existiam antes** de você rodar o comando.
3. `pasta-teste/estado_projeto.db` abre com `sqlite3 pasta-teste/estado_projeto.db "SELECT * FROM execucoes;"` e retorna 1 linha real.
4. `.aidd/cache/_phase_02_analise.json` contém texto de resposta da Anthropic API **especificamente sobre a ideia que você digitou** — rode com 2 ideias diferentes, os JSONs têm que ter conteúdo diferente.

### Teste anti-alucinação específico desta fase
Delete a pasta `scripts/phases/02_analisador.py` de propósito e rode de novo. **Tem que falhar com exit code 1** e uma mensagem de erro real (não um "print de sucesso mesmo assim"). Se o comando "funcionar" mesmo com o arquivo deletado, alguma coisa está mockada escondida.

### Esforço real estimado
20-30 horas. Custo: ~$2-5 em chamadas de API Anthropic para testes (poucos tokens por chamada).

---

## FASE 1 — v9.0 External Learning (pode começar em paralelo à Fase 0)

### O que será criado
```
scripts/external/hn_client.py       (~40 linhas)
scripts/external/github_client.py   (~40 linhas)
scripts/external/cache.py           (~30 linhas, TTL de 1h para não abusar das APIs)
```

### O que faz de verdade
```python
import requests
def get_top_hn_stories(n=5):
    ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:n]
    return [requests.get(f"https://hacker-news.firebaseio.com/v0/item/{i}.json").json() for i in ids]
```
Isso é a implementação inteira da parte "HN" — 3 linhas reais, sem teatro.

### Comando de verificação
```bash
python scripts/external/hn_client.py
```

### O que você DEVE VER
- Títulos de posts reais do Hacker News **de agora**. Para confirmar que não é hardcoded: rode o comando, anote os títulos, espere 2 horas, rode de novo — os títulos/scores têm que ter mudado (HN muda o ranking constantemente).
- Se rodar sem internet (`--offline` ou desligando o wifi), **tem que falhar** com `ConnectionError` real, não retornar dados "de fallback" silenciosamente.

### Teste anti-alucinação específico
```bash
python scripts/external/hn_client.py > run1.txt
python scripts/external/hn_client.py > run2.txt
diff run1.txt run2.txt
```
Diferença esperada nos scores/comentários (dados vivos). Se `diff` retornar vazio sempre, é cache disfarçado ou dado estático.

### Esforço real
4-6 horas. Custo: $0 (APIs gratuitas).

---

## FASE 2 — v11.0 Neuro-Symbolic / Verificação Formal (paralelo, mas precisa de um passo prévio)

### Passo prévio obrigatório (não existia antes)
Escrever as regras dos Gates G0/G1/G2 em formato **estruturado**, não prosa solta:
```
scripts/gates/regras.json
{
  "G0": {"exige": ["canal_whitelist_nao_vazio"], "proibe": []},
  "G1": {"exige": ["url_retorna_http_200"], "proibe": []},
  "G2": {"exige": ["toda_citacao_tem_video_id"], "proibe": ["citacao_orfa"]}
}
```

### O que será criado
```
scripts/gates/verificador_z3.py  (~80 linhas)
```

### O que faz de verdade
```python
from z3 import Solver, Bool, Implies, Not, sat

def verificar_consistencia(regras):
    s = Solver()
    condicoes = {nome: Bool(nome) for regra in regras.values() for nome in regra['exige'] + regra['proibe']}
    for gate, regra in regras.items():
        for exige in regra['exige']:
            s.add(condicoes[exige])
        for proibe in regra['proibe']:
            s.add(Not(condicoes[proibe]))
    resultado = s.check()
    return str(resultado)  # 'sat' ou 'unsat', literal do Z3 — não fabricado
```

### Dependência real
```bash
pip install z3-solver
```

### Comando de verificação
```bash
python scripts/gates/verificador_z3.py
```

### O que você DEVE VER
A palavra literal `sat` ou `unsat` **impressa pelo próprio Z3**, não por um `print()` meu. Para provar que é real: edite `regras.json` inserindo uma contradição de propósito (ex.: Gate A exige X, Gate B proíbe X) e rode de novo — tem que virar `unsat` e o Z3 tem que conseguir listar qual regra conflitou (`s.unsat_core()`).

### Teste anti-alucinação
```bash
python -c "import z3; print(z3.get_version_string())"
```
Se isso falhar (`ModuleNotFoundError`), a fase inteira é impossível de ter rodado — é o teste mais simples de todos: a biblioteca existe ou não existe no ambiente.

### Esforço real
10-15 horas (a maior parte é formalizar as regras, não o código Z3 em si).

---

## FASE 3 — v6.0 Maestro (1 decisão real via LLM) — depende da Fase 0

### O que será criado
Nenhum arquivo novo — isso é a implementação real de `scripts/phases/04_decisor.py`, já especificado na Fase 0. Não existe "v6.0" separado do núcleo; era um erro de design anterior tratar isso como camada extra.

### Comando de verificação
```bash
python scripts/phases/04_decisor.py --ideia "CLI para validar schemas JSON"
python scripts/phases/04_decisor.py --ideia "Dashboard web de métricas em tempo real"
diff <(cat saida1.json) <(cat saida2.json)
```

### O que você DEVE VER
- `saida1.json` decide "Skill local" (CLI não precisa rodar em background) com uma justificativa mencionando "CLI" e "schemas JSON" explicitamente no texto.
- `saida2.json` decide algo diferente (provavelmente "MCP" ou "processo separado", por ser web/tempo-real) com justificativa mencionando "dashboard" e "tempo real".
- Se as duas justificativas forem intercambiáveis (a mesma frase genérica serviria para qualquer ideia), a decisão não é real — é template disfarçado.

### Esforço real
Já contado dentro da Fase 0 (é o mesmo arquivo `04_decisor.py`).

---

## FASE 4 — v7.0 Swarm (3 LLMs reais, personas diferentes) — depende da Fase 3

### O que será criado
```
scripts/phases/04b_decisor_swarm.py  (~120 linhas)
```

### O que faz de verdade
3 chamadas reais e **sequenciais** (não threads fake) à API Anthropic, cada uma com um `system prompt` diferente:
```python
PERSONAS = [
    "Você é um arquiteto de software focado em manutenibilidade a longo prazo.",
    "Você é um engenheiro de segurança focado em superfície de ataque.",
    "Você é um engenheiro de performance focado em custo operacional.",
]
respostas = [chamar_llm(system=p, ideia=ideia) for p in PERSONAS]
```
Agregação real: conta qual opção (Skill/MCP/Hook) apareceu mais vezes nas 3 respostas estruturadas (schema JSON forçado); se houver empate 1-1-1, marca `escalar_para_humano=True` de verdade (não decide por índice de lista).

### Comando de verificação
```bash
python scripts/phases/04b_decisor_swarm.py --ideia "Bot que modera conteúdo em tempo real 24/7"
cat .aidd/cache/_phase_04b_swarm.json | jq '.respostas_brutas'
```

### O que você DEVE VER
3 blocos de texto **diferentes entre si**, cada um mencionando explicitamente a persona que o gerou (ex.: o de segurança falando de rate-limiting/abuso, o de performance falando de custo de rodar 24/7). Se os 3 textos forem parecidos/genéricos, a diversidade de personas não está funcionando de verdade — está usando o mesmo prompt 3x.

### Custo real
3x o custo de 1 chamada de LLM por decisão. Isso é dinheiro real por execução — você precisa aprovar esse custo recorrente antes de eu automatizar isso em produção.

### Esforço real
15-20 horas.

---

## FASE 5 — v8.0 Self-Modifying REDEFINIDO: Sugestão de Patch — depende da Fase 0

### O que será criado
```
scripts/autocorrecao/gerador_patch.py  (~100 linhas)
patches/  (pasta onde os diffs sugeridos são salvos, nunca aplicados sozinhos)
```

### O que faz de verdade
Quando um Gate falha, captura o traceback real do Python (`traceback.format_exc()`), manda para o LLM com o código-fonte real do arquivo que falhou, pede um diff no formato unificado (`--- a/arquivo\n+++ b/arquivo\n@@ ...`), salva em `patches/sugestao-{timestamp}.diff`. **Nunca aplica sozinho.**

### Comando de verificação
```bash
# Provocar uma falha de propósito (ex: renomear um campo obrigatório no schema)
python scripts/orquestrador.py /pasta-teste --forcar-erro-gate-g2
ls patches/
git apply --check patches/sugestao-*.diff
echo "Diff é válido: exit $?"
```

### O que você DEVE VER
- Um arquivo `.diff` real na pasta `patches/`.
- `git apply --check` retornando exit code 0 (prova de que o diff é sintaticamente aplicável de verdade, não texto solto).
- Depois de você mesmo rodar `git apply patches/sugestao-XXX.diff` manualmente e rodar o pipeline de novo: o erro que você provocou não acontece mais.

### Teste anti-alucinação
Se o patch sugerido for genérico (`# TODO: corrigir isso`) em vez de um diff real e aplicável, é fraude. `git apply --check` falhando é a prova objetiva.

### Esforço real
10-12 horas.

---

## FASE 6 — v10.0 Predictive Gates — só começa depois de 20+ execuções REAIS da Fase 0

### Pré-requisito não-negociável
Esta fase **não pode ter uma única linha de código escrita antes** de existirem pelo menos ~20 execuções reais registradas em `estado_projeto.db` (gerado pela Fase 0, rodado por você em ideias reais ao longo do uso normal). Não adianta eu "simular" isso — os dados têm que ser de execuções que de fato aconteceram.

### O que será criado
```
scripts/analytics/query_falhas.py  (~60 linhas)
```

### O que faz de verdade
```sql
SELECT gate_nome, COUNT(*) as falhas, 
       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM execucoes) as taxa_falha
FROM gates_log WHERE status = 'FAIL'
GROUP BY gate_nome ORDER BY falhas DESC;
```
Query SQL real contra dados reais. Sem "87% accuracy" inventado.

### Comando de verificação
```bash
sqlite3 estado_projeto.db < scripts/analytics/query_falhas.py
```

### O que você DEVE VER
Uma tabela com números que **batem com o que você lembra** de ter visto falhar nas suas próprias execuções anteriores. Se o número não corresponder à sua experiência real de uso, a query está errada ou os dados não estão sendo logados corretamente — e isso é verificável por você diretamente, sem precisar confiar em mim.

### Esforço real
6-8 horas de código + **semanas de uso real acumulando dados antes disso ser possível.**

---

## FASE 7 — v12.0 REDEFINIDO: Reaproveitamento de Templates — depende de 2+ execuções reais

### O que será criado
```
templates/  (pasta)
scripts/templates/salvar_template.py   (~50 linhas)
scripts/templates/buscar_similar.py    (~50 linhas)
```

### O que faz de verdade
Depois que um projeto é gerado com nota real (Fase 0/passo 07) acima de um limiar, salva `.aidd/config.json` + a decisão real da Fase 3/4 em `templates/{hash-da-ideia}.json`. Na próxima geração, calcula similaridade de texto simples (ex.: `difflib.SequenceMatcher`, sem LLM) contra ideias anteriores salvas, e se a similaridade > 70%, reaproveita a decisão salva em vez de chamar o LLM de novo (economia real de tokens, mensurável).

### Comando de verificação
```bash
python scripts/orquestrador.py /pasta-A --ideia "CLI Python para validar JSON"
python scripts/orquestrador.py /pasta-B --ideia "CLI Python para validar YAML"
cat pasta-B/.aidd/cache/_phase_04_decisao.json | jq '.reaproveitado_de'
```

### O que você DEVE VER
O segundo projeto mostrando `"reaproveitado_de": "pasta-A"` no JSON, e o log de tokens da Fase 3/4 mostrando **zero chamadas de LLM** na segunda execução (economia real e mensurável, não alegada).

### Esforço real
8-10 horas.

---

## FASE 8 — v13.0 Orchestrator: integração final, sem score fabricado

### O que muda
`scripts/orquestrador.py` (o único arquivo real que já existe hoje) passa a chamar, em sequência real, os módulos das Fases 0-7 acima — nada de somar inteiros arbitrários (`+20+20+30...`). O Phase 7 final apresenta **só a checklist objetiva** definida na Fase 0.

### Comando de verificação final (o teste que prova que TUDO isso é real, de ponta a ponta)
```bash
python scripts/orquestrador.py /pasta-final --ideia "API REST para gerenciar tarefas" --modo completo
cat pasta-final/AVALIACAO-AUTO-CRITICA.md
```

### O que você DEVE VER
Um relatório com linhas do tipo:
```
[✅] README.md existe (verificado: os.path.exists)
[✅] Git inicializado (verificado: .git/ existe)
[✅] 7/7 gates executados e logados
[❌] Gate G2 falhou 1x (ver patches/sugestao-003.diff)
[✅] Template reaproveitado de execução anterior (economia: 1,840 tokens)
```
Nenhuma linha "Score: 450/100". Nenhuma linha "Confiança: 87%" sem uma query ou cálculo real por trás mostrado.

---

## RESUMO DE ORDEM E ESFORÇO TOTAL

| Ordem | Fase | Pode paralelizar? | Horas reais | Custo API |
|---|---|---|---|---|
| 1 | Fase 0 (Núcleo) | Não — bloqueia tudo | 20-30h | ~$5 |
| 2 | Fase 1 (v9.0) | Sim, junto com Fase 0 | 4-6h | $0 |
| 3 | Fase 2 (v11.0) | Sim, junto com Fase 0 | 10-15h | $0 |
| 4 | Fase 3 (v6.0) | Não — precisa Fase 0 | incluso na Fase 0 | — |
| 5 | Fase 4 (v7.0) | Não — precisa Fase 3 | 15-20h | 3x por decisão |
| 6 | Fase 5 (v8.0) | Não — precisa Fase 0 | 10-12h | ~$2 |
| 7 | Fase 7 (v12.0) | Não — precisa 2+ execuções reais | 8-10h | $0 |
| 8 | Fase 6 (v10.0) | Não — precisa 20+ execuções reais e SEMANAS de uso | 6-8h | $0 |
| 9 | Fase 8 (integração) | Não — última | 8-10h | — |

**Total de código:** ~80-110 horas reais (não as "1680h" fantasiadas do relatório anterior).
**Total de custo de API para desenvolvimento/testes:** ~$10-20, mais custo recorrente de uso normal depois.

Nenhuma fase começa a ser codificada até você aprovar explicitamente qual fase primeiro.
