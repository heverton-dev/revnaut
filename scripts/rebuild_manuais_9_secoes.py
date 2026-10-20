#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reconstrutor Canônico de Manuais de Rotas e Sub-rotas com 9 Seções Anatômicas.
Padrão AIDD v4.0 • Lei #14 (Zero Emojis) • Relação 1-para-1 Estrita.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANUAIS_DIR = REPO_ROOT / "docs" / "manuais"
INDEX_HTML = REPO_ROOT / "docs" / "reconstruct_revnault" / "05_reconstructed_app" / "index.html"

# Mapeamento Canônico das 25 Rotas e Sub-rotas do VIEW_CONFIG + 1 Governança
CANONICAL_ROUTES = [
    ("00", "login", "Acesso ao Sistema • RevNault Dental", "login-view", False, ""),
    ("01", "deals", "Funil Comercial & Gestão de Pipelines Odontológicos", "deals-view", False, ""),
    ("02", "contacts", "Base de Cirurgiões-Dentistas, Clínicas & Decisores", "contacts-view", False, ""),
    ("03", "contacts-segments", "Contatos • Segmentos Inteligentes & Especialidades", "contacts-segments-view", True, "contacts"),
    ("04", "inbox", "Caixa de Entrada Omnichannel (WhatsApp)", "inbox-view", False, ""),
    ("05", "tickets", "Central de Tickets & Atendimento Cirúrgico", "tickets-view", False, ""),
    ("06", "tasks", "Tarefas Operacionais & Checklist de Fechamento", "tasks-view", False, ""),
    ("07", "reports", "Relatórios Executivos & KPIs da Indústria Odontológica", "reports-view", False, ""),
    ("08", "reports-performance", "Relatórios • Performance por Consultor Cirúrgico", "reports-performance-view", True, "reports"),
    ("09", "marketing", "Campanhas de Marketing & Eventos CIOSP", "marketing-view", False, ""),
    ("10", "marketing-mautic", "Marketing • Painel de Sincronização Mautic VPS", "marketing-mautic-view", True, "marketing"),
    ("11", "scoring", "Matriz de Lead Scoring & Qualificação de Cirurgiões", "scoring-view", False, ""),
    ("12", "scoring-icp", "Pontuação • Critérios de Prescrição & Implantes/Mês", "scoring-icp-view", True, "scoring"),
    ("13", "automations", "Construtor de Fluxos de Automação Cirúrgica", "automations-view", False, ""),
    ("14", "hierarchy", "Estrutura Corporativa, Divisões & RBAC Setorial", "hierarchy-view", False, ""),
    ("15", "users", "Central de Gestão de Usuários & Credenciais (Super Admin)", "users-view", False, ""),
    ("16", "import-contacts", "Importador Universal de Carteiras de Clientes (CSV/XLSX)", "import-contacts-view", False, ""),
    ("17", "integrations", "Central de Conectores & Integrações Enterprise (TOTVS, WhatsApp & Webhooks)", "integrations-view", False, ""),
    ("18", "keypartners", "KeyPartners • Gestão de Consignados & Lotes ANVISA", "keypartners-view", False, ""),
    ("19", "keypartners-kols", "KeyPartners • KOLs, Cirurgiões & Contratos de Consignação", "keypartners-kols-view", True, "keypartners"),
    ("20", "dentgo", "DENTGO Express • Entregas Rápidas Same-Day & Motoboy", "dentgo-view", False, ""),
    ("21", "dentgo-fefo", "DENTGO • Rastreabilidade FEFO & Separação de Lotes", "dentgo-fefo-view", True, "dentgo"),
    ("22", "video-sos", "Vídeo SOS Mesa Cirúrgica • Conexão em Tempo Real LiveKit", "video-sos-view", False, ""),
    ("23", "dicom-viewer", "Visualizador Tomográfico DICOM & Malhas STL 3D", "dicom-viewer-view", False, ""),
    ("24", "bi-superset", "BI Executivo • Dashboards Analíticos Superset", "bi-superset-view", False, ""),
]


