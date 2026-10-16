# -*- coding: utf-8 -*-
"""
Testes TDD - TICKET-02: Presets Plug & Play Odontológicos e CRUD de Hierarquia
Valida a geração idempotente de organogramas e bloqueio de loops na árvore.
"""

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_apply_multinacional_enterprise_preset():
    """Valida aplicação do preset multinacional enterprise (4 BUs odontológicas)."""
    payload = {"preset_name": "multinacional_enterprise"}
    res = client.post("/api/v1/hierarchy/presets/apply", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["success"] is True
    assert data["preset"] == "multinacional_enterprise"
    assert data["business_units_count"] >= 4
    assert data["teams_count"] >= 4
    assert data["roles_count"] >= 4

    # Verifica se as BUs odontológicas existem
    res_bu = client.get("/api/v1/hierarchy/business-units")
    assert res_bu.status_code == 200
    bus = res_bu.json()
    bu_codes = [b["code"] for b in bus]
    assert "BU_CIRURGIA_DIRETA" in bu_codes
    assert "BU_CADCAM" in bu_codes
    assert "BU_ENSINO_MANDIC" in bu_codes
    assert "BU_KEY_ACCOUNTS" in bu_codes


def test_apply_fabrica_enxuta_preset():
    """Valida preset enxuto para fábricas menores / distribuidores."""
    payload = {"preset_name": "fabrica_enxuta"}
    res = client.post("/api/v1/hierarchy/presets/apply", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["preset"] == "fabrica_enxuta"


def test_create_custom_team_and_anti_loop_validation():
    """Lei #13: Prova que a API rejeita relações de parentesco circular (anti-loop DAG)."""
    # 1. Cria BU de teste
    res_bu = client.post("/api/v1/hierarchy/business-units", json={
        "name": "Divisão Experimental",
        "code": "BU_TEST_EXP"
    })
    assert res_bu.status_code in [200, 201]
    bu_id = res_bu.json()["id"]

    # 2. Cria Time Pai A
    res_a = client.post("/api/v1/hierarchy/teams", json={
        "name": "Equipe Pai A",
        "business_unit_id": bu_id,
        "parent_id": None
    })
    assert res_a.status_code in [200, 201]
    team_a_id = res_a.json()["id"]

    # 3. Cria Time Filho B apontando para Time A
    res_b = client.post("/api/v1/hierarchy/teams", json={
        "name": "Equipe Filha B",
        "business_unit_id": bu_id,
        "parent_id": team_a_id
    })
    assert res_b.status_code in [200, 201]
    team_b_id = res_b.json()["id"]

    # 4. Tenta criar Time C apontando para Time B
    res_c = client.post("/api/v1/hierarchy/teams", json={
        "name": "Equipe Neta C",
        "business_unit_id": bu_id,
        "parent_id": team_b_id
    })
    assert res_c.status_code in [200, 201]
    team_c_id = res_c.json()["id"]

    # 5. Tentativa de fazer Time A virar filho de Time C (Loop A -> B -> C -> A) DEVE FALHAR (HTTP 422)
    res_loop = client.put(f"/api/v1/hierarchy/teams/{team_a_id}/parent", json={
        "parent_id": team_c_id
    })
    assert res_loop.status_code == 422, "API deve bloquear relações cíclicas na árvore hierárquica"
    assert "circular" in res_loop.json()["detail"].lower() or "loop" in res_loop.json()["detail"].lower()


def test_gate_morde_invalid_preset_name():
    """Lei #13: Prova que a API rejeita presets inexistentes com HTTP 400 ou 422."""
    res = client.post("/api/v1/hierarchy/presets/apply", json={"preset_name": "preset_inexistente_alien"})
    assert res.status_code in [400, 422]
