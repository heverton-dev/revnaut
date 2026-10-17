# 🚀 INSTALLATION & DEPLOYMENT

**Instalando skill `aidd-project-generator` em novos projetos**

---

## ✅ Status Atual

Skill está **pronta para produção** em:

```
~/.claude/skills/aidd-project-generator/
├── SKILL.md
├── MODEL-STRATEGY.md
├── USER-GUIDE.md
├── EXAMPLES.md
├── FAQ.md
├── TROUBLESHOOTING.md
├── INSTALLATION.md (este arquivo)
├── orquestrador.py
└── scripts/phases/
    ├── 01_pesquisador.py
    ├── 02_analisador.py
    ├── 03_designer.py
    ├── 04_decisor.py
    ├── 05_criador.py
    ├── 06_documentador.py
    └── utils_modelo.py
```

---

## 📥 Instalação em Novo Projeto

### Opção A: Symlink (Recomendado - Espaço)

```bash
# Em novo projeto
cd ~/novo-projeto

# Criar symlink para skill global
ln -s ~/.claude/skills/aidd-project-generator ./.aidd/skill-generator

# Rodar
python ./.aidd/skill-generator/scripts/orquestrador.py --ideia "..."
```

**Vantagem:** Atualizar skill global atualiza todos projetos automaticamente  
**Desvantagem:** Requer suporte a symlinks (OK no Linux/Mac, Windows precisa de permissão)

---

### Opção B: Copiar Pasta (Segurança)

```bash
# Em novo projeto
cd ~/novo-projeto

# Copiar skill para projeto
cp -r ~/.claude/skills/aidd-project-generator ./.aidd/generator

# Rodar
python ./.aidd/generator/scripts/orquestrador.py --ideia "..."
```

**Vantagem:** Projeto é independente, pode customizar  
**Desvantagem:** Atualizar skill depois requer cópia manual

---

### Opção C: Usar CLI Direto (Simples)

```bash
# De qualquer pasta, rodar skill global direto
python ~/.claude/skills/aidd-project-generator/scripts/orquestrador.py \
  --ideia "Sua ideia"

# Cria output/ com projeto gerado
```

**Vantagem:** Mais simples, sem setup  
**Desvantagem:** Projeto fica em output/ (não em pasta específica)

---

## 🎨 Customização por Projeto

Se copiou a skill para seu projeto (Opção B):

### 1. Customizar Prompts

```bash
# Editar prompts específicos do projeto
vim .aidd/generator/scripts/phases/02_analisador.py

# Alterar PROMPT_ANALISADOR_IDEIA para seu domínio
```

### 2. Adicionar Fases Customizadas

```bash
# Criar nova fase (07_deployer.py)
touch .aidd/generator/scripts/phases/07_deployer.py

# Seguir mesmo padrão das outras phases
```

### 3. Modificar Estrutura Gerada

```bash
# Editar template de projeto gerado
vim .aidd/generator/scripts/phases/05_criador.py

# Adicionar mais arquivos ao projeto criado
```

---

## 🔄 Manutenção de Skill Global

### Atualizar Skill para Todos Projetos

```bash
# 1. Fazer mudanças em ~/.claude/skills/aidd-project-generator/
vim ~/.claude/skills/aidd-project-generator/scripts/phases/02_analisador.py

# 2. Commit
cd ~/.claude/skills/aidd-project-generator/
git add -A
git commit -m "Melhoria: ..."

# 3. Todos projetos com symlink recebem update automaticamente
# (se copiaram, precisam fazer cp -r novamente)
```

---

## 📦 Versioning

Skill segue versionamento semântico:

```
VERSÃO ATUAL: 2.1
├─ MAJOR (2): Mudanças no core (5 camadas AIDD)
├─ MINOR (1): Novas phases, prompts melhorados
└─ PATCH (não usado): Bug fixes menores
```

### Quando Atualizar

```
2.0 → 2.1: Novas features (seguro, usar tudo novo)
2.1 → 3.0: Breaking changes (talvez precise customizar)
```

---

## ✅ Checklist de Instalação

- [ ] Skill copiada/symlinked para novo projeto
- [ ] Python 3.10+ disponível (`python --version`)
- [ ] Pasta `.aidd/cache/` tem permissão de escrita
- [ ] Network ativo (Phase 1 precisa GitHub API)
- [ ] Rodar teste: `python orquestrador.py --ideia "Test"`
- [ ] Verificar output/ foi criado
- [ ] Ler USER-GUIDE.md
- [ ] Pronto!

---

## 🎯 Próximos Passos

### Para Novo Projeto

```bash
# 1. Copiar/symlink skill
cp -r ~/.claude/skills/aidd-project-generator ./

# 2. Rodar skill
python ./aidd-project-generator/scripts/orquestrador.py \
  --ideia "Sua ideia"

# 3. Projeto criado em output/seu-projeto/
cd output/seu-projeto

# 4. Ler CLAUDE.md para instruções personalizadas
cat .claude/CLAUDE.md

# 5. Começar desenvolvimento!
```

### Para Múltiplos Projetos

```bash
# 1. Criar estrutura global
mkdir -p ~/projetos-aidd

# 2. Copiar skill uma vez
cp -r ~/.claude/skills/aidd-project-generator ~/projetos-aidd/generator

# 3. Para cada novo projeto, symlink
cd ~/projetos-aidd/projeto-1
ln -s ../generator ./skill

# 4. Rodar skill de qualquer projeto
python ./skill/scripts/orquestrador.py --ideia "..."
```

---

## 🔗 Links Úteis

- **USER-GUIDE.md** — Como usar (comece aqui)
- **EXAMPLES.md** — 5 casos reais
- **FAQ.md** — Perguntas comuns
- **TROUBLESHOOTING.md** — Erros e soluções
- **MODEL-STRATEGY.md** — Modelos e herança
- **SKILL.md** — Documentação técnica

---

## 📊 Estatísticas

```
Skill Size: ~10MB (scripts + docs)
Setup Time: <1 minuto
First Run: ~2 minutos
Dependencies: Python 3.10+ (nenhuma extern)
Performance: 1 skill = múltiplos projetos
Maintenance: Mínimo (código estável)
```

---

**Versão:** 2.1  
**Status:** ✅ Pronto para deploy  
**Última atualização:** 29/08/2026  
**Suporte:** Veja FAQ.md + TROUBLESHOOTING.md
