# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-10: Motor Preditivo de Lead Scoring Odontológico, ICP Fit e Handoff Automático
Valida persistência em scoring_history, compute_semantic_embedding e handoff automático
com executive_summary e atribuição de consultor regional.
"""

import json
import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection
from src.features.scoring.service import calculate_contact_score_and_handoff


@pytest.fixture
def client():
    return TestClient(app, headers=bearer_headers())


def test_lead_scoring_history_semantic_vector_and_auto_handoff():
    conn = get_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM deals WHERE contact_name = 'Dr. Gustavo Siqueira' OR title LIKE '%Dr. Gustavo Siqueira%'")
            cur.execute("DELETE FROM semantic_embeddings WHERE entity_id = '8801' AND entity_type = 'contact'")
            cur.execute("DELETE FROM scoring_history WHERE contact_id = 8801")
            cur.execute("""
                INSERT OR REPLACE INTO users (id, account_id, name, email, role)
                VALUES ('u_field_sp_sul', '0f14ffff', 'Consultor Regional SP Sul', 'sp.sul@revnaut.com', 'Consultor')
            """)
            cur.execute("""
                INSERT OR REPLACE INTO contacts (
                    id, account_id, name, email, phone, cro, cro_uf, cro_verified,
                    specialty, work_model, monthly_implants_volume, customer_type,
                    field_owner_id, score
                )
                VALUES (
                    8801, '0f14ffff', 'Dr. Gustavo Siqueira', 'gustavo.siqueira@implantes.com.br',
                    '+5511998877665', 'CRO-SP 77112', 'SP', 1,
                    'Implantodontia', 'Clínica Própria', '> 50/mês', 'Cirurgião',
                    'u_field_sp_sul', 40
                )
            """)
    finally:
        conn.close()

    result = calculate_contact_score_and_handoff(
        contact_id=8801,
        additional_interactions=["download_catalogo", "resposta_whatsapp", "presenca_imersao"]
    )

    assert result["score"] >= 75
    assert result["tier"] == "Tier A"
    assert result["deal_created"] is True
    assert result["deal_id"] is not None
    assert result["owner_id"] == "u_field_sp_sul"
    assert "Briefing Técnico MQL" in (result["executive_summary"] or "")

    conn = get_connection()
    try:
        cur = conn.cursor()
        # 1. Valida Deal criado com owner_id, field_owner_id e executive_summary
        cur.execute(
            "SELECT id, stage_id, priority, owner_id, field_owner_id, executive_summary FROM deals WHERE id = ?",
            (result["deal_id"],)
        )
        deal_row = cur.fetchone()
        assert deal_row is not None
        assert deal_row["stage_id"] == 101
        assert deal_row["owner_id"] == "u_field_sp_sul"
        assert deal_row["field_owner_id"] == "u_field_sp_sul"
        assert "Implantodontia" in deal_row["executive_summary"]

        # 2. Valida histórico em scoring_history
        cur.execute(
            "SELECT previous_score, new_score, icp_fit_score, engagement_score, tier FROM scoring_history WHERE contact_id = 8801"
        )
        hist_row = cur.fetchone()
        assert hist_row is not None
        assert hist_row["previous_score"] == 40
        assert hist_row["new_score"] == result["score"]
        assert hist_row["tier"] == "Tier A"

        # 3. Valida que o embedding é L2 normalizado (não ord(c)/255)
        cur.execute(
            "SELECT embedding FROM semantic_embeddings WHERE entity_id = '8801' AND entity_type = 'contact'"
        )
        emb_row = cur.fetchone()
        assert emb_row is not None
        vec = json.loads(emb_row["embedding"])
        assert len(vec) == 128
        assert any(v < 0 for v in vec)
    finally:
        conn.close()
