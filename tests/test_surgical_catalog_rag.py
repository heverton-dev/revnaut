# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-26: Copiloto RAG de Catálogos Técnicos, Torques e Sequência de Fresagem (pgvector)
"""

import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import get_connection, init_db
from src.features.intelligence import surgical_rag


@pytest.fixture
def client():
    return TestClient(app, headers=bearer_headers())


@pytest.fixture(autouse=True)
def clean_catalog_embeddings():
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM semantic_embeddings WHERE entity_type = 'catalog_chunk'")
        conn.commit()
    finally:
        conn.close()


def test_ingest_and_query_catalog_cone_morse_torque_and_drills():
    # 1. Ingestão de chunk técnico oficial do Catálogo Cirúrgico Cone Morse
    chunk_res = surgical_rag.ingest_catalog_chunk(
        source_manual="Manual Cirúrgico Cone Morse Pro - Edição 2026",
        page_number=42,
        implant_line="Cone Morse 3.5x13",
        bone_type="Tipo II",
        content_chunk=(
            "Para o implante Cone Morse 3.5x13 mm em osso de densidade Tipo II, "
            "a sequência obrigatória de fresagem é: Lança 2.0 -> Piloto 2/3 -> Helicoidal 2.8 -> Cônica 3.5. "
            "Torque de inserção recomendado de 32 N.cm a 45 N.cm. "
            "Para o minipilar cônico protético, o torque de assentamento é estritamente 20 N.cm."
        ),
        drill_sequence=["Lança 2.0", "Piloto 2/3", "Helicoidal 2.8", "Cônica 3.5"],
        recommended_implant_torque_ncm=32.0,
        recommended_prosthetic_torque_ncm=20.0,
        account_id="0f14ffff"
    )

    assert chunk_res["status"] == "INGESTED"
    assert chunk_res["chunk_id"].startswith("cat-")

    # 2. Ingestão de outro chunk de outra linha (Hexágono Externo)
    surgical_rag.ingest_catalog_chunk(
        source_manual="Manual Linha Hexágono Externo Master",
        page_number=18,
        implant_line="Hexágono Externo 4.1x10",
        bone_type="Tipo I",
        content_chunk="Implante HE 4.1x10 mm para osso denso Tipo I exige broca countersink e torque de 50 N.cm.",
        drill_sequence=["Lança 2.0", "Broca 3.0", "Broca 4.1", "Countersink"],
        recommended_implant_torque_ncm=50.0,
        recommended_prosthetic_torque_ncm=30.0,
        account_id="0f14ffff"
    )

    # 3. Consulta técnica RAG pelo atendente/consultor no Chatwoot
    query_text = "Qual a sequência de brocas para o implante Cone Morse 3.5x13 em osso tipo II e qual o torque do minipilar?"
    search_res = surgical_rag.query_surgical_catalog(
        query=query_text,
        bone_type="Tipo II",
        min_similarity=0.70,
        account_id="0f14ffff"
    )

    assert search_res["matched"] is True
    assert search_res["similarity_score"] >= 0.70
    assert search_res["source_manual"] == "Manual Cirúrgico Cone Morse Pro - Edição 2026"
    assert search_res["page_number"] == 42
    assert search_res["recommended_implant_torque_ncm"] == 32.0
    assert search_res["recommended_prosthetic_torque_ncm"] == 20.0
    assert search_res["drill_sequence"] == ["Lança 2.0", "Piloto 2/3", "Helicoidal 2.8", "Cônica 3.5"]
    assert "Pág. 42" in search_res["answer"]


def test_rag_query_unmatched_low_similarity():
    query_text = "Como instalar lentes de contato dentais em resina composta?"
    search_res = surgical_rag.query_surgical_catalog(
        query=query_text,
        min_similarity=0.75,
        account_id="0f14ffff"
    )

    assert search_res["matched"] is False
    assert search_res["drill_sequence"] == []


def test_catalog_rag_api_endpoints(client):
    # Ingestão via API
    ingest_payload = {
        "source_manual": "Manual Prótese Digital 2026",
        "page_number": 15,
        "implant_line": "Multi-Unit Angulado 17 graus",
        "bone_type": "Todos",
        "content_chunk": "O minipilar Multi-Unit angulado de 17 graus exige torque de inserção de 25 N.cm com chave hexagonal 1.2 mm.",
        "drill_sequence": [],
        "recommended_implant_torque_ncm": None,
        "recommended_prosthetic_torque_ncm": 25.0
    }
    res_ingest = client.post("/api/v1/intelligence/catalog-rag/ingest", json=ingest_payload)
    assert res_ingest.status_code == 201
    assert res_ingest.json()["status"] == "INGESTED"

    # Query via API
    query_payload = {
        "query": "Qual o torque do minipilar Multi-Unit angulado de 17 graus?",
        "min_similarity": 0.65
    }
    res_query = client.post("/api/v1/intelligence/catalog-rag/query", json=query_payload)
    assert res_query.status_code == 200
    q_data = res_query.json()
    assert q_data["matched"] is True
    assert q_data["recommended_prosthetic_torque_ncm"] == 25.0
    assert q_data["page_number"] == 15
