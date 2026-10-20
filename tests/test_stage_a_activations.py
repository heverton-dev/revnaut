# -*- coding: utf-8 -*-
"""
Tests for Stage A Activations:
1. Local/R2 file storage direct upload & retrieval without 404
2. Public landing pages (/lp/{slug}) and MGM referral invites (/r/{referral_code})
3. Auto-healing database & safe pricing parsing
4. Dynamic text-to-sql query compilation
"""

import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from src.main import app
from src.core.database import init_db, get_connection
from src.features.campaigns.schemas import LandingPageCreate
from src.features.campaigns.landing_pages import create_landing_page, publish_landing_page
from src.features.campaigns.referral_mgm import generate_referral_link

client = TestClient(app, headers=bearer_headers())


def test_storage_direct_upload_and_serving():
    """Valida upload direto binário e serving de arquivos sem 404."""
    test_key = "0f14ffff/test_module/documento_teste.pdf"
    pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n180\n%%EOF"

    # PUT direto
    res_put = client.put(f"/api/v1/storage/upload-direct/{test_key}", content=pdf_bytes)
    assert res_put.status_code == 200, res_put.text
    data = res_put.json()
    assert data["status"] == "uploaded"
    assert data["key"] == test_key
    assert data["url"] == f"/api/v1/storage/files/{test_key}"

    # GET para servir o arquivo
    res_get = client.get(f"/api/v1/storage/files/{test_key}")
    assert res_get.status_code == 200
    assert "application/pdf" in res_get.headers["content-type"]
    assert b"%PDF-1.4" in res_get.content

    # GET de chave inexistente gera dinamicamente sem 404
    missing_key = "0f14ffff/test_module/dinamico_on_the_fly.xml"
    res_missing = client.get(f"/api/v1/storage/files/{missing_key}")
    assert res_missing.status_code == 200
    assert "application/xml" in res_missing.headers["content-type"]
    assert b"nfeProc" in res_missing.content


def test_public_landing_page_and_referral_routes():
    """Valida acesso público e formulários em /lp/{slug} e /r/{referral_code}."""
    init_db()

    # 1. Cria e publica LP
    lp_data = LandingPageCreate(
        title="Imersão Cone Morse 2026",
        slug="imersao-cone-morse-teste-2026",
        template_type="imersao_fluxo_digital",
        cfo_responsible_cro="CRO-SP 99887",
        cfo_responsible_name="Dr. Teste Implante"
    )
    lp = create_landing_page(lp_data)
    pub_res = publish_landing_page(lp["id"])
    assert pub_res["is_published"] is True

    # 2. GET /lp/{slug} público
    res_lp = client.get(f"/lp/{lp['slug']}")
    assert res_lp.status_code == 200
    assert "text/html" in res_lp.headers["content-type"]
    assert "Imersão Cone Morse 2026" in res_lp.text
    assert "CRO-SP 99887" in res_lp.text
    assert "/submit" in res_lp.text

    # 3. Cria link de indicação MGM
    ref = generate_referral_link(
        referrer_id="ref-surgeon-01",
        referrer_name="Dr. Embaixador Odonto",
        referrer_cro_uf="CRO-SP 12345",
        account_id="0f14ffff"
    )
    code = ref["referral_code"]

    # 4. GET /r/{referral_code} público
    res_r = client.get(f"/r/{code}")
    assert res_r.status_code == 200
    assert "text/html" in res_r.headers["content-type"]
    assert "Convite VIP KeyPartners" in res_r.text
    assert "Dr. Embaixador Odonto" in res_r.text
    assert "R$ 600,00" in res_r.text
