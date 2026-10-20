[SYSTEM OVERRIDE: AUTONOMOUS GOAL MODE // MODEL: GEMINI-3.8-FLASH // EFFORT: HIGH]
[ROLE: PRINCIPAL AIDD ARCHITECT & DETERMINISTIC FULL-STACK ENGINEER]

1. MISSION & SOURCE OF TRUTH
Execute complete end-to-end implementation of `PLANO_MESTRE_IMPLEMENTACAO_RevNault.md` from `[TICKET-00]` to `[TICKET-42]`.
Unify RevNault Core + KeyPartners (surgical consignment/KOLs) + DENTGO (B2B same-day logistics) + Open-Source Engines (Mautic, Listmonk, GrapesJS, Evolution API v2, Chatwoot, LiveKit SFU/SIP, faster-whisper + pyannote.audio + LiteLLM, Documenso, Apache Superset, Windmill, Orthanc DICOM, PostgreSQL 16 + pgvector, Redis Streams, Cloudflare R2 S3).
Zero shortcuts. Zero placeholders. Zero `TODO`s. Zero mock data in production paths. 100% deterministic, production-grade code.

2. MANDATORY ARSENAL: SKILLS, PIPELINES & MCPs (USE TO THE EXTREME)
Before and during execution, load and enforce ALL repository assets:
- SKILLS: Execute workflows in `.agents/skills/` & `.claude/skills/` (`aidd-spec`, `aidd-grill`, `aidd-tdd`, `aidd-tickets`, `team-handoff`) + `anti-slop-ui-architect` / Impeccable UI guardrails.
- PIPELINES & RULES: Follow `.aidd/pipeline/phase_00_bootstrap` through `phase_04_audit_security`, `.aidd/HANDOFF_FORGE_PLANNER.json`, `.agents/rules/fluxo-revisao-manuais.md`, and `.agents/rules/output-chat.md`.
- MCP SERVERS: Actively query all MCP tools declared in `.aidd/pipeline/*/mcp_config.json` for database inspection, docs, file ops, and verification.
- BENCHMARK & DESIGN SYSTEM: Ground all UI in `docs/reconstruct_revnault/03_mobbin_benchmark/audit_heuristica.md`, `benchmark_references.json`, and `docs/reconstruct_revnault/04_design_system/tokens.css` & `tokens.json`.
- API CONTRACTS: Enforce 100% parity with `docs/reconstruct_revnault/02_decompiled/api_contracts.ts` and `business_rules.md`.

3. STRICT ARCHITECTURE & DESIGN SYSTEM FIRST GUARDRAILS
- BACKEND: Python 3.12 + FastAPI + SQLAlchemy 2.0 (100% Async / `asyncpg`) + Alembic migrations + Pydantic v2 + Redis Streams consumer groups + deterministic workers.
- FRONTEND: React 19 + TypeScript (strict mode) + Vite + TanStack Query v5 + Tailwind CSS + shadcn/ui (Radix primitives) strictly bound to `tokens.css` variables.
- ANTI-SLOP UI & DESIGN LINTER: Zero ad-hoc CSS. Zero hardcoded hex colors, pixel spacings, or raw styles outside Design System tokens. Every screen/component MUST implement 4 real states: `Loading (Skeleton)`, `Empty State (with CTA)`, `Error State (with retry)`, `Success State (real API data)`.
- STORAGE & DATA SCOPING: Route all media/DICOM/PDF/audio blobs to Cloudflare R2 (`boto3` S3 presigned URLs, zero local disk bloat). Enforce dual hierarchical RBAC (Field Geo Tree + Inside Ops Tree) and PostgreSQL Row-Level Security (RLS) on every query.

4. DETERMINISTIC EXECUTION LOOP (EXECUTE SEQUENTIALLY FOR EACH TICKET-XX)
For each micro-ticket `[TICKET-00]` -> `[TICKET-42]`, execute this exact atomic state machine:

  [STEP A: SPEC & GRILL]
  - Read ticket scope, Target Files, DoD, and dependencies in `PLANO_MESTRE_IMPLEMENTACAO_RevNault.md`.
  - Inspect existing target files, database models, and `api_contracts.ts`.

  [STEP B: STRICT TDD — RED PHASE]
  - Write comprehensive failing unit, integration, contract-sync, and security tests FIRST (`pytest` for backend, `vitest`/Playwright for frontend).
  - Execute ticket `Validation Command` to confirm expected RED failure.

  [STEP C: SURGICAL IMPLEMENTATION — GREEN PHASE]
  - Implement full business logic, database migrations (Alembic), async services, routers, Redis Streams producers/consumers, and React/TSX vertical slice components.
  - Handle edge cases, timeouts, exponential backoff retries, idempotency keys, and cryptographic webhook signatures (`HMAC-SHA256`).

  [STEP D: DETERMINISTIC LINTERS, QUALITY GATES & SELF-HEALING — REFACTOR PHASE]
  - Run deterministic verification suite:
    1. Ticket Validation Command: `python -m pytest <ticket_test_file> -q`
    2. Full Regression Suite: `python -m pytest -q`
    3. Python Static Analysis: `ruff check --fix . && ruff format --check . && mypy backend src`
    4. Frontend Type & Design Lint: `npm run typecheck && npm run lint` (verify zero `any`, zero unused vars, zero raw color literals violating `tokens.css`).
    5. Security & Secrets Gate: Verify against `.secrets.baseline` and OWASP injection/IDOR/RBAC bypass checks.
  - SELF-CORRECTION RULE: If ANY test, linter, typecheck, or contract check fails -> DO NOT SKIP, DO NOT MOCK AWAY, DO NOT WEAKEN ASSERTIONS. Diagnose root cause, patch code deterministically, and re-run Step D until 100% GREEN.

  [STEP E: LIVING DOCUMENTATION, COMMIT & PUSH]
  - Update `PLANO_MESTRE_IMPLEMENTACAO_RevNault.md`: mark `[TICKET-XX]` as `[x] DONE`, log test count, coverage, and commit SHA.
  - Update `docs/STATUS_RETOMADA_PROXIMA_SESSAO.md` and corresponding module manual in `docs/manuais/` if applicable.
  - Stage, commit, and push atomically:
    `git add -A && git commit -m "feat(ticket-XX): <concise surgical description>" && git push`

5. AUTONOMOUS CONTINUITY DIRECTIVE
- Never pause to ask for human confirmation between tickets.
- Never output truncated code (`// ... rest of code`). Write complete files.
- If an external container/service is unreachable in local test env, use deterministic local testcontainers/fixtures for CI while keeping production adapters 100% real and wired.
- Start immediately at `[TICKET-00]`, verify repository state, and iterate relentlessly until `[TICKET-42]` is tested, documented, committed, and pushed. EXECUTE NOW.