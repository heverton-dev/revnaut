# -*- coding: utf-8 -*-
"""
Motor de Webhooks Outbound com Assinatura Criptográfica HMAC-SHA256,
Proteção Estrita contra SSRF e Circuit Breaker Automático.
"""

from __future__ import annotations
import os
import json
import uuid
import time
import hmac
import hashlib
import socket
import ipaddress
import urllib.parse
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error
from fastapi import HTTPException

from src.core.database import get_connection, init_db
from src.core.events import EventBus, StreamName, default_event_bus
from src.core.security import encrypt_secret, decrypt_secret


def _resolve_plaintext_secret(raw_secret: Optional[str], encrypted_col: Optional[str] = None) -> str:
    """Descriptografa segredo em repouso (AES-256-GCM) ou retorna plaintext legado."""
    candidate = encrypted_col or raw_secret or ""
    if not candidate:
        return ""
    if candidate.startswith("whsec_"):
        return candidate
    try:
        return decrypt_secret(candidate)
    except Exception:
        return raw_secret or candidate


class SSRFSecurityException(HTTPException):
    def __init__(self, detail: str = "SSRF Protection: Destino de rede privada ou interna não permitido"):
        super().__init__(status_code=400, detail=detail)


class CircuitBreakerTrippedException(HTTPException):
    def __init__(self, detail: str = "Circuit Breaker ativado após 15 falhas consecutivas. Assinatura suspensa."):
        super().__init__(status_code=422, detail=detail)


def validate_target_url_safe(url: str) -> None:
    """
    Inspeciona determinísticamente a URL de destino contra ataques de Server-Side Request Forgery (SSRF).
    Bloqueia estritamente endereços de loopback, ranges privados RFC1918, link-local e metadados de nuvem.
    """
    if not url or not isinstance(url, str):
        raise SSRFSecurityException("URL de webhook inválida ou ausente")

    parsed = urllib.parse.urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        raise SSRFSecurityException(f"Esquema de URL não permitido: '{parsed.scheme}'. Apenas HTTP e HTTPS são aceitos.")

    hostname = (parsed.hostname or "").lower().strip()
    if not hostname:
        raise SSRFSecurityException("Hostname ausente na URL fornecida")

    # Bloqueio imediato de nomes conhecidos de loopback e metadados de nuvem
    blocked_hosts = {
        "localhost", "127.0.0.1", "0.0.0.0", "::1",
        "169.254.169.254", "metadata.google.internal", "instance-data"
    }
    if hostname in blocked_hosts or hostname.endswith(".local") or hostname.endswith(".internal"):
        raise SSRFSecurityException(f"Destino proibido por política de segurança SSRF: '{hostname}'")

    # Resolução de DNS e validação dos IPs retornados
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)

            if (
                ip_obj.is_private or
                ip_obj.is_loopback or
                ip_obj.is_link_local or
                ip_obj.is_reserved or
                ip_obj.is_multicast
            ):
                raise SSRFSecurityException(
                    f"Acesso bloqueado por SSRF: o hostname '{hostname}' resolve para IP privado/reservado ({ip_str})"
                )
    except socket.gaierror:
        # Hostnames que não resolvem no DNS (ex: domínios de teste ou inexistentes)
        # Se for formato de IP literal inválido, bloqueia
        try:
            ip_obj = ipaddress.ip_address(hostname)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                raise SSRFSecurityException(f"IP privado direto bloqueado por SSRF: {hostname}")
        except ValueError:
            pass


def compute_hmac_signature(secret: str, payload_bytes: bytes) -> str:
    """Calcula a assinatura criptográfica HMAC-SHA256 no formato sha256={digest}."""
    sig = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return f"sha256={sig}"


def verify_hmac_signature(secret: str, payload_bytes: bytes, signature_header: str) -> bool:
    """Verifica se o cabeçalho X-RevNault-Signature bate com o HMAC-SHA256 do payload."""
    expected = compute_hmac_signature(secret, payload_bytes)
    return hmac.compare_digest(expected, signature_header)


