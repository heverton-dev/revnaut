# ❓ FAQ: Perguntas Frequentes

---

## 🤔 Sobre a Skill

### P: O que é `aidd-project-generator`?
**A:** Uma skill que gera projetos completos em 6 fases seguindo arquitetura AIDD 5-camadas. Você fornece uma ideia, e ela retorna uma estrutura pronta para desenvolvimento com Git, banco de dados, documentação e gates de validação.

### P: Qual é a diferença entre AIDD e desenvolvimento normal?
**A:** AIDD (AI-Driven Development) coloca LLM como força multiplicadora, não substituição:
- Determina o máximo de trabalho em Python (90%+)
- Usa LLM apenas para análise/síntese crítica
- Cada fase tem gates (validações) que retornam sucesso/falha
- Zero magia: tudo é transparente e rastreável

### P: Preciso conhecer AIDD para usar?
**A:** Não! A skill ensina enquanto funciona:
1. CLAUDE.md — Instruções personalizadas para seu projeto
2. .aidd/rules.md — 10 Leis AIDD explicadas
3. _phase_*_index.json — Auditoria completa de cada fase
4. Tudo é em português e bem documentado

---

## 🎯 Sobre Modelos e Tokens

### P: Qual modelo devo usar?
**A:** 
- **Default (Haiku):** 90% dos casos. Rápido, econômico (55k tokens)
- **Opus:** Se análise parecer superficial. Melhor qualidade, mas mais caro (75k tokens)
- **Fable:** Prototipagem rápida, máxima economia (25k tokens)

### P: Como funciona a herança de modelo?
**A:** 
```
Seu harness (Claude Code) define:
├─ /fast OFF (Haiku) → Todas fases usam Haiku
├─ /fast ON (Opus) → Todas fases usam Opus
└─ /model opus → Força Opus em todas fases

Você PODE override por phase:
--phase-2-model opus → Phase 2 usa Opus, resto herda
```

### P: Posso mudar modelo depois de já ter criado um projeto?
**A:** Sim! Rerun o orquestrador com `--phase-2-model opus` e ele recalcula apenas essa phase, reutilizando cache das outras.

### P: Quanto custam os tokens?
**A:**
- Haiku: ~55k tokens = $0.05 (pricing Haiku)
- Opus: ~75k tokens = $0.40 (pricing Opus)
- Fable: ~25k tokens = $0.02 (pricing Fable)

### P: Por que Phase 1, 4, 5 usam 0 tokens?
**A:** Porque rodam 100% em Python local:
- Phase 1: busca em GitHub API (Python)
- Phase 4: modal interativo (Python)
- Phase 5: criação de arquivos (Python)

Só Phase 2, 3, 6 usam LLM (análise, design, narrativas).

---

## 🛠️ Sobre Uso

### P: Como executo a skill?
**A:**
```bash
# Via Claude Code (recomendado)
/aidd-project-generator

# Via terminal
python ~/.claude/skills/aidd-project-generator/scripts/orquestrador.py \
  --ideia "Sua ideia aqui"

# Com opções
python ... --ideia "..." --phase-2-model opus --verbose
```

### P: Quanto tempo leva?
**A:** ~2 minutos para 6 fases (paralelo onde possível).
- Phase 1: 10s
- Phase 2: 5s
- Phase 3: 10s (5 subagentes)
- Phase 4: 2s
- Phase 5: 1s
- Phase 6: 5s
- Total: ~33s em paralelo ideal, ~2min com fallback

### P: Posso pular uma fase?
**A:** Sim! `--skip-phase 4` pula Phase 4.

### P: Posso retomar de uma fase anterior?
**A:** Sim! `--resume-from-phase 3` começa em Phase 3, reutilizando cache de 1-2.

### P: E se a internet cair no meio?
**A:** Cache fica em `.aidd/cache/_phase_*.json`. Rerun com `--resume-from-phase 3` e continua.

---

## 📂 Sobre o Projeto Gerado

### P: Onde fica o projeto criado?
**A:** Em `output/seu-projeto-nome/` (mesmo diretório onde rodou a skill).

