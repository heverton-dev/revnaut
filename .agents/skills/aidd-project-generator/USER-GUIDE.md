# 📖 USER GUIDE: aidd-project-generator v2.1

**Gera projetos completos em 6 fases seguindo arquitetura AIDD**

---

## ⚡ Início Rápido (5 min)

### Via Claude Code (Recomendado)

```
/aidd-project-generator
```

Modal interativo aparece. Você escolhe:
1. **Ideia do projeto** — Digite sua descrição
2. **Opções avançadas** — (opcional) modelos, cache, verbose
3. **Começar** — Executa 6 fases automaticamente

Resultado: Pasta `output/` com projeto completo

### Via Terminal

```bash
# Modo rápido (fallback para mocks)
python ~/.claude/skills/aidd-project-generator/scripts/orquestrador.py \
  --ideia "Sua ideia aqui"

# Modo verbose (vê cada passo)
python ... --ideia "..." --verbose

# Com override de modelo
python ... --ideia "..." --phase-2-model opus --phase-3-model opus
```

---

## 📋 O Que Cada Fase Faz

### Phase 1: Pesquisador de Referências
**Entrada:** Ideia do projeto  
**Saída:** 5-8 projetos similares encontrados  
**Gates:** HTTP 200, atividade recente, estrutura GitHub  
**Tempo:** 30s  
**Tokens:** 0 (Python puro)

```
Exemplo:
  Ideia: "API REST para gerenciar tarefas"
  Encontra: FastAPI examples, Django REST, Flask-RESTX, etc
```

---

### Phase 2: Analisador da Ideia
**Entrada:** Ideia + referências  
**Saída:** Especificação estruturada (objetivo, stack, arquitetura)  
**Gates:** Schema válido, zero alucinação, qualidade  
**Tempo:** 5s  
**Tokens:** 5k (LLM estratégica)

```
Exemplo output:
{
  "objetivo": "API REST com FastAPI + SQLite",
  "publico_alvo": "Engenheiros Python",
  "stack_recomendado": {
    "linguagem": "Python 3.10+",
    "framework": "FastAPI",
    "banco": "SQLite"
  }
}
```

---

### Phase 3: Designer AIDD (5 Subagentes)
**Entrada:** Ideia + análise  
**Saída:** Arquitetura AIDD completa  
**Subagentes:** Arquiteto, Engenheiro, Tokens, Ferramentas, Gates  
**Gates:** 5 camadas, scripts viáveis, determinismo ≥80%  
**Tempo:** 10s  
**Tokens:** 30k (5 agents paralelos)

```
Exemplo output:
- 5 Camadas AIDD definidas
- 3 Scripts Python propostos
- 88% determinismo (economia de tokens)
- Skills e MCPs recomendados
```

---

### Phase 4: Decisor Global/Local
**Entrada:** Design AIDD  
**Output:** Decisões de escopo (GLOBAL ou LOCAL)  
**Escolhas:**
- CLAUDE.md: GLOBAL (reutilizável) ou LOCAL (projeto-específico)?
- Skills: GLOBAL ou LOCAL?
- MCPs: GLOBAL ou LOCAL?
- Hooks: GLOBAL ou LOCAL?
- Agents.md: GLOBAL ou LOCAL?
- Scripts: GLOBAL ou LOCAL?

**Gates:** Decisões válidas, symlinks resolvem  
**Tempo:** 2s  
**Tokens:** 0 (Python puro)

---

### Phase 5: Criador de Projeto
**Entrada:** Decisões Global/Local  
**Saída:** Pasta com projeto estruturado  
**Cria:**
- `.aidd/config.json` — Metadados AIDD
- `CLAUDE.md` — Instruções para agente
- `.gitignore` — Excludir secrets
- `requirements.txt` — Dependências
- `README.md` — Documentação
- `.aidd/rules.md` — 10 Leis AIDD
- `estado_projeto.db` — SQLite
- Git init + commit inicial

**Gates:** E1-E5 (estrutura, git, sqlite) + S1 (segurança)  
**Tempo:** 1s  
**Tokens:** 0 (Python puro)

---

### Phase 6: Documentador Tripartite
**Entrada:** Projeto criado  
**Saída:** Documentação em 3 formatos
- HTML (interativo com busca)
- Markdown (versionável, Git-friendly)
- PDF (formal, imprimível)

**Gates:** F1-F3 (renderização, validação)  
**Tempo:** 2s  
**Tokens:** 20k (LLM narrativas)

---

## 🎛️ Opções de Linha de Comando

