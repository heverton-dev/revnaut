---
name: adaptar-lovable-aidd
description: Use quando o usuário pedir para adaptar/adequar/converter um projeto exportado do Lovable (ou Bolt) para um projeto convencional — sair do lock-in Lovable, adicionar env/.env.example, testes, typecheck, lint, CI/CD, estrutura de pastas, segurança/RLS. Dispara também em "tirar do Lovable", "export do Lovable", "projeto convencional", "migrar projeto do Lovable", "produção" a partir de app gerado por IA.
---

# Adaptar Projeto Lovable → Convencional (com AIDD)

## Visão geral

Projeto exportado do Lovable é um protótipo Vite + React + Tailwind + Supabase
funcional, mas sem a engenharia que o torna um projeto convencional: env,
testes, typecheck, lint, CI, estrutura, segurança. Esta skill adapta o projeto
**e** instala as 5 peças do kit AIDD (`.agents/aidd`) para que a adaptação não
regrida: quem gera não aprova, checagens são determinísticas, tipo novo é 1
entrada em registro, commit vermelho é bloqueado por hook, e todo problema
corrigido vira teste de regressão.

**Princípio central:** a adaptação não termina quando o app roda — termina
quando as 5 peças AIDD estão presentes e verdes, porque sem elas a base volta a
acumular débito no próximo ciclo de geração por IA.

## Quando usar

- Projeto exportado do Lovable/Bolt (Vite+React+TS+Supabase) que precisa virar
  projeto convencional de verdade.
- Usuário pede "sair do Lovable", "tirar do lock-in", "projeto convencional",
  "migrar/adequar/adaptar projeto do Lovable".
- Continuar desenvolvimento fora da plataforma Lovable.

## Quando NÃO usar

- Projeto que já é convencional (env, testes, CI, hooks presentes).
- Pedido só de feature/fix pontual — isso é trabalho normal, não adaptação.
- Usuário quer apenas exportar/copiar o código sem transformação.

## Pré-requisito

- Kit AIDD instalado (`.agents/aidd` ou `tooling/kit-fundacao-aidd`).
- Python disponível para `analisar-projeto.py`/`instalar.py`.

---

## Procedimento

### Passo 1 — Localizar o kit AIDD

Resolução em ordem, use o **primeiro** que existir:

1. Flag `--kit <caminho>` fornecida pelo usuário.
2. `PROJETO/.agents/aidd/` (submodule no projeto-alvo).
3. `PROJETO/.agents/skills/aidd/` (submodule recolocado).
4. `PROJETO/tooling/kit-fundacao-aidd/`.
5. `~/.agents/aidd/` (cross-runtime).
6. Se nenhum existir: **não improvise**. Pergunte ao usuário o caminho do kit
   (ou se deve instalá-lo) antes de qualquer escrita.

### Passo 2 — Diagnóstico (somente leitura, nunca grava)

1. **Confirme que é projeto Lovable:** `package.json` com Vite+React, pasta
   `src/integrations/supabase/`, `supabase/migrations/`, `vite.config.*`.
2. **Rode o analisador do kit:**
   ```bash
   python <kit>/analisar-projeto.py <PROJETO>
   ```
   Leia o relatório antes de propor qualquer coisa. Nunca pule este passo.
3. **Levante os gaps convencionais** (inspecione, não assuma):
   - `.env.example` ausente, `.env` versionado no git, chaves inline no código.
   - `SUPABASE_SERVICE_ROLE_KEY` no bundle/client (vazamento de segredo).
   - Sem scripts de `test`/`typecheck`/`lint` no `package.json`.
   - Sem `.github/workflows/`, sem README real.
   - RLS ausente/frágil nas migrations (`supabase/migrations/`).
   - Candidatos a registro declarativo: `if <x> == "..."` repetido em ≥2
     arquivos ou campos do mesmo conceito hardcoded.

### Passo 3 — Decidir o caminho

- **Padrão:** manter a stack (Vite + React + TS) e torná-la convencional.
- **Next.js:** somente se o usuário exigir SSR/SEO/desempenho. Sem isso,
  **não** migre de framework — reescrever stack é risco sem benefício pedido.