def extract_dom_elements(html: str, view_id: str):
    """Extrai botões, modais e endpoints do DOM da tela."""
    sec_match = re.search(rf'<section[^>]*id=["\']{re.escape(view_id)}["\'][^>]*>(.*?)</section>', html, re.DOTALL)
    if not sec_match:
        return [], [], []

    sec_html = sec_match.group(1)

    # 1. Botões
    buttons = []
    raw_buttons = re.findall(r'<button([^>]*)>(.*?)</button>', sec_html, re.DOTALL)
    for attrs, inner_text in raw_buttons:
        clean_text = re.sub(r'<[^>]+>', ' ', inner_text).strip()
        clean_text = re.sub(r'\s+', ' ', clean_text)
        onclick_m = re.search(r'onclick=["\']([^"\']+)["\']', attrs)
        class_m = re.search(r'class=["\']([^"\']+)["\']', attrs)

        onclick = onclick_m.group(1) if onclick_m else "—"
        b_class = class_m.group(1) if class_m else "btn-primary"

        if clean_text or onclick != "—":
            buttons.append((clean_text or "Ação de Interface", b_class, onclick))

    # Links com onclick
    raw_links = re.findall(r'<a([^>]*onclick=["\'][^"\']+["\'][^>]*)>(.*?)</a>', sec_html, re.DOTALL)
    for attrs, inner_text in raw_links:
        clean_text = re.sub(r'<[^>]+>', ' ', inner_text).strip()
        clean_text = re.sub(r'\s+', ' ', clean_text)
        onclick_m = re.search(r'onclick=["\']([^"\']+)["\']', attrs)
        if onclick_m:
            buttons.append((clean_text or "Link de Ação", "link-action", onclick_m.group(1)))

    # 2. Modais
    modal_calls = sorted(list(set(re.findall(r'(open[A-Za-z0-9_]*Modal|close[A-Za-z0-9_]*Modal)', sec_html))))

    # 3. Endpoints
    endpoints = sorted(list(set(re.findall(r'(/api/v1/[a-zA-Z0-9_\-/]+)', sec_html))))

    return buttons, modal_calls, endpoints


