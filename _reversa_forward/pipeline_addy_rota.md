# Pipeline Addy Osmani — Melhoria e Correção de Rota (RevNault)

> Copie o **Bloco 0** (variáveis), substitua os valores `{{...}}` e cole cada **Fase** em sequência na sessão.
> Cada fase termina com um **Gate** binário. Só avance se o gate passar. Cada fase respeita o limite de 3 a 5 passos do `CLAUDE.md`.

---

## Bloco 0 — Variáveis (preencha uma vez)

```text
ROTA_METODO      = {{GET|POST|PUT|PATCH|DELETE}}
ROTA_PATH        = {{/api/v1/access/me}}
ROTA_FRONT       = {{/rbac  (rota TanStack, ou "nenhuma")}}
ARQ_BACKEND      = {{src/features/access/router.py, schemas.py, service.py}}
ARQ_FRONTEND     = {{frontend/src/features/rbac/AccessAdminMatrix.tsx}}
ARQ_CONTRATO     = {{frontend/src/api_contracts.ts}}
ARQ_TESTES       = {{tests/features/access/}}
SINTOMA          = {{o que está errado hoje: erro, status code, comportamento}}
OBJETIVO         = {{resultado esperado em 1 frase}}
RELATORIO_AUDIT  = {{docs/auditorias_rotas/V3/<arquivo>}}
FORA_DE_ESCOPO   = {{o que NÃO deve ser tocado}}
```

---

## Fase 0 — Contexto e baseline

```text
Skills: agent-skills:using-agent-skills, agent-skills:context-engineering

Alvo: {{ROTA_METODO}} {{ROTA_PATH}} (front: {{ROTA_FRONT}}).
Carregue SOMENTE: {{ARQ_BACKEND}}, {{ARQ_FRONTEND}}, {{ARQ_CONTRATO}}, {{ARQ_TESTES}} e a seção desta rota em {{RELATORIO_AUDIT}}.
Consulte o grafo (codebase-memory-mcp) antes de Grep/Glob.

Tarefas:
1. Rode os testes existentes da rota e registre o baseline (passam/falham).
2. Reproduza o sintoma: {{SINTOMA}}. Registre request, response e status.
3. Liste dependências diretas (quem chama, quem é chamado).

Gate 0: baseline registrado + sintoma reproduzido. Se não reproduzir, pare e informe.
Saída: 1 linha de status + bullets curtos.
```

---

## Fase 1 — Definir (requisitos e spec)

```text
Skills: agent-skills:interview-me, agent-skills:spec-driven-development, agent-skills:constraint-driven-development
Comando: /spec

Objetivo: {{OBJETIVO}}.
Faça no máximo 5 perguntas sobre lacunas (regras de RBAC, erros esperados, compatibilidade com o front). Se eu responder "assuma", use o padrão mais seguro.

Gere a spec com critérios de aceite BINÁRIOS (passa/falha) cobrindo:
- contrato (request, response, códigos 200/400/401/403/404/422)
- autenticação e autorização (rota exige sessão assinada; X-User-Id só para impersonação de superadmin)
- comportamento em erro (fail-closed)
- UI (estados loading, vazio, erro; sem emojis, ícones SVG Lucide)

Restrições fixas: Lei #11 (TanStack + Python puro + SQLite WAL + OpenAPI 3.1), Lei #14 (zero emojis), toda rota /api/v1 autenticada, sem stubs.
Fora de escopo: {{FORA_DE_ESCOPO}}.

Gate 1: spec salva e eu aprovei. Sem aprovação, não avance.
```

---

## Fase 2 — Planejar

```text
Skills: agent-skills:planning-and-task-breakdown, agent-skills:source-driven-development
Comando: /plan

Quebre a spec em tarefas verticais (backend + contrato + front por fatia), cada uma com:
- critério de aceite ligado à spec
- arquivos tocados (blast radius mínimo)
- teste que a prova
- dependência (Blocked by)

Antes de decidir padrões de FastAPI/Pydantic/TanStack Router/OpenAPI 3.1, confirme na documentação oficial e cite a fonte.

Gate 2: lista ordenada de tarefas, cada uma com teste associado. Aguarde meu OK.
```

---

## Fase 3 — Construir (loop por tarefa)

```text
Skills: agent-skills:test-driven-development, agent-skills:incremental-implementation, agent-skills:debugging-and-error-recovery
Comando: /build

Execute a tarefa {{N}} do plano. Ciclo obrigatório:
1. RED: escreva o teste que falha e rode (deve falhar pelo motivo certo).
2. GREEN: implemente o mínimo; rode o teste da tarefa e o conjunto da rota.
3. Commit atômico (conventional commits). Só os arquivos da tarefa.

Se algo quebrar: reproduzir, localizar, corrigir a causa raiz, proteger com teste. Não enfraqueça nem remova testes.
Regras: sem stubs, sem mocks de produção, edições por search/replace, saída de comandos filtrada com tail/grep.

Gate 3: testes da tarefa verdes + testes da rota sem regressão. Repita a Fase 3 para cada tarefa.
```

---

## Fase 4 — Contrato e interface