```bash
python orquestrador.py [OPTIONS]

REQUERIDO:
  --ideia TEXT          Descrição da ideia do projeto

OPCIONAL:
  --cache-dir PATH      Diretório de cache (default: .aidd/cache)
  --phase-2-model MODEL Modelo Phase 2 (haiku|sonnet|opus|fable)
  --phase-3-model MODEL Modelo Phase 3 (haiku|sonnet|opus|fable)
  --phase-6-model MODEL Modelo Phase 6 (haiku|sonnet|opus|fable)
  
  --skip-phase N        Pular fase específica (1-6)
  --resume-from N       Retomar de fase anterior (usa cache)
  
  --verbose             Output detalhado com logs
  --json                Retorna output em JSON puro
  -h, --help            Mostra ajuda
```

---

## 📊 Exemplos Prácticos

### Exemplo 1: Projeto Simples (Haiku default)

```bash
python orquestrador.py --ideia "Aplicação de TODO em Python"

# Output esperado:
# ✅ Phase 1: 7 referências encontradas
# ✅ Phase 2: Análise completa (Haiku)
# ✅ Phase 3: Design AIDD definido (Haiku + 5 subagentes)
# ✅ Phase 4: 3 GLOBAL, 3 LOCAL
# ✅ Phase 5: Projeto criado em output/todo-app/
# ✅ Phase 6: Documentação tripartite
# 
# Tokens: 55k
```

### Exemplo 2: Projeto Complexo (Opus para análise)

```bash
python orquestrador.py \
  --ideia "Sistema de marketplace com microserviços, OAuth2, webhooks" \
  --phase-2-model opus \
  --phase-3-model opus

# Phase 2 usa Opus: análise mais profunda (8.5k tokens)
# Phase 3 usa Opus: 5 subagentes mais robustos (15k tokens)
# Total: ~75k tokens (vs 55k Haiku)
# Custo extra: ~$0.25
# Benefício: 40% mais qualidade na análise + design
```

### Exemplo 3: Teste Rápido (Fable para economia)

```bash
python orquestrador.py \
  --ideia "Calculadora simples" \
  --phase-2-model fable \
  --phase-3-model fable

# Máxima economia: ~25k tokens
# Speed: ⚡⚡⚡
# Qualidade: ✅ (ok para protótipos)
```

### Exemplo 4: Modo Verbose com Logs

```bash
python orquestrador.py \
  --ideia "API REST" \
  --verbose

# Mostra cada gate, cada decisão, cada arquivo criado
# Ideal para debugging ou aprender como funciona
```

---

## 🔍 Verificar Resultado

Após execução, verifique:

```bash
# Ver estrutura gerada
ls -la output/seu-projeto/

# Ver logs de cada phase
ls -la output/seu-projeto/.aidd/cache/_phase_*_index.json

# Ver configuração AIDD
cat output/seu-projeto/.aidd/config.json

# Ver regras do projeto
cat output/seu-projeto/.aidd/rules.md

# Git foi inicializado?
cd output/seu-projeto
git log --oneline
```

---

## 🎯 Fluxo de Trabalho Típico

```
1. Pensar na ideia
   └─ "Quero criar um extrator de dados YouTube"

2. Rodar skill
   python orquestrador.py --ideia "Extrair dados YouTube"

3. Esperar ~2 minutos
   └─ 6 fases executam (paralelo onde possível)

4. Pasta criada: output/yt-extrator/
   ├─ Estrutura AIDD pronta
   ├─ Git inicializado
   ├─ Dependências listadas
   └─ Documentação tripartite

5. Entrar na pasta
   cd output/yt-extrator

6. Começar a desenvolver!
   ├─ Implementar Phase 1 de seu código
   ├─ Seguir guias em CLAUDE.md
   └─ Consultar .aidd/rules.md para leis AIDD
```

---

## ❓ Perguntas Comuns

**P: Qual modelo devo usar?**
A: Haiku default é 90% do tempo. Tente Opus se análise parecer superficial.

**P: Posso mudar modelo depois?**
A: Sim! Rerun com `--phase-2-model opus` e ele recalcula apenas essa phase.

**P: Quanto custam os tokens?**
A: ~55k por projeto (Haiku). Com Opus: ~75k. Fable: ~25k.

**P: Posso reutilizar a skill em outro projeto?**
A: Sim! Copie `~/.claude/skills/aidd-project-generator/` para novo harness.

**P: Como vejo o que foi gerado?**
A: Tudo está em `output/seu-projeto/` e logs em `.aidd/cache/_phase_*.json`

---

## 📞 Suporte

- Erro em Phase 2? → Veja TROUBLESHOOTING.md
- Dúvida sobre modelos? → Veja MODEL-STRATEGY.md
- Não entendo AIDD? → Veja `.aidd/rules.md` no projeto criado
- Lei de Transparência? → Veja .aidd/LEI-FUNDAMENTAL-TRANSPARENCIA.md

---

**Versão:** 2.1  
**Última atualização:** 29/08/2026  
**Status:** ✅ Pronto para usar
