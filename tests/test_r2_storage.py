# -*- coding: utf-8 -*-
"""
TDD for [TICKET-01] Cloudflare R2 Object Storage & Presigned URLs
Validates:
- R2StorageClient presigned upload & download URL generation
- Strict multi-tenant partitioning ({tenant_id}/{module}/{yyyy}/{mm}/{uuid}.{ext})
- Rejection of prohibited / malicious executable MIME types and extensions (.exe, .sh)
- Rejection of cross-tenant key access
- FastAPI storage router endpoints (/api/v1/storage/presign-upload, presign-download)
"""

import pytest
from fastapi.testclient import TestClient
from src.core.storage import R2StorageClient, StorageSecurityException
from src.main import app

client = TestClient(app)


def test_r2_storage_key_partitioning():
    """Valida particionamento multi-tenant determinístico da chave R2."""
    storage = R2StorageClient()
    key = storage.generate_storage_key(
        tenant_id="tenant-alpha",
        module="dicom",
        filename="tomografia_mandibula.dcm",
        custom_uuid="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        year=2026,
        month=10,
    )
    assert key == "tenant-alpha/dicom/2026/10/a1b2c3d4-e5f6-7890-abcd-ef1234567890.dcm"


def test_r2_presigned_upload_url_generation():
    """Gera URL pré-assinada de upload com 900s de expiração para MIME médico/documental."""
    storage = R2StorageClient()
    key = "tenant-alpha/contracts/2026/10/termo_consignacao.pdf"
    res = storage.generate_presigned_upload_url(
        key=key,
        content_type="application/pdf",
        expires_in=900,
    )
    assert "upload_url" in res
    assert "key" in res
    assert res["key"] == key
    assert "https://" in res["upload_url"] or "http://" in res["upload_url"] or res["upload_url"].startswith("/api/v1/storage")


def test_r2_blocks_malicious_extensions():
    """Bloqueia arquivos executáveis e scripts maliciosos (.exe, .sh, .bat)."""
    storage = R2StorageClient()
    with pytest.raises(StorageSecurityException) as exc_info:
        storage.generate_storage_key(
            tenant_id="tenant-alpha",
            module="uploads",
            filename="malware.exe",
        )
    assert "extensão proibida" in str(exc_info.value).lower()

    with pytest.raises(StorageSecurityException):
        storage.generate_presigned_upload_url(
            key="tenant-alpha/uploads/2026/10/script.sh",
            content_type="application/x-sh",
        )


def test_r2_cross_tenant_access_blocked():
    """Garante bloqueio de acesso quando um tenant tenta acessar chave de outro tenant."""
    storage = R2StorageClient()
    # Chave pertence ao tenant-alpha
    foreign_key = "tenant-alpha/contracts/2026/10/secret.pdf"

    # tenant-beta tenta gerar download da chave do tenant-alpha
    with pytest.raises(StorageSecurityException) as exc_info:
        storage.validate_tenant_access(tenant_id="tenant-beta", key=foreign_key)
    assert "acesso cruzado" in str(exc_info.value).lower()


def test_storage_api_presign_endpoints():
    """Testa endpoints da API de storage com headers de autenticação/tenant."""
    # 1. Presign upload
    payload = {
        "filename": "kit_cirurgico_anvisa.pdf",
        "module": "consignments",
        "content_type": "application/pdf",
    }
    response = client.post(
        "/api/v1/storage/presign-upload",
        json=payload,
        headers={"X-Account-ID": "0f14ffff"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "upload_url" in data
    assert "key" in data
    assert data["key"].startswith("0f14ffff/consignments/")

    # 2. Presign download da mesma chave
    download_res = client.get(
        f"/api/v1/storage/presign-download?key={data['key']}",
        headers={"X-Account-ID": "0f14ffff"},
    )
    assert download_res.status_code == 200
    assert "download_url" in download_res.json()

    # 3. Tentativa de download por outro tenant (bloqueado)
    unauthorized_res = client.get(
        f"/api/v1/storage/presign-download?key={data['key']}",
        headers={"X-Account-ID": "tenant-adversary"},
    )
    assert unauthorized_res.status_code in (403, 400)
