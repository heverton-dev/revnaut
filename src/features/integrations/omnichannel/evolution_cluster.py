# -*- coding: utf-8 -*-
"""
Vertical Slice: Evolution API v2 Cluster Sharding
Balanceamento distribuído de instâncias de WhatsApp entre múltiplos nós (100 a 1.000 instâncias).
"""

from __future__ import annotations
import hashlib
import uuid
from typing import Any, Dict, List, Optional
from src.core.database import get_connection, init_db

DEFAULT_SHARDS = [
    "http://evolution-shard-1:8080",
    "http://evolution-shard-2:8080",
    "http://evolution-shard-3:8080"
]

MOCK_QR_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


def select_optimal_shard(
    instance_name: str,
    available_shards: Optional[List[str]] = None,
    account_id: str = "0f14ffff"
) -> str:
    """
    Seleciona deterministicamente o nó de shard com menor carga ativa no cluster.
    Em caso de empate, utiliza consistent hashing sobre o nome da instância.
    """
    init_db()
    shards = available_shards or DEFAULT_SHARDS
    if not shards:
        raise ValueError("Nenhum nó de shard configurado no cluster")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT shard_node_url, COUNT(*) as cnt FROM whatsapp_instances WHERE account_id = ? GROUP BY shard_node_url",
            (account_id,)
        )
        counts = {r["shard_node_url"]: int(r["cnt"]) for r in cur.fetchall()}

        # Ordena prioritariamente pela menor contagem de instâncias, depois por hash determinístico
        def sort_key(s: str):
            c = counts.get(s, 0)
            h = int(hashlib.sha256(f"{instance_name}:{s}".encode("utf-8")).hexdigest()[:8], 16)
            return (c, h)

        sorted_shards = sorted(shards, key=sort_key)
        return sorted_shards[0]
    finally:
        conn.close()


def provision_whatsapp_instance(
    instance_name: str,
    consultant_user_id: Optional[str] = None,
    phone_number: Optional[str] = None,
    account_id: str = "0f14ffff",
    shard_nodes: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Provisiona nova instância da Evolution API v2 no nó de menor carga do cluster.
    """
    init_db()
    clean_name = instance_name.strip()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM whatsapp_instances WHERE instance_name = ? AND account_id = ?",
            (clean_name, account_id)
        )
        existing = cur.fetchone()
        if existing:
            return dict(existing)

        chosen_shard = select_optimal_shard(
            instance_name=clean_name,
            available_shards=shard_nodes,
            account_id=account_id
        )

        instance_id = f"winst-{uuid.uuid4().hex[:8]}"
        cur.execute("""
            INSERT INTO whatsapp_instances (
                id, account_id, instance_name, consultant_user_id,
                shard_node_url, phone_number, status, qr_code_base64
            ) VALUES (?, ?, ?, ?, ?, ?, 'CONNECTING', ?)
        """, (
            instance_id, account_id, clean_name, consultant_user_id,
            chosen_shard, phone_number, MOCK_QR_BASE64
        ))
        conn.commit()

        cur.execute("SELECT * FROM whatsapp_instances WHERE id = ?", (instance_id,))
        return dict(cur.fetchone())
    finally:
        conn.close()


def get_instance(instance_name: str, account_id: str = "0f14ffff") -> Dict[str, Any]:
    """Retorna detalhes da instância do WhatsApp."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM whatsapp_instances WHERE instance_name = ? AND account_id = ?",
            (instance_name.strip(), account_id)
        )
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Instância de WhatsApp '{instance_name}' não encontrada")
        return dict(row)
    finally:
        conn.close()


def list_instances(account_id: str = "0f14ffff") -> List[Dict[str, Any]]:
    """Lista todas as instâncias do cluster no tenant."""
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM whatsapp_instances WHERE account_id = ? ORDER BY created_at DESC",
            (account_id,)
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
