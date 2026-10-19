# Canonical AIDD Governance & Directives

> **Governance Standard:** Zero Stubs, Strict Determinism, Context Optimization (<1500 tokens), Absolute Cache Invariance.

---

## 1. Core Execution Constraints

- **Thinking constraint:** Think strictly in compact English. No meta-deliberation. Focus only on architectural invariants and edge cases. Under 150 words of reasoning.
- **Execution limit:** Resolve tasks in 3 to 5 discrete steps. Stop and request confirmation if more steps are required.
- **Output format (Rule 10):** Silent executor. Return code edits and 1-line execution status only. Do not explain what was changed unless explicitly asked. Do not repeat code in conversational reply.
  - When prose is requested, strictly shape answers as:
    1. One top sentence stating what to do or what happened. No preamble.
    2. Short bulleted body. Facts, numbers, findings. No narration of steps taken.
    3. One closing suggestion block, separated from the body.
  - **Token budget:** Target ≤300 tokens for normal answer, ≤600 for technical answer.
- **Editing rule:** Always use exact search/replace block tools (`replace_file_content`). Never dump entire rewritten files into output.
- **Bash rule:** Always pipe verbose commands to tail/grep. E.g., `pytest 2>&1 | tail -n 25`. Never dump raw bundle outputs, logs, or lockfiles into context.
- **Graph-first:** Query knowledge graph (`codebase-memory-mcp` MCP) before Grep, Glob, or full file reads.
- **Docs Ingestion constraint:** Read ONLY living canonical documentation (`docs/protocolos/`, `AGENTS.md`, `MEMORY.md`).

---

## 2. Inviolable Laws

1. **Determinism First:** Use deterministic scripts, AST, regex, or JSON Schema. Never use LLM for mechanical tasks.
2. **Binary Quality:** Every change must pass Quality Gates (exit 0 = pass, exit 1 = block).
3. **Structured Persistence:** Persist state in audit files (JSON, SQLite), never in volatile conversation memory.
4. **Extreme Token Economy:** Minimalist prompts, compact English core rules, dense PT-BR user responses only when requested.
5. **Zero Stubs / Zero Mocks:** 100% functional, typed production code with real tests.
6. **Agnostic Supremacy:** Zero vendor lock-in across OS, harness, and LLM providers.
7. **Developer in Control:** Strictly sequential, interactive executions. Zero invisible headless background subagents.
8. **Label Honesty:** Never claim certification or test coverage beyond real automated test results.
9. **Tool Testing Discipline:** Follow the 5-step cycle (auto-fix, commit & push, clean target, clean execute, update report).
10. **Quarteto Sine Qua Non Dinâmico:** Every project generated or evolved MUST natively expose 4 pillars: Swagger Studio (`/docs`), Webhook Studio (`/webhooks`), MCP Studio (`/mcp`) and User Guide (`/docs/guia`).
11. **Padrão-Ouro de Stack Tecnológica:** Frontend em TanStack Start / TanStack Router + React + TypeScript + Tailwind CSS (Next.js é formalmente abolido — Lei #11); Backend em Python puro + SQLite WAL + OpenAPI 3.1.
12. **Anti-Docs Rot & Canonical Ingestion:** Never ingest stale docs. Living docs reside in `docs/protocolos/` and active schemas.
13. **Todo Portão Deve Provar que Morde:** Every quality gate must prove it blocks invalid inputs with exit 1 in automated tests.
14. **Zero Emojis & UI Design Hygiene (Lei #14):** É TERMINANTEMENTE PROIBIDO o uso de emojis Unicode em qualquer elemento de interface do usuário, código frontend, botões, badges, modais, alertas ou filtros. Utilize estritamente ícones vetoriais SVG inline (padrão shadcn / Lucide) com dimensões controladas e `stroke="currentColor"` quando representações visuais forem necessárias.

---

## 3. The 3 Canonical Creation Flows (A Tríade Canônica)

- **FLUXO 01 (`/pure`):** `[FORGE -> PLANNER] -> GENERATOR -> [MASTER -> ENTERPRISE -> OPS]` (From Scratch, TDD Red-Green).
- **FLUXO 02 (`/aidd-open` ou `/factory`):** `[FORGE -> PLANNER] -> FACTORY -> [MASTER -> ENTERPRISE -> OPS]` (Open-Source Engines).
- **FLUXO 03 (`/freedom`):** `[FORGE -> PLANNER] -> BRIDGE -> [MASTER -> ENTERPRISE -> OPS]` (Low-Code Lock-in Eradication).

Convergence Funnel: All flows converge into `aidd-master` (Modular VSA) -> `aidd-enterprise` (SHA-256) -> `aidd-ops` (VPS Docker Compose).

---

## 4. Procedural Skills

- `/aidd-grill`: Socratic interview protocol to resolve edge cases and invariants before code modification.
- `/aidd-spec`: Deterministic technical specification generator with binary acceptance criteria.
- `/aidd-tickets`: Atomic tracer-bullet task decomposition with bounded blast radius.
- `/aidd-tdd`: Strict Red-Green-Refactor cycle with zero stubs invariant across all language runtimes.
- `/aidd-diagnose`: 5-phase scientific fault triage integrated with `codebase-memory-mcp`.
- `/aidd-handoff`: Compact session context serialization directly into `secoes/`.


---

# Reversa

> Framework de Engenharia Reversa instalado neste projeto.

## Como usar

Use o fluxo adequado no chat:

- `/reversa` — descobrir e documentar um sistema existente
- `/reversa-new` — criar PRD e specs para um projeto novo
- `/reversa-forward` — implementar ou evoluir código a partir das specs
- `/reversa-migrate` — planejar a migração de um sistema legado
- `/reversa-docs` — gerar o mini-site visual da documentação
- `/reversa-agents-help` — consultar o catálogo completo de agentes

## Comportamento ao ativar

Quando o usuário digitar `/reversa` ou a palavra `reversa` sozinha em uma mensagem:

1. Ative o skill `reversa` disponível em `.claude/skills/reversa/SKILL.md`
2. Se não encontrar em `.claude/skills/`, tente `.agents/skills/reversa/SKILL.md`
3. Leia o SKILL.md na íntegra e siga exatamente as instruções do Reversa

## Regra não-negociável

Por padrão, nunca apague, modifique ou sobrescreva arquivos pré-existentes do projeto legado:
o Reversa escreve apenas em `.reversa/`, `_revnault_sdd/`, `_reversa_docs/`, `_reversa_forward/`, `_reversa_bugs/` e `_reversa_refactor/`.
A única exceção é a política configurável abaixo, controlada exclusivamente pelo usuário.

Antes de criar, modificar ou apagar qualquer arquivo fora das pastas próprias do Reversa, leia `.reversa/reversa-config.json` e obedeça ao resultado:

- Arquivo ausente, JSON inválido ou campo com tipo errado: trate como `allowLegacyEdits: false` (falha segura, nenhuma escrita fora das pastas do Reversa).
- `allowLegacyEdits: false`: recuse a escrita, informando o caminho recusado, o estado atual da config e o que o usuário deve editar para liberar.
- `allowLegacyEdits: true` com `allowedPaths` não vazio: escreva apenas em caminhos que casem com algum glob da lista (globs relativos à raiz do projeto, com `/`, suportando `*` e `**`).
- `allowLegacyEdits: true` com `allowedPaths` vazio ou ausente: projeto liberado; avise uma vez por sessão que a liberação é irrestrita.

Nunca crie nem edite `.reversa/reversa-config.json` por iniciativa própria: pedido na conversa não é liberação implícita, alterações nesse arquivo são ato exclusivo do usuário.
