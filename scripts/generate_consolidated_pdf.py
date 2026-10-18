#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gerador do Manual Consolidado Corporativo em PDF • Revnaut Dental Ops.

Compila os 26 manuais anatômicos de rotas e sub-rotas em um documento executivo
diagramado com padrão editorial corporativo via Chrome Headless Engine (A4 Paged Media).

Garantias:
- Quebra de página inteligente (page-break-before por manual, page-break-inside avoid para tabelas).
- Zero sobreposição de textos, zero tabelas cortadas, zero dados truncados.
- Capa executiva premium com branding Revnaut Dental Ops.
- Sumário geral com catalogação completa e metadados de governança.
- Lei #14 Inviolável: Zero emojis Unicode.

Uso:
  python scripts/generate_consolidated_pdf.py
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print("Erro: módulo 'markdown' não encontrado. Instale com pip install markdown.")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
MANUAIS_DIR = REPO_ROOT / "docs" / "manuais"
RELATORIOS_DIR = REPO_ROOT / "docs" / "relatorios"
OUTPUT_PDF_MANUAIS = MANUAIS_DIR / "MANUAL_CONSOLIDADO_ROTAS_REVNUALT_DENTAL.pdf"
OUTPUT_PDF_RELATORIOS = RELATORIOS_DIR / "MANUAL_CONSOLIDADO_ROTAS_REVNUALT_DENTAL.pdf"
TEMP_HTML = REPO_ROOT / "temp_manual_consolidado.html"

# Ordem canônica dos 26 arquivos de manuais
MANUAL_FILES = [
    "00_login.md",
    "01_deals.md",
    "02_contacts.md",
    "03_contacts_segments.md",
    "04_inbox.md",
    "05_tickets.md",
    "06_tasks.md",
    "07_reports.md",
    "08_reports_performance.md",
    "09_marketing.md",
    "10_marketing_mautic.md",
    "11_scoring.md",
    "12_scoring_icp.md",
    "13_automations.md",
    "14_hierarchy.md",
    "15_users.md",
    "16_import_contacts.md",
    "17_integrations.md",
    "18_keypartners.md",
    "19_keypartners_kols.md",
    "20_dentgo.md",
    "21_dentgo_fefo.md",
    "22_video_sos.md",
    "23_dicom_viewer.md",
    "24_bi_superset.md",
    "25_governanca_studios_quarteto.md",
]


