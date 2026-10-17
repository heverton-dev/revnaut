# 🚀 SKILL: aidd-project-generator v2.1

**Gera projetos completos em 6 fases seguindo arquitetura AIDD 5-camadas**

---

## 📌 O Que Faz

Você dá uma **ideia de projeto** e essa skill:

1. **Pesquisa** referências similares (GitHub, HuggingFace, Replit)
2. **Analisa** sua ideia contra as referências
3. **Desenha** arquitetura AIDD completa (5 camadas + gates + scripts)
4. **Decide** se será GLOBAL ou LOCAL (Skills, MCPs, Hooks, CLAUDE.md)
5. **Cria** projeto com estrutura pronta (git init, SQLite, README)
6. **Documenta** em tripartite (HTML + Markdown + PDF)

**Resultado:** Projeto pronto para desenvolver com AIDD estruturado desde dia 1.

---

## 💻 Como Invocar

### **Via Claude Code (Recomendado)**

```
/aidd-project-generator
```

Ativa modal interativo que guia você pelas 6 fases.

### **Via CLI (Avançado)**

```bash
cd seu-projeto
python ~/.claude/skills/aidd-project-generator/orquestrador.py \
  --ideia "Descrição do seu projeto" \
  --cache-dir ".aidd/cache"
```

### **Modo Rápido (Testes)**

```bash
python ~/.claude/skills/aidd-project-generator/orquestrador.py \
  --ideia "API REST" \
  --cache-dir ".aidd/cache" \
  --modo rapido
```

---

## 🎯 Estratégia de Modelos: HÍBRIDA TRANSPARENTE

### **Regra de Ouro**

> Nada oculto. Transparência total. Conhecimento = Poder.

### **Padrão: HERANÇA DO HARNESS**

Cada phase usa o **modelo do harness automaticamente**:

```
Você rodando em:           Phase 2       Phase 3       Phase 4-6
├─ /fast OFF (Haiku)  →    Haiku    +   Haiku    +    (determinístico)
├─ /fast ON (Opus)    →    Opus     +   Opus     +    (determinístico)
└─ /model opus (Opus) →    Opus     +   Opus     +    (determinístico)
```

✅ **Vantagem:** Controle centralizado. Muda uma vez, todos herdam.

### **Opcional: Sobrescrever por Fase**

Se você quer modelo diferente para fase específica:

```bash
# Phase 2 com Opus (análise profunda), Phase 3 com Haiku (economia)
python orquestrador.py \
  --ideia "Seu projeto" \
  --phase-2-model opus
```

### **Quando Sobrescrever?**

| Situação | Recomendação | Command |
|----------|--------------|---------|
| Análise superficial | Usar Opus | `--phase-2-model opus` |
| Design com 5 subagentes | Usar Opus | `--phase-3-model opus` |
| Prototipagem rápida | Manter Haiku | (default) |
| Máxima economia | Fable | `--phase-2-model fable --phase-3-model fable` |

### **Transparência em Ação**

Durante execução você verá:

```
📊 PHASE 2: Analisador da Ideia
   Modelo: Claude Haiku 4.5
   Tokens estimados: 5k
   
   🤖 Analisando com LLM...
   ✅ Análise concluída
   
📊 PHASE 3: Designer AIDD (5 Subagentes)
   Modelo: Claude Haiku 4.5
   
   🚀 Subagente 1/5: Arquiteto de Camadas
      Model: Claude Haiku 4.5
      Status: ✅ Camadas definidas
   
   🚀 Subagente 2/5: Engenheiro de Scripts
      Model: Claude Haiku 4.5
      Status: ✅ Scripts viáveis
```

E no final:

```
📋 RELATÓRIO FINAL
   Phase 2: Haiku (5,234 tokens)
   Phase 3: Haiku (8,765 tokens)
   
   💡 Dica: Se análise parecer superficial, tente:
      python orquestrador.py --ideia "..." --phase-2-model opus
```

---

## 🔐 6 FASES COMPLETAS

### **Phase 1: Pesquisador de Referências**

Busca projetos similares no GitHub, HuggingFace, Replit.

**Gates (4):**
- R1: URLs retornam HTTP 200
- R2: Atividade recente ≥90%
- R3: Estrutura GitHub válida
- R4: Mínimo 5 referências encontradas

**Tokens:** 0k (Python + GitHub API pura)

**Saída:** `_phase_01_index.json` com 5+ projetos de referência

---

### **Phase 2: Analisador da Ideia**

Analisa sua ideia + referências. Retorna especificação estruturada.

**Gates (4):**
- A1: Schema válido (4 campos obrigatórios)
- A2: Zero alucinação (mínimo 2 referências citadas)
- A3: 5 aspectos cobertos (objetivo, público, constraints, stack, arquitetura)
- A4: Qualidade profissional (texto coerente)

**Tokens:** 5k (LLM estratégica)

**Saída:** Análise estruturada em `_phase_02_index.json`

