# -*- coding: utf-8 -*-
"""
Vertical Slice: Quarteto Sine Qua Non Dinâmico (Lei #10)
- MCP Studio (/mcp)
- User Guide (/docs/guia) sincronizado com docs/manuais/
"""

import os
from pathlib import Path
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from src.features.deals.schemas import DealCreate, DealMove

router = APIRouter(tags=["Quarteto Sine Qua Non"])

MANUAIS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "manuais"


@router.get("/mcp", summary="MCP Studio (Servidor de Ferramentas de IA)")
def mcp_studio():
    return {
        "mcp_version": "1.0.0",
        "server_name": "revnaut-mcp-studio",
        "description": "Ferramentas executáveis nativas para o ecossistema Revnaut",
        "tools": [
            {
                "name": "revnaut_criar_deal",
                "description": "Cria um novo negócio na pipeline",
                "parameters": DealCreate.model_json_schema()
            },
            {
                "name": "revnaut_mover_deal",
                "description": "Move o negócio de estágio no funil",
                "parameters": DealMove.model_json_schema()
            },
            {
                "name": "revnaut_buscar_contatos",
                "description": "Busca contatos e leads por termo chave",
                "parameters": {
                    "type": "object",
                    "properties": {"q": {"type": "string", "description": "Termo de busca"}}
                }
            },
            {
                "name": "revnaut_detalhes_contato",
                "description": "Obtém histórico e detalhes clínicos de um cirurgião ou clínica",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "contact_id": {"type": "integer", "description": "ID do contato"},
                        "cro": {"type": "string", "description": "Número do CRO com UF"}
                    }
                }
            },
            {
                "name": "revnaut_listar_instituicoes",
                "description": "Lista instituições de ensino credenciadas (Mandic, ABO, APCD) e status de kits acadêmicos",
                "parameters": {"type": "object", "properties": {}}
            }
        ]
    }


from pydantic import BaseModel

class ManualItem(BaseModel):
    filename: str
    title: str
    path: str

class ManualsListResponse(BaseModel):
    total: int
    manuals: list[ManualItem]

class ManualContentResponse(BaseModel):
    filename: str
    content: str


@router.get("/api/v1/quarteto/manuais", response_model=ManualsListResponse, summary="Catálogo de Manuais de Rotas (JSON)")
def list_manuals():
    """Retorna lista de manuais disponíveis e seus conteúdos para consumo por agentes e IAs."""
    if not MANUAIS_DIR.exists():
        return {"total": 0, "manuals": []}

    files = sorted(list(MANUAIS_DIR.glob("*.md")))
    result = []
    for f in files:
        result.append({
            "filename": f.name,
            "title": f.stem.replace("_", " ").title(),
            "path": str(f.relative_to(MANUAIS_DIR.parent.parent)).replace("\\", "/")
        })
    return {"total": len(result), "manuals": result}


@router.get("/api/v1/quarteto/manuais/{filename}", response_model=ManualContentResponse, summary="Obter Conteúdo do Manual")
def get_manual_content(filename: str):
    """Retorna o texto markdown do manual especificado."""
    # Sanitização básica de caminho
    safe_name = os.path.basename(filename)
    file_path = MANUAIS_DIR / safe_name
    if not file_path.exists() or not safe_name.endswith(".md"):
        raise HTTPException(status_code=404, detail="Manual não encontrado.")
    return {
        "filename": safe_name,
        "content": file_path.read_text(encoding="utf-8")
    }



