# -*- coding: utf-8 -*-
"""
Automated Test Suite — Real Tests, Zero Mocks (Lei #5, Lei #8, Lei #13)
Valida a camada de tráfego, persistência SQLite WAL e Quarteto Sine Qua Non Dinâmico.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db, get_connection

init_db()
client = TestClient(app)


def test_health_and_sqlite_wal():
    """Testa se o SQLite opera nativamente em modo WAL."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["sqlite_journal_mode"] == "wal"
    assert data["accounts_online"] >= 1


def test_metrics_endpoint():
    """Testa retorno das métricas de receita."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "mrr" in data
    assert "pipelineTotal" in data
    assert data["pipelineTotal"] > 0


def test_pipeline_and_deals():
    """Testa listagem de estágios da pipeline com totalizadores."""
    response = client.get("/api/v1/deals")
    assert response.status_code == 200
    data = response.json()
    assert "stages" in data
    assert len(data["stages"]) == 5
    assert data["stages"][0]["name"] == "Qualificação & SDR"


def test_create_and_move_deal():
    """Testa fluxo completo de inserção e movimentação de deal."""
    new_deal = {
        "title": "Licença Piloto - Indústria X",
        "value": 45000.0,
        "company": "Indústria X S/A",
        "contact_name": "Marcos Vieira",
        "stage_id": 101,
        "priority": "alta"
    }
    create_res = client.post("/api/v1/deals", json=new_deal)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["status"] == "created"
    deal_id = created_data["id"]

    # Mover deal para estágio 103 (Proposta Comercial)
    move_res = client.put(f"/api/v1/deals/{deal_id}/stage", json={"stage_id": 103})
    assert move_res.status_code == 200
    move_data = move_res.json()
    assert move_data["new_stage_id"] == 103


def test_contacts_search():
    """Testa busca debounced de contatos."""
    response = client.get("/api/v1/contacts?q=AgroTech")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "AgroTech Brasil" in data[0]["company"]


def test_send_chat_message():
    """Testa envio de mensagem no chat omnichannel."""
    msg_payload = {"text": "Mensagem de teste automatizado via pytest."}
    response = client.post("/api/v1/conversations/chat-1/messages", json=msg_payload)
    assert response.status_code == 201
    assert response.json()["status"] == "sent"


# =============================================================================
# TESTES DO QUARTETO SINE QUA NON DINÂMICO (Lei #10)
# =============================================================================

def test_quarteto_swagger_studio():
    """Pilar I: Swagger Studio (/docs e /openapi.json)."""
    res_docs = client.get("/docs")
    assert res_docs.status_code == 200

    res_openapi = client.get("/openapi.json")
    assert res_openapi.status_code == 200
    schema = res_openapi.json()
    assert schema["info"]["title"] == "Revnaut Enterprise API & Engine"


def test_quarteto_webhook_studio():
    """Pilar II: Webhook Studio (/webhooks)."""
    response = client.get("/webhooks")
    assert response.status_code == 200
    assert "Webhook Studio" in response.text
    assert "Webhooks Configurados" in response.text


def test_quarteto_mcp_studio():
    """Pilar III: MCP Studio (/mcp)."""
    response = client.get("/mcp")
    assert response.status_code == 200
    data = response.json()
    assert data["server_name"] == "revnaut-mcp-studio"
    assert len(data["tools"]) >= 4
    tool_names = [t["name"] for t in data["tools"]]
    assert "revnaut_criar_deal" in tool_names


def test_quarteto_user_guide():
    """Pilar IV: User Guide (/docs/guia)."""
    response = client.get("/docs/guia")
    assert response.status_code == 200
    assert "Guia" in response.text
    assert "Dental Ops" in response.text or "Revenue Operations" in response.text



# =============================================================================
# TESTE DA LEI #13: PORTÃO DEVE PROVAR QUE MORDE
# =============================================================================

def test_gate_morde_invalid_deal_id():
    """Prova que a API rejeita inputs inválidos com erro 404 (morde)."""
    response = client.put("/api/v1/deals/id-inexistente-xyz/stage", json={"stage_id": 105})
    assert response.status_code == 404
    assert response.json()["detail"] == "Negócio não encontrado."


def test_frontend_and_assets_delivery():
    """Verifica entrega do frontend raiz e assets CSS/JS."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "Revnaut Dental Ops" in res_root.text or "Revnaut" in res_root.text


    res_css = client.get("/css/tokens.css")
    assert res_css.status_code == 200
    assert "--color-brand-primary" in res_css.text

    res_js = client.get("/js/app.js")
    assert res_js.status_code == 200
    assert "window.RVOPS_DATA" in res_js.text


def test_tickets_api_crud():
    """Testa listagem, criação e atualização de tickets."""
    # Listagem
    res = client.get("/api/v1/tickets")
    assert res.status_code == 200
    tickets = res.json()
    assert len(tickets) >= 4

    # Criação
    new_ticket = {
        "title": "Falha na sincronização de contatos Mautic",
        "customer_name": "Empresa Teste SA",
        "priority": "alta",
        "category": "Integração",
        "status": "aberto"
    }
    res_create = client.post("/api/v1/tickets", json=new_ticket)
    assert res_create.status_code == 201
    created_id = res_create.json()["id"]

    # Atualização de status
    res_up = client.patch(f"/api/v1/tickets/{created_id}/status", json={"status": "resolvido"})
    assert res_up.status_code == 200
    assert res_up.json()["status"] == "resolvido"


