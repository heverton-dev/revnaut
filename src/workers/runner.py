# -*- coding: utf-8 -*-
"""
Deterministic Worker Runner — Redis Streams Consumer Loop
Executa processamento contínuo em segundo plano para canais assíncronos.
"""

from __future__ import annotations
import asyncio
import json
import logging
import signal
import uuid
from typing import Any, Dict, List, Optional
from src.core.database import get_connection, init_db
from src.core.events import (
    EventBus,
    EventConsumer,
    StreamName,
    default_event_bus,
    event_consumer,
    get_registered_consumers,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("worker_runner")

_running = True


def handle_shutdown(sig, frame):
    global _running
    logger.info("Recebido sinal de desligamento gracioso...")
    _running = False


@event_consumer(StreamName.MARKETING, group_name="worker_group_marketing")
async def handle_marketing_stream(event: Dict[str, Any]) -> Dict[str, Any]:
    """Processa eventos de marketing (lead.captured, mautic.campaign_action, listmonk)."""
    init_db()
    event_type = event.get("event_type", "")
    payload = event.get("payload") or {}
    tenant_id = event.get("tenant_id") or payload.get("account_id") or "0f14ffff"

    if event_type == "mautic.campaign_action":
        conn = get_connection()
        try:
            cur = conn.cursor()
            msg_id = f"omni-{uuid.uuid4().hex[:10]}"
            cur.execute(
                """
                INSERT OR IGNORE INTO omnichannel_messages (
                    id, account_id, instance_name, remote_jid, sender_phone,
                    message_type, content, from_me
                ) VALUES (?, ?, ?, ?, ?, 'text', ?, 1)
                """,
                (
                    msg_id,
                    tenant_id,
                    str(payload.get("instance_name") or "inst_default"),
                    str(payload.get("phone") or "5511999999999@s.whatsapp.net"),
                    str(payload.get("phone") or "+5511999999999"),
                    str(payload.get("rendered_message") or payload.get("template") or "Campanha Mautic"),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    return {"status": "processed", "stream": StreamName.MARKETING.value, "event_type": event_type}


@event_consumer(StreamName.SALES, group_name="worker_group_sales")
async def handle_sales_stream(event: Dict[str, Any]) -> Dict[str, Any]:
    """Processa eventos de vendas (deal.won, call.recording_ready, deal.stage_changed)."""
    init_db()
    event_type = event.get("event_type", "")
    payload = event.get("payload") or {}
    tenant_id = event.get("tenant_id") or payload.get("account_id") or "0f14ffff"

    if event_type == "call.recording_ready":
        call_id = payload.get("call_id")
        if call_id:
            conn = get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE call_recordings SET status = 'completed' WHERE id = ? AND account_id = ?",
                    (call_id, tenant_id),
                )
                conn.commit()
            finally:
                conn.close()
    elif event_type == "deal.won":
        partner_id = payload.get("partner_id") or payload.get("contact_id")
        if partner_id:
            from src.features.keypartners.loyalty_engine import credit_loyalty_points
            credit_loyalty_points(
                partner_id=str(partner_id),
                partner_name=str(payload.get("partner_name") or payload.get("contact_name") or "Cirurgião Parceiro"),
                implants_count=int(payload.get("implants_count") or 1),
                event_origin="deal.won",
                reference_id=str(payload.get("deal_id") or ""),
                account_id=tenant_id,
            )

    return {"status": "processed", "stream": StreamName.SALES.value, "event_type": event_type}


@event_consumer(StreamName.KEYPARTNERS, group_name="worker_group_kp")
async def handle_keypartners_stream(event: Dict[str, Any]) -> Dict[str, Any]:
    """Processa eventos de consignação cirúrgica KeyPartners e rastreabilidade ANVISA."""
    init_db()
    event_type = event.get("event_type", "")
    payload = event.get("payload") or {}
    tenant_id = event.get("tenant_id") or payload.get("account_id") or "0f14ffff"

    if event_type == "keypartners.postop_reported":
        partner_id = payload.get("agreement_id") or payload.get("partner_id")
        consumed_qty = int(payload.get("consumed_count") or payload.get("implants_count") or 0)
        if partner_id and consumed_qty > 0:
            from src.features.keypartners.loyalty_engine import credit_loyalty_points
            credit_loyalty_points(
                partner_id=str(partner_id),
                partner_name=str(payload.get("partner_name") or "Clínica Parceira"),
                implants_count=consumed_qty,
                event_origin="keypartners.postop_reported",
                reference_id=str(payload.get("surgical_order_id") or ""),
                account_id=tenant_id,
            )

    return {"status": "processed", "stream": StreamName.KEYPARTNERS.value, "event_type": event_type}


@event_consumer(StreamName.DENTGO, group_name="worker_group_dentgo")
async def handle_dentgo_stream(event: Dict[str, Any]) -> Dict[str, Any]:
    """Processa eventos de pronta-entrega expressa DENTGO e FEFO Flash Deals."""
    init_db()
    event_type = event.get("event_type", "")
    return {"status": "processed", "stream": StreamName.DENTGO.value, "event_type": event_type}


@event_consumer(StreamName.CX, group_name="worker_group_cx")
async def handle_cx_stream(event: Dict[str, Any]) -> Dict[str, Any]:
    """Processa eventos de Customer Experience, RMA ANVISA e acompanhamento pós-operatório."""
    init_db()
    event_type = event.get("event_type", "")
    return {"status": "processed", "stream": StreamName.CX.value, "event_type": event_type}


@event_consumer(StreamName.WEBHOOKS, group_name="worker_group_webhooks")
async def handle_webhooks_stream(event: Dict[str, Any]) -> Dict[str, Any]:
    """Processa fila de despacho de webhooks outbound com assinatura HMAC-SHA256."""
    init_db()
    event_type = event.get("event_type", "")
    payload = event.get("payload") or {}
    tenant_id = event.get("tenant_id") or payload.get("account_id") or "0f14ffff"

    if event_type:
        from src.features.webhooks.outbound_dispatcher import OutboundWebhookDispatcher
        dispatcher = OutboundWebhookDispatcher()
        dispatcher.dispatch_event(event_name=event_type, payload_data=payload, account_id=tenant_id)

    return {"status": "processed", "stream": StreamName.WEBHOOKS.value, "event_type": event_type}


@event_consumer(StreamName.AUDIT, group_name="worker_group_audit")
async def handle_audit_stream(event: Dict[str, Any]) -> Dict[str, Any]:
    """Processa trilha de auditoria e telemetria operacional."""
    init_db()
    event_type = event.get("event_type", "")
    return {"status": "processed", "stream": StreamName.AUDIT.value, "event_type": event_type}


def build_registered_worker_consumers(bus: Optional[EventBus] = None) -> List[ tuple[EventConsumer, Any] ]:
    target_bus = bus or default_event_bus
    pairs: List[tuple[EventConsumer, Any]] = []
    for item in get_registered_consumers():
        consumer = EventConsumer(
            target_bus,
            item["stream_name"],
            group_name=item["group_name"],
        )
        pairs.append((consumer, item["handler"]))
    return pairs


async def run_workers(bus: Optional[EventBus] = None, max_iterations: Optional[int] = None) -> int:
    target_bus = bus or default_event_bus
    worker_pairs = build_registered_worker_consumers(target_bus)
    logger.info("Iniciando pool de %d workers determinísticos nos canais Redis Streams...", len(worker_pairs))

    processed_total = 0
    iterations = 0
    while _running:
        for consumer, handler in worker_pairs:
            try:
                ok = await consumer.process_next(handler=handler)
                if ok:
                    processed_total += 1
            except Exception as e:
                logger.error("Erro no loop do consumidor %s: %s", consumer.stream_key, e)
        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break
        await asyncio.sleep(0.05)

    return processed_total


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    asyncio.run(run_workers())
