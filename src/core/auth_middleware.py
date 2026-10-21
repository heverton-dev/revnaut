# -*- coding: utf-8 -*-
"""
Middleware ASGI de Autenticação e Isolamento de Tenant para /api/v1/* (secure by default).

- Toda rota /api/v1 exige sessão válida, exceto a allowlist explícita PUBLIC_ROUTES.
- Sessão: token Bearer HMAC (com validade) no header Authorization; o cookie HttpOnly de sessão
  só é aceito em GET/HEAD (arquivos em <img>, <audio> e downloads), nunca em métodos mutáveis.
- Webhooks de provedores: assinatura nativa do provedor (src.core.webhook_auth) ou sessão válida
  (botões de simulação da interface). Webhooks que já validam HMAC no handler passam direto.
- Tenant: account_id em query, header X-Account-ID ou corpo JSON diferente do tenant do usuário
  autenticado retorna 403; sem account_id na query, o tenant do usuário é injetado.
"""

from __future__ import annotations

import json
import re
from http.cookies import SimpleCookie
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple
from urllib.parse import parse_qsl, urlencode

from src.core import config
from src.core.database import get_connection
from src.core.webhook_auth import PROVIDER_WEBHOOK_VERIFIERS

API_PREFIX = "/api/v1"
MAX_INSPECTED_JSON_BYTES = 2 * 1024 * 1024

# Rotas públicas por desenho (método, regex do caminho completo)
PUBLIC_ROUTES: Tuple[Tuple[str, str], ...] = (
    ("GET", r"/api/v1/health"),
    ("POST", r"/api/v1/auth/login"),
    ("POST", r"/api/v1/auth/logout"),
    ("POST", r"/api/v1/auth/forgot-password"),
    ("POST", r"/api/v1/auth/reset-password-with-token"),
    ("POST", r"/api/v1/campaigns/public/lp/[^/]+/submit"),
    ("POST", r"/api/v1/campaigns/referral/register"),
)

# Webhooks cujo handler já valida HMAC do provedor (OMNICHANNEL_WEBHOOK_SECRET)
HANDLER_SIGNED_WEBHOOKS: Tuple[Tuple[str, str], ...] = (
    ("POST", r"/api/v1/webhooks/evolution"),
    ("POST", r"/api/v1/webhooks/chatwoot"),
    ("POST", r"/api/v1/webhooks/mautic"),
    ("POST", r"/api/v1/webhooks/mautic/campaign-action"),
)

_PUBLIC_RE = [(m, re.compile(p + r"/?$")) for m, p in PUBLIC_ROUTES + HANDLER_SIGNED_WEBHOOKS]

ASGIApp = Callable[[Dict[str, Any], Callable[[], Awaitable[Dict[str, Any]]], Callable[[Dict[str, Any]], Awaitable[None]]], Awaitable[None]]


def is_public_route(method: str, path: str) -> bool:
    return any(m == method and rx.match(path) for m, rx in _PUBLIC_RE)


