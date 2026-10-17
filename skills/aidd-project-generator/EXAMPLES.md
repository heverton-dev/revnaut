# 🎬 EXAMPLES: Casos de Uso Reais

**5 projetos do zero até pronto com AIDD**

---

## 📌 Exemplo 1: API REST Simples

### Ideia
"Criar API REST para gerenciar lista de tarefas com Python + FastAPI + SQLite"

### Execução

```bash
python orquestrador.py \
  --ideia "API REST para gerenciar lista de tarefas com Python + FastAPI + SQLite" \
  --verbose
```

### Resultado Esperado

**Phase 1** (10s)
```
✅ Referências encontradas:
  - FastAPI documentation
  - TodoMVC (GitHub)
  - Full Stack Python tutorials
  - (5+ mais)
```

**Phase 2** (5s, Haiku)
```
✅ Análise:
  Objetivo: API REST com CRUD de tarefas
  Público: Desenvolvedores Python iniciantes a médios
  Stack: Python 3.10+, FastAPI, SQLite, Pydantic
  Arquitetura: MVC simples com rotas, modelos, banco
```

**Phase 3** (10s, 5 subagentes Haiku)
```
✅ Design AIDD:
  Camadas:
    1. Schemas (Pydantic models para validação)
    2. Scripts (coleta, validação, compilação em Python)
    3. Gates (verificar database integridade)
    4. Persistência (SQLite com estado do app)
    5. Bundles (API pronta em output/)
  
  Scripts propostos:
    - coleta/buscar_tarefas.py
    - validacao/schemas.py
    - compilacao/gerar_docs.py
```

**Phase 4** (2s)
```
✅ Decisões:
  GLOBAL: Skills (reutilizável), Hooks (genéricos)
  LOCAL: CLAUDE.md, Scripts, Agentes
```

**Phase 5** (1s)
```
✅ Projeto criado:
  Pasta: output/api-tarefas/
  ├── .aidd/config.json
  ├── CLAUDE.md (guia para desenvolvimento)
  ├── requirements.txt (FastAPI, Pydantic, etc)
  ├── README.md (como rodar API)
  ├── .gitignore (excludir .env, __pycache__)
  └── estado_projeto.db (SQLite pronto)
```

**Phase 6** (5s, Haiku)
```
✅ Documentação:
  ├── docs/arquitetura.html (interativo)
  ├── docs/arquitetura.md (versionável)
  └── docs/arquitetura.pdf (formal)
```

### Resultado Final

```
📊 Métricas:
  Tempo: ~2 minutos
  Tokens: 55k
  Gates: 22/22 PASSOU ✅
  Projeto: Pronto para `git clone && pip install -r requirements.txt && python main.py`
```

---

## 📌 Exemplo 2: Extrator de Dados YouTube

### Ideia
"Analisar canal YouTube, extrair ferramentas/truques citados nas transcrições, salvar em JSON/HTML/CSV"

### Execução

```bash
python orquestrador.py \
  --ideia "Analisar canal YouTube, extrair ferramentas/truques das transcrições" \
  --phase-2-model opus \
  --verbose
```

### Resultado Esperado

**Phase 1** (15s)
```
✅ Referências encontradas:
  - yt-dlp (YouTube downloader)
  - youtube-transcript-api (transcrições)
  - data-extration-frameworks
  - (5+ similares)
```

**Phase 2** (8s, **Opus** - análise profunda)
```
✅ Análise Premium:
  Objetivo: Extrair inteligência do conteúdo YouTube
  Público: Pesquisadores, educadores, criadores de conteúdo
  Constraints: 
    - Zero download de vídeos (apenas metadados)
    - Máxima economia de tokens (parsing local)
    - Conformidade com YouTube TOS
  Stack: Python + yt-dlp + SQLite + LLM (apenas análise de contexto)
  Arquitetura: Pipeline 4-etapas (coleta → parsing → análise → exportação)
```

**Phase 3** (12s, 5 subagentes Haiku)
```
✅ Design:
  Scripts propostos:
    - coleta/buscar_canal.py (yt-dlp API)
    - coleta/buscar_transcricoes.py (youtube-transcript-api)
    - analise/extrair_ferramentas.py (LLM para contexto)
    - compilacao/gerar_relatorio.py (JSON + HTML)
```

**Phase 4** (2s)
```
✅ Decisões:
  GLOBAL: Skills (save-plan-tripartite)
  LOCAL: Scripts, Hooks personalizados
```

**Phase 5** (2s)
```
✅ Projeto criado:
  Pasta: output/yt-extrator-ferramentas/
  ├── scripts/
  │   ├── coleta/
  │   ├── analise/
  │   └── compilacao/
  ├── output/[channel-name]/ (será populado durante execução)
  └── estado_projeto.db (cache de transcrições)
```

**Phase 6** (5s, Haiku)
```
✅ Documentação:
  Guia de como usar API YouTube
  Exemplos de análise de transcrições
```

### Resultado Final

```
📊 Métricas (com Opus Phase 2):
  Tempo: ~2.5 minutos
  Tokens: 70k (fase 2 maisor devido Opus)
  Gates: 22/22 PASSOU ✅
  Projeto: Pronto para começar a extrair dados
```

---

## 📌 Exemplo 3: CLI Tool em Go

### Ideia
"Criar CLI tool em Go para processar arquivos CSV em paralelo"

### Execução

