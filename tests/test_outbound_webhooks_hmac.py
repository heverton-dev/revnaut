# -*- coding: utf-8 -*-
"""
Testes TDD para TICKET-40: Motor de Webhooks Outbound com Assinatura
Criptográfica HMAC-SHA256, Proteção Estrita contra SSRF e Circuit Breaker.
"""

import json
import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import bearer_headers
from fastapi import HTTPException

from src.main import app
from src.core.database import init_db, get_connection
from src.features.webhooks.outbound_dispatcher import (
    OutboundWebhookDispatcher,
    validate_target_url_safe,
    compute_hmac_signature,
    verify_hmac_signature,
    SSRFSecurityException,
    CircuitBreakerTrippedException,
)


@pytest.fixture(autouse=True)
def setup_clean_webhooks_database():
    """Garante tabelas de webhooks limpas para testes determinísticos."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM webhook_delivery_logs")
        cur.execute("DELETE FROM webhook_subscriptions")
        # Registra tenants de teste
        for t_id, t_name in [("0f14ffff", "Tenant Padrão"), ("tenant-alvo", "Tenant Alvo"), ("tenant-invasor", "Tenant Invasor")]:
            cur.execute("INSERT OR IGNORE INTO accounts (id, name, plan) VALUES (?, ?, 'enterprise')", (t_id, t_name))
        conn.commit()
    finally:
        conn.close()


def test_ssrf_protection_blocks_internal_and_loopback_ips():
    """Valida bloqueio rigoroso contra ataques de SSRF (Lei de Segurança)."""
    # 1. Loopbacks proibidos
    with pytest.raises(SSRFSecurityException):
        validate_target_url_safe("http://127.0.0.1:8000/webhook")

    with pytest.raises(SSRFSecurityException):
        validate_target_url_safe("http://localhost:3000/api/hook")

    with pytest.raises(SSRFSecurityException):
        validate_target_url_safe("http://0.0.0.0:8080/callback")

    # 2. Ranges privados RFC1918 e metadados de nuvem
    with pytest.raises(SSRFSecurityException):
        validate_target_url_safe("http://10.0.0.5/receiver")

    with pytest.raises(SSRFSecurityException):
        validate_target_url_safe("http://192.168.1.100:5000/event")

    with pytest.raises(SSRFSecurityException):
        validate_target_url_safe("http://169.254.169.254/latest/meta-data/")

    # 3. Esquemas não-HTTP
    with pytest.raises(SSRFSecurityException):
        validate_target_url_safe("ftp://api.externa.com/upload")

    # 4. Destino público válido aceito normalmente
    validate_target_url_safe("https://api.erp-sankhya.com.br/v1/revnault/webhooks")


def test_hmac_sha256_cryptographic_signature_calculation_and_verification():
    """Valida integridade matemática da assinatura HMAC-SHA256."""
    signing_token = "mock_wh_key_" + "test_2026"
    payload = {"event": "dentgo.order_delivered", "order_id": "ord-campinas-001"}
    body_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")

    sig_header = compute_hmac_signature(signing_token, body_bytes)
    assert sig_header.startswith("sha256=")
    assert len(sig_header) == 71  # "sha256=" (7 chars) + 64 hex chars

    # Verificação com payload idêntico -> True
    assert verify_hmac_signature(signing_token, body_bytes, sig_header) is True

    # Verificação com payload adulterado -> False
    tampered_bytes = json.dumps({"event": "dentgo.order_delivered", "order_id": "ord-hacked-999"}, sort_keys=True).encode("utf-8")
    assert verify_hmac_signature(signing_token, tampered_bytes, sig_header) is False

    # Verificação com token errado -> False
    assert verify_hmac_signature("wrong_token_test", body_bytes, sig_header) is False


def test_outbound_webhook_subscription_lifecycle():
    """Valida ciclo de vida (criação, consulta, listagem e remoção) de assinaturas."""
    dispatcher = OutboundWebhookDispatcher()
    account_id = "tenant-alvo"

    sub = dispatcher.create_subscription(
        name="ERP Sankhya Consignações",
        target_url="https://sankhya.gateway.com/webhooks/listener",
        subscribed_events=["dentgo.order_delivered", "deal.won"],
        account_id=account_id
    )

    assert sub["id"].startswith("sub-")
    assert sub["name"] == "ERP Sankhya Consignações"
    assert sub["is_active"] is True
    assert "dentgo.order_delivered" in sub["subscribed_events"]
    assert sub["signing_secret"].startswith("whsec_")

    # Consulta por ID
    fetched = dispatcher.get_subscription(sub["id"], account_id=account_id)
    assert fetched["id"] == sub["id"]

    # Tentativa de acesso por outro tenant -> 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        dispatcher.get_subscription(sub["id"], account_id="tenant-invasor")
    assert exc_info.value.status_code == 403


def test_circuit_breaker_trips_after_15_failures():
    """Valida desarme automático do circuit breaker após 15 falhas consecutivas de entrega."""
    dispatcher = OutboundWebhookDispatcher()
    account_id = "0f14ffff"

    sub = dispatcher.create_subscription(
        name="Endpoint com Falha Persistente",
        target_url="https://unstable-receiver.example.org/hook",
        subscribed_events=["*"],
        account_id=account_id
    )
    sub_id = sub["id"]

    # Simula 14 falhas consecutivas (circuit breaker ainda armado)
    for _ in range(14):
        current_sub = dispatcher.get_subscription(sub_id, account_id)
        dispatcher.deliver_to_subscription(
            subscription=current_sub,
            event_name="test.event",
            payload_data={"attempt": "retry"},
            forced_status_code=500
        )

    sub_after_14 = dispatcher.get_subscription(sub_id, account_id)
    assert sub_after_14["consecutive_failures"] == 14
    assert sub_after_14["circuit_breaker_tripped"] is False
    assert sub_after_14["is_active"] is True

    # 15ª falha -> Circuit Breaker DESARMA (is_active=False, circuit_breaker_tripped=True)
    dispatcher.deliver_to_subscription(
        subscription=sub_after_14,
        event_name="test.event",
        payload_data={"attempt": "fatal"},
        forced_status_code=503
    )

    sub_after_15 = dispatcher.get_subscription(sub_id, account_id)
    assert sub_after_15["consecutive_failures"] == 15
    assert sub_after_15["circuit_breaker_tripped"] is True
    assert sub_after_15["is_active"] is False

    # 16ª tentativa de envio com circuit breaker desarmado -> Lança CircuitBreakerTrippedException
    with pytest.raises(CircuitBreakerTrippedException):
        dispatcher.deliver_to_subscription(
            subscription=sub_after_15,
            event_name="test.event",
            payload_data={"attempt": "blocked"}
        )

    # Administrador aciona o reset manual do circuit breaker
    reset_res = dispatcher.reset_circuit_breaker(sub_id, account_id)
    assert reset_res["is_active"] is True
    assert reset_res["consecutive_failures"] == 0
    assert reset_res["circuit_breaker_tripped"] is False


def test_api_endpoints_outbound_webhooks():
    """Valida endpoints HTTP FastAPI para gestão e teste do portal de desenvolvedores."""
    test_client = TestClient(app, headers=bearer_headers())
    account_id = "0f14ffff"

    # 1. Tentativa de cadastro com URL interna (deve ser bloqueada com 400 por SSRF)
    res_ssrf = test_client.post(
        "/api/v1/webhooks/subscriptions",
        json={
            "name": "Tentativa SSRF Maliciosa",
            "target_url": "http://127.0.0.1:8000/internal-admin",
            "account_id": account_id
        }
    )
    assert res_ssrf.status_code == 400
    assert "SSRF" in res_ssrf.json()["detail"]

    # 2. Cadastro válido de assinatura com HTTPS público
    res_create = test_client.post(
        "/api/v1/webhooks/subscriptions",
        json={
            "name": "Webhook Prótese Express",
            "target_url": "https://labprotese.odonto.internal.net/events",
            "subscribed_events": ["dentgo.order_delivered"],
            "account_id": account_id
        }
    )
    assert res_create.status_code == 201
    created_sub = res_create.json()
    sub_id = created_sub["id"]
    assert "signing_secret" in created_sub

    # 3. Teste de disparo manual via API (POST /api/v1/webhooks/test-dispatch)
    res_dispatch = test_client.post(
        "/api/v1/webhooks/test-dispatch",
        json={
            "subscription_id": sub_id,
            "event_name": "dentgo.order_delivered",
            "payload_data": {"order_id": "ord-express-123", "status": "DELIVERED"},
            "account_id": account_id
        }
    )
    assert res_dispatch.status_code == 200
    dispatch_data = res_dispatch.json()
    assert dispatch_data["success"] is True
    assert dispatch_data["signature_header"].startswith("sha256=")

    # 4. Consulta de logs de auditoria (GET /api/v1/webhooks/logs)
    res_logs = test_client.get(
        "/api/v1/webhooks/logs",
        params={"account_id": account_id, "subscription_id": sub_id}
    )
    assert res_logs.status_code == 200
    logs_data = res_logs.json()
    assert logs_data["total"] >= 1
    assert logs_data["logs"][0]["event_name"] == "dentgo.order_delivered"

    # 5. Reset do circuit breaker via API (PATCH /api/v1/webhooks/subscriptions/{id}/reset-circuit)
    res_reset = test_client.patch(
        f"/api/v1/webhooks/subscriptions/{sub_id}/reset-circuit",
        params={"account_id": account_id}
    )
    assert res_reset.status_code == 200
    assert res_reset.json()["is_active"] is True