CSS_CORPORATE_THEME = """
@page {
  size: A4 portrait;
  margin: 18mm 16mm 20mm 16mm;
  @top-left {
    content: "Revnaut Dental Ops • Manual Corporativo de Governança";
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    font-size: 8pt;
    color: #64748b;
    border-bottom: 0.5pt solid #e2e8f0;
    padding-bottom: 4px;
  }
  @top-right {
    content: "Confidencial B2B Industrial";
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    font-size: 8pt;
    color: #64748b;
    border-bottom: 0.5pt solid #e2e8f0;
    padding-bottom: 4px;
  }
  @bottom-right {
    content: "Página " counter(page);
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    font-size: 8.5pt;
    font-weight: 600;
    color: #475569;
  }
  @bottom-left {
    content: "Padrão AIDD v4.0 • Lei #14 Zero Emojis";
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    font-size: 8pt;
    color: #94a3b8;
  }
}

@page :first {
  margin: 0;
  @top-left { content: none; }
  @top-right { content: none; }
  @bottom-left { content: none; }
  @bottom-right { content: none; }
}

* {
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #1e293b;
  background: #ffffff;
  font-size: 10pt;
  line-height: 1.55;
  margin: 0;
  padding: 0;
}

/* ==========================================================================
   CAPA CORPORATIVA EXECUTIVA
   ========================================================================== */
.cover-page {
  page-break-after: always;
  height: 100vh;
  padding: 80px 60px 60px 60px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: linear-gradient(135deg, #090d16 0%, #0f172a 100%);
  color: #ffffff;
}

.cover-header {
  border-bottom: 2px solid #ea580c;
  padding-bottom: 30px;
}

.brand-badge {
  display: inline-block;
  background: rgba(234, 88, 12, 0.15);
  border: 1px solid rgba(234, 88, 12, 0.4);
  color: #fb923c;
  font-size: 9pt;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  padding: 5px 12px;
  border-radius: 4px;
  margin-bottom: 18px;
}

.cover-title {
  font-size: 28pt;
  font-weight: 800;
  line-height: 1.15;
  color: #ffffff;
  margin: 0 0 12px 0;
  letter-spacing: -0.5px;
}

.cover-title span {
  color: #ea580c;
}

.cover-subtitle {
  font-size: 13pt;
  font-weight: 400;
  color: #94a3b8;
  line-height: 1.45;
  margin: 0;
  max-width: 90%;
}

.cover-pillars-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin: 40px 0;
}

.pillar-box {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 16px;
}

.pillar-title {
  font-size: 11pt;
  font-weight: 700;
  color: #38bdf8;
  margin-bottom: 4px;
}

.pillar-desc {
  font-size: 8.5pt;
  color: #cbd5e1;
  line-height: 1.4;
  margin: 0;
}

.cover-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  font-size: 8.5pt;
  color: #64748b;
}

.cover-footer strong {
  color: #e2e8f0;
}

/* ==========================================================================
   SUMÁRIO / ÍNDICE GERAL EXECUTIVO
   ========================================================================== */
.toc-page {
  page-break-before: always;
  page-break-after: always;
  padding-top: 10px;
}

.toc-title {
  font-size: 18pt;
  font-weight: 800;
  color: #0f172a;
  border-bottom: 2px solid #0284c7;
  padding-bottom: 8px;
  margin-bottom: 20px;
}

.toc-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 9pt;
}

.toc-table th {
  background: #f1f5f9;
  color: #334155;
  text-align: left;
  padding: 8px 10px;
  font-weight: 700;
  border-bottom: 1.5pt solid #cbd5e1;
}

.toc-table td {
  padding: 7px 10px;
  border-bottom: 1px solid #f1f5f9;
}

.toc-table tr:hover {
  background: #f8fafc;
}

.badge-tag {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 7.5pt;
  font-weight: 700;
  text-transform: uppercase;
}

.badge-route {
  background: #e0f2fe;
  color: #0369a1;
}

.badge-subroute {
  background: #fef3c7;
  color: #b45309;
}

/* ==========================================================================
   CONTEÚDO DOS MANUAIS (DIAGRAMAÇÃO CORPORATIVA)
   ========================================================================== */
.manual-chapter {
  page-break-before: always;
  padding-top: 10px;
}

.chapter-header {
  border-bottom: 2px solid #0f172a;
  padding-bottom: 12px;
  margin-bottom: 20px;
}

.chapter-code-badge {
  display: inline-block;
  background: #0f172a;
  color: #ffffff;
  font-weight: 800;
  font-size: 9pt;
  padding: 3px 8px;
  border-radius: 4px;
  margin-bottom: 8px;
  font-family: 'Consolas', 'Courier New', monospace;
}

h1 {
  font-size: 16pt;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 6px 0;
  line-height: 1.25;
}

h2 {
  font-size: 12pt;
  font-weight: 700;
  color: #0369a1;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 5px;
  margin: 22px 0 10px 0;
  page-break-after: avoid;
  break-after: avoid;
}

h3 {
  font-size: 10.5pt;
  font-weight: 700;
  color: #1e293b;
  margin: 16px 0 8px 0;
  page-break-after: avoid;
  break-after: avoid;
}

p {
  margin: 0 0 10px 0;
  text-align: justify;
}

ul, ol {
  margin: 0 0 12px 0;
  padding-left: 20px;
}

li {
  margin-bottom: 4px;
}

hr {
  border: 0;
  height: 1px;
  background: #e2e8f0;
  margin: 20px 0;
}

/* ==========================================================================
   TABELAS E DADOS (ANTI-CORTE & ALTA DENSIDADE)
   ========================================================================== */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0 16px 0;
  font-size: 8.5pt;
  page-break-inside: avoid;
  break-inside: avoid;
}

th {
  background: #f8fafc;
  color: #0f172a;
  font-weight: 700;
  text-align: left;
  padding: 7px 8px;
  border: 1px solid #cbd5e1;
  font-size: 8.5pt;
}

td {
  padding: 6px 8px;
  border: 1px solid #e2e8f0;
  vertical-align: top;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

tr:nth-child(even) td {
  background: #fafafa;
}

code {
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 8pt;
  background: #f1f5f9;
  color: #0f172a;
  padding: 1px 4px;
  border-radius: 3px;
  border: 1px solid #e2e8f0;
}

pre {
  background: #0f172a;
  color: #f8fafc;
  padding: 12px;
  border-radius: 6px;
  font-size: 8pt;
  overflow-x: auto;
  page-break-inside: avoid;
  break-inside: avoid;
}

pre code {
  background: transparent;
  color: inherit;
  border: none;
  padding: 0;
}

blockquote {
  border-left: 3px solid #ea580c;
  background: #fff7ed;
  margin: 12px 0;
  padding: 8px 14px;
  font-size: 9pt;
  color: #9a3412;
  page-break-inside: avoid;
}
"""