```text
Skills: agent-skills:api-and-interface-design

Revise {{ROTA_METODO}} {{ROTA_PATH}}:
- schemas Pydantic versus OpenAPI 3.1 gerado
- sincronia com {{ARQ_CONTRATO}} (tipos do front)
- consistência de códigos e corpo de erro com as rotas vizinhas
- compatibilidade retroativa (quem mais consome esta rota)

Gate 4: OpenAPI e api_contracts.ts alinhados; typecheck do front sem erros.
```

---

## Fase 5 — Segurança

```text
Skills: agent-skills:security-and-hardening
Agente: agent-skills:security-auditor

Audite a rota: authn/authz, IDOR e escalonamento de privilégio no RBAC, validação de entrada, vazamento de dados em resposta e log, fail-closed, rate limit onde aplicável.
Para cada achado: severidade, cenário concreto, correção. Corrija críticos e altos com teste que prova o bloqueio (o gate precisa provar que morde, exit 1).

Gate 5: nenhum achado crítico ou alto em aberto; testes negativos de acesso presentes.
```

---

## Fase 6 — Validação em tela real

```text
Skills: agent-skills:browser-testing-with-devtools, agent-skills:frontend-ui-engineering
Agente: agent-skills:test-engineer

Suba o app local e valide {{ROTA_FRONT}} no navegador:
- fluxo feliz, vazio, erro, 401 e 403
- console sem erros, requests de rede com status esperado
- responsivo (mobile 375, tablet 768, desktop)
- a11y básica (foco, rótulos, contraste)
- sem emojis na UI

Opcional (só se a auditoria apontar gargalo): agent-skills:performance-optimization.

Gate 6: capturas e logs anexados; zero erros de console.
```

---

## Fase 7 — Simplificar e revisar

```text
Skills: agent-skills:code-simplification, agent-skills:code-review-and-quality
Comandos: /code-simplify, depois /review
Agente: agent-skills:code-reviewer

Simplifique sem mudar comportamento (testes verdes antes e depois).
Revise em 5 eixos: correção, legibilidade, arquitetura, segurança, performance.
Liste achados por severidade; corrija os de bloqueio.

Gate 7: zero bloqueios na revisão; diff contém apenas o escopo da spec.
```

---

## Fase 8 — Prova adversarial

```text
Skills: agent-skills:doubt-driven-development, fable:fable-judge

Trate "pronto" como um conjunto de afirmações. Reexecute você mesmo:
- testes da rota e suíte completa afetada
- lint e typecheck
- reprodução do SINTOMA original (deve estar corrigido)
- git diff: conferir que nenhum teste foi enfraquecido e nada fora de escopo mudou

Veredito: VERIFIED, VERIFIED WITH CAVEATS ou REFUTED, com evidência de cada afirmação.

Gate 8: VERIFIED (ou caveats aceitos por mim).
```

---

## Fase 9 — Entrega

```text
Skills: agent-skills:documentation-and-adrs, agent-skills:git-workflow-and-versioning, agent-skills:shipping-and-launch, agent-skills:observability-and-instrumentation
Comando: /ship

1. ADR curto: decisão, alternativas, consequências (em docs/protocolos/ se for canônico).
2. Observabilidade: log estruturado e métrica de erro da rota.
3. Checklist de ship: testes, lint, typecheck, migração (se houver), rollback.
4. Commits limpos; PR com descrição objetiva (o que mudou, como testar, risco).

Gate 9: checklist de ship 100% marcado. Não faça push sem meu comando.
```

---

## Prompt único (modo rápido)

```text
Rota alvo: {{ROTA_METODO}} {{ROTA_PATH}} (front {{ROTA_FRONT}}).
Sintoma: {{SINTOMA}}. Objetivo: {{OBJETIVO}}. Fora de escopo: {{FORA_DE_ESCOPO}}.
Arquivos: {{ARQ_BACKEND}} | {{ARQ_FRONTEND}} | {{ARQ_CONTRATO}} | {{ARQ_TESTES}}.

Execute o pipeline Addy Osmani em lotes, parando em cada gate para meu OK:
Lote A (definir): using-agent-skills, context-engineering, interview-me, /spec, constraint-driven-development, /plan.
Lote B (construir): source-driven-development, test-driven-development, incremental-implementation, debugging-and-error-recovery, api-and-interface-design.
Lote C (verificar e entregar): security-and-hardening, browser-testing-with-devtools, /code-simplify, /review, doubt-driven-development, fable-judge, /ship.

Regras: TDD Red-Green, zero stubs, Lei #11 e #14, toda rota /api/v1 autenticada, saída silenciosa (1 linha de status + bullets), nunca enfraquecer testes, sem push sem autorização.
```

---

## Checklist final

- [ ] Sintoma reproduzido e corrigido
- [ ] Spec aprovada, critérios binários atendidos
- [ ] Testes novos provam que o gate morde (exit 1)
- [ ] OpenAPI e `api_contracts.ts` sincronizados
- [ ] Segurança sem críticos ou altos
- [ ] Tela validada sem erros de console
- [ ] Revisão e `fable-judge` aprovados
- [ ] ADR e commits entregues