**Modelos:**
- Default: herda do harness (Haiku)
- Opcional: `--phase-2-model opus` para análise mais profunda

---

### **Phase 3: Designer AIDD**

Orquestra **5 subagentes em paralelo** para desenhar arquitetura completa.

**Subagentes:**
1. **Arquiteto de Camadas** — Define 5 camadas AIDD
2. **Engenheiro de Scripts** — Projeta scripts Python viáveis
3. **Especialista em Tokens** — Calcula economia (alvo: 80%+)
4. **Arquiteto de Ferramentas** — Recomenda Skills/MCPs/Hooks
5. **Especialista em Gates** — Desenha validações mecânicas

**Gates (3):**
- D1: 5 camadas AIDD presentes
- D2: Scripts têm viabilidade verificada
- D3: Economia de tokens ≥80%

**Tokens:** 30k (5 subagentes LLM paralelos)

**Saída:** Design AIDD completo em `_phase_03_index.json`

**Modelos:**
- Default: herda do harness (Haiku)
- Opcional: `--phase-3-model opus` para orquestração paralela mais robusta

---

### **Phase 4: Decisor Global/Local**

Modal interativo: escolha se cada artefato será GLOBAL ou LOCAL.

**Decisões:**
- CLAUDE.md: GLOBAL (reutilizável) ou LOCAL (específico projeto)?
- Skills: GLOBAL ou LOCAL?
- MCPs: GLOBAL ou LOCAL?
- Hooks: GLOBAL ou LOCAL?
- Agents.md: GLOBAL ou LOCAL?
- Scripts: GLOBAL ou LOCAL?

**Gates (2):**
- C1: Decisões válidas (GLOBAL ou LOCAL)
- C2: Symlinks resolvem para global

**Tokens:** 0k (Python puro, modal interativo)

**Saída:** Configuração aprovada em `_phase_04_index.json` + symlinks criados

---

### **Phase 5: Criador de Projeto**

Cria estrutura completa do projeto com segurança.

**Cria:**
- `.aidd/config.json` — Metadados AIDD
- `CLAUDE.md` — Instruções para o agente
- `.gitignore` — Excludir dependências
- `requirements.txt` — Dependências Python
- `README.md` — Documentação
- `.aidd/rules.md` — 10 Leis AIDD
- Git init + commit inicial
- SQLite schema (`yt_videos_processados`)

**Gates (6):**
- E1: Arquivos criados (4 principais)
- E2: Git inicializado
- E3: SQLite schema válido
- E4: Permissões corretas
- E5: README gerado
- **S1: Auditoria de Segurança** ✅
  - Verifica .gitignore
  - Valida requirements.txt
  - Detecta secrets hard-coded
  - Checa README com seção de security

**Tokens:** 0k (Python puro)

**Saída:** Projeto completo em `_phase_05_index.json` + git commit

---

### **Phase 6: Documentador Tripartite**

Gera documentação em 3 formatos: HTML (interativo) + MD (versionável) + PDF (formal).

**Gates (3):**
- F1: HTML renderiza sem erros
- F2: PDF gerado via Typst
- F3: Markdown válido (lint)

**Tokens:** 20k (LLM narrativas + templates)

**Saída:** Documentação em `docs/` + `_phase_06_index.json`

**Modelos:**
- Default: herda do harness (Haiku)
- Opcional: `--phase-6-model opus` para narrativas mais ricas

---

## 📊 TOTAIS

| Métrica | Valor |
|---------|-------|
| **Fases** | 6 |
| **Gates Mecânicos** | 22 |
| **Subagentes Paralelos** | 5 (Phase 3) |
| **Tokens Totais** | ~60k |
| **Economia vs Ingênuo** | 90%+ (500k → 60k) |
| **Determinismo Médio** | 88% (Python + Scripts) |
| **Tempo Total** | ~2 min (paralelo) |

---

## 🎨 Exemplos de Uso

### **Exemplo 1: Projeto Simples (Haiku Default)**

```bash
/aidd-project-generator

> Digite sua ideia:
  Uma API REST para gerenciar tarefas com FastAPI + SQLite

🔄 Iniciando 6 fases...
✅ Phase 1: 8 referências encontradas
✅ Phase 2: Análise concluída (Haiku)
✅ Phase 3: Design AIDD definido (Haiku + 5 subagentes)
✅ Phase 4: Decisões tomadas (3 GLOBAL, 3 LOCAL)
✅ Phase 5: Projeto criado com git init
✅ Phase 6: Documentação tripartite gerada

📊 Relatório Final
   Tokens: 58k
   Gates: 22/22 PASSOU ✅
   Projeto: ~/meu-projeto/
```

### **Exemplo 2: Projeto Complexo (Opus + Análise Profunda)**

