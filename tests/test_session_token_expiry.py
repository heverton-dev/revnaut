# -*- coding: utf-8 -*-
"""Validade do token de sessão HMAC (SESSION_TTL_SECONDS) e efeito nas rotas autenticadas."""

from __future__ import annotations

import hashlib
import hmac
import time

from fastapi.testclient import TestClient

from src.core.config import SESSION_SECRET_KEY as SECRET_KEY, SESSION_TTL_SECONDS
from src.features.auth.service import SESSION_CLOCK_SKEW_SECONDS, create_session_token, verify_session_token
from src.main import app


def _token_issued_at(user_id: str, issued_at: int) -> str:
    sig = hmac.new(SECRET_KEY.encode("utf-8"), f"{user_id}:{issued_at}".encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{user_id}.{issued_at}.{sig}"


def test_fresh_token_is_valid():
    assert verify_session_token(create_session_token("usr-superadmin-god")) == "usr-superadmin-god"


def test_token_expires_after_ttl():
    now = time.time()
    issued = int(now)
    token = _token_issued_at("usr-superadmin-god", issued)
    assert verify_session_token(token, now=issued + SESSION_TTL_SECONDS) == "usr-superadmin-god"
    assert verify_session_token(token, now=issued + SESSION_TTL_SECONDS + 1) is None


def test_token_from_the_future_is_rejected():
    now = int(time.time())
    assert verify_session_token(_token_issued_at("usr-superadmin-god", now + SESSION_CLOCK_SKEW_SECONDS + 60), now=now) is None
    assert verify_session_token(_token_issued_at("usr-superadmin-god", now + 30), now=now) == "usr-superadmin-god"


def test_tampered_or_malformed_tokens_are_rejected():
    token = create_session_token("usr-field-ricardo")
    user, ts, sig = token.split(".")
    assert verify_session_token(f"usr-superadmin-god.{ts}.{sig}") is None
    assert verify_session_token(f"{user}.{int(ts) + 1}.{sig}") is None
    assert verify_session_token(f"{user}.nao-numerico.{sig}") is None
    assert verify_session_token("sem-pontos") is None
    assert verify_session_token("") is None


def test_expired_token_is_rejected_by_market_intel_routes():
    client = TestClient(app)
    expired = _token_issued_at("usr-superadmin-god", int(time.time()) - SESSION_TTL_SECONDS - 10)
    res = client.get("/api/v1/market-intel/me", headers={"Authorization": f"Bearer {expired}"})
    assert res.status_code == 401
    ok = client.get("/api/v1/market-intel/me", headers={"Authorization": f"Bearer {create_session_token('usr-superadmin-god')}"})
    assert ok.status_code == 200
