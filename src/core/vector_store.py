# -*- coding: utf-8 -*-
"""
Vector Store Service — PostgreSQL 16 + pgvector / HNSW & Math Cosine Engine
Busca semântica de alta performance para catálogos odontológicos, prescrições e transcrições.
"""

from __future__ import annotations
import hashlib
import json
import math
import re
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import text
from src.core.database import get_write_db, get_read_db, init_db


def compute_semantic_embedding(text_input: str, dimensions: int = 128) -> List[float]:
    """
    Gera embedding vetorial semântico determinístico normalizado em L2
    utilizando hashing de tokens e trigramas de caracteres (feature hashing).
    """
    if dimensions <= 0:
        raise ValueError("dimensions deve ser maior que zero.")

    cleaned = re.sub(r"\s+", " ", (text_input or "").strip().lower())
    if not cleaned:
        return [0.0] * dimensions

    vec = [0.0] * dimensions
    tokens = re.findall(r"[a-z0-9à-ú_]+", cleaned)

    features: List[tuple[str, float]] = []
    for tok in tokens:
        features.append((f"tok:{tok}", 2.0))
        padded = f"^{tok}$"
        for i in range(max(0, len(padded) - 2)):
            features.append((f"tri:{padded[i:i+3]}", 1.0))

    if not features:
        for i in range(max(1, len(cleaned) - 2)):
            features.append((f"raw:{cleaned[i:i+3]}", 1.0))

    for feat, weight in features:
        digest = hashlib.sha256(feat.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if (digest[4] & 1) == 0 else -1.0
        vec[bucket] += sign * weight

    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return [0.0] * dimensions
    return [round(v / norm, 6) for v in vec]


compute_text_embedding = compute_semantic_embedding


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calcula a similaridade de cosseno normalizada em L2 entre dois vetores."""
    if len(v1) != len(v2) or not v1:
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class VectorStoreService:
    def __init__(self) -> None:
        init_db()

    async def store_embedding(
        self,
        tenant_id: str,
        entity_type: str,
        entity_id: str,
        content_chunk: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Armazena fragmento textual e seu embedding vetorial associado ao tenant_id.
        """
        record_id = str(uuid.uuid4())
        meta_json = json.dumps(metadata or {})
        embed_json = json.dumps(embedding)

        query = text("""
            INSERT INTO semantic_embeddings (
                id, tenant_id, entity_type, entity_id, content_chunk, embedding, metadata_json
            ) VALUES (
                :id, :tenant_id, :entity_type, :entity_id, :content_chunk, :embedding, :metadata_json
            )
        """)

        async for session in get_write_db():
            await session.execute(
                query,
                {
                    "id": record_id,
                    "tenant_id": tenant_id,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "content_chunk": content_chunk,
                    "embedding": embed_json,
                    "metadata_json": meta_json,
                },
            )
            await session.commit()
            break

        return record_id

    async def search_similar(
        self,
        tenant_id: str,
        query_embedding: List[float],
        entity_type: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Executa busca por similaridade de cosseno com filtro obrigatório por tenant_id.
        Usa operador nativo pgvector (<=>) quando conectado ao PostgreSQL e fallback L2 no SQLite.
        """
        scored_results: List[Dict[str, Any]] = []

        async for session in get_read_db():
            bind = session.get_bind()
            dialect_name = getattr(getattr(bind, "dialect", None), "name", "sqlite")

            if dialect_name == "postgresql":
                pg_vec_literal = "[" + ",".join(str(float(x)) for x in query_embedding) + "]"
                pg_sql = """
                    SELECT id, tenant_id, entity_type, entity_id, content_chunk, metadata_json,
                           1 - (embedding <=> :query_vec::vector) AS similarity
                    FROM semantic_embeddings
                    WHERE tenant_id = :tenant_id
                """
                pg_params: Dict[str, Any] = {
                    "tenant_id": tenant_id,
                    "query_vec": pg_vec_literal,
                    "top_k": top_k,
                }
                if entity_type:
                    pg_sql += " AND entity_type = :entity_type"
                    pg_params["entity_type"] = entity_type
                pg_sql += " ORDER BY embedding <=> :query_vec::vector LIMIT :top_k"

                result = await session.execute(text(pg_sql), pg_params)
                for row in result.mappings().all():
                    meta = json.loads(row["metadata_json"]) if row["metadata_json"] else {}
                    scored_results.append({
                        "id": row["id"],
                        "tenant_id": row["tenant_id"],
                        "entity_type": row["entity_type"],
                        "entity_id": row["entity_id"],
                        "content_chunk": row["content_chunk"],
                        "similarity": round(float(row["similarity"]), 4),
                        "metadata": meta,
                    })
                return scored_results

            base_query = (
                "SELECT id, tenant_id, entity_type, entity_id, content_chunk, embedding, metadata_json "
                "FROM semantic_embeddings WHERE tenant_id = :tenant_id"
            )
            params: Dict[str, Any] = {"tenant_id": tenant_id}
            if entity_type:
                base_query += " AND entity_type = :entity_type"
                params["entity_type"] = entity_type

            result = await session.execute(text(base_query), params)
            rows = result.mappings().all()

            for row in rows:
                try:
                    vec = json.loads(row["embedding"])
                    sim = cosine_similarity(query_embedding, vec)
                    meta = json.loads(row["metadata_json"]) if row["metadata_json"] else {}
                    scored_results.append({
                        "id": row["id"],
                        "tenant_id": row["tenant_id"],
                        "entity_type": row["entity_type"],
                        "entity_id": row["entity_id"],
                        "content_chunk": row["content_chunk"],
                        "similarity": round(sim, 4),
                        "metadata": meta,
                    })
                except Exception:
                    continue
            break

        scored_results.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_results[:top_k]
