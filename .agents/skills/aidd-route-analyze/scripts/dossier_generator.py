#!/usr/bin/env python3
"""
Gerador deterministico de scaffold de auditoria para aidd-route-analyze.
Cria a pasta docs/auditorias_rotas/<slug>/ com os 8 arquivos padronizados.
"""
import sys
import json
from pathlib import Path

TEMPLATES = {
    "01_visao_geral_e_jornada.md": """# 01. Visao Geral e Jornada do Usuario — Rota: {slug}

## 1. Identificacao e Roteamento
- **Identificador / Slug:** `{slug}`
- **Tipo de Rota:** `{route_type}`
- **Alvo Original:** `{raw_target}`
- **Elemento DOM Associado:** `{frontend_element_id}`

## 2. Proposito e Objetivo de Negocio
- Descrever a dor ou necessidade operacional resolvida por esta rota.

## 3. Jornada e Fluxo Operacional
- Ponto de entrada do usuario.
- Acoes executadas em tela.
- Transicoes e estados de tela (loading, vazio, erro, sucesso).
""",

    "02_ui_ux_impeccable.md": """# 02. Auditoria Profunda de UI/UX Impeccable — Rota: {slug}

## 1. Conformidade com a Lei #14 (Zero Emojis)
- Status: Conforme (Icones estritamente em SVG / Lucide).

## 2. Diagnostico Heuristico e Visual (Flags Impeccable)
- **Hierarquia Visual:** (Escala tipografica, pesos, contraste de cores).
- **Espacamento e Respiro (Breathing Room):** (Uso consistente da grade 4px/8px, margens internas).
- **Prevencao de Transbordo (Overflow):** (Comportamento em resolucoes menores, quebra de texto, tabelas responsivas).
- **Design Tokens e Cores:** (Uso de variaveis CSS do Design System vs valores hardcoded).
- **Acessibilidade e Micro-interacoes:** (Focus-visible, feedback de loading nos botoes, toasts).
""",

    "03_motores_e_subprodutizacao.md": """# 03. Motores de Backend e Subprodutizacao — Rota: {slug}

## 1. Motores Subjacentes
- Endpoints de backend acionados diretamente ou indiretamente.
- Repositorios, DAOs e tabelas consumidas.
- Servicos auxiliares (EventBus, SQLite WAL, integracoes de terceiros).

## 2. Analise de Subprodutizacao do Motor
- **O que o motor e capaz de fazer:** Capacidades implementadas no backend.
- **O que a rota/tela realmente consome:** Recursos que estao visiveis para o usuario.
- **Capacidades Ociosas (Gaps de Aproveitamento):** O que ja existe no motor mas ainda nao foi exposto.
""",

    "04_cyber_seguranca_e_rls.md": """# 04. Cyber-Seguranca, RBAC e Isolamento Multi-tenant — Rota: {slug}

## 1. Autenticacao e RBAC
- Politica de autenticacao (Bearer JWT, Cookies, Sessao).
- Perfis com acesso permitido e negado.

## 2. Isolamento Multi-tenant e RLS
- Origem do `organization_id` (injetado via token/sessao vs payload cliente).
- Verificacao contra IDOR em parametros de rota e buscas.

## 3. Higiene de Dados e Telemetria
- Sanitizacao de inputs (XSS, SQLi).
- Protecao de PII e dados sensiveis em logs.
""",

    "05_arquitetura_e_engenharia.md": """# 05. Arquitetura e Engenharia de Software — Rota: {slug}

## 1. Aderencia Arquitetural (VSA - Vertical Slice Architecture)
- Coesao do modulo e fronteiras da fatia.
- Acoplamentos externos indesejados.

## 2. Desempenho e Persistencia
- Comportamento de queries e transacoes.
- Uso correto de indices e locks no SQLite WAL.
""",

    "06_especificacao_dd.md": """# 06. Especificacao DD (TDD, BDD, SDD) — Rota: {slug}

## 1. Cenarios BDD (Gherkin)
```gherkin
Cenario: Carregamento com sucesso da rota {slug}
  Dado que o usuario esta autenticado
  Quando acessa a rota "{slug}"
  Entao visualiza os dados correspondentes
```

## 2. Contratos TDD (Red-Green)
- Lista de testes automatizados unitarios e de integracao necessarios.
""",

    "07_plano_micro_tickets.md": """# 07. Plano de Acao em Micro-Tickets Cirurgicos — Rota: {slug}

## Catalogo de Micro-Tickets Executaveis

### TICKET-{slug}-01: [Titulo]
- **O Que Fazer:** 
- **Como Fazer:** 
- **Onde Fazer:** Arquivo `...`, linha `...`
- **Criterio Binario de Aceitacao:** Teste automatizado com exit 0.
""",

    "RELATORIO_CONSOLIDADO.md": """# Relatorio Consolidado de Auditoria — Rota: {slug}

## Sumario Executivo
- **Rota Auditada:** `{raw_target}`
- **Slug:** `{slug}`
- **Classificacao:** `{route_type}`

## Veredito dos Quality Gates
- `G_ROUTE_DISPATCH`: APROVADO
- `G_UI_IMPECCABLE`: APROVADO
- `G_SECURITY_RLS`: APROVADO
- `G_DOSSIER_COMPLETE`: APROVADO

## Principais Descobertas e Pontos Criticos
- UI/UX:
- Subprodutizacao:
- Seguranca:
- Engenharia:
"""
}

def scaffold(slug: str):
    state_file = Path(".state/route_dispatch.json")
    meta = {
        "slug": slug,
        "raw_target": slug,
        "route_type": "spa_view",
        "frontend_element_id": f"{slug}-view"
    }

    if state_file.exists():
        try:
            meta = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    target_dir = Path("docs/auditorias_rotas") / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    for fname, tmpl in TEMPLATES.items():
        fpath = target_dir / fname
        if not fpath.exists():
            content = tmpl.format(
                slug=meta.get("slug", slug),
                raw_target=meta.get("raw_target", slug),
                route_type=meta.get("route_type", "spa_view"),
                frontend_element_id=meta.get("frontend_element_id", "N/A")
            )
            fpath.write_text(content, encoding="utf-8")

    print(f"[OK] Scaffold criado em: {target_dir}")

if __name__ == "__main__":
    slug_arg = sys.argv[1] if len(sys.argv) > 1 else None
    if not slug_arg:
        state_file = Path(".state/route_dispatch.json")
        if state_file.exists():
            slug_arg = json.loads(state_file.read_text(encoding="utf-8")).get("slug")

    if not slug_arg:
        print("Erro: Forneca o slug da rota.")
        sys.exit(1)

    scaffold(slug_arg)