### P: O que vem dentro do projeto?
**A:**
```
output/seu-projeto/
├── .aidd/           # Config AIDD
│   ├── config.json
│   ├── rules.md
│   └── cache/_phase_*.json  # Auditoria completa
├── .claude/
│   └── CLAUDE.md    # Guia para você seguir
├── .git/            # Git já inicializado
├── .gitignore       # Excludi secrets
├── requirements.txt # Dependências Python
├── README.md        # Documentação
├── docs/            # Documentação tripartite (HTML + MD + PDF)
└── estado_projeto.db # SQLite pronto para usar
```

### P: Preciso usar tudo que foi gerado?
**A:** Não! Use o que fizer sentido para seu projeto:
- CLAUDE.md: ✅ Leia sempre (instruções personalizadas)
- .aidd/rules.md: ✅ Consulte enquanto desenvolve
- requirements.txt: ✅ Instale dependências sugeridas
- .gitignore: ✅ Use como base
- README.md: Customize conforme necessário
- docs/: Consulte para entender arquitetura

### P: Posso modificar o projeto criado?
**A:** Claro! É seu projeto:
- Edite CLAUDE.md conforme precisar
- Customize .gitignore
- Adicione mais dependências em requirements.txt
- Crie novos commits no Git
- Modifique README.md

---

## 🔐 Sobre Segurança

### P: A skill rouba meus dados?
**A:** Não. Tudo roda localmente:
- Phase 1: Busca em GitHub (public API)
- Phase 2-3-6: LLM via provider do harness (geralmente Anthropic)
- Phase 4-5: Python puro no seu computador
- Nenhum dado é enviado para terceiros além do LLM provider

### P: Gate S1 detecta secrets?
**A:** Sim! Phase 5 verifica:
- `.gitignore` criado
- `requirements.txt` existe
- README menciona segurança
- Detecta padrões de secrets (AWS_KEY, API_TOKEN, etc)

### P: O projeto não devolve erro de segurança?
**A:** Se Gate S1 falhar, Phase 5 não cria o projeto. Corrija o `.gitignore` e tente novamente.

---

## 🎓 Sobre AIDD

### P: O que são as 5 Camadas AIDD?
**A:**
1. **Contratos** — Schemas JSON (tipagem estrita)
2. **Determinismo** — Scripts Python (100% local)
3. **Gates** — Validações mecânicas (exit 0/1)
4. **Persistência** — SQLite (estado do projeto)
5. **Bundles** — Artefatos finais (output/ estruturado)

### P: O que são as 10 Leis AIDD?
**A:** Veja `.aidd/rules.md` no projeto gerado. São diretrizes como:
- R-TOKEN: Economia severa de tokens
- R-DETERMINISMO: Máximo trabalho em Python
- R-GATES: Validações mecânicas
- etc

### P: Preciso seguir TODAS as 10 Leis?
**A:** Elas são recomendações baseadas em milhares de horas de engenharia agêntica. Seguir aumenta qualidade e reduz tokens em 90%.

---

## 🐛 Sobre Problemas

### P: Phase 2 falhou, e agora?
**A:** 
1. Veja `.aidd/cache/_phase_02_index.json` para erro detalhado
2. Verifique sua ideia (muito vaga? muito específica?)
3. Rerun com `--phase-2-model opus` (mais tokens = análise mais robusta)
4. Se falhar novamente, veja TROUBLESHOOTING.md

### P: Skill retornou erro "Agent não disponível"
**A:** Isso é normal! Significa:
- Rodando como script CLI (sem LLM em tempo real)
- Skill usa fallback automático com dados estruturados
- Resultado é mock, mas válido para testes
- Em Claude Code, usaria Agent real

### P: Onde vejo os logs detalhados?
**A:**
```bash
# Ver output de cada phase
cat .aidd/cache/_phase_01_index.json

# Ver com pretty-print
cat .aidd/cache/_phase_02_index.json | python -m json.tool

# Ver logs de todos
ls -la .aidd/cache/_phase_*.json
```

---

## 📞 Onde Procurar Ajuda?

| Dúvida | Arquivo |
|--------|---------|
| Como usar? | USER-GUIDE.md |
| Exemplos reais? | EXAMPLES.md |
| Erro/problema? | TROUBLESHOOTING.md |
| Modelos e tokens? | MODEL-STRATEGY.md |
| Transparência? | .aidd/LEI-FUNDAMENTAL-TRANSPARENCIA.md |
| AIDD conceitos? | .aidd/rules.md (no projeto gerado) |

---

**Versão:** 2.1  
**Última atualização:** 29/08/2026  
**Status:** Completo
