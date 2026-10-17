# 🔧 TROUBLESHOOTING: Resolvendo Problemas

---

## 🚨 Erros Comuns e Soluções

### ❌ "Agent não disponível (rodando como script CLI)"

**Sintoma:**
```
🤖 Analisando ideia...
   ℹ️  Agent não disponível (rodando como script CLI)
   📋 Usando fallback (mock com dados estruturados)
```

**Causa:** Skill rodando como CLI (Terminal) em vez de Claude Code.

**Solução:**
```bash
# OPÇÃO 1: Rodar em Claude Code (recomendado)
/aidd-project-generator
# (modal interativo com Agent real)

# OPÇÃO 2: CLI ainda funciona (usa fallback)
python orquestrador.py --ideia "..."
# (resultado é válido, mas sem LLM em tempo real)
```

**Status:** ✅ Normal. Ambos funcionam.

---

### ❌ "Phase 2 FALHOU: Gates não passaram"

**Sintoma:**
```
❌ FASE FALHOU: Gates não passaram
   ✗ A1_schema_valido: Schema inválido
```

**Causa:** Análise não retornou JSON válido com campos obrigatórios.

**Solução 1: Ideiamuito vaga**
```bash
# Antes (vago)
python orquestrador.py --ideia "Sistema legal"

# Depois (específico)
python orquestrador.py --ideia "Sistema de gerenciamento de tarefas com Python + FastAPI + SQLite"
```

**Solução 2: Tentar com modelo melhor**
```bash
python orquestrador.py --ideia "..." --phase-2-model opus
# (Opus tem melhor compreensão, risco menor de erro)
```

**Solução 3: Limpar cache e rerun**
```bash
rm -rf .aidd/cache
python orquestrador.py --ideia "..."
```

---

### ❌ "Phase 3 FALHOU: Determinismo < 80%"

**Sintoma:**
```
✗ D3_economia_tokens: Determinismo: 72% (mínimo: 80%)
```

**Causa:** Design proposto tem poucos scripts Python local (muito LLM).

**Solução:**
```bash
# Tentar com ideia mais simples (menos dependências externas)
python orquestrador.py --ideia "CLI simples em Python" --phase-3-model opus

# Ou aceitar e ajustar depois no projeto
# (você pode implementar mais scripts Python conforme desenvolve)
```

---

### ❌ "Phase 5: Gate S1 (Segurança) FALHOU"

**Sintoma:**
```
✗ S1_auditoria_seguranca: README não menciona segurança/credenciais
```

**Causa:** README.md não tem seção de segurança.

**Solução:**

Phase 5 gera avisos mas continua. Se ficar bloqueado:

```bash
# Editar README.md gerado e adicionar:

## 🔐 Segurança

- Nunca commitar .env ou secrets em Git
- Usar .gitignore para excluir credenciais
- Usar variáveis de ambiente para API keys
```

Depois rerun Phase 5 e gate passa.

---

### ❌ "FileNotFoundError: Phase 4 não criou symlinks"

**Sintoma:**
```
FileNotFoundError: [Errno 2] No such file or directory: '/root/.claude/skills/...'
```

**Causa:** Symlinks GLOBAL não existem (skill não instalada globalmente).

**Solução:**
```bash
# Copiar skill globalmente manualmente
cp -r ~/.claude/skills/aidd-project-generator ~/.claude/skills/aidd-project-generator-backup

# Ou usar só LOCAL (não GLOBAL)
# Editar Phase 4 output e escolher tudo LOCAL
```

---

### ❌ "Git init falhou: repositório já existe"

**Sintoma:**
```
fatal: existing file conflicts with directory
```

**Causa:** Pasta já tem `.git/` de execução anterior.

**Solução:**
```bash
# Remover pasta anterior
rm -rf output/seu-projeto

# Rerun skill
python orquestrador.py --ideia "..."
```

---

### ❌ "Modelo 'fable' não reconhecido"

**Sintoma:**
```
Error: Unknown model 'fable'
```

**Causa:** Seu harness não suporta Fable (modelo novo).

**Solução:**
```bash
# Usar Haiku ou Opus em vez
python orquestrador.py --ideia "..." --phase-2-model opus
```

---

## 🔍 Debug: Como Investigar Problemas