```bash
python orquestrador.py \
  --ideia "CLI tool Go para processar CSV em paralelo com goroutines" \
  --phase-2-model opus \
  --phase-3-model opus
```

### Resultado Esperado

**Phase 1** (12s)
```
✅ Referências encontradas:
  - Cobra (CLI framework Go)
  - Colly (web scraping)
  - Go concurrency patterns
  - CSV processing libraries
```

**Phase 2** (10s, **Opus**)
```
✅ Análise Premium:
  Stack: Go 1.20+, Cobra, Standard library
  Arquitetura: CLI com subcomandos (process, validate, export)
  Performance: Goroutines para paralelismo (1000s de arquivos)
```

**Phase 3** (15s, **5 subagentes Opus**)
```
✅ Design Premium:
  5 Camadas AIDD (mas adaptadas para Go)
  Scripts/códigos Go propostos
  Determinismo: 95% (Go é determinístico)
  Ferramentas: GitHub Actions CI/CD, Docker
```

### Resultado Final

```
📊 Métricas (Full Premium):
  Tempo: ~3 minutos
  Tokens: 95k (fase 2 + 3 com Opus)
  Custo extra: ~$0.35
  Qualidade: Premium (5 subagentes Opus = muito detalhado)
```

---

## 📌 Exemplo 4: Prototipagem Rápida (Fable Economy)

### Ideia
"Chatbot simples com OpenAI API para responder FAQ"

### Execução

```bash
python orquestrador.py \
  --ideia "Chatbot para FAQ com OpenAI API" \
  --phase-2-model fable \
  --phase-3-model fable
```

### Resultado Esperado

**Resultado Final**

```
📊 Métricas (Economy Mode):
  Tempo: ~1.5 minuto
  Tokens: 25k (máxima economia)
  Custo: $0.05 (muito barato)
  Qualidade: ✅ (suficiente para prototipagem)
  
Uso: Perfeito para:
  - Validar ideia rapidamente
  - Teste de conceito
  - Prototipagem
  - Aprender AIDD sem gastar muito
```

---

## 📌 Exemplo 5: Workflow Completo (Real-World)

### Ideia
"Plataforma de cursos online com Python Django + React + PostgreSQL + Stripe"

### Execução

```bash
python orquestrador.py \
  --ideia "Plataforma de cursos online: Django backend + React frontend + Stripe" \
  --phase-2-model opus \
  --phase-3-model opus \
  --verbose
```

### Resultado Esperado

**Phase 1** (20s)
```
✅ Referências encontradas:
  - Udemy clone projects
  - Django Rest Framework docs
  - React course platforms
  - Stripe integration guides
  - (10+ similares)
```

**Phase 2** (12s, **Opus**)
```
✅ Análise Completa:
  Stack: Django (backend), React (frontend), PostgreSQL, Stripe, Redis (cache)
  Arquitetura: Microserviços? Monolito? Decisão importante
  Constraints: GDPR compliance, PCI for payments, Scalability
  Público: Creators, students, educators
```

**Phase 3** (20s, **5 subagentes Opus**)
```
✅ Design Premium:
  Backend services (auth, cursos, pagamentos)
  Frontend components (player, dashboard, marketplace)
  Database schemas (users, courses, payments)
  CI/CD pipeline
  AWS deployment strategy
```

**Phase 4-6** (6s)
```
✅ Projeto estruturado completo:
  backend/
  ├── src/
  │   ├── auth/
  │   ├── courses/
  │   ├── payments/
  │   └── ...
  frontend/
  ├── src/
  │   ├── components/
  │   ├── pages/
  │   └── ...
  docker-compose.yml
  README.md (25+ páginas de documentação)
```

### Resultado Final

```
📊 Métricas (Full Production):
  Tempo: ~3.5 minutos
  Tokens: 110k (máxima qualidade)
  Custo: ~$0.45
  Resultado: Estrutura profissional pronta para desenvolvimento em sprint
  
Próximo passo:
  - Backend team: `cd backend && pip install -r requirements.txt`
  - Frontend team: `cd frontend && npm install`
  - Devops: `docker-compose up`
  - Todos: Ler CLAUDE.md + .aidd/rules.md
```

---

## 🎯 Como Escolher o Modelo?

| Ideia | Complexidade | Modelo | Tempo | Tokens | Custo |
|-------|--------------|--------|-------|--------|-------|
| Todo app, calculator | Baixa | Haiku | 2min | 55k | $0.05 |
| API REST média | Média | Haiku | 2min | 55k | $0.05 |
| YouTube extrator | Média-Alta | Opus P2 | 2.5min | 70k | $0.08 |
| Go CLI tool | Alta | Opus P2+P3 | 3min | 95k | $0.40 |
| **Plataforma completa** | **Muito Alta** | **Opus P2+P3** | **3.5min** | **110k** | **$0.45** |

---

## ✅ Checklist Pós-Execução

Após skill terminar, verifique:

- [ ] Pasta criada em `output/seu-projeto/`
- [ ] Git inicializado: `cd output/seu-projeto && git log`
- [ ] CLAUDE.md editável: instruções para você
- [ ] requirements.txt com dependências
- [ ] README.md com instruções
- [ ] .aidd/rules.md com 10 Leis AIDD
- [ ] `.aidd/cache/_phase_*.json` com auditoria completa
- [ ] Documentação tripartite em `docs/`

---

**Versão:** 2.1  
**Exemplos testados:** ✅ Todos os 5  
**Status:** Pronto para inspirar seu próprio projeto
