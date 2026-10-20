# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-28: Réguas Automatizadas de Acompanhamento Pós-Operatório Clínico B2C (24h / 48h / 72h / 7d)
"""

import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection, init_db
from src.features.automations import postop_patient_care


@pytest.fixture
def client():
    return TestClient(app, headers=bearer_headers())


@pytest.fixture(autouse=True)
def clean_postop_data():
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM postop_patient_care_schedules")
        cur.execute("DELETE FROM tickets WHERE category = 'Pós-Operatório Crítico'")
        conn.commit()
    finally:
        conn.close()


def test_start_postop_schedule_creates_4_milestones():
    sched = postop_patient_care.start_postop_care_schedule(
        patient_name="Carlos Eduardo Silveira",
        patient_phone="+5511998877665",
        surgeon_name="Dr. Roberto Implantodontista",
        surgeon_phone="+5511988776655",
        procedure_name="Implante Unitário Dente 21 com Enxerto Ósseo Bio-Oss",
        surgery_date="2026-10-18",
        account_id="0f14ffff"
    )

    assert sched["id"].startswith("posop-")
    assert sched["status"] == "ACTIVE"
    assert len(sched["milestones"]) == 4

    codes = [m["code"] for m in sched["milestones"]]
    assert codes == ["24h", "48h", "72h", "7d"]

    # Validar datas relativas determinísticas
    m_24h = sched["milestones"][0]
    assert m_24h["target_date"] == "2026-10-19"
    assert "Dor, Sangramento" in m_24h["title"]

    m_7d = sched["milestones"][3]
    assert m_7d["target_date"] == "2026-10-25"
    assert "Remoção de Suturas" in m_7d["title"]


def test_postop_feedback_normal_recovery():
    sched = postop_patient_care.start_postop_care_schedule(
        patient_name="Mariana Souza",
        patient_phone="+5511999990000",
        surgeon_name="Dr. Roberto",
        surgeon_phone="+5511988880000",
        procedure_name="Exodontia + Implante Imediato",
        surgery_date="2026-10-18"
    )

    feedback_text = "Boa tarde! Tomei os remédios certinho, fiz compressa gelada e quase não tenho dor. Tudo tranquilo."
    res = postop_patient_care.process_patient_feedback(
        schedule_id=sched["id"],
        feedback_text=feedback_text,
        milestone_code="24h"
    )

    assert res["is_critical"] is False
    assert res["detected_triggers"] == []
    assert res["alert_ticket_id"] is None
    assert res["surgeon_alert_sent"] is False
    assert res["updated_status"] == "ACTIVE"
    assert "recuperação está dentro do esperado" in res["patient_response_message"]


def test_postop_feedback_critical_triggers_red_alert_ticket():
    sched = postop_patient_care.start_postop_care_schedule(
        patient_name="João Pedro Santos",
        patient_phone="+5521998811223",
        surgeon_name="Dra. Camila Cirurgiã",
        surgeon_phone="+5521977665544",
        procedure_name="Protocolo Branemark Superior com 6 Implantes",
        surgery_date="2026-10-18"
    )

    # Paciente relata intercorrência clínica grave nas 24h
    feedback_text = "Doutora Camila, estou com sangramento forte na gengiva e inchaço no rosto que não para, muita dor!"
    res = postop_patient_care.process_patient_feedback(
        schedule_id=sched["id"],
        feedback_text=feedback_text,
        milestone_code="24h"
    )

    assert res["is_critical"] is True
    assert "sangramento" in res["detected_triggers"]
    assert "inchaço" in res["detected_triggers"]
    assert "muita dor" in res["detected_triggers"]
    assert res["surgeon_alert_sent"] is True
    assert res["updated_status"] == "ALERT_TRIGGERED"
    assert res["alert_ticket_id"] is not None
    assert res["alert_ticket_id"].startswith("tkt-posop-")
    assert "canal prioritário" in res["patient_response_message"]

    # Verificar que o ticket P0 foi inserido no banco com prioridade alta
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT title, priority, category, customer_name FROM tickets WHERE id = ?", (res["alert_ticket_id"],))
        ticket = cur.fetchone()
        assert ticket is not None
        assert "ALERTA VERMELHO PÓS-OP (24h)" in ticket[0]
        assert ticket[1] == "alta"
        assert ticket[2] == "Pós-Operatório Crítico"
        assert ticket[3] == "João Pedro Santos"
    finally:
        conn.close()


def test_postop_api_endpoints(client):
    start_payload = {
        "patient_name": "Fernanda Lima",
        "patient_phone": "+5541991234567",
        "surgeon_name": "Dr. Fernando Cirurgião",
        "surgeon_phone": "+5541998765432",
        "procedure_name": "Enxerto em Seio Maxilar",
        "surgery_date": "2026-10-18"
    }

    # 1. POST /api/v1/automations/postop-care/start
    res_start = client.post("/api/v1/automations/postop-care/start", json=start_payload)
    assert res_start.status_code == 201
    s_data = res_start.json()
    schedule_id = s_data["id"]
    assert s_data["status"] == "ACTIVE"

    # 2. POST /api/v1/automations/postop-care/{schedule_id}/feedback
    feedback_payload = {
        "feedback_text": "Estou com sangramento intenso e o parafuso soltou na gaze",
        "milestone_code": "24h"
    }
    res_fb = client.post(f"/api/v1/automations/postop-care/{schedule_id}/feedback", json=feedback_payload)
    assert res_fb.status_code == 200
    fb_data = res_fb.json()
    assert fb_data["is_critical"] is True
    assert fb_data["updated_status"] == "ALERT_TRIGGERED"

    # 3. GET /api/v1/automations/postop-care/{schedule_id}
    res_get = client.get(f"/api/v1/automations/postop-care/{schedule_id}")
    assert res_get.status_code == 200
    assert res_get.json()["status"] == "ALERT_TRIGGERED"

    # 4. GET /api/v1/automations/postop-care
    res_list = client.get("/api/v1/automations/postop-care?status=ALERT_TRIGGERED")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1
