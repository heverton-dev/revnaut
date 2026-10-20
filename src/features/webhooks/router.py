# -*- coding: utf-8 -*-
"""
Vertical Slice: Webhooks & Event Telemetry (Pilar II da Governança AIDD)
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from src.core.database import get_connection

router = APIRouter(tags=["Quarteto Sine Qua Non"])


@router.get("/webhooks", response_class=HTMLResponse, summary="Webhook Studio")
def webhook_studio():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, url, event_type, is_active FROM webhooks")
    hooks = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT id, status_code, payload, delivered_at FROM webhook_logs ORDER BY id DESC LIMIT 15")
    logs = [dict(r) for r in cur.fetchall()]
    conn.close()

    hooks_rows = "".join([
        f"<tr><td>{h['name']}</td><td><code>{h['url']}</code></td><td><span class='badge'>{h['event_type']}</span></td><td><span class='badge-status'>Ativo</span></td></tr>"
        for h in hooks
    ]) or "<tr><td colspan='4'>Nenhum webhook registrado.</td></tr>"

    logs_rows = "".join([
        f"<tr><td>#{l['id']}</td><td><span class='badge-status'>{l['status_code']}</span></td><td><pre>{l['payload']}</pre></td><td>{l['delivered_at']}</td></tr>"
        for l in logs
    ]) or "<tr><td colspan='4'>Nenhum log registrado ainda.</td></tr>"

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
      <title>RevNault • Webhook Studio</title>
      <link rel="icon" type="image/svg+xml" href="/favicon.svg">
      <link rel="alternate icon" href="/favicon.ico">
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
      <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; scrollbar-width: thin; scrollbar-color: rgba(255, 255, 255, 0.14) transparent; }}
        *::-webkit-scrollbar {{ width: 5px; height: 5px; }}
        *::-webkit-scrollbar-track {{ background: transparent; }}
        *::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.12); border-radius: 9999px; }}
        *::-webkit-scrollbar-thumb:hover {{ background: rgba(255, 115, 0, 0.45); }}
        body {{ font-family: 'Inter', -apple-system, sans-serif; background: #08090d; color: #f8fafc; padding: 32px 40px; line-height: 1.5; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 20px; }}
        .header-title {{ display: flex; align-items: center; gap: 12px; }}
        .header-icon {{ width: 36px; height: 36px; border-radius: 8px; background: rgba(255,115,0,0.12); color: #ff7300; display: flex; align-items: center; justify-content: center; }}
        h2 {{ font-size: 20px; font-weight: 700; color: #ffffff; letter-spacing: -0.3px; }}
        .subtitle {{ color: #94a3b8; font-size: 13px; margin-top: 2px; }}
        .btn {{ background: linear-gradient(135deg, #ff7300, #ff8c24); color: white; border: none; padding: 9px 18px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }}
        .btn-secondary {{ background: #181d2b; color: #f8fafc; border: 1px solid rgba(255,255,255,0.08); }}
        .card {{ background: #131722; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08); padding: 24px; margin-bottom: 24px; }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }}
        h3 {{ font-size: 15px; font-weight: 600; color: #ffffff; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 13px; }}
        th {{ background: #0c0e14; text-transform: uppercase; font-size: 11px; font-weight: 600; color: #64748b; letter-spacing: 0.5px; }}
        tr:hover td {{ background: rgba(255,255,255,0.02); }}
        pre {{ background: #0c0e14; padding: 8px 12px; border-radius: 6px; font-size: 11.5px; color: #38bdf8; font-family: 'JetBrains Mono', monospace; border: 1px solid rgba(255,255,255,0.05); max-width: 440px; overflow-x: auto; }}
        .badge {{ background: rgba(56,189,248,0.12); color: #38bdf8; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 11px; border: 1px solid rgba(56,189,248,0.25); }}
        .badge-status {{ background: rgba(52,211,153,0.12); color: #34d399; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-family: 'JetBrains Mono', monospace; border: 1px solid rgba(52,211,153,0.25); }}
      </style>
    </head>
    <body>
      <div class="header">
        <div class="header-title">
          <div class="header-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          </div>
          <div>
            <h2>Webhook Studio</h2>
            <p class="subtitle">Pilar II da Governança AIDD: Telemetria e Entrega de Eventos em Tempo Real</p>
          </div>
        </div>
        <div style="display: flex; gap: 10px;">
          <a href="/" class="btn btn-secondary">Voltar ao App</a>
          <a href="/docs" class="btn">Swagger Studio</a>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>Webhooks Configurados (Listeners)</h3>
        </div>
        <table>
          <thead><tr><th>Nome</th><th>URL de Destino</th><th>Evento</th><th>Status</th></tr></thead>
          <tbody>{hooks_rows}</tbody>
        </table>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>Histórico de Disparos & Entregas Recentes</h3>
        </div>
        <table>
          <thead><tr><th>ID</th><th>Status Code</th><th>Payload JSON</th><th>Timestamp</th></tr></thead>
          <tbody>{logs_rows}</tbody>
        </table>
      </div>
    </body>
    </html>
    """


# ==============================================================================
# REST API: Portal de Desenvolvedores & Webhooks Outbound (TICKET-40)
# ==============================================================================

