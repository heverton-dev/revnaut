import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection

client = TestClient(app)

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
    }, headers={"X-User-Id": "usr_superadmin"})
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
    res_approve = client.post(f"/api/v1/deals/{deal_id}/approve-credit", headers={"X-User-Id": "usr_superadmin"})
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
    assert "attachment; filename=pipeline_revnaut_dental.csv" in res.headers["content-disposition"]
    csv_text = res.text
    assert "ID,Titulo,Empresa,Contato,Valor_R$,Estagio,Prioridade,Previsao_Fechamento" in csv_text
    assert len(csv_text.splitlines()) > 1
