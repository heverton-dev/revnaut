# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-10: Motor Preditivo de Lead Scoring Odontológico, ICP Fit e Handoff Automático
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection
from src.features.scoring.service import calculate_contact_score_and_handoff


@pytest.fixture
def client():
    return TestClient(app)


def test_lead_scoring_icp_calculation_and_vector_persistence():
    # Limpa dados anteriores do contato 8801
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM deals WHERE contact_name = 'Dr. Gustavo Siqueira' OR title LIKE '%Dr. Gustavo Siqueira%'")
            cur.execute("DELETE FROM semantic_embeddings WHERE entity_id = '8801' AND entity_type = 'contact'")
            cur.execute("""
                INSERT OR REPLACE INTO contacts (
                    id, account_id, name, email, phone, cro, cro_uf, cro_verified,
                    specialty, work_model, monthly_implants_volume, customer_type, score
                )
                VALUES (
                    8801, '0f14ffff', 'Dr. Gustavo Siqueira', 'gustavo.siqueira@implantes.com.br',
                    '+5511998877665', 'CRO-SP 77112', 'SP', 1,
                    'Implantodontia', 'Clínica Própria', '> 50/mês', 'Cirurgião', 40
                )
            """)
        conn.commit()
    finally:
        conn.close()

    # Executa cálculo com interações de engajamento (download de catálogo + resposta no WhatsApp)
    result = calculate_contact_score_and_handoff(
        contact_id=8801,
        additional_interactions=["download_catalogo", "resposta_whatsapp", "presenca_imersao"]
    )

    assert result["score"] >= 75
    assert result["tier"] == "Tier A"
    assert result["deal_created"] is True
    assert result["deal_id"] is not None

    # Valida que o deal foi criado no estágio 101 (Qualificação & SDR)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, pipeline_id, stage_id, priority, title FROM deals WHERE id = ?", (result["deal_id"],))
        deal_row = cur.fetchone()
        assert deal_row is not None
        assert deal_row["stage_id"] == 101
        assert deal_row["priority"] == "alta"

        # Valida que o vetor foi persistido na tabela semantic_embeddings
        cur.execute("SELECT COUNT(*) FROM semantic_embeddings WHERE entity_id = '8801' AND entity_type = 'contact'")
        emb_count = cur.fetchone()[0]
        assert emb_count >= 1
    finally:
        conn.close()

    # Valida anti-duplicação: segunda execução para o mesmo lead não deve duplicar o deal
    result2 = calculate_contact_score_and_handoff(contact_id=8801)
    assert result2["score"] >= 75
    assert result2["deal_created"] is False
    assert result2["deal_id"] == result["deal_id"]


def test_lead_scoring_handoff_api_endpoint(client):
    # Cria contato de teste e limpa deals prévios
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM deals WHERE contact_name = 'Dra. Patricia Neves' OR title LIKE '%Dra. Patricia Neves%'")
            cur.execute("DELETE FROM semantic_embeddings WHERE entity_id = '8802' AND entity_type = 'contact'")
            cur.execute("""
                INSERT OR REPLACE INTO contacts (
                    id, account_id, name, email, phone, cro, cro_uf, cro_verified,
                    specialty, monthly_implants_volume, score
                )
                VALUES (
                    8802, '0f14ffff', 'Dra. Patricia Neves', 'patricia.neves@odonto.com.br',
                    '+552199881122', 'CRO-RJ 55441', 'RJ', 1,
                    'Cirurgia Bucomaxilofacial', '> 50/mês', 30
                )
            """)
        conn.commit()
    finally:
        conn.close()

    # Dispara avaliação preditiva via API
    payload = {
        "contact_id": 8802,
        "interactions": ["download_catalogo", "resposta_whatsapp", "presenca_imersao"]
    }
    res = client.post("/api/v1/scoring/evaluate-handoff", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["score"] >= 75
    assert data["deal_id"] is not None
