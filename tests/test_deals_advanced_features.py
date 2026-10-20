import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection

client = TestClient(app, headers=bearer_headers())

def test_deal_inline_update_and_timeline():
    # 1. Obter negócio existente
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, value, stage_id FROM deals LIMIT 1")
    row = cur.fetchone()
    conn.close()
    assert row is not None, "Deveria existir ao menos um deal no banco de teste"
    deal_id = row["id"]

    # 2. Testar Edição Inline (PUT /api/v1/deals/{deal_id})
    res_update = client.put(f"/api/v1/deals/{deal_id}", json={
        "value": 45000.0,
        "expected_close_date": "2026-11-30",
        "priority": "alta",
        "comment": "Ajuste de margem acordado em conferência"
    }, headers={"X-User-Id": "usr-superadmin-god"})
    assert res_update.status_code == 200
    data = res_update.json()
    assert data["value"] == 45000.0
    assert data["expected_close_date"] == "2026-11-30"
    assert data["priority"] == "alta"

    # 3. Testar Histórico e Timeline (GET /api/v1/deals/{deal_id}/timeline)
    res_timeline = client.get(f"/api/v1/deals/{deal_id}/timeline")
    assert res_timeline.status_code == 200
    timeline_data = res_timeline.json()
    assert "timeline" in timeline_data
    logs = timeline_data["timeline"]
    assert len(logs) > 0
    actions = [l["action"] for l in logs]
    assert "VALUE_UPDATE" in actions
    assert "CLOSE_DATE_UPDATE" in actions


def test_credit_limit_lock_and_approval():
    # Criar um negócio com valor > 150.000 no estágio inicial 101
    from src.features.deals.service import create_deal
    from src.features.deals.schemas import DealCreate

    deal = create_deal(DealCreate(
        title="Aquisição de Tomógrafo 3D Odontológico",
        company="Odonto Prime Hospitalar",
        contact_name="Dr. Fernando",
        value=185000.0,
        stage_id=101,
        priority="alta"
    ))
    deal_id = deal["id"]

    # Tentar mover diretamente para estágio 104 (Consignação) ou 105 (Fechado) sem aprovação
    res_fail = client.put(f"/api/v1/deals/{deal_id}/stage", json={"stage_id": 104})
    assert res_fail.status_code == 422
    assert "Trava de Limite de Crédito" in res_fail.json()["detail"]

    # Aprovar crédito
    res_approve = client.post(f"/api/v1/deals/{deal_id}/approve-credit", headers={"X-User-Id": "usr-superadmin-god"})
    assert res_approve.status_code == 200
    assert res_approve.json()["credit_approved"] is True

    # Tentar mover novamente para estágio 104 - agora deve passar
    res_success = client.put(f"/api/v1/deals/{deal_id}/stage", json={"stage_id": 104})
    assert res_success.status_code == 200
    assert res_success.json()["new_stage_id"] == 104


def test_export_deals_csv():
    res = client.get("/api/v1/deals/export/csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "attachment; filename=pipeline_revnault_dental.csv" in res.headers["content-disposition"]
    csv_text = res.text
    assert "ID,Titulo,Empresa,Contato,Valor_R$,Estagio,Prioridade,Previsao_Fechamento" in csv_text
    assert len(csv_text.splitlines()) > 1


def test_create_deal_with_pipeline_and_owner():
    from tests.test_data_scoping import setup_scoping_fixture
    setup_scoping_fixture()

    payload = {
        "title": "Prospecção SDR - Clínica OdontoMaster",
        "value": 35000.0,
        "company": "OdontoMaster Implantes",
        "contact_name": "Dr. Lucas Lima",
        "pipeline_id": 2,
        "stage_id": 201,
        "priority": "alta"
    }
    res = client.post("/api/v1/deals", json=payload, headers={"X-User-Id": "u_cons_capital_1"})
    assert res.status_code == 201
    data = res.json()
    assert data["pipeline_id"] == 2
    assert data["stage_id"] == 201
    assert data["owner_id"] == "u_cons_capital_1"

    # Validar listagem filtrada por pipeline_id 2
    res_list = client.get("/api/v1/deals?pipeline_id=2", headers={"X-User-Id": "u_cons_capital_1"})
    assert res_list.status_code == 200
    deals_data = res_list.json()
    assert any(d["id"] == data["id"] for d in deals_data["deals"])


def test_export_deals_csv_and_parquet_endpoint():
    # Teste exportação CSV padronizada
    res_csv = client.get("/api/v1/deals/export?format=csv", headers={"X-User-Id": "usr-superadmin-god"})
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "ID,Titulo,Empresa,Contato,Valor_R$" in res_csv.text

    # Teste exportação PARQUET padronizada
    res_parquet = client.get("/api/v1/deals/export?format=parquet", headers={"X-User-Id": "usr-superadmin-god"})
    assert res_parquet.status_code == 200
    assert "application/vnd.apache.parquet" in res_parquet.headers["content-type"]
    assert len(res_parquet.content) > 0
    # Valida cabeçalho mágico 'PAR1' do formato Parquet
    assert res_parquet.content[:4] == b"PAR1"