class OutboundWebhookDispatcher:
    """
    Gerenciador e despachante de webhooks outbound com HMAC-SHA256,
    tolerância a falhas e isolamento por tenant.
    """

    MAX_CONSECUTIVE_FAILURES = 15

    def __init__(self, mock_dispatch: Optional[bool] = None):
        app_env = os.getenv("APP_ENV", "local")
        self.mock_dispatch = mock_dispatch if mock_dispatch is not None else (app_env in ("local", "test", "development"))

    def create_subscription(
        self,
        name: str,
        target_url: str,
        subscribed_events: Optional[List[str]] = None,
        signing_secret: Optional[str] = None,
        account_id: str = "0f14ffff",
    ) -> Dict[str, Any]:
        """Cadastra um novo listener/assinatura de webhook outbound com validação SSRF e segredo AES-256-GCM em repouso."""
        validate_target_url_safe(target_url)
        init_db()

        sub_id = f"sub-{uuid.uuid4().hex[:10]}"
        events = subscribed_events if (subscribed_events and len(subscribed_events) > 0) else ["*"]
        secret = signing_secret or f"whsec_{uuid.uuid4().hex}{uuid.uuid4().hex[:8]}"
        encrypted_secret = encrypt_secret(secret)

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO webhook_subscriptions (
                    id, account_id, name, target_url, subscribed_events_json,
                    signing_secret, signing_secret_encrypted, is_active, consecutive_failures, circuit_breaker_tripped
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0, 0)
            """, (
                sub_id, account_id, name, target_url, json.dumps(events),
                encrypted_secret, encrypted_secret
            ))
            conn.commit()
        finally:
            conn.close()

        # Telemetria no EventBus
        default_event_bus.publish_sync(
            stream=StreamName.AUDIT,
            event_type="webhooks.subscription_created",
            account_id=account_id,
            payload={
                "event": "webhooks.subscription_created",
                "subscription_id": sub_id,
                "account_id": account_id,
                "target_url": target_url,
            },
        )

        return {
            "id": sub_id,
            "account_id": account_id,
            "name": name,
            "target_url": target_url,
            "subscribed_events": events,
            "signing_secret": secret,
            "signing_secret_encrypted": encrypted_secret,
            "is_active": True,
            "consecutive_failures": 0,
            "circuit_breaker_tripped": False,
        }

    def list_subscriptions(self, account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
        """Lista todas as assinaturas de webhook do tenant."""
        init_db()
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, account_id, name, target_url, subscribed_events_json,
                       signing_secret, signing_secret_encrypted, is_active, consecutive_failures, circuit_breaker_tripped,
                       created_at
                FROM webhook_subscriptions
                WHERE account_id = ?
                ORDER BY created_at DESC
            """, (account_id,))
            rows = cur.fetchall()
            subs = []
            for r in rows:
                d = dict(r)
                d["subscribed_events"] = json.loads(d["subscribed_events_json"])
                d["signing_secret"] = _resolve_plaintext_secret(d.get("signing_secret"), d.get("signing_secret_encrypted"))
                d["is_active"] = bool(d["is_active"])
                d["circuit_breaker_tripped"] = bool(d["circuit_breaker_tripped"])
                del d["subscribed_events_json"]
                subs.append(d)
            return subs
        finally:
            conn.close()

    def get_subscription(self, subscription_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
        """Obtém detalhes da assinatura validando tenant."""
        init_db()
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, account_id, name, target_url, subscribed_events_json,
                       signing_secret, signing_secret_encrypted, is_active, consecutive_failures, circuit_breaker_tripped,
                       created_at
                FROM webhook_subscriptions
                WHERE id = ?
            """, (subscription_id,))
            row = cur.fetchone()
        finally:
            conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Assinatura de webhook não encontrada")
        if row["account_id"] != account_id:
            raise HTTPException(status_code=403, detail="Acesso não autorizado à assinatura de outro tenant")

        d = dict(row)
        d["subscribed_events"] = json.loads(d["subscribed_events_json"])
        d["signing_secret"] = _resolve_plaintext_secret(d.get("signing_secret"), d.get("signing_secret_encrypted"))
        d["is_active"] = bool(d["is_active"])
        d["circuit_breaker_tripped"] = bool(d["circuit_breaker_tripped"])
        del d["subscribed_events_json"]
        return d

    def delete_subscription(self, subscription_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
        """Remove a assinatura de webhook do tenant."""
        sub = self.get_subscription(subscription_id, account_id)
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM webhook_subscriptions WHERE id = ?", (subscription_id,))
            conn.commit()
            return {"success": True, "deleted_id": subscription_id}
        finally:
            conn.close()

    def reset_circuit_breaker(self, subscription_id: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
        """Reativa manualmente uma assinatura cujo circuit breaker foi acionado."""
        sub = self.get_subscription(subscription_id, account_id)
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE webhook_subscriptions
                SET is_active = 1, consecutive_failures = 0, circuit_breaker_tripped = 0
                WHERE id = ?
            """, (subscription_id,))
            conn.commit()
        finally:
            conn.close()

        return {
            "subscription_id": subscription_id,
            "is_active": True,
            "consecutive_failures": 0,
            "circuit_breaker_tripped": False,
            "message": "Circuit breaker resetado com sucesso. Assinatura reativada.",
        }

    def deliver_to_subscription(
        self,
        subscription: Dict[str, Any],
        event_name: str,
        payload_data: Dict[str, Any],
        timeout_seconds: float = 5.0,
        forced_status_code: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Executa a entrega HTTP do webhook com assinatura criptográfica HMAC-SHA256,
        medição de latência em milissegundos e controle do circuit breaker.
        """
        if not subscription.get("is_active") or subscription.get("circuit_breaker_tripped"):
            raise CircuitBreakerTrippedException()

        target_url = subscription["target_url"]
        validate_target_url_safe(target_url)

        delivery_id = f"del-{uuid.uuid4().hex[:10]}"
        timestamp = int(time.time())

        full_envelope = {
            "id": delivery_id,
            "event": event_name,
            "timestamp": timestamp,
            "account_id": subscription["account_id"],
            "data": payload_data,
        }
        body_bytes = json.dumps(full_envelope, ensure_ascii=False, sort_keys=True).encode("utf-8")
        plaintext_secret = _resolve_plaintext_secret(
            subscription.get("signing_secret"),
            subscription.get("signing_secret_encrypted"),
        )
        signature_header = compute_hmac_signature(plaintext_secret, body_bytes)

        start_time = time.perf_counter()
        status_code = None
        response_body = ""
        success = False

        if forced_status_code is not None:
            # Modo explícito para simulações de teste
            status_code = forced_status_code
            success = (200 <= status_code < 300)
            response_body = f'{{"simulated_status": {status_code}}}'
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        elif self.mock_dispatch:
            # Em modo local/teste, simula entrega bem-sucedida
            status_code = 200
            success = True
            response_body = '{"status": "delivered", "receiver": "mock_receiver"}'
            latency_ms = round((time.perf_counter() - start_time) * 1000 + 12.5, 2)
        else:
            req = urllib.request.Request(
                target_url,
                data=body_bytes,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "RevNault-Webhook-Dispatcher/1.0",
                    "X-RevNault-Signature": signature_header,
                    "X-RevNault-Event": event_name,
                    "X-RevNault-Delivery": delivery_id,
                },
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
                    status_code = response.getcode()
                    response_body = response.read()[:1024].decode("utf-8", errors="replace")
                    success = (200 <= status_code < 300)
            except urllib.error.HTTPError as e:
                status_code = e.code
                response_body = e.read()[:512].decode("utf-8", errors="replace")
                success = False
            except Exception as e:
                status_code = 504
                response_body = f"Network/Timeout Error: {str(e)[:255]}"
                success = False
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Atualização do Circuit Breaker na base
        conn = get_connection()
        try:
            cur = conn.cursor()
            if success:
                new_failures = 0
                tripped = 0
                is_active = 1
            else:
                new_failures = subscription.get("consecutive_failures", 0) + 1
                tripped = 1 if new_failures >= self.MAX_CONSECUTIVE_FAILURES else 0
                is_active = 0 if tripped else 1

            cur.execute("""
                UPDATE webhook_subscriptions
                SET consecutive_failures = ?, circuit_breaker_tripped = ?, is_active = ?
                WHERE id = ?
            """, (new_failures, tripped, is_active, subscription["id"]))

            cur.execute("""
                INSERT INTO webhook_delivery_logs (
                    id, subscription_id, account_id, event_name, target_url,
                    payload_json, signature_header, status_code, response_body,
                    latency_ms, attempt, success
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (
                delivery_id, subscription["id"], subscription["account_id"],
                event_name, target_url, body_bytes.decode("utf-8", errors="replace"),
                signature_header, status_code, response_body, latency_ms,
                1 if success else 0
            ))
            conn.commit()
        finally:
            conn.close()

        return {
            "success": success,
            "subscription_id": subscription["id"],
            "delivery_id": delivery_id,
            "signature_header": signature_header,
            "status_code": status_code or 500,
            "latency_ms": latency_ms,
            "circuit_breaker_tripped": bool(tripped if not success else False),
            "response_preview": response_body[:200],
        }

    def dispatch_event(
        self,
        event_name: str,
        payload_data: Dict[str, Any],
        account_id: str = "0f14ffff",
    ) -> List[Dict[str, Any]]:
        """Despacha evento para todas as assinaturas ativas do tenant que escutam o evento."""
        init_db()
        subs = self.list_subscriptions(account_id)
        results = []

        for s in subs:
            if not s["is_active"] or s["circuit_breaker_tripped"]:
                continue
            evts = s.get("subscribed_events", [])
            if "*" in evts or event_name in evts:
                try:
                    res = self.deliver_to_subscription(s, event_name, payload_data)
                    results.append(res)
                except Exception:
                    pass

        return results

    def list_delivery_logs(
        self,
        account_id: str = "0f14ffff",
        subscription_id: Optional[str] = None,
        event_name: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Consulta histórico de logs de entrega para auditoria."""
        init_db()
        conn = get_connection()
        try:
            cur = conn.cursor()
            query = """
                SELECT id, subscription_id, account_id, event_name, target_url,
                       signature_header, status_code, response_body, latency_ms,
                       attempt, success, created_at
                FROM webhook_delivery_logs
                WHERE account_id = ?
            """
            params: List[Any] = [account_id]
            if subscription_id:
                query += " AND subscription_id = ?"
                params.append(subscription_id)
            if event_name:
                query += " AND event_name = ?"
                params.append(event_name)

            query += f" ORDER BY created_at DESC LIMIT {int(limit)}"
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            logs = []
            for r in rows:
                item = dict(r)
                item["success"] = bool(item["success"])
                logs.append(item)
            return logs
        finally:
            conn.close()
