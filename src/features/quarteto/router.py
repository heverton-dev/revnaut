# -*- coding: utf-8 -*-
"""
Vertical Slice: Quarteto Sine Qua Non Dinâmico (Lei #10)
- MCP Studio (/mcp)
- User Guide (/docs/guia)
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from src.features.deals.schemas import DealCreate, DealMove

router = APIRouter(tags=["Quarteto Sine Qua Non"])


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
                "name": "revnaut_metricas",
                "description": "Obtém métricas em tempo real de MRR e pipeline",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "revnaut_consultar_consignado",
                "description": "Consulta caixas cirúrgicas consignadas, saldos e lotes ANVISA em clínicas",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "consignment_id": {"type": "string", "description": "ID da caixa consignada (ex: csg_neodent_01)"}
                    }
                }
            },
            {
                "name": "revnaut_registrar_baixa_cirurgica",
                "description": "Registra consumo cirúrgico de implante/componente em caixa consignada",
                "parameters": {
                    "type": "object",
                    "required": ["consignment_id", "product_sku", "quantity"],
                    "properties": {
                        "consignment_id": {"type": "string", "description": "ID da caixa consignada"},
                        "product_sku": {"type": "string", "description": "Código SKU do produto consumido"},
                        "quantity": {"type": "integer", "description": "Quantidade consumida na cirurgia"},
                        "patient_ref": {"type": "string", "description": "Referência ou prontuário do paciente"},
                        "dentist_cro": {"type": "string", "description": "CRO do cirurgião responsável"}
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


@router.get("/docs/guia", response_class=HTMLResponse, summary="Guia do Usuário")
def user_guide():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
      <title>Revnaut Dental Ops • Guia do Usuário</title>
      <link rel="icon" type="image/svg+xml" href="/favicon.svg">
      <link rel="alternate icon" href="/favicon.ico">
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; scrollbar-width: thin; scrollbar-color: rgba(255, 255, 255, 0.14) transparent; }
        *::-webkit-scrollbar { width: 5px; height: 5px; }
        *::-webkit-scrollbar-track { background: transparent; }
        *::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.12); border-radius: 9999px; }
        *::-webkit-scrollbar-thumb:hover { background: rgba(255, 115, 0, 0.45); }
        body { font-family: 'Inter', -apple-system, sans-serif; line-height: 1.6; max-width: 880px; margin: 40px auto; padding: 0 24px; background: #08090d; color: #f8fafc; }
        h1, h2, h3 { color: #ffffff; }
        h1 { border-bottom: 2px solid #ff7300; padding-bottom: 14px; font-size: 24px; font-weight: 700; margin-bottom: 20px; }
        h2 { font-size: 17px; font-weight: 600; margin-top: 28px; margin-bottom: 10px; color: #ff8c24; }
        p { color: #94a3b8; font-size: 14px; margin-bottom: 14px; }
        .alert { background: rgba(255, 115, 0, 0.08); border-left: 4px solid #ff7300; padding: 14px 18px; margin: 24px 0; border-radius: 6px; color: #f8fafc; font-size: 13.5px; }
        code { background: #131722; border: 1px solid rgba(255,255,255,0.08); padding: 3px 7px; border-radius: 4px; font-family: monospace; color: #38bdf8; font-size: 13px; }
        a { color: #ff7300; font-weight: 600; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .top-nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 16px; }
        .btn { background: #181d2b; color: #f8fafc; border: 1px solid rgba(255,255,255,0.08); padding: 7px 14px; border-radius: 6px; font-size: 13px; font-weight: 500; }
      </style>
    </head>
    <body>
      <div class="top-nav">
        <span style="font-size: 13px; color: #64748b;">Governança AIDD • Pilar IV • Dental Industry Edition</span>
        <a href="/" class="btn">Voltar à Plataforma</a>
      </div>

      <h1>Guia Operacional — Revnaut Dental Ops</h1>
      <p>Manual operacional e de governança técnica para indústrias odontológicas, consultores cirúrgicos, distribuidores e coordenadores acadêmicos.</p>
      
      <div class="alert">
        <strong>Padrão Quarteto Sine Qua Non:</strong> Esta documentação viva reflete diretamente os contratos de produção em SQLite WAL, rastreabilidade ANVISA e OpenAPI 3.1.
      </div>

      <h2>1. Gestão de Consignações & Baixa Cirúrgica</h2>
      <p>O módulo de Consignação rastreia caixas cirúrgicas e gaveteiros instalados em hospitais e clínicas parceiras. Cada consumo cirúrgico efetuado atualiza o saldo físico, dispara faturamento automático e emite ordem de reposição do lote consumido.</p>

      <h2>2. Instituições de Ensino & Kits Acadêmicos</h2>
      <p>Gerencie parcerias com faculdades de odontologia (Ex: São Leopoldo Mandic, ABO, APCD). Acompanhe turmas de especialização em implantodontia e prótese, contratos de kits cirúrgicos e alinhamento com professores KOLs.</p>

      <h2>3. Funis de Vendas Especializados</h2>
      <p>Os pipelines atendem 4 frentes: <em>Cirurgiões & Venda Direta / Consignação</em>, <em>Instituições de Ensino & Kits Acadêmicos</em>, <em>Distribuidores & Contratos Atacado</em> e <em>Key Opinion Leaders (KOLs) & CIOSP</em>.</p>

      <h2>4. Automações e Webhooks</h2>
      <p>Acesse o <a href="/webhooks">Webhook Studio</a> para gerenciar eventos externos ou integre seus agentes cirúrgicos de IA utilizando as ferramentas expostas no <a href="/mcp">MCP Studio</a>.</p>

      <h2>5. Referência de APIs</h2>
      <p>A documentação técnica detalhada dos endpoints está acessível no <a href="/docs">Swagger Studio</a>.</p>
    </body>
    </html>
    """

