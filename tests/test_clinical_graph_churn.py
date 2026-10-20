# -*- coding: utf-8 -*-
"""
Testes de Homologação: TICKET-09 - Grafo Clínico KOL & Radar Anti-Churn (RFM Odontológico)
Valida vínculos N:N, ecossistema do implante, identificação de Speakers e radar determinístico de churn.
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import get_connection

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_intelligence_fixture():
    """Garante integridade e dados de teste para os testes de inteligência clínica."""
    conn = get_connection()
    cur = conn.cursor()
    acc = "0f14ffff"

    try:
        # Limpa dados anteriores de teste
        cur.execute("DELETE FROM contact_institutions WHERE account_id = ?", (acc,))

        # Garante instituições de teste (Faculdade, Clínica e Lab CAD/CAM)
        cur.execute("DELETE FROM institutions WHERE account_id = ? AND id LIKE ?", (acc, "inst_test_%"))
        cur.execute("""
            INSERT INTO institutions (id, account_id, name, institution_type, city, state, coordinator_name)
            VALUES 
            ('inst_test_mandic', ?, 'Faculdade São Leopoldo Mandic', 'Faculdade / Pós-Graduação', 'Campinas', 'SP', 'Dr. Coordenador Mandic'),
            ('inst_test_clinica_prime', ?, 'Clínica Odonto Prime Jardins', 'Clínica / Hospital Dia', 'São Paulo', 'SP', 'Dr. Responsável Prime'),
            ('inst_test_lab_digital', ?, 'Laboratório Digital CAD/CAM Pro', 'Laboratório Prótese CAD/CAM', 'Curitiba', 'PR', 'Técnico Especialista')
        """, (acc, acc, acc))

        # Cria cirurgiões de teste específicos para a inteligência
        cur.execute("DELETE FROM contacts WHERE account_id = ? AND email LIKE ?", (acc, "%test.intelligence%"))
        
        # 1. Cirurgião KOL Speaker (Leciona na Mandic + opera na Clínica Prime + consome Lab CAD/CAM)
        cur.execute("""
            INSERT INTO contacts (account_id, name, email, phone, company, score, cro, uf, specialty, clinic_name, monthly_implant_volume, reorder_cycle_days, last_order_date)
            VALUES (?, 'Dr. Ricardo KOL Speaker', 'ricardo.test.intelligence@dentalops.com', '(11) 98888-1111', 'Instituto Cirúrgico Ricardo', 95, '12345', 'SP', 'Implantodontia e Prótese', 'Instituto Cirúrgico Ricardo', 60, 15, ?)
        """, (acc, (datetime.now(timezone.utc) - timedelta(days=35)).strftime("%Y-%m-%d %H:%M:%S")))
        kol_contact_id = cur.lastrowid

        # 2. Cirurgiã Ativa e Saudável (Compra frequente, baixo risco de churn)
        cur.execute("""
            INSERT INTO contacts (account_id, name, email, phone, company, score, cro, uf, specialty, clinic_name, monthly_implant_volume, reorder_cycle_days, last_order_date)
            VALUES (?, 'Dra. Camila Ativa', 'camila.test.intelligence@dentalops.com', '(21) 97777-2222', 'Clínica Camila Implantes', 70, '67890', 'RJ', 'Cirurgia Oral Menor', 'Clínica Camila Implantes', 30, 20, ?)
        """, (acc, (datetime.now(timezone.utc) - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")))
        healthy_contact_id = cur.lastrowid

        conn.commit()
    finally:
        conn.close()

    return {
        "kol_contact_id": kol_contact_id,
        "healthy_contact_id": healthy_contact_id,
        "institutions": {
            "mandic": "inst_test_mandic",
            "clinica": "inst_test_clinica_prime",
            "lab": "inst_test_lab_digital"
        }
    }


def test_link_contact_to_institutions_and_query_links(setup_intelligence_fixture):
    """Valida a criação de vínculos N:N entre cirurgião e instituições (TICKET-09 Item 1)."""
    fixture = setup_intelligence_fixture
    kol_id = fixture["kol_contact_id"]
    insts = fixture["institutions"]

    # 1. Vínculo Acadêmico (Leciona na Faculdade Mandic -> Speaker/KOL)
    payload_teaching = {
        "contact_id": kol_id,
        "institution_id": insts["mandic"],
        "relationship_type": "teaches_at",
        "role_title": "Professor Coordenador do Curso de Cirurgia Guiada",
        "is_kol": True,
        "notes": "Speaker de renome nacional, ministra aulas para 40 pós-graduandos anuais"
    }
    res_t = client.post("/api/v1/intelligence/links", json=payload_teaching)
    assert res_t.status_code == 201
    data_t = res_t.json()
    assert data_t["contact_id"] == kol_id
    assert data_t["institution_id"] == insts["mandic"]
    assert data_t["is_kol"] is True
    assert data_t["institution_name"] == "Faculdade São Leopoldo Mandic"

    # 2. Vínculo Clínico (Opera na Clínica Prime)
    payload_clinic = {
        "contact_id": kol_id,
        "institution_id": insts["clinica"],
        "relationship_type": "operates_at",
        "role_title": "Cirurgião Convidado",
        "is_kol": False
    }
    res_c = client.post("/api/v1/intelligence/links", json=payload_clinic)
    assert res_c.status_code == 201

    # 3. Vínculo Protético (Parceiro de Lab CAD/CAM)
    payload_lab = {
        "contact_id": kol_id,
        "institution_id": insts["lab"],
        "relationship_type": "partner_cadcam",
        "role_title": "Cliente VIP Scanner Intraoral",
        "is_kol": False
    }
    res_l = client.post("/api/v1/intelligence/links", json=payload_lab)
    assert res_l.status_code == 201
    link_lab_id = res_l.json()["id"]

    # 4. Consulta de Vínculos por Cirurgião
    res_list = client.get(f"/api/v1/intelligence/links/contact/{kol_id}")
    assert res_list.status_code == 200
    links = res_list.json()
    assert len(links) == 3
    rel_types = [l["relationship_type"] for l in links]
    assert "teaches_at" in rel_types
    assert "operates_at" in rel_types
    assert "partner_cadcam" in rel_types

    # 5. Remoção de Vínculo
    res_del = client.delete(f"/api/v1/intelligence/links/{link_lab_id}")
    assert res_del.status_code == 200
    assert res_del.json()["success"] is True

    # Confirma remoção
    res_list_after = client.get(f"/api/v1/intelligence/links/contact/{kol_id}")
    assert len(res_list_after.json()) == 2


def test_clinical_graph_and_kol_speakers_identification(setup_intelligence_fixture):
    """Valida montagem da topologia do Grafo Clínico e agrupamento de Speakers KOL."""
    fixture = setup_intelligence_fixture
    kol_id = fixture["kol_contact_id"]
    insts = fixture["institutions"]

    # Vincula o cirurgião à universidade e clínica
    client.post("/api/v1/intelligence/links", json={
        "contact_id": kol_id,
        "institution_id": insts["mandic"],
        "relationship_type": "kol_speaker",
        "role_title": "Speaker Internacional",
        "is_kol": True
    })
    client.post("/api/v1/intelligence/links", json={
        "contact_id": kol_id,
        "institution_id": insts["clinica"],
        "relationship_type": "operates_at"
    })

    # 1. Consulta Grafo Clínico (TICKET-DASH-04: tenant do usuário autenticado)
    res_graph = client.get(
        "/api/v1/intelligence/clinical-graph",
        headers={"X-User-Id": "usr-superadmin-god"},
    )
    assert res_graph.status_code == 200
    graph = res_graph.json()
    assert graph["total_nodes"] >= 3
    assert graph["total_edges"] >= 2
    assert graph["kol_speakers_count"] >= 1

    surgeon_nodes = [n for n in graph["nodes"] if n["node_type"] == "surgeon"]
    assert len(surgeon_nodes) >= 1
    assert any("Dr(a). Dr. Ricardo KOL" in n["label"] for n in surgeon_nodes)

    # 2. Consulta Lista de KOLs / Speakers
    res_kols = client.get("/api/v1/intelligence/kol-speakers")
    assert res_kols.status_code == 200
    kols_data = res_kols.json()
    assert kols_data["total_kols"] >= 1
    speaker = next(s for s in kols_data["speakers"] if s["contact_id"] == kol_id)
    assert speaker["name"] == "Dr. Ricardo KOL Speaker"
    assert "Faculdade São Leopoldo Mandic" in speaker["teaching_institutions"]
    assert "Clínica Odonto Prime Jardins" in speaker["affiliated_clinics"]


def test_dental_rfm_churn_risk_radar(setup_intelligence_fixture):
    """Valida o Radar Anti-Churn com o algoritmo RFM Odontológico (TICKET-09 Item 2)."""
    fixture = setup_intelligence_fixture
    kol_id = fixture["kol_contact_id"]
    healthy_id = fixture["healthy_contact_id"]

    res_radar = client.get(
        "/api/v1/intelligence/churn-risk",
        headers={"X-User-Id": "usr-superadmin-god"},
    )
    assert res_radar.status_code == 200
    radar = res_radar.json()

    # Valida estrutura de resumo
    summary = radar["summary"]
    assert summary["total_monitored"] >= 2
    assert "critical_count" in summary
    assert "high_risk_count" in summary
    assert "medium_risk_count" in summary
    assert "low_risk_count" in summary

    items = radar["radar"]
    assert len(items) >= 2

    # 1. Cirurgião em risco crítico:
    # Dr. Ricardo comprava a cada 15 dias e está há 35 dias sem faturar (> 30 dias sem faturamento com ciclo <= 20)
    critical_item = next(i for i in items if i["contact_id"] == kol_id)
    assert critical_item["avg_reorder_interval_days"] == 15
    assert critical_item["days_since_last_order"] >= 30
    assert critical_item["days_overdue"] >= 15
    assert critical_item["churn_risk_score"] >= 80
    assert critical_item["churn_risk_level"] == "critico"
    assert "visita técnica presencial" in critical_item["recommended_action"].lower()

    # 2. Cirurgiã saudável:
    # Dra. Camila tem ciclo de 20 dias e comprou há 5 dias (days_overdue == 0)
    healthy_item = next(i for i in items if i["contact_id"] == healthy_id)
    assert healthy_item["avg_reorder_interval_days"] == 20
    assert healthy_item["days_since_last_order"] <= 10
    assert healthy_item["days_overdue"] == 0
    assert healthy_item["churn_risk_level"] == "baixo"
    assert healthy_item["churn_risk_score"] < 40


def test_intelligence_links_validation_fails_for_nonexistent_entities():
    """Valida que o gate de entrada rejeita com 400 tentativa de vincular entidades inexistentes."""
    bad_payload = {
        "contact_id": 9999999,
        "institution_id": "inst_inexistente_999",
        "relationship_type": "operates_at"
    }
    res = client.post("/api/v1/intelligence/links", json=bad_payload)
    assert res.status_code == 400
    assert "não encontrado" in res.json()["detail"].lower()