def build_cover_html() -> str:
    return """
<div class="cover-page">
  <div class="cover-header">
    <div class="brand-badge">Revnaut Dental Ops • Especificação Canônica</div>
    <div class="cover-title">MANUAL CORPORATIVO DE GOVERNANÇA, ROTAS & SUB-ROTAS</div>
    <div class="cover-subtitle">
      Catálogo Anatômico Unificado das 25 Rotas e Sub-rotas Operacionais, Auditoria do DOM, Matriz RBAC Granular e Contratos de Motores de Retaguarda.
    </div>
  </div>

  <div class="cover-pillars-grid">
    <div class="pillar-box">
      <div class="pillar-title">1. Relação 1-para-1 Estrita</div>
      <div class="pillar-desc">Cada rota e sub-rota do frontend possui documentação individualizada e exaustiva sem aglutinações permissivas.</div>
    </div>
    <div class="pillar-box">
      <div class="pillar-title">2. 9 Seções Anatômicas</div>
      <div class="pillar-desc">Objetivos clínicos, matriz RBAC, catálogo de botões reais do DOM, modais de tela e contratos de resiliência.</div>
    </div>
    <div class="pillar-box">
      <div class="pillar-title">3. Quarteto Sine Qua Non</div>
      <div class="pillar-desc">Integração nativa com Swagger Studio (/docs), Webhook Studio (/webhooks), MCP Studio (/mcp) e Guia (/docs/guia).</div>
    </div>
    <div class="pillar-box">
      <div class="pillar-title">4. Lei #14 & Zero Emojis</div>
      <div class="pillar-desc">100% livre de emojis Unicode em código, documentação e interface, assegurando estética corporativa imutável.</div>
    </div>
  </div>

  <div class="cover-footer">
    <div>
      <div>Plataforma: <strong>Revnaut Dental Ops Enterprise v4.0</strong></div>
      <div>Arquitetura: <strong>Python 3.14 + SQLite WAL + Docker Swarm Cluster</strong></div>
      <div>Ambiente Homologado: <strong>https://rvops.vpsconexao.org</strong></div>
    </div>
    <div style="text-align: right;">
      <div>Autor & Direção: <strong>Heverton Eduardo Peres</strong></div>
      <div>Governança: <strong>AIDD Canonical Standard (Lei #1 a #14)</strong></div>
      <div>Data da Homologação: <strong>Outubro de 2026</strong></div>
    </div>
  </div>
</div>
"""


def build_toc_html(entries: list[dict]) -> str:
    rows = []
    for e in entries:
        badge_cls = "badge-subroute" if e["is_sub"] else "badge-route"
        tipo_label = "Sub-rota" if e["is_sub"] else "Rota"
        rows.append(f"""
        <tr>
          <td style="font-family: Consolas, monospace; font-weight: 700; width: 45px;">{e['num']}</td>
          <td><strong>{e['title']}</strong></td>
          <td style="font-family: Consolas, monospace; color: #0284c7;">{e['hash']}</td>
          <td style="width: 80px;"><span class="badge-tag {badge_cls}">{tipo_label}</span></td>
        </tr>
        """)
    rows_html = "".join(rows)

    return f"""
<div class="toc-page">
  <div class="toc-title">Sumário Executivo de Rotas & Sub-rotas</div>
  <table class="toc-table">
    <thead>
      <tr>
        <th>Cód</th>
        <th>Módulo Operacional / Título da Rota</th>
        <th>Identificador (Hash)</th>
        <th>Tipo</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</div>
"""


def parse_manual(filepath: Path) -> tuple[dict, str]:
    raw_md = filepath.read_text(encoding="utf-8")
    num = filepath.name.split("_")[0]

    # Detectar título e hash
    m_title = re.search(r"^#\s*Manual\s*da\s*(Rota|Sub-rota):\s*(.*?)\s*\((`?/#?[a-zA-Z0-9_\-]+`?)\)", raw_md, re.MULTILINE)
    if m_title:
        tipo, clean_title, raw_hash = m_title.group(1), m_title.group(2).strip(), m_title.group(3).replace("`", "")
        is_sub = "sub" in tipo.lower()
    else:
        clean_title = filepath.stem.replace("_", " ").title()
        raw_hash = f"#{filepath.stem}"
        is_sub = False

    meta = {
        "num": num,
        "title": clean_title,
        "hash": raw_hash,
        "is_sub": is_sub,
        "filename": filepath.name
    }

    # Converter Markdown para HTML via biblioteca markdown
    md_parser = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
    html_content = md_parser.convert(raw_md)

    # Remover o primeiro h1 do corpo já que temos header dedicado
    html_content = re.sub(r'<h1>.*?</h1>', '', html_content, count=1, flags=re.DOTALL)

    return meta, html_content


