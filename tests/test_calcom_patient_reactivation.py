# -*- coding: utf-8 -*-
"""
Testes TDD para TICKET-36: Motor de Agendamento Inteligente Cal.com e
Loop de Reativação Preventiva de Pacientes (6/12/18m).
"""

from __future__ import annotations
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection, init_db
from src.features.automations import calcom_reactivation

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_calcom_db():
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM calcom_bookings WHERE account_id = '0f14ffff'")
        cur.execute("DELETE FROM patient_reactivation_schedules WHERE account_id = '0f14ffff'")
        cur.execute("DELETE FROM omnichannel_messages WHERE account_id = '0f14ffff'")
        conn.commit()
    finally:
        conn.close()


def test_schedule_patient_reactivation_milestones():
    """Valida geração determinística dos 3 marcos de reativação: 180d, 365d e 540d."""
    surgery_date = "2026-01-01"
    schedules = calcom_reactivation.schedule_patient_reactivation(
        patient_name="Roberto Silveira",
        patient_phone="+5511991234567",
        surgeon_name="Dr. Lucas Mendes",
        procedure_name="Protocolo All-on-4 Superior",
        surgery_date=surgery_date,
        account_id="0f14ffff",
        base_calcom_url="https://cal.com/dr-lucas-mendes"
    )

    assert len(schedules) == 3
    milestones = [s["milestone_days"] for s in schedules]
    assert milestones == [180, 365, 540]

    # Validação de cálculo das datas de disparo
    s_dt = datetime.strptime(surgery_date, "%Y-%m-%d")
    d180 = (s_dt + timedelta(days=180)).strftime("%Y-%m-%d")
    d365 = (s_dt + timedelta(days=365)).strftime("%Y-%m-%d")
    d540 = (s_dt + timedelta(days=540)).strftime("%Y-%m-%d")

    assert schedules[0]["scheduled_dispatch_date"] == d180
    assert schedules[1]["scheduled_dispatch_date"] == d365
    assert schedules[2]["scheduled_dispatch_date"] == d540

    for s in schedules:
        assert s["status"] == "PENDING"
        assert "cal.com/dr-lucas-mendes" in s["calcom_booking_link"]
        assert "Roberto" in s["calcom_booking_link"]


def test_scan_and_dispatch_due_reactivations():
    """Simula paciente com cirurgia realizada há 180 dias; valida scanner e disparo de mensagem."""
    # Cirurgia realizada exatamente 180 dias atrás em relação à data de referência
    ref_date = "2026-07-01"
    surgery_date = (datetime.strptime(ref_date, "%Y-%m-%d") - timedelta(days=180)).strftime("%Y-%m-%d")

    calcom_reactivation.schedule_patient_reactivation(
        patient_name="Dona Maria Aparecida",
        patient_phone="+5511987654321",
        surgeon_name="Dra. Juliana Prado",
        procedure_name="Implantes Unitários Cone Morse",
        surgery_date=surgery_date,
        account_id="0f14ffff"
    )

    # Executa scanner na data de referência
    result = calcom_reactivation.scan_and_dispatch_due_reactivations(
        reference_date=ref_date,
        account_id="0f14ffff"
    )

    assert result["dispatched_count"] >= 1
    dispatched = result["dispatched_items"]
    found = [d for d in dispatched if d["patient_name"] == "Dona Maria Aparecida"]
    assert len(found) == 1
    assert found[0]["milestone_days"] == 180
    assert found[0]["status"] == "DISPATCHED"

    # Confirma persistência da mensagem na tabela de omnichannel
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT content FROM omnichannel_messages WHERE remote_jid LIKE ?", ("%987654321%",))
        row = cur.fetchone()
        assert row is not None
        assert "Dona Maria Aparecida" in row["content"]
        assert "cal.com" in row["content"]
    finally:
        conn.close()