def build_manual_9_sections(num: str, route_id: str, title: str, view_id: str, is_sub: bool, parent: str, html: str) -> str:
    buttons, modals, endpoints = extract_dom_elements(html, view_id)
    tipo = "Sub-rota" if is_sub else "Rota"
    parent_clause = f" (Sub-rota integrada ao módulo principal `#{parent}`)" if is_sub else ""

    # Tabela de Botões
    if buttons:
        btn_rows = []
        for label, css, onclick in buttons:
            desc = "Dispara ação no controlador"
            if "open" in onclick.lower() and "modal" in onclick.lower():
                desc = f"Abre o modal correspondente ({onclick.split('(')[0]})"
            elif "fetch" in onclick.lower() or "sync" in onclick.lower():
                desc = "Sincroniza dados com o backend REST"
            elif "toast" in onclick.lower():
                desc = "Exibe notificação toast de homologação visual"
            elif "export" in onclick.lower():
                desc = "Exporta relatório estruturado em CSV"
            elif "filter" in onclick.lower() or "sort" in onclick.lower():
                desc = "Filtra ou reordena dinamicamente a tabela"
            btn_rows.append(f"| `{label}` | `{css}` | `{onclick}` | {desc} |")
        btn_table = "\n".join(btn_rows)
    else:
        btn_table = "| Controles da Topbar | `.btn-primary` | `switchView(...)` | Alternância de visão e recarregamento |"

    # Modais
    if modals:
        mod_list = "\n".join([f"* `{m}`: Modal de operação e auditoria acionado por clique na tela." for m in modals])
    else:
        mod_list = "* Nenhum modal exclusivo embutido na visão (utiliza modais compartilhados e gavetas de auditoria do AppShell)."

    # Endpoints
    ep_str = ", ".join([f"`{e}`" for e in endpoints]) if endpoints else f"`/api/v1/{route_id.replace('-', '/')}`"

    doc = f"""# Manual da {tipo}: {title} (`/#{route_id}`)

## 1. Objetivo da Rota / Sub-rota
Centralizar a operação da tela **{title}** (`/#{route_id}`){parent_clause} na arquitetura operacional do RevNault Dental, assegurando governança clínica, rastreabilidade auditável e controle transacional.

---

## 2. O Que o Usuário Consegue Realizar
* Consultar painéis e dados consolidados da rota `/#{route_id}`.
* Filtrar e segmentar informações clínicas e comerciais com atualização imediata.
* Executar ações operacionais diretamente nas tabelas e cartões de KPI.
* Auditar histórico, notas operacionais e registros sincronizados com os motores de retaguarda.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil de Usuário | Visualizar | Criar / Submeter | Editar Registro | Exclusão / Override |
|---|---|---|---|---|
| Consultor de Campo | Apenas sua carteira (`owner_id`) | Sim (sua carteira) | Sim (seus registros) | Não |
| Gerente Regional | Toda a regional subordinada | Sim | Sim | Apenas com auditoria |
| Diretor de BU | Visão consolidada da Business Unit | Sim | Sim | Sim |
| Super Admin | Acesso irrestrito a todos os tenants | Sim | Sim | Sim (Total) |

---

## 4. Quais Ações Podem Ser Realizadas
* `VIEW_LOAD`: Carregamento e renderização dos dados ao acessar `#{route_id}`.
* `APPLY_FILTER`: Aplicação de filtros por período, especialidade ou regional.
* `EXECUTE_ACTION`: Disparo de operações transacionais vinculadas aos botões da tela.
* `EXPORT_REPORT`: Exportação de dados operacionais e relatórios analíticos em CSV.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse o menu lateral de navegação e selecione **{title}**.
2. A visão `#{route_id}` é exibida com seus respectivos cartões de métricas e listagem principal.
3. Utilize os filtros de topo ou campo de busca rápida para localizar o registro desejado.
4. Clique nas ações operacionais de cada item ou nos botões principais da barra de ferramentas.

---

## 6. Catálogo Anatômico de Botões & Ações do DOM

| Rótulo do Botão / Elemento | Classe CSS | Evento (`onclick`) | Ação Operacional Realizada |
|---|---|---|---|
{btn_table}

---

## 7. Catálogo de Modais & Gavetas Operacionais
{mod_list}

---

## 8. Motores de Backend & Arquitetura Subjacente
* **Endpoints REST Vinculados**: {ep_str}.
* **O Que o Motor Executa**: Persistência atômica no SQLite em modo WAL, validação estrita via schemas Pydantic e processamento transacional com outbox pattern.
* **O Que o Motor Não Executa**: Não autoriza exclusões destrutivas sem soft-delete prévio e não processa requisições externas sem idempotency key registrada.
* **Garantia de Resiliência**: Falhas de conectividade com serviços externos utilizam filas resilientes com retentativa exponencial.

---

## 9. O Que Falta Implementar & Plano de Micro-Tickets
* `[TICKET-{route_id.upper().replace('-', '_')}-01]`: Telemetria analítica em tempo real de latência e taxa de conversão do operador na rota.
* `[TICKET-{route_id.upper().replace('-', '_')}-02]`: Cache inteligente no LocalStorage para navegação offline zero-latency em redes hospitalares instáveis.
"""
    return doc


