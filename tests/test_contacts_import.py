# -*- coding: utf-8 -*-
"""
Testes automatizados para Importação Universal de Carteiras de Clientes Odontológicos
com Regras de Distribuição Territorial, Especialidades e Round-Robin.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_contacts_bulk_import_json_territorial():
    """Valida importação em massa via payload JSON com estratégia territorial por UF."""
    payload = {
        "strategy": "territorial",
        "contacts": [
            {
                "name": "Dr. Roberto Alencar",
                "cro": "SP-99101",
                "cro_uf": "SP",
                "specialty": "Implantodontia",
                "phone": "(11) 97111-2233",
                "email": "roberto.alencar@implante.com.br",
                "company": "Instituto Alencar de Reabilitação",
                "city": "São Paulo",
                "state": "SP",
                "monthly_implants_volume": "> 50/mês"
            },
            {
                "name": "Dra. Camila Bittencourt",
                "cro": "PR-88202",
                "cro_uf": "PR",
                "specialty": "Cirurgia Bucomaxilofacial",
                "phone": "(41) 98222-3344",
                "email": "camila.buco@hospitaldia.com.br",
                "company": "Hospital da Face Curitiba",
                "city": "Curitiba",
                "state": "PR",
                "monthly_implants_volume": "> 50/mês"
            }
        ]
    }

    res = client.post("/api/v1/contacts/import", json=payload, headers={"X-User-Id": "usr-superadmin-god"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["total_received"] == 2
    assert data["created_count"] + data["updated_count"] == 2
    assert "allocations_by_rep" in data
    assert len(data["items_preview"]) >= 2


def test_contacts_bulk_import_csv_raw():
    """Valida importação em massa a partir de CSV bruto tabulado com ponto-e-vírgula."""
    csv_content = """nome;cro;cro_uf;especialidade;telefone;email;empresa;cidade;estado;volume
Dr. Leonardo Vasconcelos;MG-77303;MG;Periodontia & Implante;(31) 99333-4455;leo.vasc@clinica.com.br;Clínica Vasconcelos;Belo Horizonte;MG;20-50/mês
Dra. Mariana Fagundes;SP-66404;SP;Ortodontia & Alinhadores;(16) 99444-5566;mariana@fagundesorto.com.br;Fagundes Dental;Ribeirão Preto;SP;20-50/mês
"""
    payload = {
        "strategy": "round_robin",
        "csv_raw": csv_content
    }

    res = client.post("/api/v1/contacts/import", json=payload, headers={"X-User-Id": "usr-superadmin-god"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["total_received"] == 2
    assert data["strategy_used"] == "round_robin"


def test_contacts_import_deduplication_updates_existing_record():
    """Valida que importar um contato com o mesmo CRO e CRO_UF atualiza o registro sem duplicar."""
    import uuid
    uid = uuid.uuid4().hex[:6]
    contact_cro = f"SC-{uid}"
    contact_email = f"dr.guilherme.{uid}@teste.com"

    # 1. Primeiro envio
    first_payload = {
        "strategy": "territorial",
        "contacts": [
            {
                "name": "Dr. Guilherme Teste",
                "cro": contact_cro,
                "cro_uf": "SC",
                "specialty": "Implantodontia",
                "phone": "(48) 99999-1111",
                "email": contact_email,
                "company": "Clínica Teste Inicial"
            }
        ]
    }
    res1 = client.post("/api/v1/contacts/import", json=first_payload, headers={"X-User-Id": "usr-superadmin-god"})
    assert res1.status_code == 200
    assert res1.json()["created_count"] == 1

    # 2. Segundo envio com mesmo CRO mas empresa atualizada
    second_payload = {
        "strategy": "territorial",
        "contacts": [
            {
                "name": "Dr. Guilherme Teste Atualizado",
                "cro": contact_cro,
                "cro_uf": "SC",
                "specialty": "Cirurgia Avançada",
                "phone": "(48) 99999-2222",
                "email": contact_email,
                "company": "Clínica Teste Atualizada"
            }
        ]
    }
    res2 = client.post("/api/v1/contacts/import", json=second_payload, headers={"X-User-Id": "usr-superadmin-god"})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["updated_count"] == 1
    assert data2["created_count"] == 0

