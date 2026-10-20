# -*- coding: utf-8 -*-
"""
Testes TDD para TICKET-39: Servidor de Imagiologia Médica Orthanc DICOM
e Visualizador 3D de Tomografias / STL no Cloudflare R2 com Anonimização LGPD.
"""

import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from fastapi import HTTPException

from src.main import app
from src.core.database import init_db, get_connection
from src.features.intelligence.orthanc_dicom import OrthancDicomClient


@pytest.fixture(autouse=True)
def setup_clean_imaging_database():
    """Garante tabela de estudos limpa e tenants registrados para testes determinísticos."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM imaging_studies")
        # Registra contas de teste para integridade referencial da foreign key
        test_tenants = [
            ("tenant-clinica-alphaville", "Clínica Alphaville"),
            ("tenant-clinica-sorriso", "Clínica Sorriso"),
            ("tenant-hospital-a", "Hospital A"),
            ("tenant-hospital-b", "Hospital B"),
            ("tenant-odonto-master", "Odonto Master"),
            ("outro-tenant-invasor", "Tenant Invasor"),
            ("0f14ffff", "Default Tenant"),
        ]
        for t_id, t_name in test_tenants:
            cur.execute(
                "INSERT OR IGNORE INTO accounts (id, name, plan) VALUES (?, ?, 'enterprise')",
                (t_id, t_name)
            )
        conn.commit()
    finally:
        conn.close()


def test_orthanc_client_upload_presign():
    """Valida geração de URL pré-assinada no R2 e anonimização LGPD do paciente."""
    client = OrthancDicomClient()
    account_id = "tenant-clinica-alphaville"

    # 1. Upload de Tomografia Cone Beam
    dicom_presign = client.create_upload_presign(
        file_name="mandibula_tomografia_conebeam",
        study_type="DICOM_CBCT",
        jaw_type="MANDIBULA",
        slice_count=128,
        patient_name="Carlos Eduardo Silva",
        deal_id="deal-cirurgia-001",
        ticket_id="ticket-suporte-001",
        implant_site="36",
        anonymize_lgpd=True,
        account_id=account_id
    )

    assert dicom_presign["study_id"].startswith("study-")
    assert "upload_presigned_url" in dicom_presign
    assert dicom_presign["anonymized"] is True
    # O identificador do paciente deve ser pseudonimizado (não pode conter o nome original)
    assert "Carlos" not in dicom_presign["patient_anonymized_id"]
    assert dicom_presign["patient_anonymized_id"].startswith("ANON-PAC-")
    assert dicom_presign["r2_storage_key"].endswith(".dcm")
    assert "imaging/dicom_cbct" in dicom_presign["r2_storage_key"]
    assert dicom_presign["orthanc_dicom_port"] == 4242

    # 2. Upload de Escaneamento Intraoral STL
    stl_presign = client.create_upload_presign(
        file_name="arco_superior_escaneado.stl",
        study_type="INTRAORAL_STL",
        jaw_type="MAXILA",
        slice_count=1,
        patient_name="Ana Paula Ferreira",
        deal_id="deal-cirurgia-002",
        anonymize_lgpd=True,
        account_id=account_id
    )

    assert stl_presign["study_type"] == "INTRAORAL_STL"
    assert stl_presign["r2_storage_key"].endswith(".stl")
    assert "imaging/intraoral_stl" in stl_presign["r2_storage_key"]


def test_orthanc_client_viewer_session():
    """Valida emissão de token de visualização 3D, métricas ósseas e streaming."""
    client = OrthancDicomClient()
    account_id = "tenant-clinica-sorriso"

    presign = client.create_upload_presign(
        file_name="conebeam_panoramico.dcm",
        study_type="DICOM_CBCT",
        jaw_type="MANDIBULA",
        slice_count=96,
        patient_name="Roberto Santos",
        implant_site="46",
        account_id=account_id
    )
    study_id = presign["study_id"]

    viewer_session = client.generate_viewer_session(study_id=study_id, account_id=account_id)

    assert viewer_session["study_id"] == study_id
    assert viewer_session["viewer_token"].startswith("vt_")
    assert "stream" in viewer_session["viewer_stream_url"]
    assert "token=" in viewer_session["r2_public_url"]
    assert viewer_session["jaw_type"] == "MANDIBULA"
    assert viewer_session["bone_density_estimate"] == "D1_DENSO"
    assert viewer_session["bone_thickness_mm"] > 8.0
    assert viewer_session["recommended_implant_diameter_mm"] == 4.3


def test_anatomical_jaw_density_and_implant_calibration():
    """Valida calibração anatômica de densidade óssea e dimensões do implante."""
    client = OrthancDicomClient()

    # Mandíbula posterior -> Osso denso D1/D2, maior diâmetro (4.3mm)
    m_metrics = client.estimate_bone_metrics(jaw_type="MANDIBULA", implant_site="46")
    assert m_metrics["bone_density_estimate"] == "D1_DENSO"
    assert m_metrics["recommended_implant_diameter_mm"] == 4.3

    # Maxila posterior -> Osso trabeculado D3, diâmetro médio (3.75mm)
    max_metrics = client.estimate_bone_metrics(jaw_type="MAXILA", implant_site="16")
    assert max_metrics["bone_density_estimate"] == "D3_POROSO"
    assert max_metrics["recommended_implant_diameter_mm"] == 3.75

    # Região estética anterior (incisivo central 11) -> Calibrado para perfil estético estreito (3.5mm)
    ant_metrics = client.estimate_bone_metrics(jaw_type="MAXILA", implant_site="11")
    assert ant_metrics["recommended_implant_diameter_mm"] == 3.5


def test_multitenant_isolation_and_security():
    """Valida bloqueio rigoroso de acesso entre tenants (403 Forbidden)."""
    client = OrthancDicomClient()
    tenant_a = "tenant-hospital-a"
    tenant_b = "tenant-hospital-b"

    presign = client.create_upload_presign(
        file_name="tomografia_sigilosa.dcm",
        study_type="DICOM_CBCT",
        account_id=tenant_a
    )
    study_id = presign["study_id"]

    # Consulta por tenant dono -> Sucesso
    study_data = client.get_study(study_id=study_id, account_id=tenant_a)
    assert study_data["id"] == study_id

    # Tentativa de acesso por outro tenant -> Deve ser bloqueado com 403
    with pytest.raises(HTTPException) as exc_info:
        client.get_study(study_id=study_id, account_id=tenant_b)
    assert exc_info.value.status_code == 403

    # Tentativa de gerar viewer token por outro tenant -> Deve ser bloqueado com 403
    with pytest.raises(HTTPException) as exc_info_vt:
        client.generate_viewer_session(study_id=study_id, account_id=tenant_b)
    assert exc_info_vt.value.status_code == 403

    # Estudo inexistente -> Deve retornar 404
    with pytest.raises(HTTPException) as exc_info_nf:
        client.get_study(study_id="study-inexistente", account_id=tenant_a)
    assert exc_info_nf.value.status_code == 404


def test_api_endpoints_orthanc_imaging():
    """Valida endpoints HTTP do FastAPI para Imagiologia Médica Orthanc e aliases."""
    test_client = TestClient(app, headers=bearer_headers())
    account_id = "0f14ffff"  # a API vincula o tenant ao usuário autenticado

    # 1. POST /api/v1/imaging/studies/upload-presign
    upload_payload = {
        "file_name": "exame_tomografia_3d.dcm",
        "study_type": "DICOM_CBCT",
        "jaw_type": "MAXILA",
        "slice_count": 64,
        "patient_name": "Mariana Oliveira",
        "deal_id": "deal-implante-allon4",
        "ticket_id": "ticket-cirurgia-01",
        "implant_site": "21",
        "anonymize_lgpd": True,
        "account_id": account_id
    }
    res_presign = test_client.post("/api/v1/imaging/studies/upload-presign", json=upload_payload)
    assert res_presign.status_code == 200
    presign_data = res_presign.json()
    study_id = presign_data["study_id"]
    assert "upload_presigned_url" in presign_data
    assert presign_data["patient_anonymized_id"].startswith("ANON-PAC-")

    # 2. GET /api/v1/imaging/studies/{study_id}/viewer-token
    res_token = test_client.get(
        f"/api/v1/imaging/studies/{study_id}/viewer-token",
        params={"account_id": account_id}
    )
    assert res_token.status_code == 200
    token_data = res_token.json()
    assert token_data["study_id"] == study_id
    assert "viewer_token" in token_data
    assert token_data["recommended_implant_diameter_mm"] == 3.5

    # 3. GET /api/v1/imaging/studies/{study_id}
    res_detail = test_client.get(
        f"/api/v1/imaging/studies/{study_id}",
        params={"account_id": account_id}
    )
    assert res_detail.status_code == 200
    detail_data = res_detail.json()
    assert detail_data["id"] == study_id
    assert detail_data["deal_id"] == "deal-implante-allon4"

    # 4. GET /api/v1/imaging/studies
    res_list = test_client.get(
        "/api/v1/imaging/studies",
        params={"account_id": account_id, "deal_id": "deal-implante-allon4"}
    )
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert list_data["total"] >= 1
    assert list_data["studies"][0]["id"] == study_id

    # 5. Tentativa de violação cross-tenant pela API (retorna 403)
    res_forbidden = test_client.get(
        f"/api/v1/imaging/studies/{study_id}/viewer-token",
        params={"account_id": "outro-tenant-invasor"}
    )
    assert res_forbidden.status_code == 403

    # 6. Alias sob /api/v1/intelligence/imaging/studies
    res_alias = test_client.get(
        f"/api/v1/intelligence/imaging/studies/{study_id}/viewer-token",
        params={"account_id": account_id}
    )
    assert res_alias.status_code == 200