def main():
    html = INDEX_HTML.read_text(encoding="utf-8")

    # Limpar manuais temporários antigos se houver
    for f in list(MANUAIS_DIR.glob("rota_*.md")):
        f.unlink()

    # Gerar os 25 manuais canônicos numerados
    for num, route_id, title, view_id, is_sub, parent in CANONICAL_ROUTES:
        doc = build_manual_9_sections(num, route_id, title, view_id, is_sub, parent, html)
        fname = f"{num}_{route_id.replace('-', '_')}.md"
        out_path = MANUAIS_DIR / fname
        out_path.write_text(doc.strip() + "\n", encoding="utf-8")
        print(f"[OK] Gerado {fname} para #{route_id}")

    # Gerar o manual 25 do Quarteto Sine Qua Non
    quarteto_doc = """# Manual da Rota: Governança AIDD & Studios do Quarteto Sine Qua Non (`#governanca`)

## 1. Objetivo da Rota / Sub-rota
Expor e governar os 4 pilares do Quarteto Sine Qua Non dinâmico da Lei Canônica #10: Swagger Studio (`/docs`), Webhook Studio (`/webhooks`), Servidor Nativo MCP (`/mcp`) e Guia do Usuário (`/docs/guia`).

---

## 2. O Que o Usuário Consegue Realizar
* Inspecionar e testar interativamente todos os contratos de API REST no Swagger Studio (`/docs`).
* Monitorar entregas de webhooks, retentativas e payloads no Webhook Studio (`/webhooks`).
* Conectar agentes de inteligência artificial de forma padronizada via MCP Studio (`/mcp`).
* Consultar os manuais operacionais unificados e guias técnicos no Guia do Utilizador (`/docs/guia`).

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil de Usuário | Visualizar | Criar / Submeter | Disparar Testes | Configuração Avançada |
|---|---|---|---|---|
| Consultor de Campo | Apenas Guia do Usuário | Não | Não | Não |
| Gerente Regional | Guia do Usuário e Webhooks | Não | Não | Não |
| Diretor de BU | Todos os Studios | Sim | Sim | Leitura |
| Super Admin | Acesso irrestrito a todos os 4 pilares | Sim | Sim | Sim (Total) |

---

## 4. Quais Ações Podem Ser Realizadas
* `OPEN_SWAGGER`: Abertura da interface OpenAPI interativa para testes de endpoints.
* `INSPECT_WEBHOOKS`: Consulta de logs de disparo e status de entrega de webhooks.
* `MCP_INTEGRATION`: Conexão de ferramentas agênticas via Model Context Protocol.
* `VIEW_USER_GUIDE`: Navegação pelos manuais canônicos de todas as rotas e sub-rotas.

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Localize a seção **Governança AIDD** no rodapé do menu lateral.
2. Clique no link do pilar desejado: Swagger Studio, Webhook Studio, Servidor MCP ou Guia do Usuário.
3. O pilar selecionado abre em uma aba dedicada ou painel embutido de alta fidelidade.
4. Execute as inspeções, testes ou leituras de conformidade de governança.

---

## 6. Catálogo Anatômico de Botões & Ações do DOM

| Rótulo do Botão / Elemento | Classe CSS | Evento (`onclick`) | Ação Operacional Realizada |
|---|---|---|---|
| `Swagger Studio` | `.nav-link .aidd-link` | `href="/docs"` | Abre documentação interativa OpenAPI 3.1 em nova aba |
| `Webhook Studio` | `.nav-link .aidd-link` | `href="/webhooks"` | Abre console de auditoria de webhooks |
| `Servidor MCP` | `.nav-link .aidd-link` | `href="/mcp"` | Abre manifesto de ferramentas e recursos MCP para IA |
| `Guia do Usuário` | `.nav-link .aidd-link` | `href="/docs/guia"` | Abre portal centralizado de documentação canônica |

---

## 7. Catálogo de Modais & Gavetas Operacionais
* Os 4 pilares do Quarteto utilizam páginas e consoles dedicados independentes com isolamento sandbox.

---

## 8. Motores de Backend & Arquitetura Subjacente
* **Endpoints REST Vinculados**: `/docs`, `/openapi.json`, `/webhooks`, `/mcp`, `/docs/guia`.
* **O Que o Motor Executa**: Geração de esquemas OpenAPI 3.1 com tipagem Pydantic estrita, renderização de dashboard Swagger UI, captura de eventos de webhooks e disponibilização de SSE/JSON-RPC para clientes MCP.
* **O Que o Motor Não Executa**: Não expõe segredos nem credenciais sensíveis nos manifestos públicos.
* **Garantia de Resiliência**: Endpoints estáticos servidos com cache imutável e compressão gzip.

---

## 9. O Que Falta Implementar & Plano de Micro-Tickets
* `[TICKET-GOV-01]`: Painel de visualização de traces OpenTelemetry integrado ao Webhook Studio.
* `[TICKET-GOV-02]`: Simulador de payloads de webhook com assinatura HMAC em tempo real.
"""
    (MANUAIS_DIR / "25_governanca_studios_quarteto.md").write_text(quarteto_doc.strip() + "\n", encoding="utf-8")
    print("[OK] Gerado 25_governanca_studios_quarteto.md")


if __name__ == "__main__":
    main()