```bash
python orquestrador.py \
  --ideia "Sistema de marketplace com microserviços, OAuth2, webhooks" \
  --phase-2-model opus \
  --phase-3-model opus

🔄 Iniciando 6 fases com modelos customizados...
✅ Phase 1: 12 referências (Postgres, Stripe, etc)
✅ Phase 2: Análise PROFUNDA (Opus) — 8.5k tokens
✅ Phase 3: Design robusto (Opus) — 15k tokens
✅ Phase 4: Decisões tomadas
✅ Phase 5: Projeto estruturado
✅ Phase 6: Documentação rica

📊 Relatório Final
   Tokens: 75k (vs 60k default)
   Gates: 22/22 PASSOU ✅
   Custo extra: +$0.25 com Opus
   Valor adicionado: 40% mais qualidade na análise
```

---

## 🛠️ Parâmetros CLI Completos

```bash
python orquestrador.py --help

Posicionais:
  (nenhum — configurar via flags)

Opcionais:
  --ideia TEXT                  Descrição da ideia do projeto [REQUERIDO]
  --cache-dir PATH              Diretório de cache (default: .aidd/cache)
  --modo {normal|rapido}        Modo de execução (default: normal)
  
  --phase-2-model {haiku|sonnet|opus|fable}
                                Modelo para Phase 2 (default: herança)
  --phase-3-model {haiku|sonnet|opus|fable}
                                Modelo para Phase 3 (default: herança)
  --phase-6-model {haiku|sonnet|opus|fable}
                                Modelo para Phase 6 (default: herança)
  
  --skip-phase {1|2|3|4|5|6}    Pular fase específica (para debug)
  --resume-from-phase {1-6}     Retomar de fase anterior (cache)
  
  -v, --verbose                 Output detalhado (gates, logs)
  --json                        Retorna output em JSON puro
  -h, --help                    Mostra esta mensagem
```

---

## 📚 Arquivos Gerados

```
seu-projeto/
├── .aidd/
│   ├── cache/
│   │   ├── _phase_01_index.json    # Referências encontradas
│   │   ├── _phase_02_index.json    # Análise estruturada
│   │   ├── _phase_03_index.json    # Design AIDD
│   │   ├── _phase_04_index.json    # Decisões Global/Local
│   │   ├── _phase_05_index.json    # Criação de projeto
│   │   ├── _phase_06_index.json    # Documentação
│   │   └── data/                   # JSONs brutos por phase
│   ├── config.json                 # Metadados AIDD
│   └── rules.md                    # 10 Leis AIDD
├── docs/
│   ├── PROJECT-SPEC-*.md           # Rastreamento de progresso
│   ├── arquitetura.html            # Documentação interativa
│   ├── arquitetura.md              # Documentação versionável
│   └── arquitetura.pdf             # Documentação formal
├── .claude/
│   └── CLAUDE.md                   # Instruções para agente
├── .gitignore
├── requirements.txt
├── README.md
└── estado_projeto.db               # SQLite (R11)
```

---

## 🔐 Segurança

**Gate S1 (Phase 5) verifica:**
- ✅ `.gitignore` criado (excluindo `.env`, `credentials.json`, etc)
- ✅ `requirements.txt` existe (zero dependências em git)
- ✅ Detecta secrets hard-coded (AWS_KEY, API_TOKEN patterns)
- ✅ README menciona security practices
- ✅ Permissões de arquivo (scripts executáveis)

**Nenhum projeto é criado sem passar por S1.**

---

## 🧪 Testes

```bash
# Testar Phase 1 isolado
python scripts/phases/01_pesquisador.py "API REST" --cache-dir .test

# Testar Phase 2 com dados de Phase 1
python scripts/phases/02_analisador.py "API REST" \
  --cache-dir .test \
  --referencias '{...}'

# Testar todas as 6 fases sequencialmente
python scripts/test_end_to_end.py --ideia "Seu projeto"
```

---

## 💡 Filosofia

Esta skill implementa **5 leis críticas de engenharia agêntica:**

1. **R-TOKEN** — 90%+ determinismo (economia severa)
2. **R-DETERMINISMO** — Tudo que pode rodar localmente roda (zero token waste)
3. **R-TRANSPARÊNCIA** — Nada oculto (você vê qual modelo, quantos tokens)
4. **R-REPLICABILIDADE** — Mesma ideia = Mesmo projeto sempre
5. **R-MODULARIDADE** — Cada artefato é independente e combinável

---

## 📞 Suporte

- **Dúvidas sobre modelo:** Veja `MODEL-STRATEGY.md`
- **Erro em gate:** Revisar `_phase_XX_index.json` (JSON com diagnóstico completo)
- **Cache corrompido:** `rm -rf .aidd/cache && python orquestrador.py --resume-from-phase 1`
- **Customizações:** Editar `scripts/phases/XX_*.py` (Python puro, sem Magic)

---

**Versão:** 2.1  
**Última atualização:** 29/08/2026  
**Status:** ✅ Pronto para produção  
**Autor:** Claude + AIDD Framework  
**Licença:** MIT (uso livre)