def test_tasks_api_crud():
    """Testa listagem, criação e toggle de tarefas."""
    # Listagem
    res = client.get("/api/v1/tasks")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) >= 4

    # Criação
    new_task = {
        "title": "Homologar pipeline de webhooks com cliente",
        "due_date": "Hoje, 18:00",
        "assignee": "Thiago Hortolan",
        "priority": "alta"
    }
    res_create = client.post("/api/v1/tasks", json=new_task)
    assert res_create.status_code == 201
    t_id = res_create.json()["id"]

    # Alternar status
    res_toggle = client.patch(f"/api/v1/tasks/{t_id}/toggle", json={"completed": True})
    assert res_toggle.status_code == 200
    assert res_toggle.json()["completed"] == 1


def test_pipelines_endpoint():
    """Testa listagem de funis de venda disponíveis."""
    res = client.get("/api/v1/pipelines")
    assert res.status_code == 200
    pipes = res.json()
    assert len(pipes) >= 1
    assert any("Cirurgiões" in p["name"] or "Consignação" in p["name"] or "B2B" in p["name"] for p in pipes)


def test_create_contact_endpoint():
    """Testa criação e listagem de novos contatos."""
    payload = {
        "name": "Mariana Souza Test",
        "email": "mariana.souza@enterprise.com",
        "phone": "+55 11 99988-7766",
        "company": "Enterprise Global SA",
        "tags": ["Google Ads (GCLID)"]
    }
    res = client.post("/api/v1/contacts", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]


def test_favicon_endpoints():
    """Testa entrega dos endpoints de favicon em SVG e ICO."""
    res_svg = client.get("/favicon.svg")
    assert res_svg.status_code == 200
    assert "image/svg+xml" in res_svg.headers.get("content-type")

    res_ico = client.get("/favicon.ico")
    assert res_ico.status_code == 200


def test_campaigns_api_crud_and_metrics():
    """Testa listagem, criação e métricas de campanhas de mídia com ROAS e CAC."""
    # 1. Listagem
    res = client.get("/api/v1/campaigns")
    assert res.status_code == 200
    camps = res.json()
    assert len(camps) >= 3
    assert any(c["utm_source"] == "google" for c in camps)
    assert camps[0]["roas"] >= 0.0

    # 2. Métricas agregadas
    res_m = client.get("/api/v1/campaigns/metrics")
    assert res_m.status_code == 200
    metrics = res_m.json()
    assert metrics["total_spend"] > 0
    assert metrics["avg_roas"] > 0
    assert metrics["active_campaigns_count"] >= 1

    # 3. Criação de nova campanha
    new_camp = {
        "name": "Expansão FinTech Brasil Q1",
        "channel": "LinkedIn InMail & Cold Mail",
        "utm_source": "linkedin",
        "utm_medium": "inmail",
        "utm_campaign": "fintech-q1",
        "budget": 12000.0,
        "spend": 3200.0,
        "revenue": 18500.0,
        "leads_count": 94,
        "deals_count": 8,
        "status": "ativa"
    }
    res_create = client.post("/api/v1/campaigns", json=new_camp)
    assert res_create.status_code == 201
    created = res_create.json()
    assert created["name"] == new_camp["name"]
    assert created["utm_campaign"] == "fintech-q1"
    assert created["roas"] == round(18500.0 / 3200.0, 2)
    assert created["cac"] == round(3200.0 / 8, 2)


def test_campaigns_gate_morde_invalid_status():
    """Lei #13: Prova que a API rejeita status de campanha inválido com HTTP 422."""
    bad_payload = {
        "name": "Campanha Inválida",
        "channel": "Google Ads",
        "utm_source": "google",
        "utm_medium": "cpc",
        "utm_campaign": "invalid",
        "budget": 1000.0,
        "status": "status_inexistente_xyz"
    }
    res = client.post("/api/v1/campaigns", json=bad_payload)
    assert res.status_code == 422


