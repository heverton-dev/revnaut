# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-18: Gestão de Key Opinion Leaders (KOLs), Embaixadores e Metas de Comodato
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import init_db
from src.features.keypartners import kol_management


@pytest.fixture
def client():
    return TestClient(app)


def test_kol_contract_compliant_consumption():
    init_db()

    # 1. Cadastra contrato de KOL com motor cirúrgico em comodato
    kol = kol_management.create_kol_contract(
        kol_name="Prof. Dr. Marcelo Gusmão",
        cro_uf="CRO-SP-88123",
        equipment_name="Motor Cirúrgico Neodent Neo Surgery Plus",
        asset_tag="PAT-MTR-2026-042",
        min_monthly_implants_target=20,
        clinical_lectures_quota=2,
        account_id="0f14ffff"
    )
    assert kol["id"].startswith("kol-")
    assert kol["compliance_status"] == "COMPLIANT"
    assert kol["current_month_consumption"] == 0

    # 2. Simula consumo mensal de 22 implantes (Meta batida >= 20)
    eval_res = kol_management.record_monthly_consumption(
        contract_id=kol["id"],
        consumed_implants_count=22,
        account_id="0f14ffff"
    )
    assert eval_res["compliance_status"] == "COMPLIANT"
    assert eval_res["current_month_consumption"] == 22
    assert eval_res["regional_alert"] is False

    # 3. Submete caso clínico comprobatório no Cloudflare R2
    evid_res = kol_management.submit_clinical_evidence(
        contract_id=kol["id"],
        r2_key="cases/kol-042/caso_protocolo_allon4.pdf",
        title="Reabilitação All-on-4 com Carga Imediata",
        account_id="0f14ffff"
    )
    assert evid_res["success"] is True
    assert "cases/kol-042/caso_protocolo_allon4.pdf" in evid_res["evidence_r2_keys_json"]


def test_kol_contract_non_compliant_alert():
    init_db()

    # Cadastra KOL com scanner intraoral exigindo 30 implantes/mês
    kol = kol_management.create_kol_contract(
        kol_name="Dra. Roberta Valente (Embaixadora)",
        cro_uf="CRO-RJ-44112",
        equipment_name="Scanner Intraoral Virtuo Vivo",
        asset_tag="PAT-SCN-2026-015",
        min_monthly_implants_target=30,
        account_id="0f14ffff"
    )

    # Simula consumo de apenas 8 implantes no mês (Meta não atingida < 30)
    eval_res = kol_management.record_monthly_consumption(
        contract_id=kol["id"],
        consumed_implants_count=8,
        account_id="0f14ffff"
    )
    assert eval_res["compliance_status"] == "NON_COMPLIANT_ALERT"
    assert eval_res["current_month_consumption"] == 8
    assert eval_res["regional_alert"] is True
    assert "Alerta para Gerência Regional" in eval_res["alert_message"]


def test_kol_api_endpoints(client):
    # 1. POST /api/v1/keypartners/kol-contracts
    create_body = {
        "kol_name": "Prof. Fernando Silveira",
        "cro_uf": "CRO-MG-33221",
        "equipment_name": "Kit Cirúrgico Guiado Titanium Master",
        "asset_tag": "PAT-KIT-991",
        "min_monthly_implants_target": 15,
        "clinical_lectures_quota": 1
    }
    res_create = client.post("/api/v1/keypartners/kol-contracts", json=create_body)
    assert res_create.status_code == 201
    kol_data = res_create.json()
    kol_id = kol_data["id"]
    assert kol_data["asset_tag"] == "PAT-KIT-991"

    # 2. GET /api/v1/keypartners/kol-contracts
    res_list = client.get("/api/v1/keypartners/kol-contracts")
    assert res_list.status_code == 200
    kols_list = res_list.json()
    assert any(k["id"] == kol_id for k in kols_list)

    # 3. POST /api/v1/keypartners/kol-contracts/{id}/record-consumption
    consume_body = {"consumed_implants_count": 18}
    res_cons = client.post(f"/api/v1/keypartners/kol-contracts/{kol_id}/record-consumption", json=consume_body)
    assert res_cons.status_code == 200
    assert res_cons.json()["compliance_status"] == "COMPLIANT"

    # 4. POST /api/v1/keypartners/kol-contracts/{id}/evidence
    evid_body = {
        "r2_key": "cases/fernando/aula_cirurgia_guiada.mp4",
        "title": "Vídeo Cirurgia Guiada ao Vivo"
    }
    res_evid = client.post(f"/api/v1/keypartners/kol-contracts/{kol_id}/evidence", json=evid_body)
    assert res_evid.status_code == 200
    assert res_evid.json()["success"] is True

    # 5. GET /api/v1/keypartners/kol-contracts/{id}
    res_get = client.get(f"/api/v1/keypartners/kol-contracts/{kol_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == kol_id
