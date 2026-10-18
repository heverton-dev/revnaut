# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-13: Copiloto Comercial "Granola-like" via LiteLLM e Auto-Preenchimento Zero-Touch do Deal
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection
from src.features.intelligence.granola_copilot import (
    extract_meeting_intelligence,
    apply_copilot_intelligence_to_deal
)


@pytest.fixture
def client():
    return TestClient(app)


def test_granola_copilot_extraction_and_zero_touch_deal_update():
    # 1. Setup Deal inicial
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM deal_objections WHERE deal_id = ?", ("d-1",))
            cur.execute("DELETE FROM tasks WHERE account_id = ? AND title LIKE ?", ("0f14ffff", "%proposta%"))
            cur.execute("""
                UPDATE deals
                SET value = 5000.0, priority = 'media'
                WHERE id = 'd-1'
            """)
        conn.commit()
    finally:
        conn.close()

    # Transcrição da reunião comercial odontológica
    transcription_text = (
        "Consultor: Olá Dr. Roberto, como alinhamos na semana passada, vim apresentar a linha de implantes Cone Morse.\n"
        "Dr. Roberto: Perfeito. Eu quero fechar uma proposta de 20 implantes Cone Morse, mas preciso de prazo de 60 dias para pagamento até sexta-feira."
    )

    # 2. Executa extração cognitiva estruturada
    extraction = extract_meeting_intelligence(
        transcription_text=transcription_text,
        deal_id="d-1",
        account_id="0f14ffff"
    )

    assert "Cone Morse" in extraction.implant_systems_mentioned
    assert extraction.suggested_deal_value is not None
    assert extraction.suggested_deal_value > 5000.0  # 20 implantes
    assert len(extraction.objections_raised) >= 1
    assert extraction.objections_raised[0]["category"] == "prazo"
    assert "60 dias" in extraction.objections_raised[0]["objection_text"]
    assert len(extraction.next_steps_tasks) >= 1
    assert "sexta-feira" in extraction.next_steps_tasks[0]["due_date"].lower()

    # 3. Aplica automaticamente ao Deal (Zero-Touch CRM)
    apply_result = apply_copilot_intelligence_to_deal(
        deal_id="d-1",
        extraction=extraction,
        account_id="0f14ffff"
    )

    assert apply_result["success"] is True
    assert apply_result["deal_id"] == "d-1"
    assert apply_result["objections_count"] >= 1
    assert apply_result["tasks_count"] >= 1

    # 4. Valida persistência no banco
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Valida que o Deal teve valor atualizado
        cur.execute("SELECT value, executive_summary FROM deals WHERE id = 'd-1'")
        deal_row = cur.fetchone()
        assert deal_row["value"] == extraction.suggested_deal_value
        assert deal_row["executive_summary"] is not None

        # Valida inserção na tabela deal_objections
        cur.execute("SELECT category, objection_text FROM deal_objections WHERE deal_id = 'd-1'")
        obj_row = cur.fetchone()
        assert obj_row is not None
        assert obj_row["category"] == "prazo"

        # Valida inserção da tarefa em tasks
        cur.execute("SELECT title, due_date FROM tasks WHERE account_id = ? AND due_date LIKE ?", ("0f14ffff", "%Sexta%"))
        task_row = cur.fetchone()
        assert task_row is not None
    finally:
        conn.close()


def test_copilot_api_endpoint(client):
    req_payload = {
        "deal_id": "d-1",
        "account_id": "0f14ffff",
        "transcription_text": (
            "Consultor: Conversamos com o Dr. Roberto sobre o implante Cone Morse.\n"
            "Dr. Roberto: Gostei bastante. Envie uma proposta de 20 implantes Cone Morse com prazo de 60 dias até sexta-feira."
        )
    }

    res = client.post("/api/v1/intelligence/copilot/extract-and-apply", json=req_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["deal_id"] == "d-1"
    assert data["extraction"]["suggested_deal_value"] is not None
    assert len(data["extraction"]["objections_raised"]) >= 1
    assert len(data["extraction"]["next_steps_tasks"]) >= 1