@router.get("/docs/guia", response_class=HTMLResponse, summary="Guia do Usuário Dinâmico")
def user_guide(manual: str = Query("README.md", description="Nome do arquivo manual a ser exibido")):
    safe_name = os.path.basename(manual)
    target_file = MANUAIS_DIR / safe_name
    if not target_file.exists() or not safe_name.endswith(".md"):
        target_file = MANUAIS_DIR / "README.md"
        safe_name = "README.md"

    # Ler lista de manuais para menu lateral
    manual_files = []
    if MANUAIS_DIR.exists():
        for f in sorted(list(MANUAIS_DIR.glob("*.md"))):
            name_clean = f.stem.replace("_", " ")
            manual_files.append((f.name, name_clean))

    nav_items_html = ""
    for f_name, f_title in manual_files:
        is_active = (f_name == safe_name)
        active_class = "active" if is_active else ""
        nav_items_html += f'<a href="/docs/guia?manual={f_name}" class="nav-item {active_class}">{f_title}</a>\\n'

    content_markdown = target_file.read_text(encoding="utf-8") if target_file.exists() else "# Manual não encontrado"

    # Escapar para injeção segura no script JS
    escaped_markdown = content_markdown.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Revnaut Dental Ops • Central de Manuais & Guia Operacional</title>
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="alternate icon" href="/favicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', -apple-system, sans-serif;
      background: #080a0f;
      color: #f1f5f9;
      display: flex;
      height: 100vh;
      overflow: hidden;
    }}
    /* Barra Lateral de Manuais */
    .sidebar {{
      width: 320px;
      background: #0c0f17;
      border-right: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }}
    .sidebar-header {{
      padding: 20px 18px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      background: rgba(0, 0, 0, 0.2);
    }}
    .brand-title {{
      font-size: 15px;
      font-weight: 700;
      color: #ffffff;
      letter-spacing: -0.3px;
    }}
    .brand-sub {{
      font-size: 11.5px;
      color: #94a3b8;
      margin-top: 2px;
    }}
    .search-box {{
      margin-top: 14px;
      position: relative;
    }}
    .search-input {{
      width: 100%;
      background: #141824;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 6px;
      padding: 8px 12px;
      color: white;
      font-size: 12.5px;
      outline: none;
    }}
    .nav-list {{
      flex: 1;
      overflow-y: auto;
      padding: 12px 8px;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}
    .nav-item {{
      display: block;
      padding: 9px 12px;
      border-radius: 6px;
      color: #94a3b8;
      text-decoration: none;
      font-size: 12.5px;
      font-weight: 500;
      transition: all 0.15s ease;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .nav-item:hover {{
      background: rgba(255, 255, 255, 0.04);
      color: #ffffff;
    }}
    .nav-item.active {{
      background: rgba(255, 115, 0, 0.12);
      color: #ff9e42;
      font-weight: 600;
      border-left: 3px solid #ff7300;
    }}
    .sidebar-footer {{
      padding: 14px 18px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      background: rgba(0,0,0,0.25);
      font-size: 11px;
      color: #64748b;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .sidebar-footer a {{
      color: #ff7300;
      text-decoration: none;
      font-weight: 600;
    }}

    /* Área Principal de Leitura */
    .content-area {{
      flex: 1;
      display: flex;
      flex-direction: column;
      background: #080a0f;
      overflow: hidden;
    }}
    .topbar {{
      height: 58px;
      padding: 0 32px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #0c0f17;
      flex-shrink: 0;
    }}
    .topbar-left {{
      font-size: 13px;
      color: #94a3b8;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .topbar-badge {{
      background: rgba(52, 211, 153, 0.15);
      color: #34d399;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
    }}
    .btn-back {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: white;
      text-decoration: none;
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 12.5px;
      font-weight: 600;
      transition: background 0.15s;
    }}
    .btn-back:hover {{
      background: rgba(255, 255, 255, 0.12);
    }}
    .doc-viewer {{
      flex: 1;
      overflow-y: auto;
      padding: 40px 60px;
      max-width: 960px;
      margin: 0 auto;
      width: 100%;
      line-height: 1.7;
    }}
    .doc-viewer h1 {{
      font-size: 26px;
      font-weight: 700;
      color: white;
      border-bottom: 2px solid #ff7300;
      padding-bottom: 14px;
      margin-bottom: 24px;
    }}
    .doc-viewer h2 {{
      font-size: 18px;
      font-weight: 600;
      color: #ff9e42;
      margin-top: 36px;
      margin-bottom: 14px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      padding-bottom: 8px;
    }}
    .doc-viewer h3 {{
      font-size: 15px;
      font-weight: 600;
      color: white;
      margin-top: 20px;
      margin-bottom: 10px;
    }}
    .doc-viewer p {{
      color: #94a3b8;
      font-size: 14px;
      margin-bottom: 16px;
    }}
    .doc-viewer ul, .doc-viewer ol {{
      margin-left: 20px;
      margin-bottom: 18px;
      color: #cbd5e1;
      font-size: 14px;
    }}
    .doc-viewer li {{
      margin-bottom: 6px;
    }}
    .doc-viewer table {{
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      background: #0f131d;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 6px;
      overflow: hidden;
      font-size: 13px;
    }}
    .doc-viewer th {{
      background: #141824;
      padding: 10px 14px;
      text-align: left;
      font-weight: 600;
      color: #cbd5e1;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }}
    .doc-viewer td {{
      padding: 10px 14px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      color: #94a3b8;
    }}
    .doc-viewer code {{
      font-family: 'JetBrains Mono', monospace;
      background: #141824;
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 2px 6px;
      border-radius: 4px;
      color: #38bdf8;
      font-size: 12.5px;
    }}
    .doc-viewer pre {{
      background: #0f131d;
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 16px;
      border-radius: 8px;
      overflow-x: auto;
      margin: 18px 0;
    }}
    .doc-viewer pre code {{
      background: none;
      border: none;
      padding: 0;
      color: #e2e8f0;
    }}
    .doc-viewer blockquote {{
      background: rgba(255, 115, 0, 0.06);
      border-left: 4px solid #ff7300;
      padding: 12px 18px;
      border-radius: 4px;
      margin: 18px 0;
      color: #f1f5f9;
      font-size: 13.5px;
    }}
  </style>
</head>
<body>
  <!-- Menu Lateral de Manuais -->
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="brand-title">Revnaut Dental Ops</div>
      <div class="brand-sub">Pilar IV • Central Viva de Manuais</div>
      <div class="search-box">
        <input type="text" class="search-input" id="search-manuals" placeholder="Filtrar manual..." oninput="filterManuals(this.value)">
      </div>
    </div>
    <nav class="nav-list" id="manuals-list">
      {nav_items_html}
    </nav>
    <div class="sidebar-footer">
      <span>Governança AIDD</span>
      <a href="/docs">Swagger Studio</a>
    </div>
  </aside>

  <!-- Área Principal de Leitura -->
  <main class="content-area">
    <header class="topbar">
      <div class="topbar-left">
        <span>Visualizando:</span>
        <strong style="color: white;">{safe_name}</strong>
        <span class="topbar-badge">SSOT Sincronizado</span>
      </div>
      <a href="/" class="btn-back">Voltar à Plataforma</a>
    </header>

    <div class="doc-viewer" id="markdown-container">
      <!-- Renderizado dinamicamente via marked.js -->
    </div>
  </main>

  <script>
    const rawMarkdown = `{escaped_markdown}`;
    document.getElementById('markdown-container').innerHTML = marked.parse(rawMarkdown);

    function filterManuals(query) {{
      const q = (query || '').toLowerCase().trim();
      document.querySelectorAll('.nav-item').forEach(el => {{
        const text = el.textContent.toLowerCase();
        el.style.display = text.includes(q) ? 'block' : 'none';
      }});
    }}
  </script>
</body>
</html>"""
