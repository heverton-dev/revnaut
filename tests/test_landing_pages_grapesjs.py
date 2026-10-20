# -*- coding: utf-8 -*-
"""
TDD Tests for TICKET-07: Construtor de Landing Pages Odontológicas (GrapesJS) e Publicação no R2
"""

import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.features.campaigns.landing_pages import (
    get_prebuilt_templates,
    create_landing_page,
    publish_landing_page,
    submit_public_lead,
)


@pytest.fixture
def client():
    return TestClient(app, headers=bearer_headers())


def test_landing_page_prebuilt_templates():
    templates = get_prebuilt_templates()
    assert len(templates) >= 3
    slugs = [t["template_type"] for t in templates]
    assert "imersao_fluxo_digital" in slugs
    assert "lancamento_kit_cirurgico" in slugs
    assert "captacao_paciente_protocolo" in slugs

    # Cada template possui blocos HTML e CSS odontológicos válidos
    t0 = templates[0]
    assert "cro" in t0["html"].lower() or "cirurgia" in t0["html"].lower()
    assert len(t0["css"]) > 20


def test_landing_page_crud_and_cfo_guard(client):
    # 1. Obter templates via API
    res_tmpl = client.get("/api/v1/campaigns/landing-pages/templates")
    assert res_tmpl.status_code == 200
    templates = res_tmpl.json()
    assert len(templates) >= 3

    # 2. Criar Landing Page a partir do template de Cirurgia Guiada
    lp_payload = {
        "title": "Imersão Cirurgia Guiada Cone Morse 2026",
        "slug": "imersao-guiada-2026",
        "template_type": "imersao_fluxo_digital",
        "cfo_responsible_cro": "CRO-SP 123456",
        "cfo_responsible_name": "Dr. Roberto Guimarães"
    }
    res_create = client.post("/api/v1/campaigns/landing-pages", json=lp_payload)
    assert res_create.status_code == 201
    created_lp = res_create.json()
    assert created_lp["slug"] == "imersao-guiada-2026"
    assert created_lp["is_published"] is False
    lp_id = created_lp["id"]

    # 3. Publicar Landing Page compilada no R2
    res_pub = client.put(f"/api/v1/campaigns/landing-pages/{lp_id}/publish")
    assert res_pub.status_code == 200
    pub_data = res_pub.json()
    assert pub_data["is_published"] is True
    assert "cdn.revnaut.app/lp/imersao-guiada-2026" in pub_data["published_r2_url"] or "r2" in pub_data["published_r2_url"]


def test_landing_page_public_submission_and_event_publishing(client):
    # Cria uma LP para teste de submissão
    lp_payload = {
        "title": "Captação Implantodontia Avançada",
        "slug": "captacao-implantes-lead",
        "template_type": "lancamento_kit_cirurgico",
        "cfo_responsible_cro": "CRO-PR 8877",
        "cfo_responsible_name": "Dra. Carolina Mendes"
    }
    res_create = client.post("/api/v1/campaigns/landing-pages", json=lp_payload)
    assert res_create.status_code in (200, 201)

    # Simular submissão de formulário público por um cirurgião com UTMs
    sub_payload = {
        "name": "Dr. Marcelo Fagundes",
        "email": "marcelo.fagundes@clinica.com.br",
        "phone": "+5541999998888",
        "cro": "CRO-PR 54321",
        "cro_uf": "PR",
        "specialty": "Implantodontia",
        "utm_source": "google_ads",
        "utm_medium": "cpc",
        "utm_campaign": "kit_cone_morse_q1"
    }

    res_sub = client.post("/api/v1/campaigns/public/lp/captacao-implantes-lead/submit", json=sub_payload)
    assert res_sub.status_code == 201
    sub_res = res_sub.json()
    assert sub_res["success"] is True
    assert sub_res["lead_id"] is not None

    # Verificar que o contato foi criado no CRM com as tags e atributos corretos
    res_contacts = client.get("/api/v1/contacts?q=Marcelo+Fagundes")
    assert res_contacts.status_code == 200
    contacts = res_contacts.json()
    assert len(contacts) >= 1
    found = next((c for c in contacts if c["email"] == "marcelo.fagundes@clinica.com.br"), None)
    assert found is not None
    assert found["cro_verified"] is True
    assert found["specialty"] == "Implantodontia"
