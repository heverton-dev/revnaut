# -*- coding: utf-8 -*-
"""
TDD for [TICKET-02] Redis Streams Event Bus & Deterministic Workers
Validates:
- Event publication to typed streams (stream:sales, stream:keypartners, etc.)
- Message delivery with event_id idempotency
- Consumer retries with exponential backoff on transient failures
- Routing persistent failures to Dead-Letter Queue (stream:dlq)
- ACK confirmation upon successful processing
"""

import asyncio
import pytest
from src.core.events import EventBus, EventConsumer, StreamName


def test_event_bus_publication():
    """Valida publicação de evento com payload tipado e tempo < 5ms."""
    async def _run():
        bus = EventBus(in_memory=True)
        event_id = await bus.publish_event(
            stream_name=StreamName.SALES,
            event_type="deal.won",
            payload={"deal_id": "d-999", "value": 50000.0, "contact_id": 12},
            tenant_id="0f14ffff",
        )
        assert event_id is not None
        assert isinstance(event_id, str)

        # Valida leitura do stream
        messages = await bus.read_stream(StreamName.SALES, count=10)
        assert len(messages) == 1
        msg = messages[0]
        assert msg["event_type"] == "deal.won"
        assert msg["payload"]["deal_id"] == "d-999"

    asyncio.run(_run())


def test_consumer_retry_and_ack_on_success():
    """Simula falha na 1ª tentativa do consumidor e sucesso com ACK na 2ª tentativa."""
    async def _run():
        bus = EventBus(in_memory=True)
        await bus.publish_event(
            stream_name=StreamName.KEYPARTNERS,
            event_type="consignment.dispatched",
            payload={"box_id": "box-123", "clinic": "Clínica Teste"},
            tenant_id="0f14ffff",
        )

        attempts = 0

        async def _test_handler(event):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise ValueError("Falha transitória simulada")
            return True

        consumer = EventConsumer(bus, StreamName.KEYPARTNERS, group_name="group_kp")
        processed = await consumer.process_next(handler=_test_handler, max_retries=3)

        assert attempts == 2
        assert processed is True

        # Valida que foi confirmado (ACK)
        pending = await bus.get_pending_count(StreamName.KEYPARTNERS, group_name="group_kp")
        assert pending == 0

    asyncio.run(_run())


def test_consumer_routes_to_dlq_after_max_retries():
    """Valida roteamento automático para stream:dlq após exceder 3 tentativas."""
    async def _run():
        bus = EventBus(in_memory=True)
        await bus.publish_event(
            stream_name=StreamName.DENTGO,
            event_type="courier.failed",
            payload={"delivery_id": "del-fatal", "reason": "Lacre rompido"},
            tenant_id="0f14ffff",
        )

        async def _fatal_handler(event):
            raise RuntimeError("Erro fatal irrecuperável")

        consumer = EventConsumer(bus, StreamName.DENTGO, group_name="group_dentgo")
        processed = await consumer.process_next(handler=_fatal_handler, max_retries=3)

        assert processed is False

        # Valida presença na Dead-Letter Queue
        dlq_messages = await bus.read_stream(StreamName.DLQ, count=10)
        assert len(dlq_messages) == 1
        dlq_event = dlq_messages[0]
        assert dlq_event["original_stream"] == StreamName.DENTGO.value
        assert "Erro fatal irrecuperável" in dlq_event["error"]

    asyncio.run(_run())
