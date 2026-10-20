# -*- coding: utf-8 -*-
"""
Testes reais do agendador do lote noturno do Radar de Concorrentes (TICKET-MKTINTEL-03).
Banco SQLite isolado via tests/conftest.py e EventBus em memória.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import pytest

import src.features.market_intel.crawler_engine as crawler_engine
from src.core.database import get_connection
from src.core.events import EventBus, StreamName
from src.workers.market_intel_scheduler import (
    TICK_EVENT_TYPE,
    MarketIntelBatchScheduler,
    publish_due_ticks,
    slot_key_for,
)
from src.workers.runner import run_workers

ACC = "0f14ffff"


def _utc(y, m, d, h, mi=0):
    return datetime(y, m, d, h, mi, tzinfo=timezone.utc)


async def _stream_events(bus: EventBus):
    records = await bus.read_stream(StreamName.MARKET_INTEL, count=1000)
    out = []
    for rec in records:
        data = rec[1] if isinstance(rec, (list, tuple)) else rec
        out.append(data)
    return out


def _tick_rows(slot_key: str):
    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute("SELECT * FROM market_intel_batch_ticks WHERE slot_key = ?", (slot_key,))]
    finally:
        conn.close()


@pytest.mark.parametrize(
    "moment,expected",
    [
        (_utc(2027, 1, 10, 0, 59), None),
        (_utc(2027, 1, 10, 1, 0), "2027-01-10T01"),
        (_utc(2027, 1, 10, 2, 30), "2027-01-10T02"),
        (_utc(2027, 1, 10, 4, 59), "2027-01-10T04"),
        (_utc(2027, 1, 10, 5, 0), None),
        (_utc(2027, 1, 10, 13, 0), None),
        (datetime(2027, 1, 9, 23, 30, tzinfo=timezone(timedelta(hours=-3))), "2027-01-10T02"),
    ],
)
def test_slot_key_only_inside_dead_window(moment, expected):
    assert slot_key_for(moment) == expected


def test_no_tick_published_outside_dead_window():
    bus = EventBus(in_memory=True)
    for hour in (0, 5, 9, 12, 18, 23):
        assert publish_due_ticks(_utc(2027, 2, 1, hour, 15), bus) == []
    assert asyncio.run(_stream_events(bus)) == []
    conn = get_connection()
    try:
        assert conn.execute("SELECT COUNT(*) FROM market_intel_batch_ticks WHERE slot_key LIKE '2027-02-01%'").fetchone()[0] == 0
    finally:
        conn.close()


def test_one_tick_per_slot_and_tenant_inside_window():
    bus = EventBus(in_memory=True)
    first = publish_due_ticks(_utc(2027, 3, 5, 2, 10), bus)
    assert [t["account_id"] for t in first] == [ACC]
    assert first[0]["slot_key"] == "2027-03-05T02"

    # Mesma hora (outra réplica do worker ou reinício): nada novo é publicado
    assert publish_due_ticks(_utc(2027, 3, 5, 2, 55), bus) == []
    assert publish_due_ticks(_utc(2027, 3, 5, 2, 59), EventBus(in_memory=True)) == []

    # Próximo slot da janela gera novo tick
    nxt = publish_due_ticks(_utc(2027, 3, 5, 3, 0), bus)
    assert [t["slot_key"] for t in nxt] == ["2027-03-05T03"]

    events = asyncio.run(_stream_events(bus))
    ticks = [e for e in events if e.get("event_type") == TICK_EVENT_TYPE]
    assert len(ticks) == 2
    rows = _tick_rows("2027-03-05T02")
    assert len(rows) == 1 and rows[0]["account_id"] == ACC and rows[0]["stream_message_id"]


def test_only_tenants_with_active_competitors_receive_ticks():
    conn = get_connection()
    try:
        conn.execute("INSERT OR IGNORE INTO accounts (id, name) VALUES ('acc-sem-radar', 'Tenant sem concorrentes ativos')")
        conn.execute(
            "INSERT OR IGNORE INTO competitors (id, account_id, name, domain, active, created_at) "
            "VALUES ('comp-inativo-x', 'acc-sem-radar', 'Inativo', 'inativo-x.com.br', 0, '2026-10-01T00:00:00+00:00')"
        )
        conn.commit()
    finally:
        conn.close()
    published = publish_due_ticks(_utc(2027, 4, 2, 1, 5), EventBus(in_memory=True))
    assert {t["account_id"] for t in published} == {ACC}


def test_scheduler_throttles_checks_between_intervals():
    mono = [1000.0]
    clock = [_utc(2027, 5, 7, 1, 1)]
    sched = MarketIntelBatchScheduler(
        bus=EventBus(in_memory=True),
        check_interval_seconds=60,
        clock=lambda: clock[0],
        monotonic=lambda: mono[0],
    )
    assert len(sched.maybe_tick()) == 1

    # Mudou a hora, mas o intervalo mínimo entre verificações não passou: não consulta
    clock[0] = _utc(2027, 5, 7, 2, 0)
    mono[0] += 30
    assert sched.maybe_tick() == []

    mono[0] += 31
    assert [t["slot_key"] for t in sched.maybe_tick()] == ["2027-05-07T02"]


def test_worker_loop_publishes_and_consumes_nightly_tick(monkeypatch):
    def local_page(url, idx):
        return f"<html><body><h1>{url}</h1><p>Implante Conico 3.5x10mm por R$ 158,00 com 9% de desconto.</p></body></html>"

    # Sem rede: a coleta (se o relógio real estiver na janela) usa páginas locais
    monkeypatch.setattr(crawler_engine, "fetch_page_passively", local_page)
    monkeypatch.setattr(crawler_engine.time, "sleep", lambda s: None)

    bus = EventBus(in_memory=True)
    sched = MarketIntelBatchScheduler(bus=bus, check_interval_seconds=0, clock=lambda: _utc(2027, 6, 3, 4, 40))
    processed = asyncio.run(run_workers(bus=bus, max_iterations=3, scheduler=sched))
    assert processed >= 1
    rows = _tick_rows("2027-06-03T04")
    assert len(rows) == 1 and rows[0]["stream_message_id"]


def test_default_scheduler_only_for_production_process(monkeypatch):
    """run_workers() sem bus injetado (processo do container) liga o agendador; desligável por env."""
    import src.workers.runner as runner

    created = []

    class Recorder(MarketIntelBatchScheduler):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            created.append(self)

        def maybe_tick(self):
            return []

    monkeypatch.setattr(runner, "MarketIntelBatchScheduler", Recorder)
    asyncio.run(runner.run_workers(max_iterations=1))
    assert len(created) == 1

    monkeypatch.setenv("MARKET_INTEL_SCHEDULER_ENABLED", "0")
    asyncio.run(runner.run_workers(max_iterations=1))
    assert len(created) == 1

    asyncio.run(runner.run_workers(bus=EventBus(in_memory=True), max_iterations=1))
    assert len(created) == 1