from typing import List, Optional
from fastapi import Query, status
from src.features.webhooks.schemas import (
    WebhookSubscriptionCreate, WebhookSubscriptionOut,
    WebhookSubscriptionListResponse, WebhookDeliveryLogOut,
    WebhookDeliveryLogsListResponse, WebhookTestDispatchPayload,
    WebhookTestDispatchResponse, WebhookResetCircuitResponse,
    WebhookDeleteResponse
)
from src.features.webhooks.outbound_dispatcher import OutboundWebhookDispatcher

dispatcher = OutboundWebhookDispatcher()


@router.post(
    "/api/v1/webhooks/subscriptions",
    response_model=WebhookSubscriptionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar nova assinatura de webhook outbound com validação SSRF"
)
def create_webhook_subscription(
    payload: WebhookSubscriptionCreate,
    account_id: str = Query("0f14ffff", description="ID do tenant")
):
    acc = payload.account_id or account_id
    return dispatcher.create_subscription(
        name=payload.name,
        target_url=payload.target_url,
        subscribed_events=payload.subscribed_events,
        signing_secret=payload.signing_secret,
        account_id=acc,
    )


@router.get(
    "/api/v1/webhooks/subscriptions",
    response_model=WebhookSubscriptionListResponse,
    summary="Listar assinaturas de webhooks do tenant"
)
def list_webhook_subscriptions(
    account_id: str = Query("0f14ffff", description="ID do tenant")
):
    subs = dispatcher.list_subscriptions(account_id=account_id)
    return {
        "subscriptions": subs,
        "total": len(subs)
    }


@router.get(
    "/api/v1/webhooks/subscriptions/{subscription_id}",
    response_model=WebhookSubscriptionOut,
    summary="Obter detalhes de uma assinatura de webhook"
)
def get_webhook_subscription(
    subscription_id: str,
    account_id: str = Query("0f14ffff", description="ID do tenant")
):
    return dispatcher.get_subscription(subscription_id=subscription_id, account_id=account_id)


@router.delete(
    "/api/v1/webhooks/subscriptions/{subscription_id}",
    response_model=WebhookDeleteResponse,
    summary="Remover assinatura de webhook"
)
def delete_webhook_subscription(
    subscription_id: str,
    account_id: str = Query("0f14ffff", description="ID do tenant")
):
    return dispatcher.delete_subscription(subscription_id=subscription_id, account_id=account_id)


@router.patch(
    "/api/v1/webhooks/subscriptions/{subscription_id}/reset-circuit",
    response_model=WebhookResetCircuitResponse,
    summary="Resetar circuit breaker e reativar assinatura de webhook suspensa"
)
def reset_webhook_circuit_breaker(
    subscription_id: str,
    account_id: str = Query("0f14ffff", description="ID do tenant")
):
    return dispatcher.reset_circuit_breaker(subscription_id=subscription_id, account_id=account_id)


@router.post(
    "/api/v1/webhooks/outbound/dispatch-test",
    response_model=WebhookTestDispatchResponse,
    summary="Testar disparo de evento com cálculo de assinatura HMAC-SHA256 (alias outbound)"
)
@router.post(
    "/api/v1/webhooks/test-dispatch",
    response_model=WebhookTestDispatchResponse,
    summary="Testar disparo de evento com cálculo de assinatura HMAC-SHA256"
)
def test_webhook_dispatch(
    payload: WebhookTestDispatchPayload,
    account_id: str = Query("0f14ffff", description="ID do tenant")
):
    acc = payload.account_id or account_id
    sub = dispatcher.get_subscription(payload.subscription_id, account_id=acc)
    test_data = payload.payload_data or {
        "order_id": "dentgo-test-order-99",
        "status": "DELIVERED",
        "hub_name": "Hub Jardins SP",
        "delivered_at": "2026-10-18T10:00:00Z"
    }
    return dispatcher.deliver_to_subscription(
        subscription=sub,
        event_name=payload.event_name,
        payload_data=test_data
    )


@router.get(
    "/api/v1/webhooks/logs",
    response_model=WebhookDeliveryLogsListResponse,
    summary="Consultar logs de auditoria e telemetria de entregas de webhooks"
)
def list_webhook_delivery_logs(
    subscription_id: Optional[str] = Query(None, description="Filtrar por assinatura"),
    event_name: Optional[str] = Query(None, description="Filtrar por nome de evento"),
    limit: int = Query(50, ge=1, le=200, description="Limite de registros"),
    account_id: str = Query("0f14ffff", description="ID do tenant")
):
    logs = dispatcher.list_delivery_logs(
        account_id=account_id,
        subscription_id=subscription_id,
        event_name=event_name,
        limit=limit
    )
    return {
        "logs": logs,
        "total": len(logs)
    }


from fastapi import HTTPException
from src.features.campaigns.listmonk_adapter import process_listmonk_webhook_event


@router.post(
    "/api/v1/webhooks/listmonk",
    response_model=dict,
    summary="Webhook Listmonk para eventos de bounce, open e click"
)
@router.post(
    "/api/v1/webhooks/listmonk/events",
    response_model=dict,
    summary="Webhook Listmonk para eventos de bounce, open e click (alias)"
)
def listmonk_webhook_endpoint(payload: dict):
    try:
        return process_listmonk_webhook_event(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


