# -*- coding: utf-8 -*-
"""
Deterministic Worker Runner — Redis Streams Consumer Loop
Executa processamento contínuo em segundo plano para canais assíncronos.
"""

from __future__ import annotations
import asyncio
import logging
import signal
import sys
from src.core.events import EventBus, EventConsumer, StreamName

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("worker_runner")

_running = True


def handle_shutdown(sig, frame):
    global _running
    logger.info("Recebido sinal de desligamento gracioso...")
    _running = False


async def run_workers():
    bus = EventBus()
    consumers = [
        EventConsumer(bus, StreamName.SALES, group_name="worker_group_sales"),
        EventConsumer(bus, StreamName.KEYPARTNERS, group_name="worker_group_kp"),
        EventConsumer(bus, StreamName.DENTGO, group_name="worker_group_dentgo"),
        EventConsumer(bus, StreamName.WEBHOOKS, group_name="worker_group_webhooks"),
    ]

    logger.info("Iniciando pool de workers determinísticos nos canais Redis Streams...")

    async def default_handler(event):
        logger.info(f"Processando evento {event.get('event_type')} (ID: {event.get('event_id')})")
        return True

    while _running:
        for consumer in consumers:
            try:
                await consumer.process_next(handler=default_handler)
            except Exception as e:
                logger.error(f"Erro no loop do consumidor {consumer.stream_key}: {e}")
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    asyncio.run(run_workers())