- Declare a escolha em 1 frase antes de começar ("vou manter Vite/React e
  focar em env/testes/CI/segurança, porque não foi pedido SSR").

### Passo 4 — Adaptar (Peça 1: Builder ≠ Critic)

Sempre que gerar material em lote, **quem gera nunca aprova o próprio
resultado**. O agente principal (ou subagente builder) produz; um subagente
`critic` **somente-leitura** aprova por etapa contra critérios objetivos. A
reprovação volta ao builder com motivo específico (arquivo/linha), nunca é
corrigida pelo crítico.

Áreas de adaptação:

1. **Env & segredos**
   - Criar `.env.example` (chaves com placeholders, sem valores reais).
   - Garantir `.gitignore` com `.env`, `.env.local`, `.env.*.local`.
   - Se `.env` está no git: `git rm --cached .env` (não apagar do disco).
   - Substituir chaves inline por `import.meta.env.VITE_*`.
   - **Banir** `SUPABASE_SERVICE_ROLE_KEY` do código do browser — é valor de
     servidor, nunca `VITE_`.
2. **Estrutura** — padronizar `src/`: `components/`, `pages/`, `services/`,
   `hooks/`, `lib/`, `types/`; preservar `components/ui` (shadcn). Remover
   artefatos específicos do Lovable que não sejam código (ex.: metadados do
   editor, se houver), sem quebrar imports.
3. **Qualidade** — Vitest + React Testing Library, `tsc --noEmit`, ESLint +
   Prettier. Adicionar scripts `test`, `typecheck`, `lint`, `build` no
   `package.json`. Um teste mínimo do service/lógica de negócio (não só de
   render) é obrigatório.
4. **CI/CD** — `.github/workflows/ci.yml` rodando typecheck + lint + test +
   build em PR/push. Deploy depende da plataforma (Vercel/Netlify/VPS); se
   for deploy real, exigir confirmação do usuário (ação outward-facing).
5. **Supabase** — conferir `supabase/config.toml`; **auditar RLS** nas
   migrations (habilitar RLS + políticas mínimas por tabela com dado de
   usuário); corrigir políticas "abertas" só com justificativa.
6. **README** — setup, env necessárias, comandos, deploy.

### Passo 5 — Instalar as Peças AIDD (2–5)

Para cada peça, **explique em 1-2 frases o que e por quê**, rode o instalador
**sem** `--aplicar` (dry-run), mostre o plano/diff, e só aplique com
confirmação explícita para aquela peça.

1. **Peça 2 — Gate determinístico:** criar `scripts/validar_<regra>.py`
   adaptado de `scripts/validar_template.py.template` do kit. Regras
   determinísticas objetivas do projeto, ex.:
   - `SUPABASE_SERVICE_ROLE_KEY` não aparece em `src/` (nem em `VITE_`).
   - `.env.example` existe; `.env` não está no índice git.
   - Sem `if tipo == "..."` nos pontos já migrados para registro.
   - Script, **nunca LLM** — se a checagem depende de julgar sentido, isso
     pertence ao critic (Peça 1), não ao script.
2. **Peça 3 — Registro declarativo:** para cada candidato do diagnóstico
   (campo hardcoded em `if x == "..."`), rodar:
   ```bash
   python <kit>/scripts/registro_declarativo_scaffold.py --conceito <nome> \
     --campos <campos> --saida src/lib/<nome>.ts
   ```
   Adaptar o esqueleto gerado ao TS e migrar os consumidores para o registro.
   Tipo novo = 1 entrada no dicionário, nunca novo `if`.
3. **Peça 4 — Nunca commitar vermelho:** instalar hook pre-commit:
   ```bash
   python <kit>/instalar.py <PROJETO> --peca hook \
     --test-cmd "npm run typecheck && npm test && npm run build"
   ```
   (dry-run primeiro; `--aplicar` após confirmação). O hook **bloqueia**
   commits quando a suite falha — é mecanismo, não promessa.
4. **Peça 5 — Postmortem → teste:** criar `POSTMORTEM.md` (molde do kit em
   `templates/POSTMORTEM.md`) e registrar **cada problema corrigido na
   adaptação** com Causa/Fix/Prevenção/Arquivos. Toda linha de Prevenção
   verificável nasce junto com um teste de regressão:
   ```bash
   python <kit>/scripts/postmortem_para_teste.py --titulo "<bug>" \
     --prevencao "<regra>" --saida tests/test_regressao_<slug>.py
   ```
   **Preencha o corpo do teste** — stub com `NotImplementedError` não conta
   como verde. Em projeto TS, o teste de regressão deve ser Vitest na mesma
   lógica (regra: prevenção verificável ⇒ teste automatizado).

### Passo 6 — Verificação

1. `npm run typecheck`, `npm test`, `npm run lint`, `npm run build` **verdes**.
2. Gates determinísticos (Peça 2) passam.
3. Hook pre-commit presente e ativo (teste: `git commit` com suite vermelha é
   bloqueado).
4. Critic (Peça 1) revisa o resultado final contra critérios objetivos.
5. Toda prevenção de postmortem tem teste de regressão preenchido e verde.

### Passo 7 — Relatório

Outcome-first em PT-BR:
- Primeira frase = o que aconteceu (projeto adaptado, 5 peças instaladas).
- Listar arquivos criados/alterados e as peças AIDD aplicadas.
- Se deploy/commit/push não foi autorizado, linha exata: `PENDING: <ação> -
  aguardando autorização`.
- Honestidade: o que não foi verificado, o que ficou fraco.

---

## Regras inegociáveis (não flexibilizar, mesmo sob pedido)

- **Nunca remover ou sobrescrever** arquivo/skill/hook já configurado. Em
  colisão: mescla não-destrutiva (hook ganha bloco extra) ou recusa e explica
  por quê. **Nunca decide sozinho.**
- **Sempre explicar antes de gravar** — toda escrita vem precedida de frase
  do que será criado/alterado e do motivo.
- **Nunca aplicar `instalar.py` com `--aplicar` sem dry-run + confirmação**
  explícita do usuário para a peça em questão.
- **Nunca instalar "todas" de uma vez sem revisão peça por peça** — a
  confirmação pode ser em lote no final, a explicação individual não.
- **Idempotente:** peça já presente = "já presente, nada a fazer", nunca
  "corrigida"/"substituída".
- **Nunca commitar vermelho:** se a suite falhar, o hook bloqueia — e o agente
  não contorna o hook.

## Racionalizações que já sabemos que falham (não usar)

| Excusa | Realidade |
|--------|-----------|
| "O CI já roda os testes, não preciso de hook local" | CI roda depois do commit; o vermelho já entrou no histórico e no repositório. O hook é o gate no momento do erro. |
| "Vou rodar os testes na mão antes de commitar" | Promessa em texto ≠ mecanismo. A Peça 4 existe justamente porque disciplina falha sob pressão. |
| "O stub de teste fica com NotImplementedError, deixo para depois" | Stub sem corpo = prevenção sem teste = débito. Preencha ou não registre a prevenção. |
| "É só 1 tipo, registro declarativo é over-engineering" | O ponto é o próximo `if tipo ==` que nascer sem registro. Se o conceito já tem 2+ hardcodes, migre. |
| "O projeto é pequeno, posso pular a estrutura" | Adaptação é o momento de acertar a estrutura; o custo cresce com o tamanho. |
| "Não rodei o analisador, já sei o que falta" | O analisador detecta o que você não conhece (hooks, convenções, candidatos). Diagnosticar primeiro é inegociável. |
| "Vou manter o .env no git, é mais simples" | `.env` versionado = segredo no histórico. `git rm --cached` + `.gitignore` agora. |

## Red flags — pare e volte ao procedimento

- Pulou o Passo 2 (diagnóstico) e foi direto editar.
- Escreveu algo antes de explicar o quê/porquê.
- Aplicou `--aplicar` sem dry-run + confirmação.
- `SUPABASE_SERVICE_ROLE_KEY` permanece em `src/`.
- `.env` ainda rastreado pelo git.
- Hook pre-commit ausente ou contornado.
- Postmortem com prevenção mas sem teste de regressão preenchido.
- Critic reprovou e o próprio gerador "corrigiu" sem voltar ao builder.

## Referências

- Kit AIDD: `.agents/aidd/README.md`, `.agents/aidd/skills/kit-fundacao-aidd/SKILL.md`
- `analisar-projeto.py` — diagnóstico (só leitura)
- `instalar.py` — instalador aditivo (dry-run por padrão)
- `scripts/validar_template.py.template`, `scripts/registro_declarativo_scaffold.py`,
  `scripts/postmortem_para_teste.py`, `templates/POSTMORTEM.md`