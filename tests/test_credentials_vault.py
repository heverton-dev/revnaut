# -*- coding: utf-8 -*-
"""
TDD for [TICKET-05] Traefik Edge Gateway, Rate Limiting & AES-256 Credentials Vault
Validates:
- AES-256-GCM symmetric encryption / decryption of sensitive secrets in memory
- Invariant: Zero plaintext secrets stored in database (encrypted_payload is always encrypted)
- Secret masking in API responses (****abcd)
- Authorized retrieval and decryption by internal services
"""

import pytest
from fastapi.testclient import TestClient
from src.core.database import get_connection, init_db
from src.core.security import encrypt_secret, decrypt_secret
from src.features.auth.service import store_tenant_credential, get_decrypted_credential, list_tenant_credentials
from src.main import app

client = TestClient(app)


def setup_module():
    init_db()


def test_aes_256_encryption_and_decryption_cycle():
    """Valida ciclo de criptografia AES-256 com chave mestre derivada via PBKDF2."""
    plaintext = "super_secret_evolution_api_token_2026_xyz123"
    ciphertext = encrypt_secret(plaintext)

    assert ciphertext != plaintext
    assert not ciphertext.startswith("super_secret")

    decrypted = decrypt_secret(ciphertext)
    assert decrypted == plaintext


def test_zero_plaintext_secrets_in_database():
    """Garante de forma determinística que a linha gravada no banco de dados não contém o segredo em texto puro."""
    tenant_id = "0f14ffff"
    service_name = "evolution_api"
    secret_value = "token_whatsapp_baileys_secret_9988"

    cred_id = store_tenant_credential(
        account_id=tenant_id,
        service_name=service_name,
        credential_type="api_token",
        secret_payload=secret_value,
        metadata={"instance": "inst_01_sp"},
    )

    # Inspeciona banco bruto
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT encrypted_payload FROM tenant_credentials WHERE id = ?", (cred_id,))
        row = cur.fetchone()
        assert row is not None
        raw_payload = row["encrypted_payload"]

        # O valor bruto gravado no banco NUNCA pode ser igual ao segredo em texto puro
        assert raw_payload != secret_value
        assert secret_value not in raw_payload

        # Descriptografia autorizada pelo serviço interno recupera o segredo original
        retrieved_secret = get_decrypted_credential(account_id=tenant_id, credential_id=cred_id)
        assert retrieved_secret == secret_value
    finally:
        conn.close()


def test_credentials_api_masks_secrets():
    """Valida mascaramento do segredo na saída da API (ex: ****9988)."""
    # 1. Cria credencial via API
    payload = {
        "service_name": "totvs_protheus",
        "credential_type": "oauth2_client_secret",
        "secret_payload": "totvs_corp_secret_key_8844",
        "metadata": {"ambiente": "producao"},
    }
    response = client.post(
        "/api/v1/auth/credentials",
        json=payload,
        headers={"X-Account-ID": "0f14ffff"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert data["masked_value"] == "****8844"
    assert "totvs_corp_secret_key" not in str(data)

    # 2. Lista credenciais via API e garante que todas saem mascaradas
    list_res = client.get(
        "/api/v1/auth/credentials",
        headers={"X-Account-ID": "0f14ffff"},
    )
    assert list_res.status_code == 200
    creds = list_res.json()
    assert isinstance(creds, list)
    target = next((c for c in creds if c["id"] == data["id"]), None)
    assert target is not None
    assert target["masked_value"] == "****8844"
