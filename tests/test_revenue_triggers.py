# -*- coding: utf-8 -*-
"""
Testes TDD - TICKET-08: Motor de Transbordo Automático de Leads Hot (Tier A) & Gatilhos de Receita
Comprova a detecção de cirurgião ICP Tier A, roteamento territorial e criação de Deal + Task com SLA de 15min.
"""

from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection

client = TestClient(app)


def test_hot_lead_tier_a_automatic_overflow():
    """Valida transbordo de cirurgião com volume >= 30 implantes/mês e score alto."""
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        # Cria cirurgião Hot Lead no território de SP
        cur.execute("""
            INSERT INTO contacts (account_id, name, email, phone, company, score, cro, cro_uf, specialty, monthly_implants_volume, state)
            VALUES ('0f14ffff', 'Dr. Alexandre Silveira', 'alexandre.silveira@odontoprime.com.br', '+55 11 99988-7766', 'Instituto Odonto Prime SP', 88, 'SP-65432', 'SP', 'Implantodontia', '> 50/mês', 'SP')
        """)
        contact_id = cur.lastrowid
    conn.close()

    res = client.post(f"/api/v1/automations/evaluate-hot-lead/{contact_id}")
    assert res.status_code == 200, res.text
    data = res.json()

    # 1. Valida identificação de Hot Lead
    assert data["is_hot_lead"] is True
    assert data["status"] == "transferred"
    assert data["sla_minutes"] == 15
    assert data["closer_id"] is not None
    assert data["closer_name"] is not None

    deal_id = data["deal_id"]
    task_id = data["task_id"]
    assert deal_id is not None
    assert task_id is not None

    # 2. Valida persistência do Deal prioritário no banco
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT id, title, priority, value, owner_id, team_id FROM deals WHERE id = ?", (deal_id,))
        deal = cur.fetchone()
        assert deal is not None
        assert deal["priority"] == "alta"
        assert deal["value"] == 65000.0
        assert "Alexandre Silveira" in deal["title"]

        # 3. Valida criação da Task com SLA de 15min
        cur.execute("SELECT id, title, priority, due_date, assignee FROM tasks WHERE id = ?", (task_id,))
        task = cur.fetchone()
        assert task is not None
        assert task["priority"] == "alta"
        assert "SLA 15min" in task["title"]
        assert task["assignee"] == data["closer_name"]

        # 4. Valida auditoria na timeline do cirurgião
        cur.execute("SELECT action, comment FROM contact_audit_logs WHERE contact_id = ? AND action = 'HOT_LEAD_OVERFLOW_TRANSBORDO'", (contact_id,))
        audit = cur.fetchone()
        assert audit is not None
        assert "SLA" in audit["comment"]
    conn.close()


def test_cold_lead_does_not_trigger_overflow():
    """Valida que lead frio ou morno não gera transbordo prematuro."""
    conn = get_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO contacts (account_id, name, email, score, monthly_implants_volume, state)
            VALUES ('0f14ffff', 'Dra. Camila Baixa Frequência', 'camila.baixa@clinica.com.br', 40, '1-5/mês', 'MG')
        """)
        contact_id = cur.lastrowid
    conn.close()

    res = client.post(f"/api/v1/automations/evaluate-hot-lead/{contact_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["is_hot_lead"] is False
    assert data["status"] == "warm_or_nurturing"
    assert data["deal_id"] is None
    assert data["task_id"] is None