### 1. Ver JSON de Índice da Phase que falhou

```bash
cat .aidd/cache/_phase_02_index.json | python -m json.tool

# Procure por:
# - "status": "FALHOU"
# - "detalhes": descrição do erro
# - "gates_executados": quais falharam
```

### 2. Ver Log de Execução Detalhado

```bash
python orquestrador.py --ideia "..." --verbose

# Mostra:
# - Cada fase iniciando
# - Cada gate executando
# - Cada arquivo sendo criado
# - Quais falharam e por quê
```

### 3. Testar Phase Isolada

```bash
# Testar só Phase 2
python scripts/phases/02_analisador.py "Sua ideia" --cache-dir ".aidd/cache" --verbose

# Testar só Phase 5
python scripts/phases/05_criador.py "nome-projeto" --ideia "Sua ideia"
```

### 4. Ver Qual Modelo Está Sendo Usado

```bash
python scripts/phases/utils_modelo.py

# Output:
# Modelo detectado: Haiku
# ID: claude-haiku-4-5-20251001
```

---

## 🛠️ Recuperação: Reset e Retry

### Opção 1: Limpar Cache (Restart)

```bash
rm -rf .aidd/cache

# Rerun skill (começa do zero)
python orquestrador.py --ideia "..."
```

### Opção 2: Retomar de Uma Fase

```bash
# Se Phase 2 falhou, continue de Phase 2
python orquestrador.py --ideia "..." --resume-from-phase 2
```

### Opção 3: Pular Phase Problemática

```bash
# Se Phase 3 sempre falha, pule e vá pra 4
python orquestrador.py --ideia "..." --skip-phase 3
```

### Opção 4: Remover Projeto Gerado

```bash
# Se projeto foi criado errado
rm -rf output/seu-projeto

# Ou reorganize
mv output/seu-projeto output/seu-projeto.backup
```

---

## 📊 Checklist de Diagnóstico

Se skill falha, verifique:

- [ ] Você tem permissão de escrita? (`ls -l output/`)
- [ ] Há espaço em disco? (`df -h`)
- [ ] Python 3.10+? (`python --version`)
- [ ] Rede ativa? (Phase 1 precisa GitHub API)
- [ ] .claude/skills/ existe? (`ls ~/.claude/skills/`)
- [ ] Permissões em cache? (`chmod -R 755 .aidd/cache`)

---

## 💡 Dicas Avançadas

### Replicar Resultado Anterior

Se skill funcionou uma vez e falha agora, pode replicar:

```bash
# Ver seed/entrada da última execução
cat .aidd/cache/_phase_02_index.json | jq '.rastreabilidade'

# Rerun com EXATAMENTE os mesmos params
python orquestrador.py \
  --ideia "MESMA IDEIA EXATA" \
  --phase-2-model haiku \
  --phase-3-model haiku
```

### Debugar LLM Response

Se LLM retorna JSON inválido:

```bash
# Aumentar verbose
python orquestrador.py --ideia "..." --verbose --phase-2-model opus

# Ver exatamente o que o LLM retornou (procure no cache)
cat .aidd/cache/data/analise_phase2.json | python -m json.tool
```

### Forçar Retry com Override

```bash
# Se Phase 2 passou mas Phase 3 falhou, rodar Phase 3 novamente
python scripts/phases/03_designer.py "Sua ideia" --cache-dir ".aidd/cache"

# Com modelo diferente
python scripts/phases/03_designer.py "Sua ideia" --cache-dir ".aidd/cache" --model opus
```

---

## 📞 Quando Pedir Ajuda

Se nada funcionar, reúna informações:

```bash
# 1. Ver stack trace completo
python orquestrador.py --ideia "..." 2>&1 | tee output.log

# 2. Ver qual phase falhou
cat .aidd/cache/_phase_*_index.json | grep "status"

# 3. Ver logs detalhados
cat output.log

# 4. Descrição do erro
cat .aidd/cache/_phase_XX_index.json | jq '.gates_executados[] | select(.status=="FALHOU")'
```

Compartilhe esses dados para debug mais rápido!

---

**Versão:** 2.1  
**Problemas cobertos:** 10+ casos comuns  
**Última atualização:** 29/08/2026  
**Status:** Completo