def test_calcom_webhook_booking_created_and_deal_creation():
    """Valida processamento do webhook BOOKING_CREATED: cria agendamento, tarefa, Deal e sala LiveKit."""
    # Agenda reativação prévia
    calcom_reactivation.schedule_patient_reactivation(
        patient_name="Carlos Eduardo",
        patient_phone="+5511977776666",
        surgeon_name="Dr. Lucas Mendes",
        procedure_name="Protocolo Implante Carga Imediata",
        surgery_date="2026-01-10",
        account_id="0f14ffff"
    )

    webhook_payload = {
        "triggerEvent": "BOOKING_CREATED",
        "payload": {
            "uid": "cal_book_999888",
            "title": "Manutenção Peri-implantar & Profilaxia",
            "startTime": "2026-07-15T14:00:00.000Z",
            "endTime": "2026-07-15T14:45:00.000Z",
            "location": "integrations:livekit",
            "organizer": {
                "name": "Dr. Lucas Mendes",
                "email": "dr.lucas@revnaut.internal"
            },
            "attendees": [
                {
                    "name": "Carlos Eduardo",
                    "email": "carlos.eduardo@paciente.internal",
                    "timeZone": "America/Sao_Paulo"
                }
            ],
            "metadata": {
                "patient_phone": "+5511977776666"
            }
        }
    }

    result = calcom_reactivation.process_calcom_webhook(
        payload=webhook_payload,
        account_id="0f14ffff"
    )

    assert result["success"] is True
    assert result["booking_uid"] == "cal_book_999888"
    assert result["deal_id"] is not None
    assert result["task_id"] is not None
    assert "https://meet.revnaut.internal" in result["meeting_url"]

    # Valida no banco se a tarefa foi criada
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT title, due_date FROM tasks WHERE id = ?", (result["task_id"],))
        task = cur.fetchone()
        assert task is not None
        assert "Carlos Eduardo" in task["title"]

        # Valida se o Deal de manutenção preventiva foi criado no Pipeline 1
        cur.execute("SELECT title, pipeline_id, value FROM deals WHERE id = ?", (result["deal_id"],))
        deal = cur.fetchone()
        assert deal is not None
        assert "Carlos Eduardo" in deal["title"]
        assert deal["pipeline_id"] == 1
        assert deal["value"] > 0

        # Valida se a régua correspondente mudou para BOOKED
        cur.execute("SELECT status FROM patient_reactivation_schedules WHERE patient_name = 'Carlos Eduardo'")
        sched = cur.fetchone()
        assert sched is not None
        assert sched["status"] == "BOOKED"
    finally:
        conn.close()


def test_api_endpoints_calcom_reactivation():
    """Valida contratos OpenAPI 3.1 dos endpoints de automação Cal.com."""
    # 1. Agendar reativação via API
    resp_sched = client.post(
        "/api/v1/automations/calcom/schedule-reactivation",
        json={
            "patient_name": "Ana Paula Souza",
            "patient_phone": "+5511966665555",
            "surgeon_name": "Dr. Fernando Torres",
            "procedure_name": "Implante Zigomático",
            "surgery_date": "2026-02-01",
            "account_id": "0f14ffff"
        }
    )
    assert resp_sched.status_code == 201
    data_sched = resp_sched.json()
    assert len(data_sched["schedules"]) == 3
    assert data_sched["patient_name"] == "Ana Paula Souza"

    # 2. Listar réguas via API
    resp_list = client.get("/api/v1/automations/calcom/schedules?patient_name=Ana Paula")
    assert resp_list.status_code == 200
    assert len(resp_list.json()) == 3

    # 3. Disparar scanner de reativação via API
    resp_scan = client.post(
        "/api/v1/automations/calcom/scan-dispatches",
        json={
            "reference_date": "2026-08-01",
            "account_id": "0f14ffff"
        }
    )
    assert resp_scan.status_code == 200
    data_scan = resp_scan.json()
    assert "dispatched_count" in data_scan

    # 4. Enviar webhook BOOKING_CREATED via API
    webhook_body = {
        "triggerEvent": "BOOKING_CREATED",
        "payload": {
            "uid": "cal_api_booking_123",
            "title": "Demonstração Scanner Intraoral 3D",
            "startTime": "2026-08-05T10:00:00.000Z",
            "endTime": "2026-08-05T11:00:00.000Z",
            "location": "integrations:livekit",
            "organizer": {
                "name": "Consultor Comercial DENTGO",
                "email": "consultor@revnaut.internal"
            },
            "attendees": [
                {
                    "name": "Ana Paula Souza",
                    "email": "ana.souza@clinica.internal"
                }
            ],
            "metadata": {
                "patient_phone": "+5511966665555"
            }
        }
    }

    resp_hook = client.post("/api/v1/automations/calcom/webhook", json=webhook_body)
    assert resp_hook.status_code == 200
    data_hook = resp_hook.json()
    assert data_hook["success"] is True
    assert data_hook["booking_uid"] == "cal_api_booking_123"

    # 5. Listar bookings via API
    resp_bookings = client.get("/api/v1/automations/calcom/bookings")
    assert resp_bookings.status_code == 200
    bookings = resp_bookings.json()
    assert len(bookings) >= 1
    assert any(b["calcom_booking_uid"] == "cal_api_booking_123" for b in bookings)
