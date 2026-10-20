# -*- coding: utf-8 -*-
"""
Autenticação obrigatória em toda a API /api/v1 (ApiAuthMiddleware), webhooks fail-closed,
isolamento de tenant, cookie de sessão restrito a GET, senhas PBKDF2 e rotação do cofre.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import time

import jwt
import pytest
from fastapi.testclient import TestClient

from src.core import config, security
from src.core.auth_middleware import HANDLER_SIGNED_WEBHOOKS, PUBLIC_ROUTES, is_public_route
from src.core.database import get_connection, init_db
from src.core.webhook_auth import PROVIDER_WEBHOOK_VERIFIERS
from src.features.auth import service as auth_service
from src.features.auth.set_password_cli import run as set_password_cli
from src.main import app
from tests.auth_helpers import SUPERADMIN_ID, bearer_headers
from tests.test_api_contracts_sync import _collect_all_api_v1_routes

anon = TestClient(app)


def _materialize(path: str) -> str:
    path = re.sub(r"\{[^}]+:path\}", "pasta/arquivo.bin", path)
    return re.sub(r"\{[^}]+\}", "x-test", path)


def _all_api_routes():
    seen = set()
    for r in _collect_all_api_v1_routes():
        for method in sorted(getattr(r, "methods", None) or []):
            if method in ("HEAD", "OPTIONS"):
                continue
            key = (method, r.path)
            if key not in seen:
                seen.add(key)
                yield key


ALL_ROUTES = sorted(_all_api_routes())
PROTECTED_ROUTES = [
    (m, p) for m, p in ALL_ROUTES
    if not is_public_route(m, _materialize(p)) and (m, p) not in PROVIDER_WEBHOOK_VERIFIERS
]


def test_inventory_is_complete_and_public_list_is_explicit():
    assert len(ALL_ROUTES) >= 240
    public = [(m, p) for m, p in ALL_ROUTES if is_public_route(m, _materialize(p))]
    assert len(public) == len(PUBLIC_ROUTES) + len(HANDLER_SIGNED_WEBHOOKS), public
    for key in PROVIDER_WEBHOOK_VERIFIERS:
        assert key in ALL_ROUTES, key


@pytest.mark.parametrize("method,path", PROTECTED_ROUTES, ids=[f"{m} {p}" for m, p in PROTECTED_ROUTES])
def test_every_protected_route_rejects_anonymous_and_forged_calls(method, path):
    url = _materialize(path)
    assert anon.request(method, url, json={}).status_code == 401
    forged = {"Authorization": f"Bearer {SUPERADMIN_ID}.{int(time.time())}.assinatura-forjada", "X-User-Id": SUPERADMIN_ID}
    assert anon.request(method, url, json={}, headers=forged).status_code == 401


def test_new_routes_are_protected_by_default():
    assert not is_public_route("GET", "/api/v1/rota-nova-qualquer")
    assert anon.get("/api/v1/rota-nova-qualquer").status_code == 401


def test_public_routes_stay_reachable_without_session():
    assert anon.get("/api/v1/health").status_code == 200
    assert anon.post("/api/v1/auth/login", json={"email": "ninguem@x.com", "password": "errada-123456"}).status_code == 401
    assert anon.post("/api/v1/auth/forgot-password", json={"email": "ninguem@x.com"}).status_code == 200
    assert anon.post("/api/v1/auth/reset-password-with-token", json={"token": "rst.x.1.y", "new_password": "x" * 14}).status_code == 400


# --------------------------------------------------------------------------------------------- webhooks

def _hmac_hex(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


@pytest.mark.parametrize("method,path", sorted(PROVIDER_WEBHOOK_VERIFIERS), ids=lambda v: str(v))
def test_provider_webhooks_reject_unsigned_calls(method, path):
    res = anon.request(method, path, content=b'{"event":"x"}', headers={"Content-Type": "application/json"})
    assert res.status_code == 401


def test_provider_webhooks_accept_valid_signatures():
    body = json.dumps({"event": "teste"}).encode()
    ct = {"Content-Type": "application/json"}
    cases = [
        ("/api/v1/webhooks/documenso/document-completed", {"X-Documenso-Secret": os.environ["DOCUMENSO_WEBHOOK_SECRET"]}),
        ("/api/v1/automations/calcom/webhook", {"X-Cal-Signature-256": _hmac_hex(os.environ["CALCOM_WEBHOOK_SECRET"], body)}),
        ("/api/v1/webhooks/listmonk", {"X-Webhook-Token": os.environ["LISTMONK_WEBHOOK_SECRET"]}),
        ("/api/v1/webhooks/listmonk/events?token=" + os.environ["LISTMONK_WEBHOOK_SECRET"], {}),
        ("/api/v1/omnichannel/webhook/evolution", {"X-Hub-Signature-256": "sha256=" + _hmac_hex(os.environ["OMNICHANNEL_WEBHOOK_SECRET"], body)}),
    ]
    for url, headers in cases:
        res = anon.post(url, content=body, headers={**ct, **headers})
        assert res.status_code != 401, (url, res.text)
        wrong = {k: (v[:-2] + "00") for k, v in headers.items()}
        if wrong:
            assert anon.post(url, content=body, headers={**ct, **wrong}).status_code == 401, url


def test_livekit_webhook_requires_server_signed_jwt():
    from src.features.communications.livekit_service import LIVEKIT_API_KEY, LIVEKIT_API_SECRET

    body = json.dumps({"event": "room_finished", "room": {"name": "sala"}}).encode()
    digest = base64.b64encode(hashlib.sha256(body).digest()).decode()
    good = jwt.encode({"iss": LIVEKIT_API_KEY, "sha256": digest, "exp": int(time.time()) + 60}, LIVEKIT_API_SECRET, algorithm="HS256")
    bad = jwt.encode({"iss": LIVEKIT_API_KEY, "sha256": digest}, "outra-chave", algorithm="HS256")
    tampered = jwt.encode({"iss": LIVEKIT_API_KEY, "sha256": "AAAA"}, LIVEKIT_API_SECRET, algorithm="HS256")
    url = "/api/v1/communications/webhooks/livekit"
    assert anon.post(url, content=body, headers={"Authorization": good, "Content-Type": "application/json"}).status_code != 401
    assert anon.post(url, content=body, headers={"Authorization": bad, "Content-Type": "application/json"}).status_code == 401
    assert anon.post(url, content=body, headers={"Authorization": tampered, "Content-Type": "application/json"}).status_code == 401


def test_webhooks_fail_closed_without_configured_secret(monkeypatch):
    monkeypatch.setenv("DOCUMENSO_WEBHOOK_SECRET", "")
    res = anon.post("/api/v1/webhooks/documenso/document-completed", json={}, headers={"X-Documenso-Secret": ""})
    assert res.status_code == 401
    monkeypatch.setenv("OMNICHANNEL_WEBHOOK_SECRET", "")
    body = b"{}"
    sig = _hmac_hex("", body)
    assert anon.post("/api/v1/webhooks/evolution", content=body, headers={"X-Hub-Signature-256": sig, "Content-Type": "application/json"}).status_code == 401


def test_interface_simulation_uses_session_instead_of_signature():
    res = anon.post("/api/v1/automations/calcom/webhook", json={"triggerEvent": "PING", "payload": {}}, headers=bearer_headers())
    assert res.status_code != 401


# --------------------------------------------------------------------------------------------- tenant e cookie

def test_foreign_tenant_in_query_header_or_body_is_forbidden():
    auth = bearer_headers()
    assert anon.get("/api/v1/dentgo/hubs?account_id=tenant-alheio", headers=auth).status_code == 403
    assert anon.get("/api/v1/dentgo/hubs", headers={**auth, "X-Account-ID": "tenant-alheio"}).status_code == 403
    res = anon.post("/api/v1/dentgo/hubs", json={"account_id": "tenant-alheio", "name": "Hub"}, headers=auth)
    assert res.status_code == 403
    assert anon.get("/api/v1/dentgo/hubs", headers=auth).status_code == 200


def test_session_cookie_only_authenticates_safe_methods():
    browser = TestClient(app, base_url="https://testserver")
    first = browser.get("/api/v1/dentgo/hubs", headers=bearer_headers())
    assert first.status_code == 200
    cookie = first.headers.get("set-cookie", "")
    assert cookie.startswith(f"{config.SESSION_COOKIE_NAME}=") and "HttpOnly" in cookie and "SameSite=Lax" in cookie
    assert "Path=/api/v1" in cookie

    assert browser.get("/api/v1/dentgo/hubs").status_code == 200  # <img>/<a>/download via cookie
    assert browser.post("/api/v1/dentgo/hubs", json={"name": "Hub via cookie"}).status_code == 401  # mutação exige Bearer
    me = browser.get("/api/v1/auth/me")
    assert me.status_code == 200 and me.json()["id"] == SUPERADMIN_ID


def test_login_sets_and_logout_clears_session_cookie():
    login_pwd = "Senha-Login-Cookie-2026!"
    auth_service.set_user_password("usr-field-ricardo", login_pwd)
    browser = TestClient(app, base_url="https://testserver")
    res = browser.post("/api/v1/auth/login", json={"email": "ricardo.campo@salesrocketbrasil.com.br", "password": login_pwd})
    assert res.status_code == 200
    assert config.SESSION_COOKIE_NAME in res.headers.get("set-cookie", "")
    assert "password_hash" not in res.json()["user"]
    out = browser.post("/api/v1/auth/logout")
    assert out.status_code == 200
    assert f'{config.SESSION_COOKIE_NAME}=""' in out.headers.get("set-cookie", "") or "Max-Age=0" in out.headers.get("set-cookie", "")


def test_cors_only_allows_configured_origins():
    evil = anon.options("/api/v1/deals", headers={"Origin": "https://site-malicioso.example", "Access-Control-Request-Method": "GET"})
    assert evil.headers.get("access-control-allow-origin") is None
    ok_origin = config.CORS_ALLOWED_ORIGINS[0]
    good = anon.options("/api/v1/deals", headers={"Origin": ok_origin, "Access-Control-Request-Method": "GET"})
    assert good.headers.get("access-control-allow-origin") == ok_origin


def test_openapi_declares_bearer_security():
    schema = anon.get("/openapi.json").json()
    assert schema["components"]["securitySchemes"]["SessionBearer"]["scheme"] == "bearer"
    assert {"SessionBearer": []} in schema["security"]


# --------------------------------------------------------------------------------------------- senhas

def test_passwords_use_salted_pbkdf2_and_legacy_hashes_are_upgraded_on_login():
    h1, h2 = auth_service.hash_password("Senha-Forte-2026!"), auth_service.hash_password("Senha-Forte-2026!")
    assert h1.startswith("pbkdf2_sha256$") and h1 != h2
    assert auth_service.verify_password("Senha-Forte-2026!", h1)[0] is True
    assert auth_service.verify_password("errada", h1)[0] is False

    legacy = hashlib.sha256(b"Legada-Valida-2026!").hexdigest()
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = 'usr-inside-camila'", (legacy,))
        conn.commit()
    finally:
        conn.close()
    res = anon.post("/api/v1/auth/login", json={"email": "camila.atendimento@salesrocketbrasil.com.br", "password": "Legada-Valida-2026!"})
    assert res.status_code == 200
    conn = get_connection()
    try:
        upgraded = conn.execute("SELECT password_hash FROM users WHERE id = 'usr-inside-camila'").fetchone()[0]
    finally:
        conn.close()
    assert upgraded.startswith("pbkdf2_sha256$")


def test_superadmin_backdoor_passwords_are_gone():
    for pwd in ("admin", "admin123", "123456", "revnault123"):
        res = anon.post("/api/v1/auth/login", json={"email": "hevertoneduardoperes@gmail.com", "password": pwd})
        assert res.status_code in (401, 429), pwd


def test_production_blocks_compromised_passwords(monkeypatch):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = 'usr-log-marcos'", (hashlib.sha256(b"admin123").hexdigest(),)
        )
        conn.commit()
    finally:
        conn.close()
    monkeypatch.setenv("REVNAULT_ENV", "production")
    res = anon.post("/api/v1/auth/login", json={"email": "marcos.logistica@salesrocketbrasil.com.br", "password": "admin123"})
    assert res.status_code == 403 and "bloqueada" in res.json()["detail"]
    with pytest.raises(Exception):
        auth_service.set_user_password("usr-log-marcos", "admin123")
    with pytest.raises(Exception):
        auth_service.set_user_password("usr-log-marcos", "curta")


def test_init_db_no_longer_overwrites_passwords():
    auth_service.set_user_password("usr-support-juliana", "Senha-Juliana-Persistente-2026!")
    init_db()
    conn = get_connection()
    try:
        stored = conn.execute("SELECT password_hash FROM users WHERE id = 'usr-support-juliana'").fetchone()[0]
    finally:
        conn.close()
    assert auth_service.verify_password("Senha-Juliana-Persistente-2026!", stored)[0] is True


def test_set_password_cli_reads_password_without_echo():
    answers = iter(["Senha-Pelo-Servidor-2026!", "Senha-Pelo-Servidor-2026!"])
    out = []
    assert set_password_cli(["roberto.gerente@salesrocketbrasil.com.br"], prompt=lambda _: next(answers), out=out.append) == 0
    conn = get_connection()
    try:
        stored = conn.execute("SELECT password_hash FROM users WHERE id = 'usr-manager-roberto'").fetchone()[0]
    finally:
        conn.close()
    assert auth_service.verify_password("Senha-Pelo-Servidor-2026!", stored)[0] is True

    mismatch = iter(["Senha-Pelo-Servidor-2026!", "Diferente-2026-xxxx"])
    assert set_password_cli(["roberto.gerente@salesrocketbrasil.com.br"], prompt=lambda _: next(mismatch), out=out.append) == 1
    weak = iter(["admin123", "admin123"])
    assert set_password_cli(["roberto.gerente@salesrocketbrasil.com.br"], prompt=lambda _: next(weak), out=out.append) == 1
    assert set_password_cli(["sem-arroba"], prompt=lambda _: "", out=out.append) == 2


def test_production_refuses_default_or_weak_secrets(monkeypatch):
    monkeypatch.setenv("REVNAULT_ENV", "production")
    monkeypatch.setattr(config, "SESSION_SECRET_KEY", config.LEGACY_DEFAULT_SECRET_KEY)
    monkeypatch.setattr(config, "VAULT_SECRET_KEY", "x" * 40)
    with pytest.raises(RuntimeError):
        config.assert_production_secrets()
    monkeypatch.setattr(config, "SESSION_SECRET_KEY", "s" * 48)
    config.assert_production_secrets()
    monkeypatch.delenv("REVNAULT_ENV")
    monkeypatch.setattr(config, "SESSION_SECRET_KEY", config.LEGACY_DEFAULT_SECRET_KEY)
    config.assert_production_secrets()


# --------------------------------------------------------------------------------------------- cofre

def test_vault_rotation_reencrypts_legacy_ciphertexts(monkeypatch):
    legacy_secret = "chave-legada-de-teste-0123456789abcdef"
    new_secret = "chave-nova-do-cofre-0123456789abcdefgh"
    monkeypatch.setattr(security, "SECRET_KEY", legacy_secret)
    monkeypatch.setattr(security, "VAULT_SECRET_KEY", legacy_secret)
    legacy_ciphertext = security.encrypt_secret("token-erp-super-secreto")

    monkeypatch.setattr(security, "VAULT_SECRET_KEY", new_secret)
    assert security.decrypt_secret(legacy_ciphertext) == "token-erp-super-secreto"  # leitura durante a transição

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO tenant_credentials (id, account_id, service_name, credential_type, encrypted_payload) "
            "VALUES ('cred-rotacao-teste', '0f14ffff', 'erp', 'api_key', ?)",
            (legacy_ciphertext,),
        )
        conn.commit()
        stats = security.rotate_vault_encryption(conn)
        assert stats["rotated"] >= 1
        rotated = conn.execute("SELECT encrypted_payload FROM tenant_credentials WHERE id = 'cred-rotacao-teste'").fetchone()[0]
        assert rotated != legacy_ciphertext
        assert security._decrypt_with(security._derive_aes_key(new_secret), rotated) == "token-erp-super-secreto"
        again = security.rotate_vault_encryption(conn)
        assert again["rotated"] == 0
    finally:
        conn.execute("DELETE FROM tenant_credentials WHERE id = 'cred-rotacao-teste'")
        conn.commit()
        conn.close()
