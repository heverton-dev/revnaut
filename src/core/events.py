# -*- coding: utf-8 -*-
"""
Redis Streams Event Bus & Deterministic Consumer Pools — RevNault Core
Canal assíncrono para integração desacoplada entre CRM, KeyPartners, DENTGO e Webhooks.
"""

from __future__ import annotations
import asyncio
import json
import os
import time
import uuid
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import redis.asyncio as aioredis


class StreamName(str, Enum):
    MARKETING = "stream:marketing"
    SALES = "stream:sales"
    KEYPARTNERS = "stream:keypartners"
    DENTGO = "stream:dentgo"
    CX = "stream:cx"
    GROWTH = "stream:growth"
    WEBHOOKS = "stream:webhooks"
    AUDIT = "stream:audit"
    MARKET_INTEL = "stream:market_intel"
    DLQ = "stream:dlq"


_REGISTERED_CONSUMERS: List[Dict[str, Any]] = []


def event_consumer(stream_name: StreamName | str, group_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator para registrar handlers determinísticos em Consumer Groups do Redis Streams.
    """
    def decorator(func: Callable[[Dict[str, Any]], Any]) -> Callable[[Dict[str, Any]], Any]:
        stream_key = stream_name.value if isinstance(stream_name, StreamName) else str(stream_name)
        entry = {
            "stream_name": stream_name,
            "stream_key": stream_key,
            "group_name": group_name,
            "handler": func,
            "name": getattr(func, "__name__", "handler"),
        }
        _REGISTERED_CONSUMERS[:] = [
            c for c in _REGISTERED_CONSUMERS
            if not (c["stream_key"] == stream_key and c["group_name"] == group_name and c["name"] == entry["name"])
        ]
        _REGISTERED_CONSUMERS.append(entry)
        return func

    return decorator


def get_registered_consumers() -> List[Dict[str, Any]]:
    return list(_REGISTERED_CONSUMERS)


class _PublishSyncDescriptor:
    """Permite chamar publish_sync tanto via EventBus.publish_sync(...) quanto via bus.publish_sync(...)."""

    def __init__(self, func: Callable[..., str]) -> None:
        self.func = func

    def __get__(self, instance: Optional["EventBus"], owner: Any = None) -> Callable[..., str]:
        target = instance if instance is not None else default_event_bus
        return lambda *args, **kwargs: self.func(target, *args, **kwargs)


class EventBus:
    def __init__(
        self,
        redis_url: Optional[str] = None,
        in_memory: bool = False,
    ) -> None:
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.in_memory = in_memory
        self._memory_streams: Dict[str, List[Dict[str, Any]]] = {}
        self._memory_groups: Dict[str, Dict[str, Any]] = {}
        self._redis_client: Optional[aioredis.Redis] = None
        self._initialized_groups: set[str] = set()

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis_client is None:
            self._redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis_client

    def _append_memory_record(self, stream_key: str, record: Dict[str, Any]) -> None:
        if stream_key not in self._memory_streams:
            self._memory_streams[stream_key] = []
        self._memory_streams[stream_key].append(record)
        # Espelha no singleton default_event_bus caso publicado em instância local efêmera
        if "default_event_bus" in globals() and default_event_bus is not None and self is not default_event_bus:
            if stream_key not in default_event_bus._memory_streams:
                default_event_bus._memory_streams[stream_key] = []
            default_event_bus._memory_streams[stream_key].append(record)

    def _publish_sync_impl(
        self,
        stream_name: Optional[StreamName | str] = None,
        event_type_or_payload: Optional[str | Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        *,
        stream: Optional[StreamName | str] = None,
        event_type: Optional[str] = None,
        account_id: Optional[str] = None,
    ) -> str:
        eff_stream = stream_name if stream_name is not None else (stream or StreamName.AUDIT)
        stream_key = eff_stream.value if isinstance(eff_stream, StreamName) else str(eff_stream)
        eff_event_or_payload = event_type_or_payload if event_type_or_payload is not None else event_type
        if isinstance(eff_event_or_payload, dict) and payload is None:
            actual_payload = dict(eff_event_or_payload)
            actual_event_type = str(
                actual_payload.get("event")
                or actual_payload.get("event_type")
                or "audit.event"
            )
        else:
            actual_event_type = str(eff_event_or_payload or "domain.event")
            actual_payload = dict(payload) if isinstance(payload, dict) else {"value": payload}

        eff_tenant = (
            tenant_id
            or account_id
            or str(actual_payload.get("account_id") or actual_payload.get("tenant_id") or "default")
        )
        event_id = idempotency_key or f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        record: Dict[str, Any] = {
            "event_id": event_id,
            "event_type": actual_event_type,
            "tenant_id": eff_tenant,
            "timestamp": time.time(),
            "payload": actual_payload,
        }
        if stream_key in (StreamName.DLQ.value, "stream:dlq"):
            record["original_stream"] = actual_payload.get("original_stream")
            record["error"] = actual_payload.get("error")

        self._append_memory_record(stream_key, record)
        return event_id

    publish_sync = _PublishSyncDescriptor(_publish_sync_impl)

    async def publish_event(
        self,
        stream_name: StreamName | str,
        event_type: str,
        payload: Dict[str, Any],
        tenant_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> str:
        stream_key = stream_name.value if isinstance(stream_name, StreamName) else str(stream_name)
        event_id = idempotency_key or f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        record: Dict[str, Any] = {
            "event_id": event_id,
            "event_type": event_type,
            "tenant_id": tenant_id or "default",
            "timestamp": time.time(),
            "payload": payload,
        }
        if stream_key in (StreamName.DLQ.value, "stream:dlq"):
            record["original_stream"] = payload.get("original_stream")
            record["error"] = payload.get("error")

        if self.in_memory:
            self._append_memory_record(stream_key, record)
            return event_id

        try:
            r = await self._get_redis()
            msg_data = {
                "event_id": event_id,
                "event_type": event_type,
                "tenant_id": tenant_id or "default",
                "timestamp": str(record["timestamp"]),
                "payload": json.dumps(payload),
            }
            await r.xadd(stream_key, msg_data, id="*")
            return event_id
        except Exception:
            self._append_memory_record(stream_key, record)
            return event_id

    async def ensure_consumer_group(
        self,
        stream_name: StreamName | str,
        group_name: str,
    ) -> None:
        stream_key = stream_name.value if isinstance(stream_name, StreamName) else str(stream_name)
        grp_key = f"{stream_key}:{group_name}"
        if grp_key not in self._memory_groups:
            self._memory_groups[grp_key] = {"offset": 0, "pending": []}

        if self.in_memory or stream_key in self._memory_streams:
            return

        if grp_key in self._initialized_groups:
            return

        try:
            r = await self._get_redis()
            # XGROUP CREATE <stream> <group> 0 MKSTREAM
            await r.xgroup_create(name=stream_key, groupname=group_name, id="0", mkstream=True)
            self._initialized_groups.add(grp_key)
        except Exception as exc:
            if "BUSYGROUP" in str(exc):
                self._initialized_groups.add(grp_key)

    async def read_stream(
        self,
        stream_name: StreamName | str,
        count: int = 10,
        group_name: Optional[str] = None,
        consumer_name: str = "consumer-1",
    ) -> List[Dict[str, Any]]:
        stream_key = stream_name.value if isinstance(stream_name, StreamName) else str(stream_name)

        if self.in_memory or stream_key in self._memory_streams:
            stream_items = self._memory_streams.get(stream_key, [])
            if group_name:
                grp_key = f"{stream_key}:{group_name}"
                if grp_key not in self._memory_groups:
                    self._memory_groups[grp_key] = {"offset": 0, "pending": []}
                grp = self._memory_groups[grp_key]
                offset = int(grp.get("offset", 0))
                batch = list(stream_items[offset : offset + count])
                grp["offset"] = offset + len(batch)
                for ev in batch:
                    ev_id = ev["event_id"]
                    if ev_id not in grp["pending"]:
                        grp["pending"].append(ev_id)
                return batch
            return list(stream_items)[:count]

        eff_group = group_name or "default_reader_group"
        await self.ensure_consumer_group(stream_key, eff_group)

        try:
            r = await self._get_redis()
            # XREADGROUP GROUP <group> <consumer> COUNT <n> STREAMS <stream> >
            res = await r.xreadgroup(
                groupname=eff_group,
                consumername=consumer_name,
                streams={stream_key: ">"},
                count=count,
            )
            items: List[Dict[str, Any]] = []
            for _stream, messages in res or []:
                for msg_id, fields in messages:
                    payload_data = json.loads(fields.get("payload", "{}"))
                    item: Dict[str, Any] = {
                        "redis_msg_id": msg_id,
                        "event_id": fields.get("event_id", msg_id),
                        "event_type": fields.get("event_type", ""),
                        "tenant_id": fields.get("tenant_id", "default"),
                        "timestamp": float(fields.get("timestamp", 0)),
                        "payload": payload_data,
                    }
                    if stream_key in (StreamName.DLQ.value, "stream:dlq"):
                        item["original_stream"] = payload_data.get("original_stream")
                        item["error"] = payload_data.get("error")
                    items.append(item)
            return items
        except Exception:
            stream_items = self._memory_streams.get(stream_key, [])
            if group_name:
                grp_key = f"{stream_key}:{group_name}"
                if grp_key not in self._memory_groups:
                    self._memory_groups[grp_key] = {"offset": 0, "pending": []}
                grp = self._memory_groups[grp_key]
                offset = int(grp.get("offset", 0))
                batch = list(stream_items[offset : offset + count])
                grp["offset"] = offset + len(batch)
                for ev in batch:
                    ev_id = ev["event_id"]
                    if ev_id not in grp["pending"]:
                        grp["pending"].append(ev_id)
                return batch
            return list(stream_items)[:count]

    async def get_pending_count(
        self,
        stream_name: StreamName | str,
        group_name: str,
    ) -> int:
        stream_key = stream_name.value if isinstance(stream_name, StreamName) else str(stream_name)
        if self.in_memory or stream_key in self._memory_streams:
            grp = self._memory_groups.get(f"{stream_key}:{group_name}", {})
            return len(grp.get("pending", []))

        try:
            r = await self._get_redis()
            info = await r.xpending(stream_key, group_name)
            return info.get("pending", 0) if isinstance(info, dict) else 0
        except Exception:
            grp = self._memory_groups.get(f"{stream_key}:{group_name}", {})
            return len(grp.get("pending", []))

    async def ack(
        self,
        stream_name: StreamName | str,
        group_name: str,
        event_id: str,
    ) -> None:
        stream_key = stream_name.value if isinstance(stream_name, StreamName) else str(stream_name)
        if self.in_memory or stream_key in self._memory_streams:
            grp_key = f"{stream_key}:{group_name}"
            if grp_key in self._memory_groups and "pending" in self._memory_groups[grp_key]:
                if event_id in self._memory_groups[grp_key]["pending"]:
                    self._memory_groups[grp_key]["pending"].remove(event_id)
            return

        try:
            r = await self._get_redis()
            await r.xack(stream_key, group_name, event_id)
        except Exception:
            pass


# Instância singleton compartilhada em nível de módulo
default_event_bus = EventBus(in_memory=True)


class EventConsumer:
    def __init__(
        self,
        bus: EventBus,
        stream_name: StreamName | str,
        group_name: str,
        consumer_name: Optional[str] = None,
    ) -> None:
        self.bus = bus
        self.stream_name = stream_name
        self.stream_key = stream_name.value if isinstance(stream_name, StreamName) else str(stream_name)
        self.group_name = group_name
        self.consumer_name = consumer_name or f"{group_name}-worker-1"

    async def read_stream(self, count: int = 1) -> List[Dict[str, Any]]:
        """
        Lê novos eventos usando Redis Consumer Groups (XGROUP CREATE + XREADGROUP >)
        ou consumo FIFO com controle de offset por grupo em memória.
        """
        return await self.bus.read_stream(
            self.stream_name,
            count=count,
            group_name=self.group_name,
            consumer_name=self.consumer_name,
        )

    async def process_next(
        self,
        handler: Callable[[Dict[str, Any]], Any],
        max_retries: int = 3,
    ) -> bool:
        """
        Consome o próximo evento com política de retentativas determinística
        (exponential backoff 2^n) e DLQ em caso de esgotamento.
        """
        messages = await self.read_stream(count=1)
        if not messages:
            return False

        event = messages[0]
        event_id = event["event_id"]
        ack_id = event.get("redis_msg_id") or event_id

        # Registra pendência no grupo caso não registrado
        grp_key = f"{self.stream_key}:{self.group_name}"
        if grp_key not in self.bus._memory_groups:
            self.bus._memory_groups[grp_key] = {"offset": 0, "pending": []}
        if event_id not in self.bus._memory_groups[grp_key]["pending"]:
            self.bus._memory_groups[grp_key]["pending"].append(event_id)

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                res = handler(event)
                if asyncio.iscoroutine(res):
                    await res
                # Sucesso: confirmação ACK
                await self.bus.ack(self.stream_name, self.group_name, ack_id)
                if ack_id != event_id:
                    await self.bus.ack(self.stream_name, self.group_name, event_id)
                return True
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    await asyncio.sleep(0.001 * (2 ** (attempt - 1)))

        # Esgotou retentativas: Move para Dead-Letter Queue (stream:dlq)
        await self.bus.publish_event(
            stream_name=StreamName.DLQ,
            event_type="event.failed",
            payload={
                "original_stream": self.stream_key,
                "original_event_id": event_id,
                "error": str(last_error),
                "payload": event.get("payload", {}),
            },
            tenant_id=event.get("tenant_id"),
        )
        await self.bus.ack(self.stream_name, self.group_name, ack_id)
        if ack_id != event_id:
            await self.bus.ack(self.stream_name, self.group_name, event_id)
        return False