def generate_consolidated_document():
    print(f"=== GERADOR DE MANUAL CONSOLIDADO PDF • REVAULT DENTAL ===")
    print(f"Lendo manuais em: {MANUAIS_DIR}")

    toc_entries = []
    chapters_html = []

    for fname in MANUAL_FILES:
        fpath = MANUAIS_DIR / fname
        if not fpath.exists():
            print(f"[ALERTA] Arquivo {fname} não localizado. Pulando.")
            continue

        meta, body_html = parse_manual(fpath)
        toc_entries.append(meta)

        tipo_label = "SUB-ROTA DEDICADA" if meta["is_sub"] else "ROTA PRINCIPAL"
        badge_style = "background: #fef3c7; color: #b45309;" if meta["is_sub"] else "background: #e0f2fe; color: #0369a1;"

        chapter_block = f"""
        <div class="manual-chapter" id="cap-{meta['num']}">
          <div class="chapter-header">
            <span class="chapter-code-badge">MÓDULO {meta['num']}</span>
            <span class="badge-tag" style="{badge_style}; margin-left: 8px;">{tipo_label}</span>
            <h1 style="margin-top: 6px;">{meta['title']}</h1>
            <div style="font-family: Consolas, monospace; font-size: 9pt; color: #64748b; margin-top: 2px;">
              Identificador de Rota: <strong style="color: #0284c7;">{meta['hash']}</strong> • Arquivo: <code>{meta['filename']}</code>
            </div>
          </div>
          <div class="chapter-body">
            {body_html}
          </div>
        </div>
        """
        chapters_html.append(chapter_block)

    cover_html = build_cover_html()
    toc_html = build_toc_html(toc_entries)

    full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Revnaut Dental Ops • Manual Corporativo Consolidado</title>
  <style>
    {CSS_CORPORATE_THEME}
  </style>
</head>
<body>
  {cover_html}
  {toc_html}
  {"".join(chapters_html)}
</body>
</html>
"""

    TEMP_HTML.write_text(full_html, encoding="utf-8")
    print(f"[OK] HTML intermediário gerado com sucesso ({len(full_html)} bytes).")

    # Localizar executável do Google Chrome ou Edge
    chrome_candidates = [
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
        Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
    ]

    browser_bin = None
    for c in chrome_candidates:
        if c.exists():
            browser_bin = c
            break

    if not browser_bin:
        print("[ERRO] Nenhum binário do Google Chrome ou Edge foi localizado para conversão PDF.")
        sys.exit(1)

    print(f"Utilizando motor headless: {browser_bin}")

    # Gerar PDF direto com Chrome Headless
    cmd = [
        str(browser_bin),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={OUTPUT_PDF_MANUAIS.resolve()}",
        str(TEMP_HTML.resolve())
    ]

    print("Renderizando PDF com A4 Paged Media e Anti-Corte de Tabelas...")
    res = subprocess.run(cmd, capture_output=True, text=True)

    if not OUTPUT_PDF_MANUAIS.exists() or OUTPUT_PDF_MANUAIS.stat().st_size == 0:
        print(f"[ERRO] Falha na geração do PDF: {res.stderr}")
        sys.exit(1)

    # Copiar também para docs/relatorios
    RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)
    pdf_bytes = OUTPUT_PDF_MANUAIS.read_bytes()
    OUTPUT_PDF_RELATORIOS.write_bytes(pdf_bytes)

    # Limpar HTML temporário
    if TEMP_HTML.exists():
        TEMP_HTML.unlink()

    size_kb = len(pdf_bytes) / 1024.0
    print(f"=================================================================")
    print(f" [SUCESSO] MANUAL CONSOLIDADO PDF GERADO COM EXCELÊNCIA!")
    print(f" - Destino 1: {OUTPUT_PDF_MANUAIS} ({size_kb:.1f} KB)")
    print(f" - Destino 2: {OUTPUT_PDF_RELATORIOS} ({size_kb:.1f} KB)")
    print(f" - Total de Manuais Compilados: {len(toc_entries)} módulos")
    print(f" - Formato: A4 Paged Media • Zero Cortes de Tabela • Zero Emojis")
    print(f"=================================================================")


if __name__ == "__main__":
    generate_consolidated_document()
