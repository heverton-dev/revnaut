#!/usr/bin/env python3
"""
Compilador Corporativo de PDF para aidd-route-analyze.
Unifica os 8 artefatos Markdown do dossie em um documento diagramado em PDF via Playwright Chromium.
Garante conformidade com Lei #14 (Zero Emojis), tipografia refinada e layout editorial A4.
"""
import sys
import json
from pathlib import Path
import markdown
from playwright.sync_api import sync_playwright

ORDERED_FILES = [
    "RELATORIO_CONSOLIDADO.md",
    "01_visao_geral_e_jornada.md",
    "02_ui_ux_impeccable.md",
    "08_botoes_modais_e_acoes.md",
    "03_motores_e_subprodutizacao.md",
    "04_cyber_seguranca_e_rls.md",
    "05_arquitetura_e_engenharia.md",
    "06_especificacao_dd.md",
    "07_plano_micro_tickets.md"
]

CSS_THEME = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

@page {
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #0f172a;
    background: #ffffff;
    line-height: 1.6;
    font-size: 10pt;
    margin: 0;
    padding: 0;
}

.cover-page {
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 100vh;
    padding: 40px 20px;
    box-sizing: border-box;
}

.cover-badge {
    display: inline-block;
    background: #f1f5f9;
    color: #475569;
    font-size: 9pt;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 6px 14px;
    border-radius: 4px;
    border-left: 3px solid #0284c7;
    margin-bottom: 24px;
    width: fit-content;
}

.cover-title {
    font-size: 28pt;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.2;
    margin: 0 0 12px 0;
}

.cover-subtitle {
    font-size: 14pt;
    font-weight: 400;
    color: #64748b;
    margin: 0 0 40px 0;
}

.cover-meta {
    border-top: 1px solid #e2e8f0;
    padding-top: 24px;
    margin-top: auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    font-size: 9pt;
    color: #64748b;
}

.cover-meta strong {
    color: #1e293b;
}

.section-page {
    page-break-before: always;
    padding-top: 10px;
}

h1 {
    font-size: 16pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 8px;
    margin-top: 24px;
    margin-bottom: 16px;
}

h2 {
    font-size: 13pt;
    font-weight: 600;
    color: #1e293b;
    margin-top: 20px;
    margin-bottom: 10px;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 4px;
}

h3 {
    font-size: 11pt;
    font-weight: 600;
    color: #334155;
    margin-top: 16px;
    margin-bottom: 8px;
}

p, ul, ol {
    margin-top: 0;
    margin-bottom: 12px;
}

ul, ol {
    padding-left: 20px;
}

li {
    margin-bottom: 4px;
}

code {
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 8.5pt;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 2px 5px;
    border-radius: 3px;
    color: #0f172a;
}

pre {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #0284c7;
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 8.5pt;
    line-height: 1.45;
    margin-bottom: 16px;
}

pre code {
    background: transparent;
    border: none;
    padding: 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
    font-size: 8.5pt;
}

th, td {
    border: 1px solid #e2e8f0;
    padding: 8px 10px;
    text-align: left;
}

th {
    background: #f8fafc;
    color: #334155;
    font-weight: 600;
}

tr:nth-child(even) td {
    background: #fafafa;
}

blockquote {
    border-left: 3px solid #0284c7;
    background: #f0f9ff;
    padding: 8px 14px;
    margin: 12px 0;
    border-radius: 0 4px 4px 0;
    font-size: 9pt;
    color: #0369a1;
}

hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 24px 0;
}
"""

def compile_pdf(slug: str) -> Path:
    target_dir = Path("docs/auditorias_rotas") / slug
    if not target_dir.exists():
        print(f"[FAIL] Diretorio do dossie {target_dir} inexistente.")
        sys.exit(1)

    state_file = Path(".state/route_dispatch.json")
    raw_target = slug
    route_type = "spa_view"
    if state_file.exists():
        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
            raw_target = data.get("raw_target", slug)
            route_type = data.get("route_type", route_type)
        except Exception:
            pass

    # Montar corpo dos documentos em HTML
    sections_html = []
    
    # 1. Capa Corporativa
    cover_html = f"""
    <div class="cover-page">
        <div class="cover-badge">AIDD Governance &middot; Route Audit Dossier</div>
        <div class="cover-title">Relatório de Auditoria Arquitetural & UI/UX</div>
        <div class="cover-subtitle">Inspeção Profunda da Rota: <code>{slug}</code></div>
        <div class="cover-meta">
            <div>
                <strong>Alvo Original:</strong><br>{raw_target}<br><br>
                <strong>Classificação:</strong><br>{route_type.upper()}
            </div>
            <div>
                <strong>Padrão de Governança:</strong><br>AIDD Canary v4.0 (Zero Stubs / Zero Emojis)<br><br>
                <strong>Emitido por:</strong><br>Orquestrador Filarmônico <code>aidd-route-analyze</code>
            </div>
        </div>
    </div>
    """
    sections_html.append(cover_html)

    # 2. Renderizar cada arquivo Markdown
    md_parser = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists"])
    for fname in ORDERED_FILES:
        fpath = target_dir / fname
        if fpath.exists():
            raw_md = fpath.read_text(encoding="utf-8", errors="ignore")
            converted = md_parser.convert(raw_md)
            sections_html.append(f'<div class="section-page">{converted}</div>')
            md_parser.reset()

    complete_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Auditoria Canônica — {slug}</title>
    <style>{CSS_THEME}</style>
</head>
<body>
    {''.join(sections_html)}
</body>
</html>
"""

    # Gravar HTML temporario para inspecao/render
    temp_html_path = target_dir / "compilado.html"
    temp_html_path.write_text(complete_html, encoding="utf-8")

    pdf_output_path = target_dir / f"RELATORIO_AUDITORIA_{slug}.pdf"

    print(f"[*] Renderizando PDF com Playwright Chromium...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(complete_html, wait_until="networkidle")
        page.pdf(
            path=str(pdf_output_path),
            format="A4",
            print_background=True,
            margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"},
            display_header_footer=True,
            header_template='<div style="font-size: 8pt; font-family: Inter, sans-serif; color: #94a3b8; width: 100%; text-align: right; padding-right: 15mm;">AIDD Route Audit Dossier</div>',
            footer_template='<div style="font-size: 8pt; font-family: Inter, sans-serif; color: #94a3b8; width: 100%; display: flex; justify-content: space-between; padding-left: 15mm; padding-right: 15mm;"><span>Confidencial &middot; Uso Interno</span><span>Página <span class="pageNumber"></span> de <span class="totalPages"></span></span></div>'
        )
        browser.close()

    print(f"[SUCCESS] PDF Corporativo gerado com sucesso em: {pdf_output_path}")
    return pdf_output_path

def main():
    slug_arg = sys.argv[1] if len(sys.argv) > 1 else None
    if not slug_arg:
        state_file = Path(".state/route_dispatch.json")
        if state_file.exists():
            slug_arg = json.loads(state_file.read_text(encoding="utf-8")).get("slug")

    if not slug_arg:
        print("[FAIL] Informe o slug da rota para compilar o PDF.")
        sys.exit(1)

    compile_pdf(slug_arg)

if __name__ == "__main__":
    main()
