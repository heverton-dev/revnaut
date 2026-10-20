# -*- coding: utf-8 -*-
"""
Agendador do Lote Noturno do Radar de Concorrentes (TICKET-MKTINTEL-03).

Publica `market_intel.batch.tick` em `stream:market_intel` uma vez por slot horário da
janela morta 01:00-05:00 UTC (slots 01, 02, 03 e 04) para cada tenant com concorrente ativo.
A deduplicação é persistida em `market_intel_batch_ticks` (PRIMARY KEY slot_key + account_id),
então várias réplicas do worker e reinícios não publicam o mesmo tick duas vezes.
Fora da janela nada é publicado.
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

from src.core.database import get_connection
from src.core.events import EventBus, StreamName, default_event_bus
from src.features.market_intel.crawler_engine import is_within_dead_window_utc

logger = logging.getLogger("market_intel_scheduler")

TICK_EVENT_TYPE = "market_intel.batch.tick"
DEFAULT_CHECK_INTERVAL_SECONDS = 60.0


def scheduler_enabled() -> bool:
    return os.getenv("MARKET_INTEL_SCHEDULER_ENABLED", "1").lower() not in ("0", "false", "no")


def slot_key_for(now_utc: datetime) -> Optional[str]:
    """Chave do slot horário (ex: '2026-10-21T02') ou None fora da janela morta."""
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    now_utc = now_utc.astimezone(timezone.utc)
    if not is_within_dead_window_utc(now_utc):
        return None
    return now_utc.strftime("%Y-%m-%dT%H")


def tenants_with_active_competitors() -> List[str]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT DISTINCT account_id FROM competitors WHERE active = 1 ORDER BY account_id").fetchall()
    finally:
        conn.close()
    return [r["account_id"] for r in rows]


def publish_due_ticks(now_utc: Optional[datetime] = None, bus: Optional[EventBus] = None) -> List[Dict[str, str]]:
    """Publica os ticks devidos no instante informado; retorna os ticks efetivamente publicados."""
    now = now_utc or datetime.now(timezone.utc)
    slot = slot_key_for(now)
    if slot is None:
        return []

    target_bus = bus or default_event_bus
    published: List[Dict[str, str]] = []
    for account_id in tenants_with_active_competitors():
        conn = get_connection()
        try:
            cur = conn.execute(
                "INSERT OR IGNORE INTO market_intel_batch_ticks (slot_key, account_id, published_at) VALUES (?, ?, ?)",
                (slot, account_id, now.astimezone(timezone.utc).isoformat()),
            )
            conn.commit()
            claimed = cur.rowcount == 1
        finally:
            conn.close()
        if not claimed:
            continue

        try:
            message_id = target_bus.publish_sync(
                StreamName.MARKET_INTEL,
                TICK_EVENT_TYPE,
                {"account_id": account_id, "slot_key": slot},
                tenant_id=account_id,
                idempotency_key=f"{TICK_EVENT_TYPE}:{account_id}:{slot}",
            )
        except Exception:
            # Libera o slot para nova tentativa na próxima verificação
            conn = get_connection()
            try:
                conn.execute("DELETE FROM market_intel_batch_ticks WHERE slot_key = ? AND account_id = ?", (slot, account_id))
                conn.commit()
            finally:
                conn.close()
            logger.exception("Falha ao publicar tick do lote noturno (%s, %s)", account_id, slot)
            continue

        conn = get_connection()
        try:
            conn.execute(
                "UPDATE market_intel_batch_ticks SET stream_message_id = ? WHERE slot_key = ? AND account_id = ?",
                (str(message_id), slot, account_id),
            )
            conn.commit()
        finally:
            conn.close()
        published.append({"account_id": account_id, "slot_key": slot, "stream_message_id": str(message_id)})
        logger.info("Tick do lote noturno publicado: tenant=%s slot=%s", account_id, slot)
    return published


class MarketIntelBatchScheduler:
    """Verificação limitada a uma vez por intervalo, chamada a cada volta do loop do worker."""

    def __init__(
        self,
        bus: Optional[EventBus] = None,
        check_interval_seconds: float = DEFAULT_CHECK_INTERVAL_SECONDS,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self.bus = bus
        self.check_interval_seconds = check_interval_seconds
        self.clock = clock
        self.monotonic = monotonic
        self._last_check: Optional[float] = None

    def maybe_tick(self) -> List[Dict[str, str]]:
        now_mono = self.monotonic()
        if self._last_check is not None and now_mono - self._last_check < self.check_interval_seconds:
            return []
        self._last_check = now_mono
        return publish_due_ticks(self.clock(), self.bus)