def test_scoring_rules_crud_and_recalculate():
    """Testa listagem, criação, atualização de regras ICP e recálculo determinístico em lote."""
    # 1. Listagem de regras iniciais
    res = client.get("/api/v1/scoring/rules")
    assert res.status_code == 200
    rules = res.json()
    assert len(rules) >= 5
    assert any(r["points"] == 30 for r in rules)

    # 2. Criação de nova regra
    new_rule = {
        "name": "Participação em Webinar Técnico 2026",
        "category": "Comportamental",
        "condition_key": "tag",
        "condition_val": "Webinar,Demo",
        "points": 20,
        "impact_description": "Cadência de follow-up técnico 48h",
        "is_active": 1
    }
    res_create = client.post("/api/v1/scoring/rules", json=new_rule)
    assert res_create.status_code == 201
    created_rule = res_create.json()
    assert created_rule["name"] == new_rule["name"]
    rule_id = created_rule["id"]

    # 3. Atualização de peso da regra
    res_up = client.put(f"/api/v1/scoring/rules/{rule_id}", json={"points": 25})
    assert res_up.status_code == 200
    assert res_up.json()["points"] == 25

    # 4. Recálculo em lote de toda a base
    res_calc = client.post("/api/v1/scoring/recalculate")
    assert res_calc.status_code == 200
    data_calc = res_calc.json()
    assert data_calc["recalculated_count"] >= 7
    assert data_calc["tier_a_count"] + data_calc["tier_b_count"] + data_calc["tier_c_count"] == data_calc["recalculated_count"]
    assert len(data_calc["ranked_leads"]) == data_calc["recalculated_count"]
    # Garante que ranking está ordenado de forma decrescente
    scores = [lead["score"] for lead in data_calc["ranked_leads"]]
    assert scores == sorted(scores, reverse=True)


def test_scoring_gate_morde_invalid_points():
    """Lei #13: Prova que a API rejeita regras com pontos fora do intervalo [1, 100] com HTTP 422."""
    bad_rule = {
        "name": "Regra com Pontuação Exorbitante",
        "category": "Firmográfico",
        "condition_key": "tag",
        "condition_val": "VIP",
        "points": 999  # Máximo permitido é 100
    }
    res = client.post("/api/v1/scoring/rules", json=bad_rule)
    assert res.status_code == 422


# =============================================================================
# TESTES DO NICHO DENTAL INDUSTRY B2B (Passo 2)
# =============================================================================

def test_institutions_api_crud():
    """Testa listagem e credenciamento de polos de ensino odontológico (Ex: Mandic)."""
    # 1. Listagem
    res = client.get("/api/v1/institutions")
    assert res.status_code == 200
    insts = res.json()
    assert len(insts) >= 4
    assert any("Mandic" in i["name"] for i in insts)

    # 2. Cadastro de nova instituição
    payload = {
        "name": "Faculdade de Odontologia de Bauru (FOB-USP)",
        "institution_type": "Universidade Pública / Pós",
        "city": "Bauru",
        "state": "SP",
        "coordinator_name": "Prof. Dr. Eduardo Sant'Ana",
        "active_students_count": 28,
        "accreditation_status": "credenciada"
    }
    res_create = client.post("/api/v1/institutions", json=payload)
    assert res_create.status_code == 201
    created = res_create.json()
    assert created["name"] == payload["name"]
    assert created["city"] == "Bauru"


def test_dental_specialized_pipelines():
    """Valida se os funis de vendas estao especializados para a industria odontologica e revops puro."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM pipelines ORDER BY id")
    names = [r["name"] for r in cur.fetchall()]
    conn.close()
    assert any("Cirurgiões" in n for n in names)
    assert any("Prospecção & SDR Outbound" in n for n in names)
    assert any("Distribuidores" in n for n in names)
    assert any("CS, Expansão" in n for n in names)


def test_contacts_dental_fields():
    """Testa presença e persistência de atributos odontológicos (CRO, UF, Especialidade)."""
    # 1. Listagem com atributos odonto
    res = client.get("/api/v1/contacts")
    assert res.status_code == 200
    contacts = res.json()
    assert len(contacts) >= 1
    # Verifica que contatos possuem CRO preenchido
    assert any(c.get("cro") is not None for c in contacts)

    # 2. Criação de cirurgião com CRO
    dentist_payload = {
        "name": "Dr. Fernando Cordeiro",
        "email": "fernando.cordeiro@mandic.edu.br",
        "phone": "+55 19 98822-1100",
        "company": "Faculdade Mandic Araras",
        "tags": ["Professor", "KOL", "Implantodontia"],
        "cro": "SP-33410",
        "cro_uf": "SP",
        "specialty": "Implantodontia",
        "work_model": "Docente Universitário",
        "monthly_implants_volume": "20-50/mês",
        "customer_type": "Professor/KOL"
    }
    res_dentist = client.post("/api/v1/contacts", json=dentist_payload)
    assert res_dentist.status_code == 201
    created_d = res_dentist.json()
    assert created_d["cro"] == "SP-33410"
    assert created_d["specialty"] == "Implantodontia"


def test_hierarchy_frontend_view_and_scope_elements():
    """TICKET-04: Testa se o frontend raiz (/) serve a view de organograma e seletor de escopo."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    # 1. View de Organograma
    assert 'id="hierarchy-view"' in html
    assert "Estrutura Corporativa, Divisões & RBAC Setorial" in html
    # 2. 4 Presets Plug & Play
    assert "Fábrica Enxuta / Distribuidor" in html
    assert "Nacional em Expansão" in html
    assert "Multidivisão de Produtos" in html
    assert "Multinacional Enterprise" in html
    # 3. Seletor de Escopo de Usuário
    assert 'id="user-scope-select"' in html
    assert "Heverton Eduardo Peres (Super Admin" in html
    # 4. Nav-link
    assert 'data-view="hierarchy"' in html
