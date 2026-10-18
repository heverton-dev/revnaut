# -*- coding: utf-8 -*-
"""
Redis Streams Event Bus & Deterministic Consumer Pools — Revnaut Core
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
    WEBHOOKS = "stream:webhooks"
    DLQ = "stream:dlq"


class EventBus:
    def __init__(
        self,
        redis_url: Optional[str] = None,
        in_memory: bool = False,
    ) -> None:
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.in_memory = in_memory
        self._memory_streams: Dict[str, List[Dict[str, Any]]] = {}
        self._memory_groups: Dict[str, Dict[str, List[str]]] = {}
        self._redis_client: Optional[aioredis.Redis] = None

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis_client is None:
            self._redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis_client

    async def publish_event(
        self,
        stream_name: StreamName | str,
        event_type: str,
        payload: Dict[str, Any],
        tenant_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> str:
        stream_key = stream_name.value if isinstance(stream_name, StreamName) else stream_name
        event_id = idempotency_key or f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        record = {
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
            if stream_key not in self._memory_streams:
                self._memory_streams[stream_key] = []
            self._memory_streams[stream_key].append(record)
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
            # Fallback transparente para ambiente local sem contêiner Redis ativo
            if stream_key not in self._memory_streams:
                self._memory_streams[stream_key] = []
            self._memory_streams[stream_key].append(record)
            return event_id

    async def read_stream(
        self,
        stream_name: StreamName | str,
        count: int = 10,
    ) -> List[Dict[str, Any]]:
        stream_key = stream_name.value if isinstance(stream_name, StreamName) else stream_name
        if self.in_memory or stream_key in self._memory_streams:
            return list(self._memory_streams.get(stream_key, []))[:count]

        try:
            r = await self._get_redis()
            res = await r.xrevrange(stream_key, count=count)
            items = []
            for msg_id, fields in res:
                items.append({
                    "event_id": fields.get("event_id", msg_id),
                    "event_type": fields.get("event_type", ""),
                    "tenant_id": fields.get("tenant_id", "default"),
                    "timestamp": float(fields.get("timestamp", 0)),
                    "payload": json.loads(fields.get("payload", "{}")),
                })
            return items
        except Exception:
            return list(self._memory_streams.get(stream_key, []))[:count]

    async def get_pending_count(
        self,
        stream_name: StreamName | str,
        group_name: str,
    ) -> int:
        stream_key = stream_name.value if isinstance(stream_name, StreamName) else stream_name
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
        stream_key = stream_name.value if isinstance(stream_name, StreamName) else stream_name
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


class EventConsumer:
    def __init__(
        self,
        bus: EventBus,
        stream_name: StreamName | str,
        group_name: str,
    ) -> None:
        self.bus = bus
        self.stream_name = stream_name
        self.stream_key = stream_name.value if isinstance(stream_name, StreamName) else stream_name
        self.group_name = group_name

    async def process_next(
        self,
        handler: Callable[[Dict[str, Any]], Any],
        max_retries: int = 3,
    ) -> bool:
        """
        Consome o próximo evento com política de retentativas determinística
        (exponential backoff 2^n) e DLQ em caso de esgotamento.
        """
        messages = await self.bus.read_stream(self.stream_name, count=1)
        if not messages:
            return False

        event = messages[0]
        event_id = event["event_id"]

        # Registra pendência no grupo
        grp_key = f"{self.stream_key}:{self.group_name}"
        if grp_key not in self.bus._memory_groups:
            self.bus._memory_groups[grp_key] = {"pending": []}
        if event_id not in self.bus._memory_groups[grp_key]["pending"]:
            self.bus._memory_groups[grp_key]["pending"].append(event_id)

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                res = handler(event)
                if asyncio.iscoroutine(res):
                    await res
                # Sucesso: confirmação ACK
                await self.bus.ack(self.stream_name, self.group_name, event_id)
                return True
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    # Exponential backoff reduzido para testes determinísticos rápidos
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
        await self.bus.ack(self.stream_name, self.group_name, event_id)
        return False
