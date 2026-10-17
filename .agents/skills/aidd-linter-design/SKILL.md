---
name: aidd-linter-design
description: Guardião determinístico de Design Tokens, Single Source of Truth (SSOT) e padronização visual UI/UX no padrão AIDD. Audita código CSS/JS/HTML contra valores arbitrários e cores hardcoded, verifica integridade de primitivas de componentes e atua como Quality Gate inquebrável (Lei #1, Lei #2 e Lei #13).
commands:
  - "/aidd-linter-design"
  - "/linter-design"
  - "/audit-tokens"
  - "/lint-tokens"
---

# AIDD-LINTER-DESIGN • Guardião Determinístico de Design Tokens & SSOT

> **Governança Canônica AIDD:** Determinismo Estrito (Lei #1), Qualidade Binária (Lei #2), Persistência Estruturada (Lei #3), Zero Stubs (Lei #5) e Todo Portão Deve Provar que Morde (Lei #13).  
> **Propósito:** Impedir a fragmentação visual e o surgimento de estilos pontuais ou cores hardcoded, assegurando que 100% da interface do usuário derive estritamente do Single Source of Truth (SSOT) de tokens e primitivas.

---

## 1. Princípios Invioláveis do Linter

1. **Zero Cores Hardcoded:** Nenhuma declaração CSS ou style inline fora de `tokens.css` pode conter `#hex`, `rgb()`, `rgba()`, `hsl()` ou `hsla()`. Todas as cores devem apontar para variáveis semânticas (`var(--color-*)`).
2. **SSOT Centralizado:** O arquivo `tokens.css` é a única fonte permitida para declarar valores literais de tokens (paleta da marca, neutros, superfícies, feedback e escalas de espaçamento/raio).
3. **Primitivas Canônicas Obrigatórias:** Nenhum botão, badge, card ou tabela deve ser escrito ad-hoc com HTML/CSS solto no JS. Devem ser instanciados pelas funções construtoras de `components.js` (`ui.Button`, `ui.Badge`, `ui.Card`, `ui.KpiCard`, `ui.DataTable`, `ui.EmptyState`, `ui.SearchBar`).
4. **Zero Emojis & UI Design Hygiene (Lei #14):** É TERMINANTEMENTE PROIBIDO o uso de emojis Unicode em qualquer elemento de interface do usuário, código frontend, botões, badges, modais, alertas ou filtros. Toda iconografia deve ser estritamente vetorial SVG inline (padrão shadcn / Lucide com `stroke="currentColor"`).
5. **Todo Portão Deve Provar que Morde (Lei #13):** O Quality Gate possui modo `--test-bite` que insere violação proposital e prova que o processo encerra com `exit 1`.

---

## 2. Gatilhos & Comandos

A skill é acionada por comando explícito ou intenção de auditoria visual:
* `/aidd-linter-design audit` — Executa a varredura nos novos componentes e tokens canônicos (`components.css`).
* `/aidd-linter-design strict` — Executa varredura profunda em todos os arquivos CSS do projeto.
* `/aidd-linter-design bite` — Valida a integridade do gate executando o teste da Lei #13 (`--test-bite`).
* `/aidd-linter-design fix` — Sugere e aplica o mapeamento automático de cores cruas para os tokens equivalentes.

Responde também a linguagem natural:
* *"audite os design tokens do projeto"*
* *"verifique se há cores hardcoded ou estilos arbitrários"*
* *"rode o linter de design do aidd"*

---

## 3. Protocolo de Execução em 3 Fases

Ao ser acionada, a skill executa sequencialmente:

### Fase 1: Integridade Estrutural dos Tokens
Verifica se `tokens.css` expõe a lista mínima de variáveis canônicas:
- `--color-brand-primary`, `--color-brand-accent`
- `--color-emerald-500`, `--color-amber-500`, `--color-rose-500`
- `--space-1` a `--space-8`
- `--radius-md`
- `--font-sans`

### Fase 2: Integridade da Biblioteca de Componentes
Verifica se `components.js` exporta a suíte completa de primitivas reusáveis:
- `Button`: Variantes primary, secondary, outline, ghost, success, danger e tamanhos sm/md/lg.
- `Badge`: Variantes com indicador `.ds-badge-dot` e conformidade WCAG.
- `Card` e `KpiCard`: Superfícies com elevação e micro-indicadores de tendência.
- `DataTable`: Tabela estruturada com cabeçalhos e alinhamentos semânticos.
- `EmptyState`: Tratamento amigável de listas e buscas sem dados.
- `SearchBar`: Campo de busca padronizado com ícone vetorial embutido.

### Fase 3: Auditoria Léxica e Quality Gate
Executa o script determinístico:
```bash
python scripts/lint_design_tokens.py
```
- Se `exit 0`: Aprovado. O pipeline prossegue.
- Se `exit 1`: Bloqueado. Exibe a lista de arquivos e linhas com violações detalhadas.

---

## 4. Integração Contínua & Pre-Commit Hook

Para garantir que desenvolvedores e agentes não subam código fora do padrão, o linter deve ser incluído em:
1. **Suite de Testes (`tests/test_lint_design_tokens.py`):** Integrado nativamente ao `unittest` / `pytest`.
2. **Git Hook (`.git/hooks/pre-commit`):** Bloqueia commits com código CSS contendo cores cruas.
3. **Rota Viva do Design System (`#/design-system`):** Fornece galeria interativa para validação visual contínua.
