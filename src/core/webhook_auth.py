# -*- coding: utf-8 -*-
"""
Verificação nativa de webhooks inbound por provedor (fail-closed).

Sem segredo configurado no ambiente, a chamada do provedor é sempre recusada.
Os segredos são lidos a cada chamada para permitir rotação sem reinício do processo.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from typing import Callable, Dict, Mapping

from src.core import config


def _secret(env_name: str) -> str:
    return os.getenv(env_name, getattr(config, env_name, "")) or ""


def _equals(a: str, b: str) -> bool:
    return bool(a) and bool(b) and hmac.compare_digest(a.strip(), b.strip())


def _hex_hmac(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def verify_documenso(headers: Mapping[str, str], body: bytes, query: Mapping[str, str]) -> bool:
    """Documenso envia o segredo configurado no webhook no header X-Documenso-Secret."""
    return _equals(headers.get("x-documenso-secret", ""), _secret("DOCUMENSO_WEBHOOK_SECRET"))


def verify_calcom(headers: Mapping[str, str], body: bytes, query: Mapping[str, str]) -> bool:
    """Cal.com assina o corpo com HMAC-SHA256 (hex) no header X-Cal-Signature-256."""
    secret = _secret("CALCOM_WEBHOOK_SECRET")
    if not secret:
        return False
    return _equals(headers.get("x-cal-signature-256", "").lower(), _hex_hmac(secret, body))


def verify_listmonk(headers: Mapping[str, str], body: bytes, query: Mapping[str, str]) -> bool:
    """Listmonk não assina webhooks: token compartilhado em X-Webhook-Token ou ?token= na URL cadastrada."""
    secret = _secret("LISTMONK_WEBHOOK_SECRET")
    return _equals(headers.get("x-webhook-token", ""), secret) or _equals(query.get("token", ""), secret)


def verify_omnichannel_hmac(headers: Mapping[str, str], body: bytes, query: Mapping[str, str]) -> bool:
    """Evolution API: HMAC-SHA256 do corpo em X-Evolution-Signature ou X-Hub-Signature-256 (prefixo sha256= opcional)."""
    secret = _secret("OMNICHANNEL_WEBHOOK_SECRET")
    sig = headers.get("x-evolution-signature") or headers.get("x-hub-signature-256") or ""
    if not secret or not sig:
        return False
    sig = sig.strip()
    if sig.lower().startswith("sha256="):
        sig = sig.split("=", 1)[1]
    return _equals(sig.lower(), _hex_hmac(secret, body))


def verify_livekit(headers: Mapping[str, str], body: bytes, query: Mapping[str, str]) -> bool:
    """
    LiveKit envia um JWT HS256 (assinado com a API secret do servidor) no header Authorization,
    com claim 'sha256' = base64(sha256(corpo)) e 'iss' = API key.
    """
    import jwt

    from src.features.communications.livekit_service import LIVEKIT_API_KEY, LIVEKIT_API_SECRET

    token = headers.get("authorization", "").strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    if not token or not LIVEKIT_API_SECRET:
        return False
    try:
        claims = jwt.decode(token, LIVEKIT_API_SECRET, algorithms=["HS256"], options={"verify_aud": False})
    except Exception:
        return False
    if LIVEKIT_API_KEY and claims.get("iss") != LIVEKIT_API_KEY:
        return False
    expected = base64.b64encode(hashlib.sha256(body).digest()).decode()
    return _equals(str(claims.get("sha256", "")), expected)


Verifier = Callable[[Mapping[str, str], bytes, Mapping[str, str]], bool]

# (método, caminho) -> verificador do provedor
PROVIDER_WEBHOOK_VERIFIERS: Dict[tuple, Verifier] = {
    ("POST", "/api/v1/webhooks/documenso/document-completed"): verify_documenso,
    ("POST", "/api/v1/communications/webhooks/livekit"): verify_livekit,
    ("POST", "/api/v1/communications/livekit/webhook"): verify_livekit,
    ("POST", "/api/v1/campaigns/webhooks/listmonk"): verify_listmonk,
    ("POST", "/api/v1/webhooks/listmonk"): verify_listmonk,
    ("POST", "/api/v1/webhooks/listmonk/events"): verify_listmonk,
    ("POST", "/api/v1/automations/calcom/webhook"): verify_calcom,
    ("POST", "/api/v1/omnichannel/webhook/evolution"): verify_omnichannel_hmac,
}