def _headers(scope: Dict[str, Any]) -> Dict[str, str]:
    return {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers", [])}


def _session_token(headers: Dict[str, str], method: str) -> Tuple[Optional[str], str]:
    auth = headers.get("authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip(), "bearer"
    if method in ("GET", "HEAD") and "cookie" in headers:
        jar = SimpleCookie()
        try:
            jar.load(headers["cookie"])
        except Exception:
            return None, ""
        morsel = jar.get(config.SESSION_COOKIE_NAME)
        if morsel and morsel.value:
            return morsel.value, "cookie"
    return None, ""


def _authenticated_user(token: Optional[str]) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    from src.features.auth.service import verify_session_token

    user_id = verify_session_token(token)
    if not user_id:
        return None
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, account_id, COALESCE(is_active, 1) AS is_active FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()
    if not row or not row["is_active"]:
        return None
    return dict(row)


async def _json_response(send, status: int, detail: Any, extra_headers: Optional[List[Tuple[bytes, bytes]]] = None) -> None:
    body = json.dumps({"detail": detail}, ensure_ascii=False).encode("utf-8")
    headers = [(b"content-type", b"application/json; charset=utf-8"), (b"content-length", str(len(body)).encode())]
    headers.extend(extra_headers or [])
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": body})


async def _read_body(receive) -> Tuple[bytes, Callable[[], Awaitable[Dict[str, Any]]]]:
    chunks: List[bytes] = []
    more = True
    while more:
        message = await receive()
        if message["type"] != "http.request":
            break
        chunks.append(message.get("body", b""))
        more = message.get("more_body", False)
    body = b"".join(chunks)
    replayed = False

    async def replay() -> Dict[str, Any]:
        nonlocal replayed
        if not replayed:
            replayed = True
            return {"type": "http.request", "body": body, "more_body": False}
        return await receive()

    return body, replay


def session_cookie_header(token: str) -> Tuple[bytes, bytes]:
    parts = [
        f"{config.SESSION_COOKIE_NAME}={token}",
        f"Path={API_PREFIX}",
        f"Max-Age={config.SESSION_TTL_SECONDS}",
        "HttpOnly",
        "SameSite=Lax",
    ]
    if config.SESSION_COOKIE_SECURE:
        parts.append("Secure")
    return b"set-cookie", "; ".join(parts).encode("latin-1")


class ApiAuthMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope.get("type") != "http" or not scope.get("path", "").startswith(API_PREFIX):
            await self.app(scope, receive, send)
            return
        method = scope.get("method", "GET").upper()
        path = scope["path"]
        if method == "OPTIONS" or is_public_route(method, path):
            await self.app(scope, receive, send)
            return

        headers = _headers(scope)
        query = dict(parse_qsl(scope.get("query_string", b"").decode("latin-1"), keep_blank_values=True))
        token, source = _session_token(headers, method)
        user = _authenticated_user(token)

        verifier = PROVIDER_WEBHOOK_VERIFIERS.get((method, path.rstrip("/")))
        if verifier is not None and user is None:
            body, receive = await _read_body(receive)
            if not verifier(headers, body, query):
                await _json_response(send, 401, "Assinatura do webhook inválida ou segredo não configurado.")
                return
            await self.app(scope, receive, send)
            return

        if user is None:
            await _json_response(
                send,
                401,
                "Não autenticado. Envie Authorization: Bearer <token de sessão> (sessão expirada exige novo login).",
                [(b"www-authenticate", b"Bearer")],
            )
            return

        account_id = user["account_id"]
        claimed = [query.get("account_id"), headers.get("x-account-id")]
        if any(c and c != account_id for c in claimed):
            await _json_response(send, 403, "Acesso negado a dados de outro tenant.")
            return

        # Fase 6 — gate de grants de navegação em APIs de domínio (banco)
        from src.features.access.service import (
            required_routes_for_path,
            resolve_role_id_from_name,
            user_can_access_routes,
        )
        from src.features.auth.service import get_user_profile

        required = required_routes_for_path(path)
        if required is not None:
            effective_id = (headers.get("x-user-id") or "").strip() or user["id"]
            profile = get_user_profile(effective_id) or {}
            # Impersonation só se o dono do token for superadmin
            owner_profile = get_user_profile(user["id"]) or {}
            if effective_id != user["id"] and not owner_profile.get("is_superadmin"):
                effective_id = user["id"]
                profile = owner_profile
            grant_user = {
                "id": profile.get("id", effective_id),
                "role_id": profile.get("role_id") or resolve_role_id_from_name(
                    profile.get("role") or ""
                ),
                "role": profile.get("role") or "",
                "is_superadmin": bool(profile.get("is_superadmin")),
            }
            if not user_can_access_routes(
                grant_user, profile.get("account_id") or account_id, required
            ):
                await _json_response(
                    send,
                    403,
                    "Acesso negado: este módulo não está liberado para o seu cargo.",
                )
                return

        content_type = headers.get("content-type", "")
        if method in ("POST", "PUT", "PATCH", "DELETE") and "application/json" in content_type:
            body, receive = await _read_body(receive)
            if body and len(body) <= MAX_INSPECTED_JSON_BYTES:
                try:
                    payload = json.loads(body)
                except ValueError:
                    payload = None
                if isinstance(payload, dict) and payload.get("account_id") not in (None, "", account_id):
                    await _json_response(send, 403, "Acesso negado a dados de outro tenant.")
                    return

        if "account_id" not in query:
            pairs = parse_qsl(scope.get("query_string", b"").decode("latin-1"), keep_blank_values=True)
            pairs.append(("account_id", account_id))
            scope = dict(scope)
            scope["query_string"] = urlencode(pairs).encode("latin-1")

        if source == "cookie":
            # GET/HEAD via cookie (img/audio/download): repassa o token já validado às dependências das rotas
            scope = dict(scope)
            scope["headers"] = [(k, v) for k, v in scope.get("headers", []) if k.lower() != b"authorization"]
            scope["headers"].append((b"authorization", f"Bearer {token}".encode("latin-1")))

        if source == "bearer":
            cookie_header = session_cookie_header(token)

            async def send_with_cookie(message):
                if message["type"] == "http.response.start":
                    message = dict(message)
                    message["headers"] = list(message.get("headers", [])) + [cookie_header]
                await send(message)

            await self.app(scope, receive, send_with_cookie)
            return

        await self.app(scope, receive, send)
